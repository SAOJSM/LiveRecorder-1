# -*- coding: utf-8 -*-

"""
Author: SAOJSM
GitHub: https://github.com/SAOJSM
Date: 2025-03-18 05:40:00
Update: 2025-03-18 05:40:00
Copyright (c) 2025-2025 by SAOJSM, All Rights Reserved.
"""
import os
import sys
import gettext
import inspect
import builtins
from pathlib import Path


def init_gettext(locale_dir, locale_name):
    gettext.bindtextdomain('zh_TW', locale_dir)
    gettext.textdomain('zh_TW')
    os.environ['LANG'] = f'{locale_name}.utf8'
    return gettext.gettext


execute_dir = os.path.split(os.path.realpath(sys.argv[0]))[0]
if os.path.exists(Path(execute_dir) / '_internal/i18n'):
    locale_path = Path(execute_dir) / '_internal/i18n'
else:
    locale_path = Path(execute_dir) / 'i18n'
_tr = init_gettext(locale_path, 'zh_TW')
original_print = builtins.print
package_name = 'streamget'


def translated_print(*args, **kwargs):
    for arg in args:
        if package_name in inspect.stack()[1].filename:
            translated_arg = _tr(str(arg))
        else:
            translated_arg = str(arg)
        original_print(translated_arg, **kwargs)
