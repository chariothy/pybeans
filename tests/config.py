CONFIG = {
    'log': {
        'level': 'DEBUG',   # 与log库的level一致，包括DEBUG, INFO, ERROR
                            #   DEBUG   - Enable stdout, file, mail （如果在dest中启用）
                            #   INFO    - Enable file, mail         （如果在dest中启用）
                            #   ERROR   - Enable mail               （如果在dest中启用）
        'dest': {
            'stdout': 1, 
            'file': 0, 
            'mail': 1       # 在mail中设置
        }
    },
    'mail': {
        'from': 'Henry TIAN <chariothy@gmail.com>',
        'to': 'Henry TIAN <chariothy@gmail.com>,Henry TIAN <6314849@qq.com>'
    },
    'smtp': {
        'host': 'smtp.gmail.com',
        'port': 25,
        'user': 'chariothy@gmail.com',
        'pwd': '123456'
    },
    'demo': {
        'host': 'smtp.gmail.com',
        'type': 1   # Env中读取出来的都是字符串，这里测试将Env中的值自动转换类型
    },
    'demo.key': {
        'from': ['Henry TIAN', 'chariothy@gmail.com'],
        'to': [['Henry TIAN', 'chariothy@gmail.com']]
    },
    'demo.key2': {
        'from': ['Henry TIAN', 'chariothy@gmail.com'],
        'to': [['Henry TIAN', 'chariothy@gmail.com']]
    },
}