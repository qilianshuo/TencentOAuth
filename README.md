#  腾讯OAuth快捷认证

> ### 开放平台文档给出了两种认证方式, `Authorization_Code`和`Implicit_Grant`.

- #### Authorization_Code  
  又称Web Server Flow； 适用于需要从web server访问的应用，例如Web网站。  
  其授权验证流程示意图如下（图片来源：OAuth2.0协议草案V21的4.1节 ）
  
  ![img](https://qzonestyle.gtimg.cn/qzone/vas/opensns/res/img/OAuth_guide_V2_1.png)
  
  对于应用而言，需要进行两步：
    1. 获取Authorization Code；  
    2. 通过Authorization Code获取Access Token

  ##### Step1：获取Authorization Code  
  - url
    > https://graph.qq.com/oauth2.0/authorize
  
  - Method
    > GET
    
  - Params
    > |     参数      | 是否必须 |                             含义                             |
    > | :-----------: | :------: | :----------------------------------------------------------: |
    > | response_type |   必须   |                 授权类型，此值固定为“code”。                 |
    > |   client_id   |   必须   |            申请QQ登录成功后，分配给应用的appid。             |
    > | redirect_uri  |   必须   | 成功授权后的回调地址，必须是注册appid时填写的主域名下的地址，建议设置为网站首页或网站的用户中心。注意需要将url进行URLEncode。 |
    > |     state     |   必须   | client端的状态值。用于第三方应用防止CSRF攻击，成功授权后回调时会原样带回。请务必严格按照流程检查用户与state参数状态的绑定。 |
    > |     scope     |   可选   | 请求用户授权时向用户显示的可进行授权的列表。<br/>可填写的值是[API文档](https://wiki.connect.qq.com/api列表)中列出的接口，如果要填写多个接口名称，请用逗号隔开。<br/>例如：scope=get_user_info,list_album,upload_pic<br/>不传则默认请求对接口get_user_info进行授权。<br/>建议控制授权项的数量，只传入必要的接口名称，因为授权项越多，用户越可能拒绝进行任何授权。 |  
    
  > 如果用户成功登录并授权，则会跳转到指定的回调地址，并在redirect_uri地址后带上Authorization Code和原始的state值。  
  > 如：PC网站：http://graph.qq.com/demo/index.jsp?code=9A5F************************06AF&state=test  
  
  ##### Step2：通过Authorization Code获取Access Token  
  > 通常此步骤是在开发者服务器上完成的, 没有样例网站可以分析.  


    
- #### Implicit_Grant  
  
  即client-side模式，是OAuth2.0认证的一种模式，又称User-Agent Flow；  
  适用于需要通过客户端访问的方式，例如需要通过浏览器的javascript代码，或者电脑/移动终端上的客户端访问时。  
  其授权验证流程示意图如下（图片来源：OAuth2.0协议草案V21的4.2节 ）  
  
  ![img](https://qzonestyle.gtimg.cn/qzone/vas/opensns/res/img/OAuth_guide_V2_2.png)  

  对于应用而言，只需要一步：构造授权地址，即可获取Access_Token。  
  
  - url  
    > https://graph.qq.com/oauth2.0/authorize  
    
  - Method  
    > GET  
    
  - Params
    > |     参数      | 是否必须 |                             含义                             |
    > | :-----------: | :------: | :----------------------------------------------------------: |
    > | response_type |   必须   |                 授权类型，此值固定为“token”。                 |
    > |   client_id   |   必须   |            申请QQ登录成功后，分配给应用的appid。             |
    > | redirect_uri  |   必须   | 成功授权后的回调地址，必须是注册appid时填写的主域名下的地址，建议设置为网站首页或网站的用户中心。注意需要将url进行URLEncode。 |
    > |     state     |   必须   | client端的状态值。用于第三方应用防止CSRF攻击，成功授权后回调时会原样带回。请务必严格按照流程检查用户与state参数状态的绑定。 |
    > |     scope     |   可选   | 请求用户授权时向用户显示的可进行授权的列表。<br/>可填写的值是[API文档](https://wiki.connect.qq.com/api列表)中列出的接口，如果要填写多个接口名称，请用逗号隔开。<br/>例如：scope=get_user_info,list_album,upload_pic<br/>不传则默认请求对接口get_user_info进行授权。<br/>建议控制授权项的数量，只传入必要的接口名称，因为授权项越多，用户越可能拒绝进行任何授权。 |  
    
  > 如果用户成功登录并授权，则会跳转到指定的回调地址，并在URL后加“#”号，带上Access Token以及expires_in等参数。  
  > 如果请求参数中传入了state，这里会带上原始的state值。如果redirect_uri地址后已经有“#”号，则加“&”号，带上相应的返回参数。  
  > 如： PC网站：http://graph.qq.com/demo/index.jsp?#access_token=FE04************************CCE2&expires_in=7776000&state=test
