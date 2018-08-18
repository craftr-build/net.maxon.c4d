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

__author__ = 'Niklas Rosenstein <rosensteinniklas@gmail.com>'
__version__ = '1.0.0'

import argparse
import glob2
import os
import re
import shutil

parser = argparse.ArgumentParser()
add_arg = parser.add_argument
add_arg('path', help = 'Path to the Cinema 4D installation.')
add_arg('outdir', help = 'The output directory to put the gathered files into.')
add_arg('-C', '--collect-resources', action = 'store_true', help = 'Collect all header and resource files into the SDK main directory.')
add_arg('-V', '--version', type = int, help = 'The Cinema 4D version if it can not be determined from the installation path.')


old_api_maindir = 'resource/_api'
old_api_sources = [
  'resource/_api/**/*',
  'resource/_api_lib/**/*',
]
old_api_resources = [
  'modules/*/res/description/*.h',
  'modules/*/res/description/*.res',
  'modules/*/*/res/description/*.h',
  'modules/*/*/res/description/*.res',
  'resource/res/description/*.h',
  'resource/res/description/*.res',
  'resource/modules/*/res/description/*.h',
  'resource/modules/*/res/description/*.res'
]
new_api_maindir = 'frameworks/cinema.framework/source'
new_api_sources = [
  'frameworks/**/*'
]
new_api_resources = [
  'resource/modules/*/description/*.h',
  'resource/modules/*/description/*.res'
]


def figure_c4d_version_from_path(path):
  base = os.path.basename(path.rstrip('/').rstrip('\\'))
  match = re.match('(\d\d\.\d\d\d)_', base)
  if match:
    parts = match.group(1).split('.')
    return int(parts[0]) * 1000 + int(parts[1])
  match = re.match('cinema.*R(\d\d)(\.\d\d\d)?', base, re.I)
  if match:
    parts = match.group(1), match.group(2).lstrip('.') or '000'
    return int(parts[0]) * 1000 + int(parts[1])
  raise ValueError('unable to detect Cinema 4D version from path: "{}"'
    .format(path))


def makedirs(path):
  if not os.path.isdir(path):
    os.makedirs(path)


def multiglob(patterns, parent = None):
  result = []
  for pattern in patterns:
    if parent: pattern = os.path.join(parent, pattern)
    result += glob2.glob(os.path.normpath(pattern))
  return result


def main():
  args = parser.parse_args()
  if not args.version:
    args.version = figure_c4d_version_from_path(args.path)
  elif args.version < 100:
    args.version = args.version * 1000

  if args.version < 16000:
    maindir = old_api_maindir
    sources = old_api_sources
    resources = old_api_resources
  else:
    maindir = new_api_maindir
    sources = new_api_sources
    resources = new_api_resources

  sources = sorted(multiglob(sources, args.path))
  resources = sorted(multiglob(resources, args.path))

  # Copy the header and source files of the SDK into the output directory
  # with the same folder structure.
  for fn_in in filter(os.path.isfile, sources):
    arcname = os.path.relpath(fn_in, args.path)
    print('Copying', arcname)
    fn_out = os.path.join(args.outdir, arcname)
    makedirs(os.path.dirname(fn_out))
    shutil.copyfile(fn_in, fn_out)

  # Copy the resource files, either pasting them into the SDK main directory
  # where also the header files are placed or in the same folder structure,
  # depending on the settings.
  for fn_in in filter(os.path.isfile, resources):
    arcname = os.path.relpath(fn_in, args.path)
    print('Copying', arcname)
    if args.collect_resources:
      arcname = os.path.join(maindir, os.path.basename(fn_in))
    fn_out = os.path.join(args.outdir, arcname)
    makedirs(os.path.dirname(fn_out))
    shutil.copyfile(fn_in, fn_out)

  # Create a file that denotes the version of the SDK.
  filename = os.path.join(args.outdir, 'c4d-sdk-{}.txt'.format(args.version))
  with open(filename, 'w') as fp:
    print('Generated with extract-c4d-sdk.py', file = fp)


if ('require' in globals() and require.main == module) or __name__ == '__main__':
  main()
