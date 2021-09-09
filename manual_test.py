import os
from pybeans.app_tool import AppTool
from pybeans.utils import print_color_table

print_color_table()
at = AppTool('test', os.getcwd())
at.D('this is demo output for debug')
at.I('this is demo output for info')
at.W('this is demo output for warn')
at.E('this is demo output for error')