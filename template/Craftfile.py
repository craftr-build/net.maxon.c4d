# craftr_module(<module_ident>)
#
# Copyright (C) <Year> <Name>
# All rights reserved.

from craftr import *
session.path.append(path.local('..'))

from craftr.ext.maxon import c4d

objects = c4d.objects(
  sources = path.glob('source/**/*.cpp'),
  include = path.local(['plugin', 'include']),
)

plugin = c4d.link(
  output = path.local('plugin/{}'.format(project_name)),
  inputs = objects,
)
