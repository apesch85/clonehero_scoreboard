from PIL import Image
import pytesseract
import os
import re
import csv
import gspread
from absl import app
from absl import flags

FLAGS = flags.FLAGS
flags.DEFINE_string('img_dir', None, 'Image directory path')
flags.DEFINE_string('csv', None, 'The CSV file path')
flags.DEFINE_string('google_sheet', None, 'The ID of the Google sheet')
flags.DEFINE_string('service_account', None,
                    'Google service account file path')
flags.DEFINE_boolean('remove_screenshots', False,
                     'Delete screenshots after processing')
flags.DEFINE_boolean('remove_captured', False,
                     'Delete only screenshots that were successfully processed')


def GetImages(path):
  file_list = []
  for filename in os.listdir(path):
    if filename.endswith('.png'):
      bw_file = '%s_bw.png' % filename[:-4]
      if not os.path.isfile(bw_file):
        file_path = os.path.join(path, filename)
        file_list.append(file_path)

  return file_list


def ProcessImages(files):
  score_dict = {}
  score_boards = []

  for file_path in files:
    img = Image.open(file_path)
    gray = img.convert('L')
    bw = gray.point(lambda x: 255 if x<100 else 0, '1')
    bw_path = '%s_bw.png' % file_path[:-4]
    bw.save(bw_path)
    score_board = pytesseract.image_to_string(bw)
    score_dict[file_path] = [score_board]

  return score_dict


def FindScores(score_dict):
  scores = []
  broken_boards = []
  stars = ''
  accuracy = ''
  difficulty = ''
  difficulty_list = ['Easy', 'Medium', 'Hard', 'Expert']
  to_delete = []

  for file_path, score_list in score_dict.items():
    score_board = score_list[0]
    match_num = re.search('\d{1,3},\d{1,3},?\d{1,3}', score_board.lower())
    match_score = re.search('score \d*', score_board.lower())
    match_stars = re.search('stars \d', score_board.lower())
    match_accuracy = re.search('(\()(\d{1,3})(\%\))', score_board.lower())
    match_difficulty = re.search('(difficulty )([a-z]{4,6})',
                                 score_board.lower())
    if match_num:
      score = match_num.group(0).split(' ')[0].replace(',', '')
      scores.append(score)
      score_dict[file_path].append(score)
    elif match_score:
      score = match_score.group(0).split(' ')[1]
      score_dict[file_path].append(score)
    else:
      board_list = score_board.splitlines()
      for difficulty in difficulty_list:
        try:
          score = board_list[board_list.index(difficulty) + 1].replace(',', '')
          if score.isdigit():
            score_dict[file_path].append(score)
        except ValueError:
          print('Difficulty: %s not found...' % difficulty)
    if match_stars:
      stars = match_stars.group(0).split(' ')[1]
    if match_accuracy:
      accuracy = match_accuracy.group(2)
    if match_difficulty:
      difficulty = match_difficulty.group(2).lower()

    if len(score_dict[file_path]) > 1:
      if FLAGS.remove_captured:
        os.remove('%s_bw.png' % file_path[:-4])
        os.remove(file_path)
      score_dict[file_path].append(stars)
      score_dict[file_path].append(accuracy)
      score_dict[file_path].append(difficulty)
    else:
      print(score_board.splitlines())
      print('Song: %s doesn\'t have good data. Removing from files to '
            'process...' % file_path)
      to_delete.append(file_path)

  for file_path in to_delete:
    del score_dict[file_path]

  return score_dict


def FindSongInfo(score_dict):
  for file_path in score_dict.keys():
    if file_path.endswith('.png'):
      title = file_path.split('/')[-1][:-19][10:].replace('-', ' ').strip()
      score = score_dict[file_path][1].strip('\'')
      stars = score_dict[file_path][2].strip('\'')
      accuracy = score_dict[file_path][3].strip('\'')
      difficulty = score_dict[file_path][4].strip('\'')
      score_year = file_path.split('/')[-1][-18:][:-4][:4]
      score_month = file_path.split('/')[-1][-18:][:-4][4:][:2]
      score_day = file_path.split('/')[-1][-18:][:-4][6:][:2]
      score_date = '%s-%s-%s' % (score_year, score_month, score_day)
      score_date = score_date.strip('\'')
      score_dict[file_path] = [title, score, difficulty, stars, accuracy,
                               score_date]

  return score_dict


def HandleCsv(csv_path, final_score_dict):
  csv_exists = os.path.isfile(csv_path)
  if csv_exists:
    with open(csv_path, 'r') as read_scores:
      csv_reader = csv.reader(read_scores)
      existing_scores = list(csv_reader)
    compared_scores = ScoreComparer(final_score_dict, existing_scores, 'csv')
    final_score_dict = compared_scores

  if final_score_dict:
    with open(csv_path, 'w') as writer:
      csvwriter = csv.writer(writer)
      for score_details in final_score_dict.values():
        title = score_details[0]
        score = score_details[1]
        stars = score_details[2]
        difficulty = score_details[3]
        accuracy = score_details[4]
        score_date = score_details[5]
        csvwriter.writerow([title, score, difficulty, stars,
                            accuracy, score_date])


def DeleteImages(path):
  for filename in os.listdir(path):
    if filename.endswith('.png'):
     file_path = os.path.join(path, filename)
     os.remove(file_path)


def GoogleSheetHandler(sheet_id, final_score_dict):
  gc = gspread.service_account()
  sh = gc.open(sheet_id)
  worksheet = sh.sheet1
  status_check = worksheet.col_values(1)
  to_delete = []
  row = 2
  cols = ['A', 'B', 'C', 'D', 'E', 'F']
  if len(status_check) == 1:
    for score_details in final_score_dict.values():
      worksheet.update('%s%s:%s%s' % (cols[0], row,
                                      cols[len(cols)-1], row),
                                      [score_details])
      row += 1
  elif len(status_check) > 1:
    row = len(status_check) + 1
    print('Existing scores found! We need to check them first to make sure '
          'we track the highest scores for songs played.')
    existing_scores = worksheet.get_all_values()[1:]
    compared_scores = ScoreComparer(final_score_dict, existing_scores,
                      'google_sheet')
    for file_path, score_details in compared_scores.items():
      try:
        cell = worksheet.find(score_details[0])
      except gspread.exceptions.CellNotFound:
        print('New song: %s found! Adding to tracker...' % score_details[0])
        cell = False
      if cell:
        worksheet.update('%s%s:%s%s' % (cols[0], cell.row,
                                        cols[len(cols) -1], cell.row),
                                        [score_details])
        to_delete.append(file_path)
    for file_path in to_delete:
      del compared_scores[file_path]

    for score_details in compared_scores.values():
      worksheet.update('%s%s:%s%s' % (cols[0], row,
                                      cols[len(cols)-1], row),
                                      [score_details])
      row += 1


def ScoreComparer(new_scores, existing_scores, output_type):
  new_score_list = new_scores.values()
  flattened_scores = [item for sublist in new_score_list for item in sublist]
  best_scores = {}
  to_delete = []
  for song in existing_scores:
    title = song[0]
    score = int(song[1])
    if title in flattened_scores:
      best_score = max(score,
                   int(flattened_scores[flattened_scores.index(title) + 1]))
    else:
      best_score = score
    if best_score > score:
      print('New high score found for: %s | Score: %s' % (title, best_score))
      difficulty = flattened_scores[flattened_scores.index(title) + 2]
      stars = flattened_scores[flattened_scores.index(title) + 3]
      accuracy = flattened_scores[flattened_scores.index(title) + 4]
      date = flattened_scores[flattened_scores.index(title) + 5]
      for file_path, song in new_scores.items():
        if song[0] == title:
          new_scores[file_path] = [title, best_score, difficulty, stars,
                                   accuracy, date]
    elif best_score <= score:
      print('New score not better than existing score for song: %s' % title)
      for file_path, new_song in new_scores.items():
        if new_song[0] == title:
          if output_type == 'google_sheet':
            to_delete.append(file_path)

  for file_path in to_delete:
    del new_scores[file_path]

  return new_scores


def main(argv):
  del argv

  file_list = GetImages(FLAGS.img_dir)
  score_dict = ProcessImages(file_list)
  updated_score_dict = FindScores(score_dict)
  final_score_dict = FindSongInfo(updated_score_dict)

  if FLAGS.csv:
    HandleCsv(FLAGS.csv, final_score_dict)

  if FLAGS.remove_screenshots:
    DeleteImages(FLAGS.img_dir)

  if FLAGS.google_sheet:
    GoogleSheetHandler(FLAGS.google_sheet, final_score_dict)


if __name__ == '__main__':
  app.run(main)

