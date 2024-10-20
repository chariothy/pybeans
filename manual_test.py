import os
from pybeans.app_tool import AppTool

#print_color_table()
app = AppTool('manual_test')
app.demo_logging()

@app.retry(n=3)
def test_retry():
    raise NotImplementedError('Test')

try:
    test_retry()
except Exception:
    print('test_retry done.')

app.ding('title', 'body')