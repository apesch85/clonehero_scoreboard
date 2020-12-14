#! /usr/bin/python3

from PIL import Image
import pytesseract
import os
import re
import csv
import pprint
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

def GetImages(path):
  file_list = []
  for filename in os.listdir(path):
    if filename.endswith('.png'):
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
    #bw_path = '%s_bw.png' % file_path[:-4]
    #bw.save(bw_path)
    score_board = pytesseract.image_to_string(bw)
    score_dict[file_path] = [score_board]

  return score_dict


def FindScores(score_dict):
  scores = []
  broken_boards = []
  stars = ''
  accuracy = ''
  difficulty = ''

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
      broken_boards.append(score_board)
    if match_stars:
      stars = match_stars.group(0).split(' ')[1]
    if match_accuracy:
      accuracy = match_accuracy.group(2)
    if match_difficulty:
      difficulty = match_difficulty.group(2)

    if match_num or match_score:
      score_dict[file_path].append(stars)
      score_dict[file_path].append(accuracy)
      score_dict[file_path].append(difficulty)

  return score_dict


def FindSongInfo(score_dict):
  for file_path in score_dict.keys():
    if file_path.endswith('.png'):
      title = file_path.split('/')[-1][:-19][10:].replace('-', ' ').strip()
      print(title)
      score = score_dict[file_path][1]
      stars = score_dict[file_path][2]
      accuracy = score_dict[file_path][3]
      difficulty = score_dict[file_path][4]
      score_year = file_path.split('/')[-1][-18:][:-4][:4]
      score_month = file_path.split('/')[-1][-18:][:-4][4:][:2]
      score_day = file_path.split('/')[-1][-18:][:-4][6:][:2]
      score_date = '%s-%s-%s' % (score_year, score_month, score_day)

      score_dict[file_path] = [title, score, stars, difficulty, accuracy,
                               score_date]

  return score_dict


def CheckCsv(csv_path):
  csv_exists = os.path.isfile(csv_path)

  return csv_exists


def HandleCsv(csv_exists, csv_path, final_score_dict):
  write_mode = 'a' if csv_exists else 'w'
  with open(csv_path, write_mode) as writer:
    csvwriter = csv.writer(writer)
    for score_details in final_score_dict.values():
      title = score_details[0]
      score = score_details[1]
      stars = score_details[2]
      difficulty = score_details[3]
      accuracy = score_details[4]
      score_date = score_details[5]
      csvwriter.writerow([title, score, stars, difficulty,
                          accuracy, score_date])


def DeleteImages(path):
  for filename in os.listdir(path):
    if filename.endswith('.png'):
     file_path = os.path.join(path, filename)
     os.remove(file_path)


def main(argv):
  del argv
  file_list = GetImages(FLAGS.img_dir)
  score_dict = ProcessImages(file_list)
  updated_score_dict = FindScores(score_dict)
  final_score_dict = FindSongInfo(updated_score_dict)
  pprint.pprint(final_score_dict)
  if FLAGS.csv:
    csv_exists = CheckCsv(FLAGS.csv)
    HandleCsv(csv_exists, FLAGS.csv, final_score_dict)
  if FLAGS.remove_screenshots:
    DeleteImages(FLAGS.img_dir)

if __name__ == '__main__':
  app.run(main)
