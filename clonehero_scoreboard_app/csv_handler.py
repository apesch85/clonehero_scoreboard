import csv
import os
from score_comparer import ScoreComparer

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
