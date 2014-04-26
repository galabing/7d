#!/usr/bin/python

import argparse
import cPickle
import math
import os
import threading

PRICE_BONUS = 0.01
VOLUME_BONUS = 1.0
EPS = 1e-5

def partition(items, num_threads):
  group_size = int(len(items)/num_threads)
  group_sizes = [group_size for i in range(num_threads)]
  m = len(items) % num_threads
  for i in range(m):
    group_sizes[i] += 1
  assert sum(group_sizes) == len(items)
  groups = []
  index = 0
  for group_size in group_sizes:
    groups.append(items[index:index+group_size])
    index += group_size
  assert index == len(items)
  return groups

def mean(values):
  return sum(values)/len(values)

def normalize(values):
  m = mean(values)
  normalized_values = [v - m for v in values]
  l = math.sqrt(sum([v*v for v in normalized_values]))
  if l >= EPS:
    normalized_values = [v/l for v in normalized_values]
  return normalized_values

def compute_means(values, index, step, num):
  offset = step*num - 1
  assert index >= offset
  assert step > 0
  return [mean(values[i:i+step])
      for i in range(index - offset, index + 1, step)]

def compute_derivatives(values, bonus):
  return [(values[i+1]-values[i])/(values[i]+bonus)
          for i in range(len(values)-1)]

def compute_features_for_date(prices, volumes, index, step, num, labels):
  if index < step*num - 1:
    return None
  p, v, dp, dv = None, None, None, None
  features = []
  for label in labels:
    if label == 'p':
      if p is None:
        p = compute_means(prices, index, step, num)
      assert len(p) == num
      features.extend(normalize(p))
    elif label == 'v':
      if v is None:
        v = compute_means(volumes, index, step, num)
      assert len(v) == num
      features.extend(normalize(v))
    elif label == 'dp':
      if dp is None:
        if p is None:
          p = compute_means(prices, index, step, num)
        dp = compute_derivatives(p, PRICE_BONUS)
      assert len(dp) == num - 1
      features.extend(normalize(dp))
    else:
      assert label == 'dv'
      if dv is None:
        if v is None:
          v = compute_means(volumes, index, step, num)
        dv = compute_derivatives(v, VOLUME_BONUS)
      assert len(dv) == num - 1
      features.extend(normalize(dv))
  return features

def compute_features_for_ticker(dates, prices, volumes, step, num, labels):
  assert len(dates) == len(prices)
  assert len(dates) == len(volumes)
  features = [None for i in range(len(dates))]
  d = -1
  for i in range(len(dates)):
    features[i] = compute_features_for_date(
        prices, volumes, i, step, num, labels)
    if features[i] is not None:
      if d < 0:
        d = len(features[i])
      else:
        assert len(features[i]) == d
  return features

def compute_features_for_tickers(input_dir, tickers, step, num, labels,
                                 output_dir, thread_name):
  count = 0
  for ticker in tickers:
    with open('%s/%s' % (input_dir, ticker), 'r') as fp:
      dates, prices, volumes = cPickle.load(fp)
    features = compute_features_for_ticker(dates, prices, volumes,
                                           step, num, labels)
    with open('%s/%s' % (output_dir, ticker), 'w') as fp:
      cPickle.dump(features, fp)
    count += 1
    if count % 100 == 0:
      print '%s: %d done' % (thread_name, count)

def compute_features(input_dir, step, num, labels, num_threads,
                     output_dir, overwrite):
  tickers = sorted(os.listdir(input_dir))
  if not overwrite:
    tickers = [ticker for ticker in tickers
               if not os.path.isfile('%s/%s' % (output_dir, ticker))]
  print 'processing %d tickers with %d thread(s)' % (len(tickers), num_threads)
  ticker_groups = partition(tickers, num_threads)
  threads = []
  for i in range(len(ticker_groups)):
    threads.append(threading.Thread(
        target=compute_features_for_tickers,
        args=(input_dir, ticker_groups[i], step, num, labels, output_dir,
              'thread-%d' % i)))
  for thread in threads:
    thread.start()
  for thread in threads:
    thread.join()

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--sanitized_dir', required=True)
  parser.add_argument('--step', required=True)
  parser.add_argument('--num', required=True)
  parser.add_argument('--features', default='p,v,dp,dv')
  parser.add_argument('--num_threads', default=1)
  parser.add_argument('--features_dir', required=True)
  parser.add_argument('--overwrite', action='store_true')
  args = parser.parse_args()
  compute_features(args.sanitized_dir, int(args.step), int(args.num),
                   args.features.split(','), int(args.num_threads),
                   args.features_dir, args.overwrite)

if __name__ == '__main__':
  main()

