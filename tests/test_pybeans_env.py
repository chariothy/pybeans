import unittest, os, logging

from pybeans import deep_merge, deep_merge_in, benchmark, is_win, is_linux, is_macos, is_darwin
from pybeans import random_sleep, dump_json, load_json, send_email, get
from pybeans import AppTool, AppToolError

from tests import CONFIG, CONFIG_DEV


class CoreTestCase(unittest.TestCase):
    def setUp(self):
        from os import environ as env
        env['TEST_ING_ENV'] = 'dev' # The first TESTING is app_name
        del env['TESTING_MAIL_FROM'], env['TESTING_MAIL_TO']
        
        self.APP_NAME = 'test-ing'
        self.APP = AppTool(self.APP_NAME, os.getcwd())
        #print(self.APP.config)
        #print(env)

    
    def test_get_config(self):
        """
        docstring
        """
        self.assertEqual(CONFIG_DEV['mail']['from'][0], self.APP.get('mail.from[0]'))
        self.assertEqual(CONFIG_DEV['mail']['from'][-1], self.APP['mail.from[-1]'])

        self.assertEqual(CONFIG_DEV['mail']['to'][0][0], self.APP.get('mail.to[0][0]'))

        self.assertEqual(CONFIG_DEV['log']['level'], self.APP['log.level'])
        self.assertEqual(CONFIG_DEV['log']['dest']['file'], self.APP['log.dest.file'])

if __name__ == '__main__':
    unittest.main()