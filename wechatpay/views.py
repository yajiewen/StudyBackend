from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
from wechatpay import models
from account import models as amodels
import requests
from django.utils import timezone
from wechatpay import setting
from wechatpay import func
from django.views.decorators.csrf import csrf_exempt  # 解除csrf验证
# Create your views here.

"""
======微信支付进行充值======
api: https://www.kidtut.net/wechatpay/buycoin/
方法: POST
参数:
    充值金额:coin_n
    cookies
后端返回值:

"""
def buycoin(request):
    if request.method == 'POST':
        coin_num = float(request.POST.get('coin_n'))
        usr_email = request.COOKIES.get('uemail')
        is_login = request.COOKIES.get('is_login')

        response_data = {
            'is_login':'no',
            'code_url':'no',
            'coin_legal':'no',
        }

        if amodels.Table.objects.filter(usr_email = usr_email).exists() and is_login and coin_num <= setting.BUY_LIMIT:
            response_data['coin_legal'] = 'yes'
            response_data['is_login'] = 'yes'

            nonce_str = func.random_str() # 拼接出随机的字符串
            total_fee = int(coin_num * 100) #单位为分(一角10分)
            body = '思达迪账户充值' #商品描述
            out_trade_no = func.order_num(usr_email) #获取订单号

            #配置请求参数
            params = {
                'appid' : setting.APP_ID, # APPID
                'mch_id' : setting.MCH_ID, # 商户号
                'nonce_str' : nonce_str, # 随机字符串
                'body' : body, # 商品描述
                'out_trade_no' : out_trade_no, # 订单编号
                'total_fee' : total_fee, # 订单总金额
                'spbill_create_ip' : setting.CREATE_IP, # 发送请求服务器的IP地址
                'notify_url' : setting.BACK_NOFIFY_URL, # 支付回调地址
                'trade_type' : setting.TRADE_TYPE, # 支付类型

            }

            sign = func.get_sign(params,setting.API_KEY) #参数签名
            params['sign'] = sign

            xml = func.trans_dict_to_xml(params)
            response = requests.request('post', setting.WECHATORDER_URL, data=xml.encode('utf-8'))  # 以POST方式向微信公众平台服务器发起请求
            data_dict = func.trans_xml_to_dict(response.content.decode('utf-8'))  # 将请求返回的数据转为字典
            print(data_dict)
    
            if data_dict.get('return_code') == 'SUCCESS':  # 如果请求成功
                response_data['code_url'] = data_dict.get('code_url') # 获取code_url


                return JsonResponse(response_data)
            return JsonResponse(response_data)
        else:
            return JsonResponse(response_data)

    else:
        return HttpResponse('bad request',status = 500)


"""
======支付承购后回调======
api: https://www.kidtut.net/wechatpay/check_pay/
方法: POST

后端返回值:

"""
@csrf_exempt  # 去除csrf验证
def check_pay(request):
    data_dict = func.trans_xml_to_dict(request.body)  # 回调数据转字典
    sign = data_dict.pop('sign')  # 取出签名
    back_sign = func.get_sign(data_dict, setting.API_KEY)  # 计算签名
    if sign == back_sign:  # 验证签名是否与回调签名相同
        '''
        检查对应业务数据的状态，判断该通知是否已经处理过，如果没有处理过再进行处理，如果处理过直接返回结果成功。
        '''
        print('支付成功！')
        return HttpResponse('SUCCESS')
    else:
        '''
            此处编写支付失败后的业务逻辑
        '''
        print('支付失败！')
        return HttpResponse('failed')
