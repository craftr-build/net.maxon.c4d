
import craftr, {path, path.join as join} from 'craftr'
import cxx from 'craftr/lang/cxx'
import {release, dirs, platform} from './BUILD.cr.py'

if release >= 17:
  version = '2.7'
elif release >= 12:
  version = '2.6'
else:
  version = None

if release >= 16:
  resource = join(dirs['resource'], 'modules', 'python')
else:
  resource = join(dirs['resource'], 'modules', 'python', 'res')

if platform == 'win':
  arch = '86' if cxx.compiler.is32bit else '64'
  fw_path = join(resource, 'Python.win' + arch + '.framework')
  lib = 'python' + version.replace('.', '')
  lib_path = join(fw_path, 'libs', 'python' + version.replace('.', ''))

  # Check if the .lib exists in the subdirectory, otherwise the stuff
  # is directly in the directory above.
  if not path.isfile(join(lib_path, lib + '.lib')):
    lib_path = path.dir(lib_path)

  # There are multiple paths where the include directory could be.
  include = join(fw_path, 'include', 'python' + version.replace('.', ''))
  if not path.isdir(include):
    include = path.join(path.dir(include), 'python' + version)
  if not path.isdir(include):
    include = path.dir(include)

  cxx.prebuilt(
    name = 'python',
    includes = [include, craftr.localpath('fix/python_api')],
    libpath = [lib_path],
  )
elif platform == 'mac':
  fw_path = join(resource, 'Python.osx.framework')
  lib = 'Python.osx'
  lib_path = fw_path
  lib_full_path = join(lib_path, lib)
  include = join(fw_path, 'include', 'python' + version)

  cxx.prebuilt(
    name = 'python',
    includes = [include, craftr.localpath('fix/python_api')],
    static_libs = [lib_full_path],
  )
elif platform == 'linux':
  cxx.prebuilt(
    name = 'python'
  )
else:
  assert False
