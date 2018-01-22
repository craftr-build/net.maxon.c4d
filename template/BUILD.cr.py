namespace = 'myplugin'
import craftr from 'craftr'
import cxx from '@craftr/cxx'
import c4d from '@craftr/maxon.c4d'

cxx.library(
  name = 'plugin',
  deps = ['//@craftr/maxon.c4d:c4d'],
  srcs = craftr.glob('src/**/*.cpp'),
  includes = ['plugin'],
  outname = craftr.localpath('plugin/' + namespace) + c4d.plugin_ext
)
