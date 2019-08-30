from django import http
from django.shortcuts import render
from django.conf import settings
from alipay import AliPay




# Create your views here.

#用户收款
from meiduo_mall.utils.my_loginrequired import MyloginRequiredMixin
from meiduo_mall.utils.response_code import RETCODE
from orders.models import OrderInfo
from pays.models import PayModel


class ALIPayView(MyloginRequiredMixin):
    def get(self,request,order_id):
        app_private_key_string = open(settings.ALIPAY_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()

        # 2,创建alipay对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=settings.ALIPAY_RETURN_URL,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )



        # 3,创建支付页面
        subject = "美多商城订单"

        # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=9999,
            subject=subject,
            return_url=settings.ALIPAY_RETURN_URL,
        )

        alipay_url = settings.ALIPAY_URL + "?" + order_string

        return http.JsonResponse({"code": RETCODE.OK, "alipay_url": alipay_url})


class PayStatus(MyloginRequiredMixin):
    def get(self,request):
        dict_data = request.GET.dict()
        sign = dict_data.pop('sign')
        trade_no = dict_data.get("trade_no")
        out_trade_no = dict_data.get('out_trade_no')
        if not all([sign, trade_no,out_trade_no]):
            return http.HttpResponseForbidden("非法请求")
        app_private_key_string = open(settings.ALIPAY_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=settings.ALIPAY_RETURN_URL,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )
        success = alipay.verify(dict_data,sign) #阿里验证最需要的两个就是signiture签名,和回调的整个数据
        if not success:
            return http.HttpResponseForbidden("订单信息错误")
        PayModel.objects.create(
            out_trade_no_id=out_trade_no,
            trade_no=trade_no
        )
        OrderInfo.objects.filter(order_id=out_trade_no).update(status=OrderInfo.ORDER_STATUS_ENUM["FINISHED"])
        context = {
            "order_id" : out_trade_no
        }
        return render(request, 'pay_success.html', context=context)










