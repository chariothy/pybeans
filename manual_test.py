import os
from pybeans.app_tool import AppTool
from pybeans.utils import print_color_table

#print_color_table()
app = AppTool('manual_test')
app.demo_logging()

@app.retry(n=3)
def test_retry():
    raise NotImplementedError('Test')

test_retry()