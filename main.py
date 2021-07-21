from TencentOAuth import TencentOAuth

if __name__ == "__main__":
    # bilibili = TencentOAuth(response_type="code", client_id="101135748",
    #                         redirect_uri="https://passport.bilibili.com/login/snsback?sns=qq&&state=7016e480e9ab11eb9bc5029950f3d232",
    #                         scope="do_like,get_user_info,get_simple_userinfo,get_vip_info,get_vip_rich_info,add_one_blog,list_album,upload_pic,add_album,list_photo,get_info,add_t,del_t,add_pic_t,get_repost_list,get_other_info,get_fanslist,get_idollist,add_idol,del_idol,get_tenpay_addr")
    # bilibili.qr_login()
    vqq = TencentOAuth(
        response_type="code", client_id="101483052",
        redirect_uri="https://access.video.qq.com/user/auth_login?vappid=11059694&vsecret=fdf61a6be0aad57132bc5cdf78ac30145b6cd2c1470b0cfe&raw=1&type=qq&appid=101483052"
    )
    vqq.qr_login()