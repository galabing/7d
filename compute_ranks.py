#!/usr/bin/python

import argparse
import cPickle
import os

def compute_ranks(sanitized_dir, open_dates_file, values_dir, ranks_dir):
  tickers = os.listdir(sanitized_dir)
  tickers.sort()
  with open(open_dates_file, 'r') as fp:
    open_dates = fp.read().splitlines()
  open_dates.sort()

  print 'processing %d tickers with %d open dates' % (
      len(tickers), len(open_dates))

  open_dates_map = dict()
  for i in range(len(open_dates)):
    open_dates_map[open_dates[i]] = i

  data = [[] for i in range(len(open_dates))]
  count = 0
  for ticker in tickers:
    with open('%s/%s' % (sanitized_dir, ticker), 'r') as fp:
      dates, prices, volumes = cPickle.load(fp)
    with open('%s/%s' % (values_dir, ticker), 'r') as fp:
      values = cPickle.load(fp)
    assert len(dates) == len(values)
    for i in range(len(dates)):
      index = open_dates_map[dates[i]]
      data[index].append([ticker, values[i]])
    count += 1
    if count % 100 == 0:
      print 'loaded %d files' % count

  ranks_map = dict()
  for ticker in tickers:
    ranks_map[ticker] = []

  # TODO: test test test!
  count = 0
  for tvs in data:
    num = 0
    for tv in tvs:
      if tv[1] is not None:
        num += 1
    tvs.sort(key=lambda item: item[1])
    skip = len(tvs) - num  # For Nones, which are at the top after sorting.
    for i in range(len(tvs)):
      rank = None
      if tvs[i][1] is not None:
        assert i >= skip
        rank = float(i-skip+1)/num
      ranks_map[tvs[i][0]].append(rank)
    count += 1
    if count % 100 == 0:
      print 'processed %d dates' % count

  count = 0
  for ticker, ranks in ranks_map.iteritems():
    with open('%s/%s' % (ranks_dir, ticker), 'w') as fp:
      cPickle.dump(ranks, fp)
    count += 1
    if count % 100 == 0:
      print 'wrote %d files' % count

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--sanitized_dir', required=True)
  parser.add_argument('--open_dates_file', required=True)
  parser.add_argument('--values_dir', required=True)
  parser.add_argument('--ranks_dir', required=True)
  args = parser.parse_args()
  compute_ranks(args.sanitized_dir, args.open_dates_file,
                args.values_dir, args.ranks_dir)

if __name__ == '__main__':
  main()

