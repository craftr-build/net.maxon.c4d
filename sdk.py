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

cxc = load_module('lang.cxx').cxc
c4d = session.module.namespace
dirs = c4d.dirs

# Gather a list of the C4D include directories.
include = [
  dirs.source,
  dirs.source + '/c4d_customgui',
  dirs.source + '/c4d_gv',
  dirs.source + '/c4d_libs',
  dirs.source + '/c4d_misc',
  dirs.source + '/c4d_misc/datastructures',
  dirs.source + '/c4d_misc/memory',
  dirs.source + '/c4d_misc/utilities',
  dirs.source + '/c4d_preview',
  dirs.source + '/c4d_scaling',
  dirs.resource + '/res/description'
]
if c4d.options.release <= 15:
  include += glob([
    dirs.resource + '/modules/*/res/description',
    dirs.c4d + '/modules/*/res/description',
    dirs.c4d + '/modules/*/*/res/description'
  ])
else:
  include += glob([dirs.resource + '/modules/*/description'])
include = map(path.norm, include)


def get_windows_framework():
  debug = c4d.options.debug
  arch = 'x64' if '64' in cxc.target_arch else 'x86'

  defines = ['__PC']
  if c4d.options.release >= 15:
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

  if debug:
    flags = []
  else:
    # These are not set by the MSVC interface.
    flags = ['/Oy-', '/Oi', '/Ob2', '/Ot', '/GF']

  if cxc.version >= '19.00.24':
    # Cinema 4D does not properly detect Visual Studio 2015 Update 3 and
    # adds `#define decltype typeof` in compilerdetection.h.
    defines += ['_HAS_DECLTYPE']

  def prepare_link(linker, builder):
    logger.info("prepare_link()")
    logger.info("----------------------------")
    suffix = '.cdl64' if cxc.target_arch == 'x64' else '.cdl'
    builder.option_kwargs.setdefault('suffix', suffix)

  return Framework('maxon.c4d',
    debug = debug,
    include = include,
    defines = defines,
    exceptions = False,
    warn = 'all',
    msvc_disable_warnings = (
      '4062 4100 4127 4131 4201 4210 4242 4244 4245 4305 4310 4324 4355 '
      '4365 4389 4505 4512 4611 4706 4718 4740 4748 4996 4595').split(),
    msvc_warnings_as_errors = ['4264'],
    msvc_compile_additional_flags = (
      '/vmg /vms /w44263 /FC /errorReport:prompt /fp:precise /Zc:wchar_t- '
      '/Gd /TP /WX- /MP /Gm- /Gs /Gy-').split() + flags,
    clangcl_compile_additional_flags = (
      '-Wno-unused-parameter -Wno-macro-redefined -Wno-microsoft-enum-value '
      '-Wno-unused-private-field'.split()
    ),
    cxc_link_prepare_callbacks = [prepare_link]
  )


def get_mac_framework():
  debug = c4d.options.debug
  stdlib = 'stdc++' if options.release <= 15 else 'c++'
  builder.option_kwargs.setdefault('cpp_stdlib', stdlib)

  defines = ['C4D_COCOA', '__MAC']
  if c4d.options.release >= 15:
    defines += ['MAXON_API', 'MAXON_TARGET_OSX']
    defines += ['MAXON_TARGET_DEBUG'] if debug else ['MAXON_TARGET_RELEASE']
    defines += ['MAXON_TARGET_64BIT']
  else:
    defines += ['_DEBUG', 'DEBUG'] if debug else ['NDEBUG']
    defines += ['__C4D_64BIT']
  if legacy_api:
    defines += ['__LEGACY_API']

  if c4d.options.release <= 15:
    flags = (
      '-fmessage-length=0 -fdiagnostics-show-note-include-stack '
      '-fmacro-backtrace-limit=0 -std=c++11 -Wno-trigraphs '
      '-fpascal-strings -Wno-missing-field-initializers -Wno-missing-prototypes '
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
      '-fpascal-strings -Wmissing-field-initializers '
      '-Wmissing-prototypes -Wno-non-virtual-dtor '
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

  def prepare_compile(compiler, builder):
    builder.add_local_framework('maxon.c4d_sdk.mac.compile',
      additional_flags = flags
    )

  return Framework('maxon.c4d_sdk',
    debug = debug,
    defines = defines,
    include = c4d.include,
    exceptions = False,
    forced_include = forced_include,
    cxc_compile_prepare_callbacks = [prepare_compile]
  )


def get_frameworks():
  if platform.name == 'win':
    c4d_sdk = get_windows_framework()
  elif platform.name == 'mac':
    c4d_sdk = get_mac_framework()
  else:
    assert False
  c4d_legacy_sdk = Framework('maxon.c4d_legacy_sdk',
    frameworks = [c4d_sdk],
    defines = ['__LEGACY_API']
  )
  return c4d_sdk, c4d_legacy_sdk
