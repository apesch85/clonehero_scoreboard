from PIL import Image
import pytesseract
import os
from score_logic import FindScores
import google_handler
import csv_handler
from absl import app
from absl import flags

FLAGS = flags.FLAGS
flags.DEFINE_string('img_dir', None, 'Image directory path')
flags.DEFINE_string('csv', None, 'The CSV file path')
flags.DEFINE_string('google_sheet', None, 'The ID of the Google sheet')
flags.DEFINE_string('service_account', None,
                    'Google service account file path')
flags.DEFINE_boolean('remove_all_screenshots', False,
                     'Delete all screenshots after processing')
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


def main(argv):
  del argv

  file_list = GetImages(FLAGS.img_dir)
  score_dict = ProcessImages(file_list)
  updated_score_dict = FindScores(score_dict, FLAGS.remove_captured)
  final_score_dict = FindSongInfo(updated_score_dict)

  if FLAGS.csv:
    csv_handler.HandleCsv(FLAGS.csv, final_score_dict)

  if FLAGS.remove_all_screenshots:
    DeleteImages(FLAGS.img_dir)

  if FLAGS.google_sheet:
    google_handler.GoogleSheetHandler(FLAGS.google_sheet, final_score_dict)


if __name__ == '__main__':
  app.run(main)

