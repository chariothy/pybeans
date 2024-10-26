from os import environ as env

CONFIG = {
    'log': {
        'level': env.get('LOG_LEVEL', 'DEBUG'),   # DEBUG, INFO, ERROR
                            #   DEBUG   - Enable stdout, file, mail （如果在dest中启用）
                            #   INFO    - Enable file, mail         （如果在dest中启用）
                            #   ERROR   - Enable mail               （如果在dest中启用）
        'dest': {
            'stdout': True, # None: disabled,
            'file': '',     # None: disabled, 
                            # PATH: log file path, 
                            # '': Default path under ./logs/
            'syslog': None, # None: disabled, or (ip, port) Ex. ('10.8.0.2', 514)
            'mail': ''      # None: disabled,
                            # MAIL: send to
                            # '': use setting ['mail']['from']
        }
    },
    'mail': {
        'from': env.get('MAIL_FROM', 'Henry TIAN <chariothy@gmail.com>')
    },
    'smtp': {
        'host': env.get('SMTP_HOST', 'smtp.gmail.com'),
        'port': env.get('SMTP_PORT', 465),
        'user': env.get('SMTP_USER', 'chariothy@gmail.com'),
        'pwd': env.get('SMTP_PWD', '123456'),
        'type': env.get('SMTP_TYPE', 'ssl')
    },
    'dingtalk': {                       # 通过钉钉机器人发送通知，具体请见钉钉机器人文档
        'token': env.get('DINGTALK_TOKEN', ''),
        'secret' : env.get('DINGTALK_SECRET', '') # 钉钉机器人的三种验证方式之一为密钥验证
    },
    'demo': {
        'host': env.get('DEMO_HOST', 'smtp.gmail.com'),
        'type': 1   # Env中读取出来的都是字符串，这里测试将Env中的值自动转换类型
    },
    'demo.key': {
        'from': ['Henry TIAN', 'chariothy@gmail.com'],
        'to': [['Henry TIAN', 'chariothy@gmail.com']]
    },
    'demo.key2': {
        'from': ['Henry TIAN', 'chariothy@gmail.com'],
        'to': [['Henry TIAN', 'chariothy@gmail.com']]
    }
}