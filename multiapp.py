#!/usr/bin/env python3

"""
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * - Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer.
 *
 * - Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 *
 * - Neither the name of prim nor the names of its contributors may be used to
 * endorse or promote products derived from this software without specific prior
 * written permission.
 *
 * See the NOTICE file distributed with this work for additional information
 * regarding copyright ownership.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
"""

import argparse
import copy
import gzip
import numpy
import random

def write_matrix(matrix, filename):
  opener = gzip.open if filename.endswith('.gz') else open
  with opener(filename, 'wb') as fd:
    for r in range(matrix.shape[0]):
      row = ''
      for c in range(matrix.shape[1]):
        row += '{},'.format(matrix[r,c])
      row += '\n'
      fd.write(row.encode())

def write_injection(nodes, nodeset, filename):
  opener = gzip.open if filename.endswith('.gz') else open
  with opener(filename, 'wb') as fd:
    inj = ''
    for node in range(nodes):
      inj += '1.0,\n' if node in nodeset else '0.0,\n'
    fd.write(inj.encode())

def random_placement(nodes, apps):
  allnodes = set(range(0, nodes))
  nodesets = [set() for _ in range(apps)]
  app = 0
  while len(allnodes) > 0:
    node = random.sample(allnodes, 1)[0]
    nodesets[app].add(node)
    allnodes.remove(node)
    app = (app + 1) % apps
  return nodesets

def striped_placement(nodes, apps):
  nodesets = [set() for _ in range(apps)]
  app = 0
  for node in range(nodes):
    nodesets[app].add(node)
    app = (app + 1) % apps
  return nodesets

def sequential_placement(nodes, apps):
  nodecounts = [nodes // apps] * apps
  for app in range(apps):
    if sum(nodecounts) == nodes:
      break
    nodecounts[app] += 1
  nodesets = [set() for _ in range(apps)]
  app = 0
  for node in range(nodes):
    nodesets[app].add(node)
    if len(nodesets[app]) == nodecounts[app]:
      app += 1
  return nodesets

placement_funcs = {'random': random_placement,
                   'striped': striped_placement,
                   'sequential': sequential_placement}


def uniform_random_pattern(nodeset, matrix):
  for src in nodeset:
    for dst in nodeset:
      if src != dst:
        matrix[src, dst] = 1.0 / (len(nodeset) - 1)

def uniform_random_self_pattern(nodeset, matrix):
  for src in nodeset:
    for dst in nodeset:
      matrix[src, dst] = 1.0 / len(nodeset)

def random_permutation_pattern(nodeset, matrix):
  dsts = copy.copy(nodeset)
  for src in nodeset:
    while True:
      dst = random.sample(dsts, 1)[0]
      if dst != src or len(dsts) == 1:
        break
    matrix[src, dst] = 1.0
    dsts.remove(dst)

def complement_pattern(nodeset, matrix):
  nodelist = sorted(list(nodeset))
  for src_idx in range(len(nodelist) // 2):
    dst_idx = len(nodelist) - 1 - src_idx
    src = nodelist[src_idx]
    dst = nodelist[dst_idx]
    matrix[src, dst] = 1.0
    matrix[dst, src] = 1.0
  if len(nodelist) % 2 == 1:
    middle = nodelist[len(nodelist) // 2]
    matrix[middle, middle] = 1.0

pattern_funcs = {
  'uniform_random': uniform_random_pattern,
  'uniform_random_self': uniform_random_self_pattern,
  'random_permutation': random_permutation_pattern,
  'complement': complement_pattern,
}


def main(args):
  random.seed(args.seed)

  # use the placement function to create a node set for each app
  nodesets = placement_funcs[args.placement](args.nodes, args.apps)
  if args.verbose:
    for app, nodeset in enumerate(nodesets):
      print('app={} size={}: {}'.format(app, len(nodeset), nodeset))

  # create matrix for each app
  matrices = [numpy.zeros((args.nodes, args.nodes)) for _ in range(args.apps)]
  for app, nodeset in enumerate(nodesets):
    if args.verbose:
      print('creating app {} matrix'.format(app))
    pattern_funcs[args.pattern[app]](nodeset, matrices[app])

  # write matrix file for each app
  for app, matrix in enumerate(matrices):
    if args.verbose:
      print('writing app {} matrix file'.format(app))
    write_matrix(matrix, args.mfile[app])

  # write injection file for each app
  for app, nodeset in enumerate(nodesets):
    if args.verbose:
      print('writing app {} injection file'.format(app))
    write_injection(args.nodes, nodeset, args.ifile[app])


if __name__ == '__main__':
  ap = argparse.ArgumentParser()
  ap.add_argument('nodes', type=int,
                  help='number of nodes')
  ap.add_argument('apps', type=int,
                  help='number of apps')
  ap.add_argument('placement', type=str,
                  choices=placement_funcs.keys(),
                  help='node placement policy for apps')
  ap.add_argument('-p', '--pattern', metavar='P', type=str, nargs='+',
                  choices=pattern_funcs.keys(),
                  help='app traffic pattern')
  ap.add_argument('-s', '--seed', type=int, default=None,
                  help='seed for randomness (if used)')
  ap.add_argument('-m', '--mfile', metavar='F', type=str, nargs='+',
                  help='output matrix file')
  ap.add_argument('-i', '--ifile', metavar='F', type=str, nargs='+',
                  help='output injection file')
  ap.add_argument('-v', '--verbose', action='store_true',
                  help='print various info as the program runs')
  args = ap.parse_args()
  if args.verbose:
    print('Args={}'.format(args))

  assert args.nodes > 0
  assert args.apps > 0
  assert args.nodes > args.apps
  assert args.pattern and len(args.pattern) == args.apps, \
    'give a pattern for each app'
  assert args.mfile and len(args.mfile) == args.apps, \
    'give a mfile for each app'
  assert args.ifile and len(args.ifile) == args.apps, \
    'give a ifile for each app'

  main(args)
