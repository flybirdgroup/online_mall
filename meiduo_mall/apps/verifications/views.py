import json
import re

from django.conf import settings
from django.shortcuts import render
from django.views import View
from itsdangerous import TimedJSONWebSignatureSerializer

from meiduo_mall.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from django import http
from meiduo_mall.libs.yuntongxun.sms import CCP
import random

# 1, 图片验证码
from meiduo_mall.utils.my_openid import encode_openid, decode_openid
from meiduo_mall.utils.response_code import RETCODE
from users import models
from users.models import User


class ImageCodeView(View):
    def get(self,request,image_code_id):
        #1,生成图片验证码
        name,text,image_data = captcha.generate_captcha()

        #2,保存到redis中
        redis_conn = get_redis_connection("code")
        redis_conn.set("image_code_%s"%image_code_id,text,300)

        #3,返回图片验证码
        return http.HttpResponse(image_data,content_type='image/jpg')

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

        # 减轻redis负担,删除图片验证码
        # redis_conn.delete("image_code_%s"%image_code_id)

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


class Find_password_step_1View(View):
    def get(self,request,username):
        image_code_id = request.GET.get("image_code_id")
        image_code = request.GET.get("text")
        if not all([image_code,image_code_id]):
            return http.JsonResponse({"errmsg":"参数不全"},status=400)
        redis_conn = get_redis_connection('code')

        image_code_redis = redis_conn.get("image_code_%s"%image_code_id)

        if not image_code_redis:
            return http.JsonResponse({"errmsg": "图片验证码已过期"}, status=400)

        # 删除图片验证码
        redis_conn.delete("image_code_%s"%image_code_id)

        #检验 图片验证码
        if image_code_redis.decode() != image_code:
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码错误'}, status=400)
        try:
            user = User.objects.get(username = username)
        except Exception as e:
            print(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '用户不存在'}, status=404)
        else:
            mobile = user.mobile
            # 2
            access_token = encode_openid({"mobile": mobile,"user_id":user.id })


            context = {
                'mobile': mobile,
                "access_token": access_token
            }
        return http.JsonResponse(context)


class Find_password_SMSG_View(View):
    def get(self,request):
        access_token = request.GET.get("access_token")
        data_dict = decode_openid(access_token)
        if data_dict is None:
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '没有数据'}, status=400)
        mobile = data_dict["mobile"]
        user_id = data_dict["user_id"]
        try:
            User.objects.get(mobile = mobile)
        except:
            return http.JsonResponse({'code': RETCODE.NODATAERR, 'errmsg':"没有该用户"}, status=400)
        from celery_tasks.sms.tasks import send_msg_code
        sms_code = "%06d" % random.randint(0, 999999)
        send_msg_code.delay(mobile, sms_code)

        print("sms_code = %s" % sms_code)
        redis_conn = get_redis_connection('code')

        # 3,1保存短信到redis中
        pipeline = redis_conn.pipeline()  # 开启管道(事务)
        pipeline.set("sms_code_%s" % mobile, sms_code, 300)
        pipeline.set("send_flag_%s" % mobile, "flag", 60)  # 设置发送标记
        pipeline.execute()  # 提交管道(事务)

        # 4,返回响应
        return http.JsonResponse({"code": 0, "errmsg": "发送成功"})


class PasswordSummitView(View):
    def get(self,request,username):
        try:
            User.objects.get(username=username)
        except Exception as e:
            print(e)
            return http.JsonResponse({'code': RETCODE.NODATAERR, 'errmsg': "没有该用户"}, status=404)
        user = User.objects.get(username=username)
        mobile = user.mobile
        sms_code = request.GET.get("sms_code")
        #判断是否空
        if not all([username,sms_code]):
            return http.JsonResponse({'code': RETCODE.NODATAERR, 'errmsg': "参数不全"}, status=400)
        redis_conn = get_redis_connection('code')
        redis_sms_code = redis_conn.get('sms_code_%s' % mobile)
        if redis_sms_code.decode() != sms_code:
            return http.JsonResponse({'code': RETCODE.NODATAERR, 'errmsg': "验证码错误"}, status=400)
        context= {
            "user_id": user.id,
            "access_token": encode_openid({"mobile": mobile,"user_id":user.id })
        }
        return http.JsonResponse(context)




