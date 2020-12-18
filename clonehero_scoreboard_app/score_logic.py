import re
import os

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
