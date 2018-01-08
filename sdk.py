
import craftr, {path} from 'craftr'
import cxx from 'craftr/lang/cxx'
import {platform, release, dirs, sources} from './BUILD.cr.py'

# Gather a list of the C4D include directories.
include = [
  dirs['source'],
  dirs['source'] + '/c4d_customgui',
  dirs['source'] + '/c4d_gv',
  dirs['source'] + '/c4d_libs',
  dirs['source'] + '/c4d_misc',
  dirs['source'] + '/c4d_misc/datastructures',
  dirs['source'] + '/c4d_misc/memory',
  dirs['source'] + '/c4d_misc/utilities',
  dirs['source'] + '/c4d_preview',
  dirs['source'] + '/c4d_scaling',
  dirs['resource'] + '/res/description'
]
if release <= 15:
  include += craftr.glob(['modules/*/res/description'], parent = dirs['resource'])
  include += craftr.glob(['modules/*/res/description'], parent = dirs['c4d'])
  include += craftr.glob(['modules/*/*/res/description'], parent = dirs['c4d'])
else:
  include += craftr.glob(['modules/*/description'], parent = dirs['resource'])
include = list(map(path.norm, include))

debug = not craftr.is_release

if platform == 'win':
  defines = ['__PC']
  if release >= 15:
    defines += ['MAXON_API', 'MAXON_TARGET_WINDOWS']
    defines += ['MAXON_TARGET_DEBUG'] if debug else ['MAXON_TARGET_RELEASE']
    if cxx.compiler.is64bit:
      defines += ['MAXON_TARGET_64BIT']
  else:
    defines += ['_DEBUG', 'DEBUG'] if debug else ['NDEBUG']
    if cxx.compiler.is64bit:
      defines += ['__C4D_64BIT', 'WIN64', '_WIN64']
    else:
      defines += ['WIN32', '_WIN32']

  if debug:
    flags = []
  else:
    # These are not set by the MSVC interface.
    flags = ['/Oy-', '/Oi', '/Ob2', '/Ot', '/GF']

  if cxx.compiler.id == 'msvc' and cxx.compiler.version >= '19.00.24':
    # Cinema 4D does not properly detect Visual Studio 2015 Update 3 and
    # adds `#define decltype typeof` in compilerdetection.h.
    defines += ['_HAS_DECLTYPE']

  plugin_ext = '.cdl64' if cxx.compiler.is64bit else '.cdl'

  cxx.library(
    name = 'c4d',
    preferred_linkage = 'static',
    srcs = sources,
    outname = 'cinema4d-{}{}$(ext)'.format(cxx.compiler.arch, '' if craftr.is_release else 'd'),
    exceptions = False,
    exported_includes = include,
    exported_defines = defines,
    options = dict(
      msvc_disable_warnings = (
        '4062 4100 4127 4131 4201 4210 4242 4244 4245 4305 4310 4324 4355 '
        '4365 4389 4505 4512 4611 4706 4718 4740 4748 4996 4595 4458').split(),
      msvc_compile_flags =  (
        '/vmg /vms /w44263 /FC /errorReport:prompt /fp:precise /Zc:wchar_t- '
        '/Gd /TP /WX- /MP /Gm- /Gs /Gy-').split() + flags,
      msvc_warnings_as_errors = ['4264'],
      #clangcl_compile_additional_flags = (
      #  '-Wno-unused-parameter -Wno-macro-redefined -Wno-microsoft-enum-value '
      #  '-Wno-unused-private-field'.split()
      #),
      #llvm_compile_additional_flags = (
      #  '-fms-memptr-rep=virtual -fms-memptr-rep=single'.split()  # /vmg /vms
      #),
    )
  )

elif platform in ('mac', 'linux'):
  stdlib = 'stdc++' if release <= 15 else 'c++'

  defines = []
  if name == 'mac':
    defines += ['C4D_COCOA', '__MAC']
    if release >= 15:
      defines += ['MAXON_TARGET_OSX']
  elif name == 'linux':
    defines += ['__LINUX']
    if release >= 15:
      defines += ['MAXON_TARGET_LINUX']
  else:
    assert False

  if release >= 15:
    defines += ['MAXON_API']
    defines += ['MAXON_TARGET_DEBUG'] if debug else ['MAXON_TARGET_RELEASE']
    defines += ['MAXON_TARGET_64BIT']
  else:
    defines += ['_DEBUG', 'DEBUG'] if debug else ['NDEBUG']
    defines += ['__C4D_64BIT']

  if release <= 15:
    flags = shell.split('''
      -fmessage-length=0 -Wno-trigraphs -Wno-missing-field-initializers
      -Wno-non-virtual-dtor -Woverloaded-virtual -Wmissing-braces -Wparentheses
      -Wno-switch -Wunused-function -Wunused-label -Wno-unused-parameter
      -Wunused-variable -Wunused-value -Wno-empty-body -Wno-uninitialized
      -Wunknown-pragmas -Wno-shadow -Wno-conversion -fstrict-aliasing
      -Wdeprecated-declarations -Wno-invalid-offsetof -msse3 -fvisibility=hidden
      -fvisibility-inlines-hidden -Wno-sign-conversion -fno-math-errno''')
    if platform == 'mac':
      flags += shell.split('''
        -mmacosx-version-min=10.6 -Wno-int-conversion -Wno-logical-op-parentheses
        -Wno-shorten-64-to-32 -Wno-enum-conversion -Wno-bool-conversion
        -Wno-constant-conversion''')
  else:
    flags = shell.split('''
      -fmessage-length=0 -Wno-trigraphs -Wmissing-field-initializers
      -Wno-non-virtual-dtor -Woverloaded-virtual -Wmissing-braces -Wparentheses
      -Wno-switch -Wunused-function -Wunused-label -Wno-unused-parameter
      -Wunused-variable -Wunused-value -Wempty-body -Wuninitialized
      -Wunknown-pragmas -Wshadow -Wno-conversion -Wsign-compare -fstrict-aliasing
      -Wdeprecated-declarations -Wno-invalid-offsetof -msse3 -fvisibility=hidden
      -fvisibility-inlines-hidden -Wno-sign-conversion -fno-math-errno''')
    if platform == 'mac':
      flags += shell.split('''
        -mmacosx-version-min=10.7 -Wconstant-conversion -Wbool-conversion
        -Wenum-conversion -Wshorten-64-to-32 -Wint-conversion''')

  if platform == 'mac':
    flags += shell.split('''
      -fdiagnostics-show-note-include-stack -fmacro-backtrace-limit=0
      -fpascal-strings -fasm-blocks -Wno-c++11-extensions -Wno-newline-eof
      -Wno-four-char-constants -Wno-exit-time-destructors
      -Wno-missing-prototypes''')
    # These flags are not usually set in the C4D SDK.
    flags += ['-Wno-unused-private-field']
  elif platform == 'linux':
    flags += shell.split('''
      -Wno-multichar -Wno-strict-aliasing -Wno-shadow -Wno-conversion-null''')

  forced_include = []
  if platform == 'mac' and release <= 15:
    if debug:
      forced_include = [path.join(dirs['source'], 'ge_mac_debug_flags.h')]
    else:
      forced_include = [path.join(dirs['source'], 'ge_mac_flags.h')]
    for f in ['__C4D_64BIT', '__MAC']:  # already in flags header
      try: defines.remove(f)
      except ValueError: pass

  cxx.library(
    name = 'c4d',
    preferred_linkage = 'static',
    srcs = sources,
    exported_includes = include,
    exported_defines = defines,
    exceptions = False,
    std = 'c++11',
    forced_include = forced_include,
  )

else:
  raise RuntimeError(platform)


cxx.prebuilt(
  name = 'c4d_legacy',
  public_deps = [':c4d'],
  defines = ['__LEGACY_API']
)


cxx.prebuilt(
  name = 'craftr-addons',
  includes = [craftr.localpath('include')]
)
