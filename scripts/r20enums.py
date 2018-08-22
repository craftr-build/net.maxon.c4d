# -*- coding: utf8 -*-
# The MIT License (MIT)
#
# Copyright (c) 2018  Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Searches for enum class declarations in R20 frameworks and can output them
as JSON or a pre-R20 legacy header file.
"""

import argparse
import json
import nr.parse
import os
import re
import sys

# Maps the R20 enum and symbol name to the respective R19 enum or symbol name.
# Note: This mapping is incomplete.
R20_RENAMES = {
  'DRAWRESULT': {
    'FAILURE': 'ERROR'
  },
  'USERAREAFLAGS': {
    '$name': 'USERAREA'
  }
}


def parse_header_enums(filename):
  with open(filename, encoding='utf8') as fp:
    scanner = nr.parse.Scanner(fp.read())

  result = []
  while True:
    match = scanner.search(r'.*?enum\s+class\s+(\w+)\s*\{', re.M | re.X)
    if not match: break
    name = match.group(1)
    data = {'name': name, 'symbols': [], 'def': {'filename': filename, 'line': scanner.cursor.lineno-1}}
    while scanner:
      line = scanner.readline().partition('//')[0].strip()
      if not line: continue
      # TODO: Theoretically the closing brace could be on the same lines
      #       as an enumeration item.
      if '}' in line: break
      key, value = line.rstrip(',').partition('=')[::2]
      data['symbols'].append([key.strip(), value.strip() or None])
    result.append(data)

  return result


def get_argument_parser(prog=None):
  parser = argparse.ArgumentParser(prog=prog)
  parser.add_argument(
    'directories',
    nargs='+',
    metavar='DIRECTORY',
    help='One or more MAXON framework directories to parse.'
  )
  parser.add_argument(
    '-f', '--format',
    choices=['json', 'legacy.h'],
    help='Output the enum data in one of the specified formats.'
  )
  return parser


def main(argv=None, prog=None):
  parser = get_argument_parser(prog)
  args = parser.parse_args(argv)

  data = []
  for directory in args.directories:
    for root, dirs, files in os.walk(directory):
      for filename in files:
        if filename.endswith('.h'):
          data += parse_header_enums(os.path.join(root, filename))

  if args.format == 'json':
    json.dump(data, sys.stdout)
  elif args.format == 'legacy.h':
    print('/* Auto-generated using r20enums.py */')
    print('#pragma once')
    print('#if API_VERSION >= 20000')
    for enum in data:
      print()
      print('// enum class {} from "{}" line {}'.format(enum['name'],
        os.path.basename(enum['def']['filename']), enum['def']['line']))
      for sym, _ in enum['symbols']:
        trnl = R20_RENAMES.get(enum['name'], {})
        dest_enum = trnl.get('$name', enum['name'])
        dest_sym = trnl.get(sym, sym)
        print('#define {0}_{1} ({2}::{3})'.format(dest_enum, dest_sym, enum['name'], sym))
        if dest_sym == 'NONE':
          # Most, but not ALL, _0 flags have been renamed to NONE.
          # But we can't just create just the _0 define because the
          # R19 flag may actually use _NONE.
          print('#define {0}_0 ({1}::{2})'.format(dest_enum, enum['name'], sym))
    print()
    print('#endif  // if API_VERSION >= 20000')


if __name__ == '__main__':
  sys.exit(main())
