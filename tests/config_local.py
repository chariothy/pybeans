CONFIG = {
    'log': {
        'level': 'INFO',
        'dest': {
            'stdout': True, # None: disabled,
            'file': './logs/app.log',   # None: disabled, 
                                        # PATH: log file path, 
                                        # '': Default path under ./logs/
            'syslog': ('10.8.0.2', 514),    # None: disabled, or (ip, port)
            'mail': 'Henry TIAN <6314849@qq.com>'   # None: disabled,
                                                    # MAIL: send to
                                                    # '': use setting ['mail']['to']
        }
    },
    'smtp': {
        'host': 'smtp.163.com',
    }
}