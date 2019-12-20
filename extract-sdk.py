# Extract the Cinema 4D SDK from a Cinema 4D installation.
# Copyright (C) 2016  Niklas Rosenstein
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = 'Niklas Rosenstein <rosensteinniklas@gmail.com>'
__version__ = '1.0.0'

import argparse
import glob2
import os
import re
import shutil
import sys
import time
import zipfile

parser = argparse.ArgumentParser()
add_arg = parser.add_argument
add_arg('path', help = 'Path to the Cinema 4D installation.')
add_arg('outdir', help = 'The output directory to put the gathered files into.')
add_arg('-C', '--collect-resources', action = 'store_true', help = 'Collect all header and resource files into the SDK main directory.')
add_arg('-V', '--version', type = float, help = 'The Cinema 4D version if it can not be determined from the installation path.')


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
  match = re.search('cinema.*R(\d\d)(\.\d\d\d)?', base, re.I)
  if match:
    if not match.group(2):
      print('warning: minor version could not be detected, specify it '
        'explicitly with --version "R{}.YYY"'.format(match.group(1)),
        file=sys.stderr)
      time.sleep(2)
    parts = match.group(1), (match.group(2) or '000').lstrip('.')
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
    args.version = int(args.version * 1000)

  if args.version < 16000:
    maindir = old_api_maindir
    sources = old_api_sources
    resources = old_api_resources
  elif args.version < 20000:
    maindir = new_api_maindir
    sources = new_api_sources
    resources = new_api_resources
  else:
    maindir = new_api_maindir
    sources = []
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

  # Newer version of C4D deliver an SDK archive out of the box.
  if args.version >= 20000:
    fn_in = os.path.join(args.path, 'sdk.zip')
    print('Unpacking sdk.zip')
    with zipfile.ZipFile(fn_in, 'r') as zp:
      zp.extractall(args.outdir)

  # Create a file that denotes the version of the SDK.
  filename = os.path.join(args.outdir, 'c4d-sdk-{}.txt'.format(args.version))
  with open(filename, 'w') as fp:
    print('Generated with extract-c4d-sdk.py', file = fp)

if __name__ == '__main__':
  main()
