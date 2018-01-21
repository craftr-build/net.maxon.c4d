
import functools
import re
import os, sys
import craftr, {path, sh} from 'craftr'
import cxx from '@craftr/cxx'

if sys.platform.startswith('win32'):
  platform = 'win'
elif sys.platform.startswith('darwin'):
  platform = 'mac'
elif sys.platform.startswith('linux'):
  platform = 'linux'
else:
  raise EnvironmentError('unsupported platform: {!r}'.format(sys.platform))

directory = craftr.options.get('maxon-c4d.directory')
version = craftr.options.get('maxon-c4d.version')
url = craftr.options.get('maxon-c4d.url')
release = craftr.options.get('maxon-c4d.release', None)
rtti = craftr.options.get('maxon-c4d.rtti', False)


# ============================================================================
# Determine the Cinema 4D installation directory and release number from the
# current working directory, OR download the Cinema 4D SDK source files if
# a specific version/url is specified.
# ============================================================================

@functools.lru_cache()
def get_c4d_path_and_release():
  path = craftr.options.get('maxon-c4d.directory', __file__) + '/'
  match = re.search(r'(.*Cinema\s+4D\s+R(\d+).*?[/\\])', path, re.I)
  if not match:
    raise EnvironmentError('C4D installation path could not be determined')
  return match.groups()

# If either the version or url options are specified, we download the
# Cinema 4D SDK instead of assuming that we can derive it from the path
# of the currently executed package.
if version or url:
  if not url:
    url = "https://public.niklasrosenstein.com/cinema4d/c4dsdkarchives/c4dsdk-${VERSION}.tar.gz"
  if version:
    url = url.replace('${VERSION}', version)
  elif '${VERSION}' in url:
    raise EnvironmentError('found ${VERSION} variable in .url option, '
      'but .version option is not set')

  directory = path.join(craftr.get_source_archive(url), 'c4dsdk-' + version)
  if not release:
    release = int(float(version.split('-', 1)[0]))
elif not directory:
  directory = get_c4d_path_and_release()[0]

if not release:
  release = int(get_c4d_path_and_release()[1])
else:
  release = int(release)

print('Maxon Cinema 4D SDK R{}'.format(version or release))

# ============================================================================
# Construct paths to all important SDK directories.
# ============================================================================

dirs = {}
dirs['c4d'] = directory
dirs['resource'] = path.join(dirs['c4d'], 'resource')
if release <= 15:
  dirs['source'] = path.join(dirs['resource'], '_api')
else:
  dirs['source'] = path.norm(path.join(dirs['c4d'], 'frameworks/cinema.framework/source'))

# ============================================================================
# Compile the Cinema 4D SDK as a static library.
# ============================================================================

sources = craftr.glob(['**/*.cpp'], parent = dirs['source'])
if not sources:
  raise EnvironmentError('no C4D SDK sources found, source directory'
    ' = "{}"'.format(dirs['source']))

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
    rtti = rtti,
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
  if platform == 'mac':
    defines += ['C4D_COCOA', '__MAC']
    if release >= 15:
      defines += ['MAXON_TARGET_OSX']
  elif platform == 'linux':
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
    flags = sh.split('''
      -fmessage-length=0 -Wno-trigraphs -Wno-missing-field-initializers
      -Wno-non-virtual-dtor -Woverloaded-virtual -Wmissing-braces -Wparentheses
      -Wno-switch -Wunused-function -Wunused-label -Wno-unused-parameter
      -Wunused-variable -Wunused-value -Wno-empty-body -Wno-uninitialized
      -Wunknown-pragmas -Wno-shadow -Wno-conversion -fstrict-aliasing
      -Wdeprecated-declarations -Wno-invalid-offsetof -msse3 -fvisibility=hidden
      -fvisibility-inlines-hidden -Wno-sign-conversion -fno-math-errno''')
    if platform == 'mac':
      flags += sh.split('''
        -mmacosx-version-min=10.6 -Wno-int-conversion -Wno-logical-op-parentheses
        -Wno-shorten-64-to-32 -Wno-enum-conversion -Wno-bool-conversion
        -Wno-constant-conversion''')
  else:
    flags = sh.split('''
      -fmessage-length=0 -Wno-trigraphs -Wmissing-field-initializers
      -Wno-non-virtual-dtor -Woverloaded-virtual -Wmissing-braces -Wparentheses
      -Wno-switch -Wunused-function -Wunused-label -Wno-unused-parameter
      -Wunused-variable -Wunused-value -Wempty-body -Wuninitialized
      -Wunknown-pragmas -Wshadow -Wno-conversion -Wsign-compare -fstrict-aliasing
      -Wdeprecated-declarations -Wno-invalid-offsetof -msse3 -fvisibility=hidden
      -fvisibility-inlines-hidden -Wno-sign-conversion -fno-math-errno''')
    if platform == 'mac':
      flags += sh.split('''
        -mmacosx-version-min=10.7 -Wconstant-conversion -Wbool-conversion
        -Wenum-conversion -Wshorten-64-to-32 -Wint-conversion''')

  if platform == 'mac':
    flags += sh.split('''
      -fdiagnostics-show-note-include-stack -fmacro-backtrace-limit=0
      -fpascal-strings -fasm-blocks -Wno-c++11-extensions -Wno-newline-eof
      -Wno-four-char-constants -Wno-exit-time-destructors
      -Wno-missing-prototypes''')
    # These flags are not usually set in the C4D SDK.
    flags += ['-Wno-unused-private-field']
  elif platform == 'linux':
    flags += sh.split('''
      -Wno-multichar -Wno-strict-aliasing -Wno-shadow -Wno-conversion-null''')

  forced_includes = []
  if platform == 'mac' and release <= 15:
    if debug:
      forced_includes = [path.join(dirs['source'], 'ge_mac_debug_flags.h')]
    else:
      forced_includes = [path.join(dirs['source'], 'ge_mac_flags.h')]
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
    rtti = rtti,
    std = 'c++11',
    forced_includes = forced_includes,
    compiler_flags = flags
  )

else:
  raise RuntimeError(platform)


cxx.prebuilt(
  name = 'craftr-addons',
  includes = [craftr.localpath('include')]
)

cxx.prebuilt(
  name = 'c4d_legacy',
  public_deps = [':craftr-addons', ':c4d'],
  defines = ['__LEGACY_API'],
  forced_includes = [craftr.localpath('include/craftr/c4d_legacy.h')]
)

# ============================================================================
# Find the Cinema 4D Python SDK.
# ============================================================================

if release >= 17:
  version = '2.7'
elif release >= 12:
  version = '2.6'
else:
  version = None

if version:
  if release >= 16:
    resource = path.join(dirs['resource'], 'modules', 'python')
  else:
    resource = path.join(dirs['resource'], 'modules', 'python', 'res')

  if platform == 'win':
    arch = '86' if cxx.compiler.is32bit else '64'
    fw_path = path.join(resource, 'Python.win' + arch + '.framework')
    lib = 'python' + version.replace('.', '')
    lib_path = path.join(fw_path, 'libs', 'python' + version.replace('.', ''))

    # Check if the .lib exists in the subdirectory, otherwise the stuff
    # is directly in the directory above.
    if not path.isfile(path.join(lib_path, lib + '.lib')):
      lib_path = path.dir(lib_path)

    # There are multiple paths where the include directory could be.
    include = path.join(fw_path, 'include', 'python' + version.replace('.', ''))
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
    fw_path = path.join(resource, 'Python.osx.framework')
    lib = 'Python.osx'
    lib_path = fw_path
    lib_full_path = path.join(lib_path, lib)
    include = path.join(fw_path, 'include', 'python' + version)

    cxx.prebuilt(
      name = 'python',
      includes = [include, craftr.localpath('fix/python_api')],
      static_libs = [lib_full_path],
    )
  elif platform == 'linux':
    # TODO: I THINK Cinema 4D comes with system Python? Gotta check.
    cxx.prebuilt(
      name = 'python'
    )
else:
  # Don't do anything, the user will get an error that the "python" target
  # does not exist, and that is because Cinema 4D of that version doesn't
  # come with Python.
  pass
