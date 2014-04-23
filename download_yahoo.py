#!/usr/bin/python

import argparse
import os

WGET = '/usr/local/bin/wget'
RETRIES = 5

def download_one(ticker, output_path, retries=RETRIES):
  url = 'http://ichart.finance.yahoo.com/table.csv?s=%s' % ticker
  cmd = '%s -q "%s" -O "%s"' % (WGET, url, output_path)
  for i in range(retries):
    if os.system(cmd) == 0:
      assert os.path.isfile(output_path)
      return True
    print '(download failed for %s, try %d)' % (url, i+1)
    if os.path.isfile(output_path):
      os.remove(output_path)
  return False

def download(ticker_file, output_dir, overwrite):
  with open(ticker_file, 'r') as fp:
    tickers = fp.read().splitlines()
  print 'downloading %d tickers' % len(tickers)

  downloaded, failed, skipped = 0, 0, 0
  for i in range(len(tickers)):
    print 'downloading %d/%d tickers: %s' % (i+1, len(tickers), tickers[i])
    output_path = '%s/%s.csv' % (output_dir, tickers[i])
    if os.path.isfile(output_path):
      if not overwrite:
        skipped += 1
        continue
      os.remove(output_path)
    ok = download_one(tickers[i], output_path)
    if ok:
      downloaded += 1
    else:
      failed += 1

  print 'downloaded: %d, failed: %d, skipped: %d' % (
      downloaded, failed, skipped)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--output_dir', required=True)
  parser.add_argument('--overwrite', action='store_true')
  args = parser.parse_args()
  download(args.ticker_file, args.output_dir, args.overwrite)

if __name__ == '__main__':
  main()

