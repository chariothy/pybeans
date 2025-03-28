from decimal import Decimal
from operator import mod
import os
from os import path
from email.utils import formataddr
import functools
import platform
from tkinter import N
from unicodedata import decimal
import warnings
import copy
from datetime import datetime
import time, random, json, re
import hmac
import urllib
import base64, hashlib

from typing import Union, Pattern

from .exception import AppToolError

REG_NUM_INDEX = re.compile(r'\[([\+\-]?\d+)\]')

WIN = 'Windows'
LINUX = 'Linux'
DARWIN = 'Darwin'
OS_SYS = platform.system()

def is_win():
    return OS_SYS == WIN

def is_linux():
    return OS_SYS == LINUX

def is_darwin():
    return OS_SYS == DARWIN

def is_macos():
    return is_darwin()

def cls():
    if is_win():
        os.system('cls')
    elif is_linux() or is_macos():
        os.system('clear')

def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)  # turn off filter
        warnings.warn("Call to deprecated function {}.".format(func.__name__),
                      category=DeprecationWarning,
                      stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)  # reset filter
        return func(*args, **kwargs)
    return new_func

def get_home_dir():
    from os.path import expanduser
    return expanduser('~')


def deep_merge_in(dict1: dict, dict2: dict) -> dict:
    """Deeply merge dictionary2 into dictionary1
    
    Arguments:
        dict1 {dict} -- Dictionary female
        dict2 {dict} -- Dictionary mail to be added to dict1
    
    Returns:
        dict -- Merged dictionary
    """
    if isinstance(dict1, dict) and isinstance(dict2, dict):
        for key in dict2.keys():
            if key in dict1.keys() and isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                deep_merge_in(dict1[key], dict2[key])
            else:
                dict1[key] = dict2[key]
    return dict1


def deep_merge(dict1: dict, dict2: dict) -> dict:
    """Deeply merge dictionary2 and dictionary1 then return a new dictionary
    
    Arguments:
        dict1 {dict} -- Dictionary female
        dict2 {dict} -- Dictionary mail to be added to dict1
    
    Returns:
        dict -- Merged dictionary
    """
    if isinstance(dict1, dict) and isinstance(dict2, dict):
        dict1_copy = dict1.copy()
        for key in dict2.keys():
            if key in dict1.keys() and isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                dict1_copy[key] = deep_merge(dict1[key], dict2[key])
            else:
                dict1_copy[key] = dict2[key]
        return dict1_copy
    return dict1


def send_email(from_addr: str, to_addrs: str, subject: str, text_body: str = '' \
    , smtp_config: dict = {} \
    , html_body: str = None \
    , image_paths: tuple = None, file_paths: tuple = None \
    , debug: bool = False, send_to_file: bool = False, email_file_dir=None \
    ) -> dict:
    """Helper for sending email
    
    Arguments:
        from_addr str -- From address.
            Ex. 'Henry TIAN <henrytian@163.com>'
        to_addrs str -- To address
            Ex. 'Henry TIAN <henrytian@163.com>,Henry TIAN <chariothy@gmail.com>'
        subject {str} -- Email subject
        text_body {str} -- Email text body
        html_body {str} -- Email html body
        image_paths {list|tuple} -- image file path array
        file_paths {list|tuple} -- attachment file path array
        smtp_config {dict} -- SMTP config for SMTPHandler (default: {{}}), Ex.: 
        {
            'host': 'smtp.163.com',
            'port': 465,
            'user': 'henrytian@163.com',
            'pwd': '123456',
            'type': 'ssl'         # plain / ssl (default) / tls
        }
        debug {bool} -- If True output debug info.
        send_to_file {str} -- File path for writing email info to text file.
        
    Returns:
        dict -- Email sending errors. {} if success, else {receiver: message}.
    """
    assert isinstance(from_addr, str)
    assert isinstance(to_addrs, str)
    assert isinstance(subject, str)
    assert text_body or html_body
    assert isinstance(smtp_config, dict)
    assert image_paths is None or isinstance(image_paths, (list, tuple))
    assert file_paths is None or isinstance(file_paths, (list, tuple))

    if send_to_file:
        if not email_file_dir:
            email_file_dir = os.path.join(os.getcwd(), '.logs')
        if not os.path.exists(email_file_dir):
            os.mkdir(email_file_dir)

    #TODO: Use schema to validate smtp_config

    from email.message import EmailMessage
    from email.utils import make_msgid, localtime
    from mimetypes import guess_type

    msg = EmailMessage()
    # generic email headers
    msg['From'] = from_addr
    msg['To'] = to_addrs
    msg['Subject'] = subject.replace('\n', '').replace('\r', '')
    msg['Date'] = localtime()

    # set the plain text body
    msg.set_content(text_body)

    if html_body:
        img_nodes = []
        if image_paths:
            for image_path in image_paths:
                # print(guess_type(image_path)[0].split('/', 1))
                with open(image_path, 'rb') as fp:
                    img_nodes.append({
                        'cid': make_msgid('chariothy_common'),
                        'bin': fp.read(),
                        'type': guess_type(image_path)[0].split('/', 1)
                    })
            # note that we needed to peel the <> off the msgid for use in the html.
            html_body = html_body.format(*(x['cid'][1:-1] for x in img_nodes))
        msg.add_alternative(html_body, subtype='html')

        for img_node in img_nodes:
            maintype, subtype = img_node['type']
            msg.get_payload()[1].add_related(
                img_node['bin'],
                maintype=maintype, 
                subtype=subtype, 
                cid=img_node['cid']
            )

    if file_paths:
        for file_path in file_paths:
            ctype, encoding = guess_type(file_path)
            if ctype is None or encoding is not None:
                # No guess could be made, or the file is encoded (compressed), so
                # use a generic bag-of-bits type.
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)
            
            with open(file_path, 'rb') as fp:
                file_name = os.path.basename(file_path)
                msg.add_attachment(fp.read() \
                    , maintype=maintype \
                    , subtype=subtype \
                    , filename=file_name \
                )
    
    if send_to_file or debug:
        email_file_name = now().replace(' ', '_').replace(':', '-') + '_' + str(random.randint(1000, 9999)) + '.txt'
        from email.policy import SMTP
        with open(os.path.join(email_file_dir, email_file_name), 'wb') as fp:
            fp.write(msg.as_bytes(policy=SMTP))
        result = {}

    if not send_to_file:
        from smtplib import SMTP, SMTP_SSL
        if smtp_config.get('type') == 'ssl':
            server = SMTP_SSL(smtp_config['host'], smtp_config['port'])
        elif smtp_config.get('type') == 'tls':
            server = SMTP(smtp_config['host'], smtp_config['port'])
            server.starttls()
        else:
            server = SMTP(smtp_config['host'], smtp_config['port'])
        
        server.ehlo()
        if debug:
            server.set_debuglevel(1)
        server.login(smtp_config['user'], smtp_config['pwd'])

        #result = server.sendmail(from_addr, to_addrs, msg.as_string())
        result = server.send_message(msg)
        server.quit()
    return result


def alignment(s, space, align='left'):
    """中英文混排对齐
    中英文混排时对齐是比较麻烦的，一个先决条件是必须是等宽字体，每个汉字占2个英文字符的位置。
    用print的格式输出是无法完成的。
    另一个途径就是用字符串的方法ljust, rjust, center先填充空格。但这些方法是以len()为基准的，即1个英文字符长度为1，1个汉字字符长度为3(uft-8编码），无法满足我们的要求。
    本方法的核心是利用字符的gb2312编码，正好长度汉字是2，英文是1。
    
    Arguments:
        s {str} -- 原字符串
        space {int} -- 填充长度
    
    Keyword Arguments:
        align {str} -- 对齐方式 (default: {'left'})
    
    Returns:
        str -- 对齐后的字符串

    Example:
        alignment('My 姓名', ' ', 'right')
    """
    length = len(s.encode('gb2312', errors='ignore'))
    space = space - length if space >= length else 0
    if align == 'left':
        s1 = s + ' ' * space
    elif align == 'right':
        s1 = ' ' * space + s
    elif align == 'center':
        s1 = ' ' * (space // 2) + s + ' ' * (space - space // 2)
    return s1


def get_win_dir(name):
    r"""Get windows folder path
       Read from \HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders
    
    Arguments:
        name {str} -- Name of folder path. 
        Ex. AppData, Favorites, Font, History, Local AppData, My Music, SendTo, Start Menu, Startup
            My Pictures, My Video, NetHood, PrintHood, Programs, Recent Personal, Desktop, Templates
        Note: Personal == My Documents
    """
    assert is_win()
    import winreg
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
    try:
        return winreg.QueryValueEx(key, name)[0]
    except FileNotFoundError:
        return None

@deprecated
def get_win_folder(name):
    return get_win_folder(name)


def get(dictionary: dict, key: str, default=None, check: bool = False, replacement_for_dot_in_key: str = None):
    """Get value in dictionary, keys are connected by dot, and use environment value if exists
    Get dictionary value, 
        - if key exists in environment, use env value,
        - else then if exists in dictionary, use dictionary item value,
        - else then return default value.
    Ex. _dict = {
            'a': {
                'b': 'c', 
                'd': [
                    [{'e': 'f'}]
                ]
            }
        }
        1. get('a.b', 'e') == 'c'
        
        1. get('a.c', 'e') == 'e'
        
        1. getx('a.b[0][0].e') , getx('a.b[-1][0].e')
        - will return 'f'.

    If you have to use item key with dot, you can use replacement_for_dot_in_key.
    Ex. _dict = {'a': {'b.c': 'd'}}
        3. getx('a.b#c', replacement_for_dot_in_key='#')
        - will retuurn 'd' (if no replacement_for_dot_in_key will return None)


    Args:
        dictionary (dict): dictionary data
        key (str): Key for config item which are coneected by dot.
        default (any, optional): Default value if key does exist. Defaults to None.
        replacement_for_dot_in_key (str, optional): To support keys like "a.b". If "#" is given, "a#b" can be recognized as "a.b" . Defaults to None.
        check (bool, optional): If True, func will raise exception if key does not exist . Defaults to False.

    Returns:
        any: return config value
    """
    key_parts = key.split('.')
    config = dictionary
    parsed_keys = []
    
    for key_part in key_parts:
        if replacement_for_dot_in_key:
            key_part = key_part.replace(replacement_for_dot_in_key, '.')
        parsed_keys.append(key_part)
        parsing_key = '.'.join(parsed_keys)
        config_str = f'Config("{parsing_key}")={config}'

        idx_parts = REG_NUM_INDEX.split(key_part)   # REG_NUM_INDEX.split('a[-1][0]') => ['a', '-1', '', '0', '']
        if len(idx_parts) == 1:
            # no numberic index
            # not array, it's a dict
            amend_parsed_key = '.'.join(parsed_keys[:-1])
            config_str = f'Config("{amend_parsed_key}")={config}'
            if check:
                if type(config) is not dict:
                    raise AppToolError(f'Failed to get config at "{parsing_key}": Config is not dict. {config_str}')

                if key_part not in config:
                    raise AppToolError(f'Failed to get config at "{parsing_key}": "{key_part}" is not in config. {config_str}')

            try:
                config = config.get(key_part, default)
            except (AttributeError, TypeError) as ex:
                if check:
                    raise AppToolError(f'Failed to get config at "{parsing_key}": {ex}. {config_str}')
                config = default
        else:
            # has numberic index
            # is list or tuple
            if idx_parts[0] == '':
                raise AppToolError(f'Failed to get config at "{parsing_key}": "{key_part}" should have parent.')
            if idx_parts[-1] != '':
                raise AppToolError(f'Failed to get config at "{parsing_key}": "{key_part}" should be at the tail.')

            key_indexes = list(filter(lambda x: x, idx_parts))
            key_indexes.reverse()
            key_part = key_indexes.pop()
            key_indexes.reverse()
            if type(config) is not dict or key_part not in config:
                raise AppToolError(f'Failed to get config at "{parsing_key}": "{key_part}" is not in config. {config_str}')

            config = config[key_part]
            amend_parsed_keys = parsed_keys[:-1]
            amend_parsed_keys.append(key_part)
            amend_parsed_key = '.'.join(amend_parsed_keys)
            config_str = f'Config("{amend_parsed_key}")={config}'
            if type(config) is not list and type(config) is not tuple:
                raise AppToolError(f'Failed to get config at "{parsing_key}": Config is not list or tuple. {config_str}')
                
            for key_index in key_indexes:
                try:
                    key_index = int(key_index)
                    config = config[key_index]
                except (ValueError, IndexError) as ex:
                    raise AppToolError(f'Failed to get config at "{parsing_key}": Invalid index "{key_index}", {ex}. {config_str}')

    return config


def format_size(size_byte):
    """Format file size
    If size < 1MB, show as KB
    If size < 1GB, show as MB
    ect...

    Args:
        size (float): time size
    """
    units = [
        (1024 * 1024 * 1024 * 1024, 'TB'),
        (1024 * 1024 * 1024, 'GB'),
        (1024 * 1024, 'MB'),
        (1024, 'KB'),
    ]
    
    size_byte = Decimal(str(size_byte))
    for unit in units:
        scale, name = unit
        if size_byte >= scale:
            integ = round(size_byte / scale, 2)
            return f'{normalize_num(integ)}{name}'
    return f'{normalize_num(size_byte)}B'


def normalize_num(num, n=0):
    """Remove needless zero after float
    Ex. 1.500 -> 1.5
        1.000 -> 1

    Args:
        num (float|Decimal): Float number to normailize.
        n (int, optional): Keep n digits. Defaults to 0.

    Returns:
        Decimal: Normalized number.
    """
    if type(num) != Decimal:
        num = Decimal(num)
    if n:
        num = round(num, n)
    return num.to_integral() if num == num.to_integral() else num.normalize()


def format_duration(duration_sec):
    """Format time duration
    If duration < 1s, show as ms
    If duration < 1m, show as s
    ect...

    Args:
        duration (float): time duration
    """
    if duration_sec < 1:
        return f'{normalize_num(duration_sec*1000, 3)}ms'
    
    duration_sec = Decimal(str(duration_sec))
    units = [
        (60 * 60 * 24 * 7, 'w'),
        (60 * 60 * 24, 'd'),
        (60 * 60, 'h'),
        (60, 'm'),
    ]
    
    parts = []
    for unit in units:
        scale, name = unit
        if duration_sec >= scale:
            integ = round(duration_sec / scale)
            duration_sec -= integ * scale
            parts.append(f'{integ}{name}')
    parts.append(f'{normalize_num(duration_sec, 3)}s')
    return ' '.join(parts)


def benchmark(func):
    """This is a decorator which can be used to benchmark time elapsed during running func."""
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        elapsed = end - start
        print(f'Elapsed {format_duration(elapsed)} during running {func.__name__}.')
        return result
    return new_func


def random_sleep(min=0, max=3):
    time.sleep(random.uniform(min, max))


def load_json(file_path, default=None):
    data = default
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf8') as fp:
            data = json.load(fp)
    return data


def dump_json(file_path, data, indent=2, ensure_ascii=False, lock=False):
    dir_path = os.path.dirname(file_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    with open(file_path, 'w', encoding='utf8') as fp:
        if lock and is_win():
            import fcntl
            fcntl.flock(fp, fcntl.LOCK_EX)
        json.dump(data, fp, indent=indent, ensure_ascii=ensure_ascii)


def now(format: str = "%Y-%m-%d %H:%M:%S"):
    """Shortcut

    Args:
        format (str, optional): date time format. Defaults to "%Y-%m-%d %H:%M:%S".

    Returns:
        str: now
    """
    return time.strftime(format, time.localtime())


def today(format: str = "%Y-%m-%d"):
    """Shortcut

    Args:
        format (str, optional): date time format. Defaults to "%Y-%m-%d %H:%M:%S".

    Returns:
        str: today
    """
    return time.strftime(format, time.localtime())


def get_abs_dir(dir: str):
    """Get absolute dir

    Args:
        dir (str): relative path

    Returns:
        str: absolute dir
    """
    return os.path.split(os.path.realpath(dir))[0]


def print_logo(logo_dir: str = __file__):
    """
    print logo for fun
    """
    logo_path = os.path.join(get_abs_dir(logo_dir), 'logo')
    if os.path.exists(logo_path):
        os.system(f'cat {logo_path}')


def print_author(author_dir: str = __file__):
    """
    print author for fun
    """
    logo_path = os.path.join(get_abs_dir(author_dir), 'author')
    if os.path.exists(logo_path):
        os.system(f'cat {logo_path}')
        
        
def cast(original_val, str_val: str):
    """Cast simple type from character
    Ex. int, float, bool, complex
    """
    simple_type = type(original_val)
    if simple_type == str:
        return str_val
    elif simple_type in (int, float, bool, complex):
        return simple_type(str_val)
    else:
        raise ValueError(f'Expect int/float/bool/complex, get {simple_type}')
    
    
def extract_str(reg: Pattern, content: str, default=None):
    """从字符串中提取文本信息

    Args:
        reg (Pattern): 编译后的正则对象
        content (str): 要提取内容的字符串
        default (str|None)
    """
    match = reg.search(content)
    if match:
        groups = match.groups()
        if groups:
            return groups[0].strip()
        else:
            return default
    else:
        return default
    

def find_free_port():
    from contextlib import closing
    import socket
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def print_color_table():
    """
    prints table of formatted text format options
    """
    for style in range(8):
        for fg in range(30, 38):
            s1 = ''
            for bg in range(40, 48):
                format = ';'.join([str(style), str(fg), str(bg)])
                s1 += '\x1b[%sm %s \x1b[0m' % (format, format)
                usage = f'Format: effect;foreground;background (Ex. \\x1b[{format}m {format} \\x1b[0m)'

            print(s1)
        print(usage)
    print()


def timestamp(format: str = "%Y%m%d_%H%M%S")->str:
    return time.strftime(format, time.localtime())


def pad_filename(filename: str, pad: str = None, template: str = None) -> str:
    """Pad some text into filename by template

    Args:
        template (str, optional): [template to pad]. Defaults to None.
        PAD, FILENAME, FILEEXT are available in the template.
        Ex. '{FILENAME}_{PAD}.{FILEEXT}'
        If template is None, '{FILENAME}_`timestamp`.{FILEEXT}' will be used.

    Returns:
        str: [padded filename]
    """
    fpath, fullname = path.split(filename)
    name, ext = path.splitext(fullname)
    if template is None:
        if ext:
            template = '{FILENAME}_{PAD}.{FILEEXT}'
        else:
            template = '{FILENAME}_{PAD}'
        pad = timestamp()
    return path.join(fpath, template.format(FILENAME=name, FILEEXT=ext[1:], PAD=pad))


def run(cmd, echo_cmd=False):
    import subprocess
    try:
        if echo_cmd:
            print(cmd)
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        result = e.output       # Output generated before error
        #code      = e.returncode   # Return code
    return str(result, encoding="utf-8", errors='ignore')


def demo_logging():
    from .app_tool import AppTool
    app = AppTool('pybeans_demo_logging')
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
        

def env():
    return os.environ.get('ENV')


def is_prod():
    return env() == 'prod'


def create_sign_for_dingtalk(secret: str):
    """
    docstring
    """
    timestamp = str(round(time.time() * 1000))
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return timestamp, sign


def help():
    import inspect
    local_vars = locals()
    for name, obj in local_vars.items():
        if inspect.isfunction(obj):
            signature = inspect.signature(obj)
            params = [str(param) for param in signature.parameters.values()]
            print(f"Function: {name}, Parameters: {', '.join(params)}")
            
def get_cached_file(file_path, cache_time=3600, clear_cache=False):
    """
    检查缓存文件是否有效
    
    :param file_name: 目标文件名
    :param cache_dir: 缓存目录(默认当前目录下的.cache)
    :param cache_time: 有效期秒数(默认3600秒)
    :return: 有效返回完整文件路径，否则返回None
    """
   
    # 检查文件是否存在
    if not os.path.exists(file_path):
        return None
    
    # 获取文件修改时间和当前时间
    last_modified = os.path.getmtime(file_path)
    current_time = time.time()
    
    # 检查是否在有效期内
    if (current_time - last_modified) > cache_time:
        if clear_cache:
            os.remove(file_path)
        return None
    
    # 返回绝对路径
    return os.path.abspath(file_path)