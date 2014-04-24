#!/usr/bin/python

import argparse
import cPickle
import datetime
import os

# The earliest possible date in the data set.
MIN_DATE = datetime.datetime(1900, 1, 1)
# The latest possible date in the data set.
MAX_DATE = datetime.datetime.today()
# Minimum number of stocks that trade for a day to be classified as open.
MIN_COUNT = 1000
# Minimum ratio of stocks that trade for a day to be classified as open.
MIN_RATIO = 0.9
# Maximum number of open days missingg consecutively (above this number
# the file will be considered invalid and skipped); below this threshold
# the gap will be filled by linearly interpolating adjacent data points.
MAX_GAP = 0

def init_date_stats():
  num_days = (MAX_DATE - MIN_DATE).days + 1
  return [[0, 0] for i in range(num_days)]

def get_date_from_str(s):
  return datetime.datetime.strptime(s, '%Y-%m-%d')

def get_date_from_line(line):
  dt = line[:line.find(',')]
  return get_date_from_str(dt)

def read_file_to_lines(input_file):
  with open(input_file, 'r') as fp:
    return fp.read().splitlines()

def validate_and_update_date_stats(lines, date_stats):
  assert len(lines) > 1
  assert lines[0] == 'Date,Open,High,Low,Close,Volume,Adj Close'

  # Increment stock count for all days of its lifetime.
  min_date = get_date_from_line(lines[-1])
  max_date = get_date_from_line(lines[1])
  assert min_date >= MIN_DATE
  assert max_date <= MAX_DATE
  min_index = (min_date - MIN_DATE).days
  max_index = (max_date - MIN_DATE).days + 1
  for i in range(min_index, max_index):
    date_stats[i][1] += 1

  # Validate and increment stock count for all days that it's open.
  prev_dt = None
  for i in range(1, len(lines)):
    dt, op, hi, lo, cl, vo, ac = lines[i].split(',')
    if prev_dt is None:
      prev_dt = dt
    else:
      assert dt < prev_dt
    vo, ac = float(vo), float(ac)
    assert vo >= 0
    assert ac > 0
    index = (get_date_from_str(dt) - MIN_DATE).days
    date_stats[index][0] += 1

def get_open_dates(date_stats):
  open_dates = []
  counts = [0, 0]
  for i in range(len(date_stats)):
    if date_stats[i][1] < MIN_COUNT:
      continue
    counts[1] += 1
    if float(date_stats[i][0])/date_stats[i][1] < MIN_RATIO:
      continue
    counts[0] += 1
    date = MIN_DATE + datetime.timedelta(days=i)
    open_dates.append(date.strftime('%Y-%m-%d'))
  r = float(counts[0])/counts[1]
  return open_dates, r

def fill_gap(values):
  if values[0] is None or values[-1] is None:
    return False
  for i in range(1, len(values)):
    if values[i] is not None:
      continue
    j = i + 1
    while j < len(values) and values[j] is None:
      j += 1
    gap = j - i
    if gap > MAX_GAP:
      return False
    values[i] = (values[i-1] + values[j]) / 2.0
  return True

def sanitize_by_open_dates(lines, open_dates):
  dates, prices, volumes = [], [], []
  min_date = lines[-1][:lines[-1].find(',')]
  max_date = lines[1][:lines[1].find(',')]
  i, j = len(lines) - 1, 0
  while i > 0 and j < len(open_dates):
    if open_dates[j] < min_date or open_dates[j] > max_date:
      j += 1
      continue
    ticker_date = lines[i][:lines[i].find(',')]
    if ticker_date < open_dates[j]:
      i -= 1
      continue
    dates.append(open_dates[j])
    if ticker_date > open_dates[j]:
      prices.append(None)
      volumes.append(None)
      j += 1
    else:
      dt, op, hi, lo, cl, vo, ac = lines[i].split(',')
      prices.append(float(ac))
      volumes.append(float(vo))
      i -= 1
      j += 1
  if not fill_gap(prices) or not fill_gap(volumes):
    return None
  return [dates, prices, volumes]

def sanitize(input_dir, output_dir, date_stats_file, open_dates_file):
  input_files = os.listdir(input_dir)
  print 'sanitizing %d files' % len(input_files)

  skip_phase_one = False
  if date_stats_file and os.path.isfile(date_stats_file):
    with open(date_stats_file, 'r') as fp:
      date_stats = cPickle.load(fp)
    skip_phase_one = True
  else:
    date_stats = init_date_stats()

  # Phase one, sanitize basics of input files and collect date stats.
  if not skip_phase_one:
    print 'phase 1: sanitizing basics and collecting date stats'
    count = 0
    for input_file in input_files:
      validate_and_update_date_stats(
          read_file_to_lines('%s/%s' % (input_dir, input_file)), date_stats)
      count += 1
      if count % 100 == 0:
        print '%d done' % count
    if date_stats_file:
      with open(date_stats_file, 'w') as fp:
        cPickle.dump(date_stats, fp)

  # Collect open dates.
  open_dates, r = get_open_dates(date_stats)
  print 'found %d open dates from %s to %s (%.2f%%)' % (
      len(open_dates), open_dates[0], open_dates[-1], r*100)
  if open_dates_file:
    with open(open_dates_file, 'w') as fp:
      for open_date in open_dates:
        print >> fp, open_date

  # Phase two, filter input files by open dates, fill in gaps, and output
  # sanitized files.
  print 'phase 2: filtering by open dates and writing output'
  count = 0
  sanitized, failed = 0, 0
  for input_file in input_files:
    data = sanitize_by_open_dates(
        read_file_to_lines('%s/%s' % (input_dir, input_file)), open_dates)
    if data:
      sanitized += 1
      assert input_file.endswith('.csv')
      output_file = input_file[:input_file.rfind('.')]
      with open('%s/%s' % (output_dir, output_file), 'w') as fp:
        cPickle.dump(data, fp)
    else:
      failed += 1
    count += 1
    if count % 100 == 0:
      print '%d done' % count
  print 'sanitized %d files, failed %d files' % (sanitized, failed)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--input_dir', required=True)
  # If specified, will read date stats from it (if exists) and skip the first
  # phase of validation; or write date stats to it (if doesn't exist) after
  # the first phase, to save time for future runs.
  # NO CHECK ON CONSISTENCY! The data stats file, if exists, must have been
  # generated from the same input data set and params.
  parser.add_argument('--date_stats_file')
  parser.add_argument('--open_dates_file')
  parser.add_argument('--output_dir', required=True)
  args = parser.parse_args()
  sanitize(args.input_dir, args.output_dir,
           args.date_stats_file, args.open_dates_file)

if __name__ == '__main__':
  main()

