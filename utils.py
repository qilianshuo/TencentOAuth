import json
import logging
import os
import re
import execjs
import subprocess
import sys

from PIL import Image

logger = logging.getLogger(__name__)


def re_find(pattern: str, text: str) -> str or None:
    """
    简单的正则匹配, 相当于re.findall(pattern, text)[0]
    :param pattern:
    :param text:
    :return: A str or None
    """
    result_list = re.findall(pattern, text)
    if result_list:
        return result_list[0]
    else:
        return None


def save_image(img_path: str, content: bytes) -> bool:
    """
    写入bytes到文件
    :param img_path:
    :param content:
    :return: True || False
    """
    try:
        if os.path.isfile(img_path):
            os.remove(img_path)
        with open(img_path.strip(), 'wb') as f:
            f.write(content)
        return True
    except:
        logger.error("保存图片出错")
        return False


def show_image(img_path: str) -> None:
    """
    根据不同平台调用接口展示图片, 当全部失败时调用Pillow的Image打开图片
    :param img_path:
    :return: None
    """
    try:
        if sys.platform.find('darwin') >= 0:
            subprocess.call(['open', img_path])
        elif sys.platform.find('linux') >= 0:
            subprocess.call(['xdg-open', img_path])
        else:
            os.startfile(img_path)
    except:
        img = Image.open(img_path)
        img.show()
        img.close()


def remove_image(img_path: str) -> bool:
    """
    删除图片
    :param img_path:
    :return: True || False
    """
    try:
        if sys.platform.find('darwin') >= 0:
            os.system("osascript -e 'quit app \"Preview\"'")
        os.remove(img_path)
        return True
    except:
        return False


def get_gtk(p_skey: str) -> int:
    """
    通过p_skey解析出gtk
    :param p_skey:
    :return: gtk
    """
    hash = 5381
    for i in p_skey:
        hash += (hash << 5) + ord(i)
    return str(hash & 2147483647)


def decrypt_qrsig(qrsig: str) -> str:
    """
    通过qrsig解析出ptqrtoken
    :param qrsig:
    :return:ptqrtoken
    """
    e = 0
    for c in qrsig:
        e += (e << 5) + ord(c)
    return str(2147483647 & e)


def parse_list(callback: str) -> list:
    """
    解析类似ptui_checkVC('1','8820730605511823259')的回调函数为列表
    :param callback:str
    :return:list
    """
    callback = callback[callback.find('(') + 1: callback.rfind(')')]
    lis = callback.split(',')
    return [x[1:-1] for x in lis]


def parse_dict(query: str) -> dict:
    """
    解析类似ptui_ckeckVC({"key":"value"})的回调为字典
    :param query:
    :return:dict
    """
    return json.loads(query[query.find('(') + 1: query.rfind(')')])

def init_ui()->str:
    with open('jsCode/ui.js', 'r', encoding='utf-8') as f:
        code = f.read()
    ctx = execjs.compile(code)
    return ctx.call("guid")

if __name__ == "__main__":
    print(get_gtk("L1sJ-zhMTF-OC7AYqESY*9lzuhPXksZYB5UzHD4xn5I_")=="1323152431")