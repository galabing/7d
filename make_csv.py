#!/usr/bin/python

import argparse
import cPickle
import os

BASE_DIR = '/Users/linyang/Projects/7d_data'
DATE = '2014-04-22'
SANITIZED_DIR = '%s/sanitized/%s' % (BASE_DIR, DATE)
ATTRIBUTE_DIR = '%s/attributes/%s' % (BASE_DIR, DATE)
# Headers: ticker, date, price, volume, and the following.
ATTRIBUTES = [
  ('return_1', 'r1'),
  ('return_1_rank', 'r1r'),
  ('return_2', 'r2'),
  ('return_2_rank', 'r2r'),
  ('return_3', 'r3'),
  ('return_3_rank', 'r3r'),
  ('return_4', 'r4'),
  ('return_4_rank', 'r4r'),
  ('return_5', 'r5'),
  ('return_5_rank', 'r5r'),
  ('trading_volume_5', 't5'),
  ('trading_volume_5_rank', 't5r'),
  ('trading_volume_20', 't20'),
  ('trading_volume_20_rank', 't20r'),
  ('volatility_5x1', 'v5x1'),
  ('volatility_5x1_rank', 'v5x1r'),
  ('volatility_4x5', 'v4x5'),
  ('volatility_4x5_rank', 'v4x5r'),
]
DELIMITER = '\t'

def v2s(v):
  if v is None:
    return 'null'
  return str(v)

def make_csv(csv_file):
  tickers = os.listdir(SANITIZED_DIR)
  tickers.sort()
  print 'processing %d tickers' % len(tickers)

  csv_fp = open(csv_file, 'w')
  headers = ['ticker', 'date', 'price', 'volume']
  for attribute in ATTRIBUTES:
    headers.append(attribute[0])
  m = len(headers)
  print >> csv_fp, DELIMITER.join(headers)

  count = 0
  for ticker in tickers:
    with open('%s/%s' % (SANITIZED_DIR, ticker), 'r') as fp:
      dates, prices, volumes = cPickle.load(fp)
    n = len(dates)
    assert len(prices) == n
    assert len(volumes) == n
    columns = [[ticker for i in range(n)], dates, prices, volumes]

    for attribute in ATTRIBUTES:
      with open('%s/%s/%s' % (ATTRIBUTE_DIR, attribute[1], ticker), 'r') as fp:
        values = cPickle.load(fp)
      assert len(values) == n
      columns.append(values)

    assert len(columns) == m
    for i in range(n):
      row = [v2s(columns[j][i]) for j in range(m)]
      print >> csv_fp, DELIMITER.join(row)

    count += 1
    if count % 100 == 0:
      print '%d done' % count

  csv_fp.close()

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--csv_file', required=True)
  args = parser.parse_args()
  make_csv(args.csv_file)

if __name__ == '__main__':
  main()

