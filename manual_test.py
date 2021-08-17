import os
from pybeans.app_tool import AppTool
from pybeans.utils import print_color_table

print_color_table()
at = AppTool('test', os.getcwd())
at.D('debug')
at.I('info')
at.E('error')