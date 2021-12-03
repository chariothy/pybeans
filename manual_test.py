import os
from pybeans.app_tool import AppTool
from pybeans.utils import print_color_table

print_color_table()
at = AppTool('test')
at.D('this is demo output for debug')
at.I('this is demo output for info')
at.W('this is demo output for warn')
at.E('this is demo output for error')

at.debug('this is demo output for debug')
at.info('this is demo output for info')
at.warn('this is demo output for warn')
at.error('this is demo output for error')
at.fatal('this is demo output for error')
at.ex('this is demo output for error')