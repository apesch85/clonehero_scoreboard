from PIL import Image
import pytesseract
import os
from score_logic import FindScores
import google_handler
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


def DeleteImages(path):
  for filename in os.listdir(path):
    if filename.endswith('.png'):
     file_path = os.path.join(path, filename)
     os.remove(file_path)


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

  img_dir = FLAGS.img_dir

  file_list = GetImages(img_dir)
  score_dict = ProcessImages(file_list)
  updated_score_dict = FindScores(score_dict)
  final_score_dict = FindSongInfo(updated_score_dict)

  if FLAGS.csv:
    HandleCsv(FLAGS.csv, final_score_dict)

  if FLAGS.remove_screenshots:
    DeleteImages(img_dir)

  if FLAGS.google_sheet:
    google_handler.GoogleSheetHandler(FLAGS.google_sheet, final_score_dict)



if __name__ == '__main__':
  app.run(main)

