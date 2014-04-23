#!/usr/bin/python

import argparse

def skip(line):
  CONTENTS = ('', '\xc2\xa0', 'Company Ticker')
  for content in CONTENTS:
    if line == content:
      return True
  return False

def clean_line(line):
  if not line.endswith('Russell Indexes.'):
    return line
  PATTERNS = ('As of ', 'As\xc2\xa0of ')
  for pattern in PATTERNS:
    p = line.find(pattern)
    if p > 0:
      return line[:p].rstrip()
  return None

def parse(input_file, output_file):
  with open(input_file, 'r') as fp:
    lines = fp.read().splitlines()
  tickers = []
  for line in lines:
    line = line.strip()
    if skip(line):
      continue
    line = clean_line(line)
    assert line is not None
    p = line.rfind(' ')
    tickers.append(line[p+1:])
  tickers.sort()
  with open(output_file, 'w') as fp:
    for ticker in tickers:
      print >> fp, ticker

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--input_file', required=True)
  parser.add_argument('--output_file', required=True)
  args = parser.parse_args()
  parse(args.input_file, args.output_file)

if __name__ == '__main__':
  main()

