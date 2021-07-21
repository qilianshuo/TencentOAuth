import logging
import random
import time

import requests

from utils import re_find, save_image, decrypt_qrsig, show_image, init_ui, get_gtk, remove_image

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s: %(message)s',
    datefmt='%b,%d %H:%M:%S',
    style='%'
)
logger = logging.getLogger(__name__)


class TencentOAuth:
    session = requests.session()
    _cookies = dict()
    buff = dict()

    session.headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
    }

    def __init__(self, response_type: str, client_id: str, redirect_uri: str, state: str = "authorize",
                 scope: str = "get_user_info", display: str = "PC") -> None:
        self.response_type = response_type
        self.client_id = str(client_id)
        self.redirect_uri = redirect_uri
        self.state = state
        self.scope = scope
        self.display = display
        self.buff["pt_3rd_aid"] = self.client_id
        self.init()

    def init(self):
        # QQ互联文档中使用的接口, `oauth2.0/authorize`会进行重定向, 新的地址会执行js继续重定向.
        resp = self.session.get(
            url="https://graph.qq.com/oauth2.0/authorize",
            params={
                "response_type": self.response_type,
                "client_id": self.client_id,
                "redirect_uri": self.redirect_uri,
                "state": self.state,
                "scope": self.scope,
                "display": self.display
            }
        )
        self.buff["refer_url"] = resp.url

        self.buff["api_choose"] = re_find(
            r'<input\sname="api_choose"\shidefocus=".*?"\stype=".*?"\sclass=".*?"\sid=".*?"\svalue="(.*?)"\stitle=".*?"\s.*?/>',
            resp.text)

        self.buff["crtDomain"] = re_find(r"Q.crtDomain\s=\s'(.*?)';", resp.text)
        self.buff["appid"] = re_find(r"appid=(.*?)&", resp.text)
        self.buff["daid"] = re_find(r"daid=(.*?)&", resp.text)
        self.buff["s_url"] = re_find(r"var s_url = '(.*?)';", resp.text)
        self.buff["feed_back_link"] = re_find(r"ar feed_back_link = '(.*?=)'", resp.text) + self.buff.get(
            "crtDomain") + '.appid' + self.client_id

        self.session.headers.update({"referer": "https://graph.qq.com/"})
        ui = requests.cookies.RequestsCookieJar()
        ui.set(name='ui', value=init_ui(), path='/', domain='.graph.qq.com')
        self.session.cookies.update(ui)

        self.update_cookies(self.session.cookies)
        self.buff["ui"] = self._cookies["ui"]

        self.get_pt_login_sig()

    def get_pt_login_sig(self):
        """
        初始化session, 获取登录签名login_sig
        :return: pt_login_sig
        """
        # if self.printLog:
        # print(self.printLog)
        logger.info("正在初始化登录参数, 获取login_sig")
        resp = self.session.get(
            url="https://xui.ptlogin2.qq.com/cgi-bin/xlogin",
            params={
                "appid": self.buff.get("appid"),
                "daid": self.buff.get("daid"),
                "style": "33",
                "theme": "2",
                "login_text": "授权并登录",
                "hide_title_bar": "1",
                "hide_border": "1",
                "target": "self",
                "s_url": self.buff.get("s_url"),
                "pt_3rd_aid": self.buff.get("pt_3rd_aid"),
                "pt_feedback_link": self.buff.get("feed_back_link")
            }
        )
        # dict_keys(['pt_clientip', 'pt_guid_sig', 'pt_local_token', 'pt_login_sig', 'pt_serverip', 'uikey'])
        self.update_cookies(resp.cookies)
        logger.debug("更新的Cookies: " + str(requests.utils.dict_from_cookiejar(resp.cookies)))
        self.buff["pt_login_sig"] = self.get_cookie('pt_login_sig')
        return self.buff.get("pt_login_sig")

    def get_ptqrtoken(self):
        """
        获取二维码
        :return: 二维码标识token
        """
        logger.info("正在获取登录二维码")
        resp = self.session.get(
            url="https://ssl.ptlogin2.qq.com/ptqrshow",
            params={
                "appid": self.buff.get("appid"),
                "e": "2",
                "l": "M",
                "s": "3",
                "d": "72",
                "v": "4",
                "t": str(random.random()),
                "daid": self.buff.get("daid"),
                "pt_3rd_aid": self.buff.get("pt_3rd_aid")
            }
        )
        save_image('qr_code.png', resp.content)
        self.update_cookies(resp.cookies)
        self.buff["qrsig"] = self._cookies.get("qrsig")
        self.buff["ptqrtoken"] = decrypt_qrsig(self._cookies.get("qrsig"))
        return self.buff["ptqrtoken"]

    def waiting_scan(self, ptqrtoken: str) -> str:
        """
        监控接口,获取二维码状态
        :param ptqrtoken:
        :return:重定向url
        """
        logger.info("正在等待扫描二维码")
        show_image('qr_code.png')
        api = "https://ssl.ptlogin2.qq.com/ptqrlogin"
        params = {
            "u1": self.buff.get("s_url"),
            "ptqrtoken": ptqrtoken,
            "ptredirect": "0",
            "h": "1",
            "t": "1",
            "g": "1",
            "from_ui": "1",
            "ptlang": "2052",
            "action": "2-2-" + str(int(time.time())),
            "js_ver": "21071516",
            "js_type": "1",
            "login_sig": self._cookies.get("pt_login_sig"),
            "pt_uistyle": "40",
            "aid": self.buff.get("appid"),
            "daid": self.buff.get("daid"),
            "pt_3rd_aid": self.buff.get("pt_3rd_aid")
        }
        resp = self.session.get(url=api, params=params)
        First = True
        while '登录成功' not in resp.text:
            resp = self.session.get(url=api, params=params)
            if '二维码已失效' in resp.text:
                break
            if First and '认证' in resp.text:
                logger.info("已扫描, 等待确认")
                First = False
            time.sleep(1.5)
        if '登录成功' in resp.text:
            self.buff["nickname"] = resp.text[resp.text.find('(') + 1: resp.text.rfind(')')].split(",")[5].strip()[1:-1]
            logger.info("[" + self.buff.get("nickname") + "] 确认成功")
            # resp.text--ptuiCB('0','0','https://ssl.ptlogin2.graph.qq.com/check_sig?pttype=1……&pt_3rd_aid=101135748','0','登录成功！', '娱乐至死')
            self.update_cookies(resp.cookies)
            return resp.text[resp.text.find('(') + 1: resp.text.rfind(')')].split(",")[2][1:-1]
        else:
            logger.info("二维码已失效, 请重新扫描")
            return self.waiting_scan(self.get_ptqrtoken())

    def qr_login(self):
        redirect_url = self.waiting_scan(self.get_ptqrtoken())
        remove_image('qr_code.png')
        resp = self.session.get(url=redirect_url, allow_redirects=False)
        self.update_cookies(resp.cookies)
        logger.debug("更新的Cookies: " + str(requests.utils.dict_from_cookiejar(resp.cookies)))
        self.buff["p_skey"] = self.get_cookie("p_skey")

        # self.session.get(url=redirect_url)
        self.jump()

    def jump(self):
        resp = self.session.post(
            url="https://graph.qq.com/oauth2.0/authorize",
            data={
                "response_type": self.response_type,
                "client_id": self.client_id,
                "redirect_uri": self.redirect_uri,
                "scope": self.scope,
                "state": self.state,
                "switch": "",
                "from_ptlogin": "1",
                "src": "1",
                "update_auth": "1",
                "openapi": self.buff.get("api_choose"),
                "g_tk": get_gtk(self._cookies.get("p_skey")),
                "auth_time": str(int(time.time() * 1000)),
                "ui": self.buff.get("ui")
            },
            allow_redirects=True
        )
        self.update_cookies(resp.cookies)
        if re_find(r'code=(.*?)&', resp.url) is not None:
            logger.info("Authorization Code: " + re_find(r'code=(.*?)&', resp.url))
        else:
            logger.info("Authorization Code: " + re_find(r'code=(.*)', resp.url))

    def update_cookies(self, cookie_jar: requests.cookies.RequestsCookieJar) -> bool:
        try:
            cookies_dict = requests.utils.dict_from_cookiejar(cookie_jar)
            self._cookies.update(cookies_dict)
            return True
        except:
            return False

    def get_cookies(self) -> dict:
        return self._cookies

    def get_cookie(self, key: str) -> str:
        return self._cookies.get(key)


if __name__ == "__main__":
    """Test"""
    bilibili = TencentOAuth(response_type="code", client_id="101135748",
                            redirect_uri="https://passport.bilibili.com/login/snsback?sns=qq&&state=7016e480e9ab11eb9bc5029950f3d232",
                            scope="do_like,get_user_info,get_simple_userinfo,get_vip_info,get_vip_rich_info,add_one_blog,list_album,upload_pic,add_album,list_photo,get_info,add_t,del_t,add_pic_t,get_repost_list,get_other_info,get_fanslist,get_idollist,add_idol,del_idol,get_tenpay_addr")
    bilibili.qr_login()
