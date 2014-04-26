#!/usr/bin/python

""" Reindexes sanitized data by dates.  From:
    File: [ticker]
      [date1, ..., dateN] [price1, ..., priceN] [volume1, ..., volumeN]
    To:
    File: [date]
      [ticker1, ..., tickerM] [price1, ..., priceM], [volume1, ..., volumeM]

    Assumes all the output data can be fit into memory!
"""

import argparse
import cPickle
import os

def reindex(input_dir, open_dates_file, output_dir):
  tickers = os.listdir(input_dir)
  tickers.sort()
  with open(open_dates_file, 'r') as fp:
    open_dates = fp.read().splitlines()
  open_dates.sort()

  print 'reindexing %d tickers with %d open dates' % (
      len(tickers), len(open_dates))

  open_dates_map = dict()
  for i in range(len(open_dates)):
    open_dates_map[open_dates[i]] = i

  reindexed_data = [[[], [], []] for i in range(len(open_dates))]
  count = 0
  for ticker in tickers:
    with open('%s/%s' % (input_dir, ticker), 'r') as fp:
      dates, prices, volumes = cPickle.load(fp)
    assert len(dates) == len(prices)
    assert len(dates) == len(volumes)
    for i in range(len(dates)):
      index = open_dates_map[dates[i]]
      reindexed_data[index][0].append(ticker)
      reindexed_data[index][1].append(prices[i])
      reindexed_data[index][2].append(volumes[i])
    count += 1
    if count % 100 == 0:
      print 'loaded %d files' % count

  print 'writing output files for %d dates' % len(reindexed_data)
  count = 0
  for i in range(len(reindexed_data)):
    with open('%s/%s' % (output_dir, open_dates[i]), 'w') as fp:
      cPickle.dump(reindexed_data[i], fp)
    count += 1
    if count % 100 == 0:
      print 'writed %d files' % count

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--sanitized_dir', required=True)
  parser.add_argument('--open_dates_file', required=True)
  parser.add_argument('--reindexed_dir', required=True)
  args = parser.parse_args()
  reindex(args.sanitized_dir, args.open_dates_file, args.reindexed_dir)

if __name__ == '__main__':
  main()

