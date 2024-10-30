from __future__ import absolute_import, print_function

from app.plugins.manager import PluginManager
from app.plugins.base import IPlugin, IPluginEvent, Plugin, PluginConfiguration

plugins = PluginManager()
register = plugins.register
unregister = plugins.unregister