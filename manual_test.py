import os
from pybeans.app_tool import AppTool
from pybeans.utils import print_color_table

print_color_table()
app = AppTool('test')
app.D('this is demo output for debug')
app.I('this is demo output for info')
app.W('this is demo output for warn')
app.E('this is demo output for error')

app.debug('this is demo output for debug')
app.info('this is demo output for info')
app.warn('this is demo output for warn')
app.error('this is demo output for error')
app.fatal('this is demo output for fatal')
try:
    do_nothing()
except Exception:
    app.ex('this is demo output for excatipn')