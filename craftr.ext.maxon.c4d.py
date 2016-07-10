# -*- mode: python -*-
# Copyright (C) 2015 Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from craftr import *
craftr_min_version('1.1.1')

from craftr.path import join, normpath, glob
from craftr.ext import platform, rules
from craftr.ext.compiler import gen_output, gen_objects
from os import environ
import re

is_windows = (platform.name == 'win')
is_osx = (platform.name == 'mac')

if not is_windows and not is_osx:
  raise EnvironmentError('unsupported platform "{0}"'.format(platform.name))

c4d_path = environ.get('maxon.c4d.path', None)
release = int(environ.get('maxon.c4d.release', 0))
debug = environ.get('maxon.c4d.debug', environ.get('debug', False))
mode = 'debug' if debug else 'release'
arch = platform.cxx.desc.get('target')

# =====================================================================
#   Evaluate pre-conditions and detect Cinema 4D path and release
# =====================================================================

def _get_path_and_release():
  path = (c4d_path or __file__) + '/'
  match = re.search(r'(.*Cinema\s+4D\s+R(\d+).*?[/\\])', path, re.I)
  if not match:
    return None, None
  return match.groups()

_data = _get_path_and_release()
if not c4d_path:
  if not _data[0]:
    error('Cinema 4D installation path could not be determined.')
  c4d_path = _data[0]
if not release:
  if not _data[1]:
    error('Cinema 4D release could not be determined.')
  release = int(_data[1])
del _data

resource_dir = join(c4d_path, 'resource')
if release <= 15:
  source_dir = join(resource_dir, '_api')
else:
  source_dir = normpath(c4d_path + '/frameworks/cinema.framework/source')

# =====================================================================
#   Generate source and object file lists and include directories
# =====================================================================

sources = glob(source_dir + '/**/*.cpp')

includes = [
  source_dir,
  source_dir + '/c4d_customgui',
  source_dir + '/c4d_gv',
  source_dir + '/c4d_libs',
  source_dir + '/c4d_misc',
  source_dir + '/c4d_misc/datastructures',
  source_dir + '/c4d_misc/memory',
  source_dir + '/c4d_misc/utilities',
  source_dir + '/c4d_preview',
  source_dir + '/c4d_scaling',
  resource_dir + '/res/description']
if release <= 15:
  includes += glob(resource_dir + '/modules/*/res/description')
  includes += glob(c4d_path + '/modules/*/res/description')
  includes += glob(c4d_path + '/modules/*/*/res/description')
else:
  includes += glob(resource_dir + '/modules/*/description')
includes = normpath(includes)

c4d_framework = Framework('maxon.c4d.',
  include = includes,
  external_libs = [],
)

# =====================================================================
#   Embedded Python support
# =====================================================================

python_ver = None
if release >= 17:
  python_ver = '2.7'
elif release >= 12:
  python_ver = '2.6'

if python_ver:
  if release >= 16:
    python_res = join(resource_dir, 'modules', 'python')
  else:
    python_res = join(resource_dir, 'modules', 'python', 'res')

  if is_windows:
    python_arch = '86' if arch == 'x86' else '64'
    python_fw = join(python_res, 'Python.win' + python_arch + '.framework')
    python_lib = 'python' + python_ver.replace('.', '')
    python_lib_path = join(python_fw, 'libs')
    python_lib_full = join(python_lib_path, python_lib + '.lib')
    python_include = join(python_fw, 'include')

    pylib = Framework(
      include = [python_include, path.local('fix/python_api')],
      libpath = [python_lib_path],
    )
  elif is_osx:
    python_fw = join(python_res, 'Python.osx.framework')
    python_lib = 'Python.osx'
    python_lib_path = python_fw
    python_lib_full = join(python_lib_path, python_lib)
    python_include = join(python_fw, 'include', 'python' + python_ver)

    pylib = Framework(
      include = [python_include, path.local('fix/python_api')],
      external_libs = [python_lib_full],
    )
  else:
    assert False

# =====================================================================
#   Determine application path
# =====================================================================

if is_windows:
  if arch == 'x64':
    if release < 16:
      app = join(c4d_path, 'CINEMA 4D 64 Bit.exe')
    else:
      app = join(c4d_path, 'CINEMA 4D.exe')
  elif arch == 'x86':
    app = join(c4d_path, 'CINEMA 4D.exe')
  else:
    assert False
elif is_osx:
  app = join(c4d_path, 'CINEMA 4D.app/Contents/MacOS/CINEMA 4D')
else:
  assert False

debug_args = ['-debug', '-g_alloc=debug', '-g_console=true']

# =====================================================================
#   Compiler settings
# =====================================================================

def _msvc_compile_hook(builder):
  builder.add_framework(c4d_framework)
  debug = builder.get('debug', options.get_bool('debug'))
  legacy_api = builder.get('legacy_api', False)
  builder.setdefault('exceptions', False)

  rtlib = 'static' if release <= 15 else 'dynamic'
  builder.setdefault('msvc_runtime_library', rtlib)

  defines = ['__PC']
  if release >= 15:
    defines += ['MAXON_API', 'MAXON_TARGET_WINDOWS']
    defines += ['MAXON_TARGET_DEBUG'] if debug else ['MAXON_TARGET_RELEASE']
    if arch == 'x64':
      defines += ['MAXON_TARGET_64BIT']
  else:
    defines += ['_DEBUG', 'DEBUG'] if debug else ['NDEBUG']
    if arch == 'x64':
      defines += ['__C4D_64BIT', 'WIN64', '_WIN64']
    else:
      defines += ['WIN32', '_WIN32']
  if legacy_api:
    defines += ['__LEGACY_API']

  if debug:
    flags = []
  else:
    # These are not set by the MSVC interface.
    flags = ['/Oy-', '/Oi', '/Ob2', '/Ot', '/GF']

  builder.add_framework(Framework('maxon.c4d._msvc_compile_hook',
    defines = defines,
    warn = 'all',
    msvc_disable_warnings = (
      '4062 4100 4127 4131 4201 4210 4242 4244 4245 4305 4310 4324 4355 '
      '4365 4389 4505 4512 4611 4706 4718 4740 4748 4996').split(),
    msvc_warnings_as_errors = ['4264'],
    msvc_additional_flags = (
      '/vmg /vms /w44263 /FC /errorReport:prompt /fp:precise /Zc:wchar_t- '
      '/Gd /TP /WX- /MP /Gm- /Gs /Gy-').split() + flags,
  ), local=True)

def _msvc_link_hook(builder):
  assert arch in ('x86', 'x64'), arch
  builder.add_framework(c4d_framework)
  builder.setdefault('output_type', 'dll')
  builder.setdefault('force_suffix', '.cdl64' if arch == 'x64' else '.cdl')
  if builder.get('output_type') == 'dll':
    builder.setdefault('output_suffix', '.cdl64' if arch == 'x64' else '.cdl')

def _clang_compile_hook(builder):
  builder.add_framework(c4d_framework)
  debug = builder.get('debug', options.get_bool('debug'))
  legacy_api = builder.get('legacy_api', False)
  builder.setdefault('cpp_stdlib', _clang_get_stdlib())

  defines = ['C4D_COCOA', '__MAC']
  if release >= 15:
    defines += ['MAXON_API', 'MAXON_TARGET_OSX']
    defines += ['MAXON_TARGET_DEBUG'] if debug else ['MAXON_TARGET_RELEASE']
    defines += ['MAXON_TARGET_64BIT']
  else:
    defines += ['_DEBUG', 'DEBUG'] if debug else ['NDEBUG']
    defines += ['__C4D_64BIT']
  if legacy_api:
    defines += ['__LEGACY_API']

  if release <= 15:
    flags = (
      '-fmessage-length=0 -fdiagnostics-show-note-include-stack '
      '-fmacro-backtrace-limit=0 -std=c++11 -Wno-trigraphs '
      '-fno-rtti -fpascal-strings '
      '-Wno-missing-field-initializers -Wno-missing-prototypes '
      '-Wno-non-virtual-dtor -Woverloaded-virtual -Wno-exit-time-destructors '
      '-Wmissing-braces -Wparentheses -Wno-switch -Wunused-function '
      '-Wunused-label -Wno-unused-parameter -Wunused-variable -Wunused-value '
      '-Wno-empty-body -Wno-uninitialized -Wunknown-pragmas -Wno-shadow '
      '-Wno-four-char-constants -Wno-conversion -Wno-constant-conversion '
      '-Wno-int-conversion -Wno-bool-conversion -Wno-enum-conversion '
      '-Wno-shorten-64-to-32 -Wno-newline-eof -Wno-c++11-extensions '
      '-fasm-blocks -fstrict-aliasing -Wdeprecated-declarations '
      '-Wno-invalid-offsetof -mmacosx-version-min=10.6 -msse3 '
      '-fvisibility=hidden -fvisibility-inlines-hidden -Wno-sign-conversion '
      '-Wno-logical-op-parentheses -fno-math-errno').split()
  else:
    flags = (
      '-fmessage-length=0 -fdiagnostics-show-note-include-stack '
      '-fmacro-backtrace-limit=0 -std=c++11 -Wno-trigraphs '
      '-fno-rtti -fpascal-strings -Wmissing-field-initializers '
      '-Wmissing-prototypes -Wdocumentation -Wno-non-virtual-dtor '
      '-Woverloaded-virtual -Wno-exit-time-destructors -Wmissing-braces '
      '-Wparentheses -Wno-switch -Wunused-function -Wunused-label '
      '-Wno-unused-parameter -Wunused-variable -Wunused-value -Wempty-body '
      '-Wuninitialized -Wunknown-pragmas -Wshadow -Wno-four-char-constants '
      '-Wno-conversion -Wconstant-conversion -Wint-conversion '
      '-Wbool-conversion -Wenum-conversion -Wsign-compare -Wshorten-64-to-32 '
      '-Wno-newline-eof -Wno-c++11-extensions -fasm-blocks -fstrict-aliasing '
      '-Wdeprecated-declarations -Winvalid-offsetof -mmacosx-version-min=10.7 '
      '-msse3 -fvisibility=hidden -fvisibility-inlines-hidden '
      '-Wno-sign-conversion -fno-math-errno').split()

  # These flags are not usually set in the C4D SDK.
  flags += ['-Wno-unused-private-field']

  forced_include = []
  if release <= 15:
    if debug:
      forced_include = [join(source_dir, 'ge_mac_debug_flags.h')]
    else:
      forced_include = [join(source_dir, 'ge_mac_flags.h')]

  builder.add_framework(Framework('maxon.c4d._clang_compile_hook',
    defines = defines,
    forced_include = forced_include,
    additional_flags = flags
  ), local=True)

def _clang_link_hook(builder):
  builder.add_framework(c4d_framework)
  builder.setdefault('output_type', 'dll')

def _clang_get_stdlib():
  return 'stdc++' if release <= 15 else 'c++'

ar = platform.ar
cxx = platform.cxx.fork()
ld = platform.ld.fork(language='c++')
if platform.cxx.name == 'msvc':
  cxx.register_hook('compile', _msvc_compile_hook)
  ld.register_hook('link', _msvc_link_hook)
elif platform.cxx.name in ('gcc', 'clang', 'llvm'):
  cxx.register_hook('compile', _clang_compile_hook)
  ld.register_hook('link', _clang_link_hook)
else:
  error('unsupported compiler: {0!r}'.format(cxx.name))

def objects(*args, **kwargs):
  return cxx.compile(*args, **kwargs)

def staticlib(*args, **kwargs):
  return ar.staticlib(*args, **kwargs)

def link(*args, **kwargs):
  return ld.link(*args, **kwargs)

# =====================================================================
#   C4D SDK library
# =====================================================================

c4dsdk_lib = staticlib(
  output = 'c4dsdk-r{0}-{1}'.format(release, mode),
  inputs = objects(
    sources = sources
  )
)

c4d_framework['external_libs'] += c4dsdk_lib.outputs

run = rules.run([app] + debug_args)

if is_osx: lldb = rules.run(['lldb', '--', app])

def _update_deps(path):
  # TODO: We can't do this with the "new" re-use of the platform compilers
  run.order_only_deps.append(path)
  if 'lldb' in globals():
    run.order_only_deps.append(path)

# Say Hello!
info(cxx.desc.get('version_str'))
info('Cinema 4D R{0} for {1}'.format(release, arch))
