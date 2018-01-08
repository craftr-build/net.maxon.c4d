

import functools
import re
import os, sys
import craftr, {path} from 'craftr'
import cxx from 'craftr/lang/cxx'

if sys.platform.startswith('win32'):
  platform = 'win'
elif sys.platform.startswith('darwin'):
  platform = 'mac'
elif sys.platform.startswith('linux'):
  platform = 'linux'
else:
  raise EnvironmentError('unsupported platform: {!r}'.format(sys.platform))


@functools.lru_cache()
def get_c4d_path_and_release():
  path = craftr.options.get('maxon-c4d.directory', __file__) + '/'
  match = re.search(r'(.*Cinema\s+4D\s+R(\d+).*?[/\\])', path, re.I)
  if not match:
    raise EnvironmentError('C4D installation path could not be determined')
  return match.groups()


directory = craftr.options.get('maxon-c4d.directory')
version = craftr.options.get('maxon-c4d.version')
url = craftr.options.get('maxon-c4d.url')
release = craftr.options.get('maxon-c4d.release', None)
rtti = craftr.options.get('maxon-c4d.rtti', False)

# If either the version or url options are specified, we download the
# Cinema 4D SDK instead of assuming that we can derive it from the path
# of the currently executed package.
if version or url:
  if not url:
    url = "https://public.niklasrosenstein.com/cinema4dsdk/c4dsdk-${VERSION}.tar.gz"
  if version:
    url = url.replace('${VERSION}', version)
  elif '${VERSION}' in url:
    raise EnvironmentError('found ${VERSION} variable in .url option, '
      'but .version option is not set')

  directory = craftr.get_source_archive(url)
  if not release:
    release = int(float(version.split('-', 1)[0]))
elif not directory:
  directory = get_c4d_path_and_release()[0]

if not release:
  release = int(get_c4d_path_and_release()[1])
else:
  release = int(release)

print('Maxon Cinema 4D SDK R{}'.format(version or release))


# Find important directories in the C4D installation.
dirs = {}
dirs['c4d'] = directory
dirs['resource'] = path.join(dirs['c4d'], 'resource')
if release <= 15:
  dirs['source'] = path.join(dirs['resource'], '_api')
else:
  dirs['source'] = path.norm(path.join(dirs['c4d'], 'frameworks/cinema.framework/source'))

# Gather all SDK source files.
sources = craftr.glob(['**/*.cpp'], parent = dirs['source'])
if not sources:
  raise EnvironmentError('no C4D SDK sources found, source directory'
    ' = "{}"'.format(dirs['source']))

# Load the frameworks.
import {plugin_ext} from './sdk'
import './python'


cxx.library(
  name = 'plugin',
  deps = [':c4d_legacy'],
  srcs = ['main.cpp'],
  outname = 'main' + plugin_ext,
  preferred_linkage = 'shared'
)
