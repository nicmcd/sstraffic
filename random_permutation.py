#!/usr/bin/env python3

"""
 * Copyright (c) 2016, Nic McDonald
 * All rights reserved.
 *
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
import gzip
import numpy
import random

from matrix import writeMatrix

def main(args):
  # check inputs
  assert(args.nodes > 0)

  # initialize the 2D matrix
  matrix = numpy.zeros((args.nodes, args.nodes))

  # create node set
  allnodes = set(range(0, args.nodes))

  # set the permutation
  for src in range(matrix.shape[0]):
    while True:
      dst = random.sample(allnodes, 1)[0]
      if dst != src or args.self:
        break;
    matrix[src, dst] = 1.0
    allnodes.remove(dst)

  # write the matrix to the output file
  writeMatrix(matrix, args.ofile)

if __name__ == '__main__':
  ap = argparse.ArgumentParser()
  ap.add_argument('nodes', type=int,
                  help='number of nodes')
  ap.add_argument('--self', action='store_true',
                  help='allow sending to self')
  ap.add_argument('ofile',
                  help='output file')
  args = ap.parse_args()
  main(args)
