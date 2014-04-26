#!/usr/bin/python

import argparse
import cPickle
import os

DELTA = 0.001
DELIMITER = '\t'

def make_stats(sanitized_dir, values_dir, ranks_dir, open_dates_file, csv_file):
  tickers = os.listdir(sanitized_dir)
  tickers.sort()
  with open(open_dates_file, 'r') as fp:
    open_dates = fp.read().splitlines()
  print 'processing %d tickers with %d open dates' % (
      len(tickers), len(open_dates))

  csv_fp = open(csv_file, 'w')
  headers = ['date', '0%', '10%', '20%', '30%', '40%', '50%', '60%', '70%',
             '80%', '90%', '100%']
  print >> csv_fp, DELIMITER.join(headers)

  open_dates_map = dict()
  for i in range(len(open_dates)):
    open_dates_map[open_dates[i]] = i

  data = [[[] for i in range(11)] for i in range(len(open_dates))]

  count = 0
  delta = DELTA*10
  for ticker in tickers:
    with open('%s/%s' % (sanitized_dir, ticker), 'r') as fp:
      dates, prices, volumes = cPickle.load(fp)
    with open('%s/%s' % (values_dir, ticker), 'r') as fp:
      values = cPickle.load(fp)
    with open('%s/%s' % (ranks_dir, ticker), 'r') as fp:
      ranks = cPickle.load(fp)
    assert len(dates) == len(values)
    assert len(dates) == len(ranks)
    for i in range(len(dates)):
      if ranks[i] is None:
        continue
      rank = ranks[i]*10
      ranki = int(rank)
      if rank - ranki > delta:
        ranki += 1
        if ranki - rank > delta:
          continue
      assert ranki >= 0
      assert ranki < 11
      data[open_dates_map[dates[i]]][ranki].append(values[i])
    count += 1
    if count % 100 == 0:
      print 'processed %d tickers' % count

  for i in range(len(open_dates)):
    row = [open_dates[i]]
    for j in range(11):
      if len(data[i][j]) == 0:
        row.append('null')
        continue
      m = sum(data[i][j])/len(data[i][j])
      row.append('%f' % m)
    print >> csv_fp, DELIMITER.join(row)

  csv_fp.close()

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--sanitized_dir', required=True)
  parser.add_argument('--values_dir', required=True)
  parser.add_argument('--ranks_dir', required=True)
  parser.add_argument('--open_dates_file', required=True)
  parser.add_argument('--csv_file', required=True)
  args = parser.parse_args()
  make_stats(args.sanitized_dir, args.values_dir, args.ranks_dir,
             args.open_dates_file, args.csv_file)

if __name__ == '__main__':
  main()

