#!/usr/bin/python

import argparse
import cPickle
import math
import os

def compute_returns(prices, k, values):
  for i in range(len(prices)-k):
    values[i] = (prices[i+k] - prices[i]) / prices[i]

def compute_trading_volumes(prices, volumes, k, values):
  if k > len(prices):
    return
  trading_volumes = [prices[i]*volumes[i] for i in range(len(prices))]
  for i in range(1, len(trading_volumes)):
    trading_volumes[i] += trading_volumes[i-1]
  values[k-1] = trading_volumes[k-1]
  for i in range(k, len(trading_volumes)):
    values[i] = trading_volumes[i] - trading_volumes[i-k]

def compute_volatilities(prices, num, step, values):
  for i in range(num*step, len(prices)):
    samples = prices[i-num*step:i+1:step]
    returns = [(samples[j]-samples[j-1])/samples[j-1]
               for j in range(1, len(samples))]
    m = sum(returns)/len(returns)
    for j in range(len(returns)):
      returns[j] -= m
    v = 0
    for r in returns:
      v += r*r
    v /= len(returns)
    values[i] = math.sqrt(v)

def compute_attribute_for_one(input_file, attribute, output_file):
  with open(input_file, 'r') as fp:
    dates, prices, volumes = cPickle.load(fp)
  assert len(dates) > 0
  assert len(dates) == len(prices)
  assert len(dates) == len(volumes)
  assert all([price > 0 for price in prices])
  assert all([volume >= 0 for volume in volumes])
  values = [None for i in range(len(prices))]
  if attribute[0] == 'r':
    compute_returns(prices, int(attribute[1:]), values)
  elif attribute[0] == 't':
    compute_trading_volumes(prices, volumes, int(attribute[1:]), values)
  else:
    assert attribute[0] == 'v'
    num, step = attribute[1:].split('x')
    num, step = int(num), int(step)
    compute_volatilities(prices, num, step, values)
  with open(output_file, 'w') as fp:
    cPickle.dump(values, fp)

def compute_attribute(input_dir, attribute, output_dir):
  input_files = os.listdir(input_dir)
  print 'processing %d files for %s' % (len(input_files), attribute)
  count = 0
  for input_file in input_files:
    compute_attribute_for_one(
        '%s/%s' % (input_dir, input_file), attribute,
        '%s/%s' % (output_dir, input_file))
    count += 1
    if count % 100 == 0:
      print '%d done' % count

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--input_dir', required=True)
  parser.add_argument('--attribute', required=True)
  parser.add_argument('--output_dir', required=True)
  args = parser.parse_args()
  compute_attribute(args.input_dir, args.attribute, args.output_dir)

if __name__ == '__main__':
  main()

