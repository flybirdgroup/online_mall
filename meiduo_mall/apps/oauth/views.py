from QQLoginTool.QQtool import OAuthQQ
from django.shortcuts import render
from django import http
from django.conf import settings
from django import http
from django.urls import reverse

from meiduo_mall.utils.my_carts import merge_cart_cookie_to_redis
from meiduo_mall.utils.my_openid import encode_openid, decode_openid
from meiduo_mall.utils.response_code import RETCODE
from oauth.models import OAuthQQUser, OAuthSinaUser
from django.shortcuts import render,redirect
from django.contrib.auth import logout, login, authenticate
from django_redis import get_redis_connection
from users.models import User
from weibo import APIClient
# Create your views here.

from django.views import View

class QQLoginVIEW(View):
    def get(self,request):
        #1 创建qq对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI, state='next')
        #
        # #2 获取登录界面
        login_url = oauth.get_qq_url()
        #
        # #3 返回页面
        return http.JsonResponse({'errmsg':'OK','login_url':login_url})


class OAuthCallBackView(View):
    def get(self,request):
        #1 获取参数
        code = request.GET.get('code')
        #2 校验参数
        if not code:
            return http.HttpResponseForbidden("code丢失")
        # 3 获取access_token
        oauth_qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                    redirect_uri=settings.QQ_REDIRECT_URI, state='/')

        access_token = oauth_qq.get_access_token(code=code)

        #  4 获取openid
        openid = oauth_qq.get_open_id(access_token=access_token)

        #5 判断是否绑定
        try:
            qq_user = OAuthQQUser.objects.get(openid=openid)
        except Exception as e:
            print("没有该用户")
            #初次授权
            encrypt_openid = encode_openid(openid)
            context = {"token":encrypt_openid}
            return render(request,'oauth_callback.html', context=context)
        else:
           # 非初次授权,获取梅朵用户
            user = qq_user.user
            login(request,user)
            response = redirect(reverse('contents:index'))
            response.set_cookie('username', user.username)
            response = merge_cart_cookie_to_redis(request, user, response)
            return response

    def post(self,request):
        #1 获取参数
        encry_openid = request.POST.get("access_token")
        mobile = request.POST.get("mobile")
        password = request.POST.get("pwd")
        sms_code = request.POST.get("sms_code")

        openid = decode_openid(encry_openid)

        #2 校验参数
        if not all([encry_openid,mobile,password,sms_code]):
            return http.HttpResponseForbidden("参数不全")
        redis_conn = get_redis_connection('code')#之前创建redis库设置的
        redis_sms_code = redis_conn.get("sms_code_%s"%mobile)

        if not redis_sms_code:
            return http.HttpResponseForbidden("短信过期")

        if sms_code != redis_sms_code.decode():
            return http.HttpResponseForbidden("短信码错误")

        user = authenticate(request,username = mobile, password = password)

    #     #判断用户是否存在
        #存在的情况
        if user:
            qq_user = OAuthQQUser()
            qq_user.user = user
            qq_user.openid = openid
            qq_user.save()
            login(request,user)
        #返回响应
        else:
            user = User.objects.create_user(username = mobile, mobile= mobile, password=password)
            qq_user = OAuthQQUser()
            qq_user.user = user
            qq_user.openid = openid
            qq_user.save()
            login(request, user)
        response = redirect(reverse('contents:index'))
        response.set_cookie('username', user.username)

        return response


class SinaLoginView(View):
    def get(self,request):
        client = APIClient(app_key=settings.APP_KEY, app_secret=settings.APP_SECRET,
                                        redirect_uri=settings.SINA_REDIRECT_URI)
        # #2 获取登录界面
        login_url = client.get_authorize_url()
        #
        # #3 返回页面
        return http.JsonResponse({'code': RETCODE.OK,'errmsg': 'OK', 'login_url': login_url})


class SinaCallBackView(View):
    def get(self,request):
        code = request.GET.get("code")
        if not code:
            return http.HttpResponseForbidden('code丢失')
        sina_client = APIClient(app_key=settings.APP_KEY, app_secret=settings.APP_SECRET,
                                        redirect_uri=settings.SINA_REDIRECT_URI)
        access_token_dict = sina_client.request_access_token(code=code)
        access_token = access_token_dict.get("access_token")
        uid = access_token_dict.get("uid")
        try:
            sina_user = OAuthSinaUser.objects.get(uid = uid) # 查询数据库是否有给新浪用户
        except Exception as e:
            encrypt_openid = encode_openid(uid)
            context = {"token": encrypt_openid}
            return render(request,'sina_callback.html', context=context)
        else:#如果数据库存在该用户,登录用户,把之前没登录时候的购物车cookie全部合并,重新设置cookies,返回
            user = sina_user
            login(request,user)
            response = redirect(reverse('contents: index'))
            response.set_cookie("username",user.username)
            merge_cart_cookie_to_redis(request, user, response)
            return response

    def post(self,request):
        #1 获取参数
        encry_openid = request.POST.get("access_token")
        mobile = request.POST.get("mobile")
        password = request.POST.get("pwd")
        sms_code = request.POST.get("sms_code")

        uid = decode_openid(encry_openid)

        #2 校验参数
        if not all([encry_openid,mobile,password,sms_code]):
            return http.HttpResponseForbidden("参数不全")
        redis_conn = get_redis_connection('code')#之前创建redis库设置的
        redis_sms_code = redis_conn.get("sms_code_%s"%mobile)

        if not redis_sms_code:
            return http.HttpResponseForbidden("短信过期")

        if sms_code != redis_sms_code.decode():
            return http.HttpResponseForbidden("短信码错误")

        user = authenticate(request,username = mobile, password = password)

    #     #判断用户是否存在
        #存在的情况
        if user:
            sina_user = OAuthSinaUser()
            sina_user.user = user
            sina_user.uid = uid
            sina_user.save()
            login(request,user)
        #返回响应
        else:
            user = User.objects.create_user(username = mobile, mobile= mobile, password=password)
            sina_user = OAuthSinaUser()
            sina_user.user = user
            sina_user.uid = uid
            sina_user.save()
            login(request, user)
        response = redirect(reverse('contents:index'))
        response.set_cookie('username', user.username)

        return response












