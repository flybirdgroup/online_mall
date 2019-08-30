from django.shortcuts import render
from django.views import View
from meiduo_mall.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from django import http
from meiduo_mall.libs.yuntongxun.sms import CCP
import random

# 1, 图片验证码
class ImageCodeView(View):
    def get(self,request,image_code_id):
        #1,生成图片验证码
        name,text,image_data = captcha.generate_captcha()

        #2,保存到redis中
        redis_conn = get_redis_connection("code")
        redis_conn.set("image_code_%s"%image_code_id,text,300)

        #3,返回图片验证码
        response = http.HttpResponse(image_data)
        response["Content-Type"] = "image/png"
        return response

# 2, 短信验证码
class SMSCodeView(View):
    def get(self,request,mobile):
        #1,获取参数
        image_code = request.GET.get("image_code")
        image_code_id = request.GET.get("image_code_id")

        #1,1获取短信标记,判断是否能发送
        redis_conn = get_redis_connection("code")
        flag = redis_conn.get("send_flag_%s"%mobile)
        if flag:
            return http.JsonResponse({"errmsg": "频繁发送短信"}, status=400)

        #2,校验参数
        #2,1 为空校验
        if not all([image_code,image_code_id]):
            return http.JsonResponse({"errmsg":"参数不全"},status=400)

        #2,2 图片验证码校验,是否过期
        redis_image_code = redis_conn.get("image_code_%s"%image_code_id)

        if not redis_image_code:
            return http.JsonResponse({"errmsg": "图片验证码已过期"}, status=400)

        # 删除图片验证码
        redis_conn.delete("image_code_%s"%image_code_id)

        # 判断正确性
        if image_code.lower() != redis_image_code.decode().lower():
            return http.JsonResponse({"errmsg": "图片验证码错误"}, status=400)

        #3,发送短信
        sms_code = "%06d" % random.randint(0, 999999)
        # ccp = CCP()
        # ccp.send_template_sms(mobile, [sms_code, 5], 1)

        #使用celery发送短信
        from celery_tasks.sms.tasks import send_msg_code
        send_msg_code.delay(mobile,sms_code)

        print("sms_code = %s"%sms_code )

        #3,1保存短信到redis中
        pipeline = redis_conn.pipeline() # 开启管道(事务)
        pipeline.set("sms_code_%s"%mobile,sms_code,300)
        pipeline.set("send_flag_%s"%mobile,"flag",60) # 设置发送标记
        pipeline.execute() # 提交管道(事务)

        #4,返回响应
        return http.JsonResponse({"code":0,"errmsg":"发送成功"})