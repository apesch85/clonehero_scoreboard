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
