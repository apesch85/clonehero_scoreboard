import gspread
from score_comparer import ScoreComparer


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
