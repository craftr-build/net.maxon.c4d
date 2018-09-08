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
This is a wrapper for the Cinema 4D source processor that generate a
dependency file for the files that have been parsed to produce the
generated files.
"""

import argparse
import errno
import hashlib
import os
import nr.fs
import subprocess as sp
import shutil
import sys

escape = lambda x: x.replace(' ', '\\ ')


def hash_dir(directory):
  try:
    files = os.listdir(directory)
  except OSError as e:
    if e.errno != errno.ENOENT:
      raise
    files = []
  files.sort()
  hasher = hashlib.md5()
  for filename in files:
    hasher.update(filename.encode('utf8'))
    with open(nr.fs.join(directory, filename), 'rb') as fp:
      data = fp.read()
      while True:
        data = fp.read(2048)
        if not data: break
        hasher.update(data)
  return hasher.hexdigest()


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('sourceprocessor', help='Path to the sourceprocessor.py')
  parser.add_argument('directory', help='The directory to process.')
  parser.add_argument('--write-temp-projectdefinition', action='store_true')
  parser.add_argument('--module-id')
  parser.add_argument('--type')
  parser.add_argument('argv', nargs='...')
  args = parser.parse_args()

  projectdefs = os.path.join(args.directory, 'project', 'projectdefinition.txt')
  remove_project_dir = False
  if args.write_temp_projectdefinition and not os.path.isfile(projectdefs):
    print('Creating temporary projectdefinitions.txt...')
    remove_project_dir = not os.path.isdir(os.path.dirname(projectdefs))
    nr.fs.makedirs(os.path.dirname(projectdefs))
    with open(projectdefs, 'w') as fp:
      if args.type:
        print('Type={}'.format(args.type), file=fp)
      if args.module_id:
        print('ModuleId={}'.format(args.module_id), file=fp)
      print('stylecheck=false'.format(args.type), file=fp)

  # Calculate the current cache of the directory.
  hxx_dir = os.path.join(args.directory, 'generated', 'hxx')
  hxx_hash = hash_dir(hxx_dir)

  try:
    res = sp.call([sys.executable, args.sourceprocessor, args.directory] + args.argv)
    if res != 0:
      sys.exit(res)
  finally:
    if args.write_temp_projectdefinition:
      if remove_project_dir:
        shutil.rmtree(os.path.dirname(projectdefs))
      else:
        os.remove(projectdefs)

  hxx_changed = (hash_dir(hxx_dir) != hxx_hash)

  registercpp = os.path.join(hxx_dir, 'register.cpp')
  if not os.path.isfile(registercpp):
    return

  stampfile = os.path.join(args.directory, 'generated', 'sourceprocessor.stamp')
  if not os.path.isfile(stampfile):
    print('fatal: sourceprocessor.stamp not found')
    sys.exit(1)

  files = []
  with open(stampfile) as fp:
    for line in fp:
      line = line.strip()
      if line and line not in files:
        files.append(os.path.join(args.directory, 'source', line))

  depfile = os.path.join(hxx_dir, 'register.cpp.d')

  print('Writing dependencies file:', depfile)
  with open(depfile, 'w') as fp:
    fp.write('dependencies:')
    for x in files[:-1]:
      fp.write(' ' + escape(x) + ' \\\n')
    if files:
      fp.write(' ' + escape(files[-1]) + '\n')

  # If the register.cpp does not need to be updated, its timestamp will be
  # older than that of the files that were used to parse it. We touch the
  # register.cpp so the build system nows that the update has happened
  # (timestamp newer than the inputs).
  if hxx_changed:
    print('Update timestamp:', registercpp)
    with open(registercpp, 'a'):
      os.utime(registercpp, None)

  return res

if __name__ == '__main__':
  sys.exit(main())
