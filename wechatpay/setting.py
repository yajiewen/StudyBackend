#微信支付配置
# ==================支付相关信息==================
APP_ID = 'wx8397f8696b538317' #公众号appid
MCH_ID = '1473426802' #商户号
API_KEY = 'T6m9iK73b0kn9g5v426MKfHQH7X8rKwb' #商户号密钥：微信商户平台(pay.weixin.qq.com) -->账户设置 -->API安全 -->密钥设置，设置完成后把密钥复制到这里

WECHATORDER_URL = 'https://api.mch.weixin.qq.com/pay/unifiedorder' #微信下单api
BACK_NOFIFY_URL = 'https://www.kidtut.net/wechatpay/check_pay/' #微信支付回调接口(微信那边处理订单后会来访问你的这个回调接口，相当于同通知你，你在接口中进行相应的操作)
CREATE_IP = '47.242.184.92' #终端的ip
TRADE_TYPE = 'NATIVE' #交易类型(扫码支付)

BUY_LIMIT = 100 #单次充值的金额限制
