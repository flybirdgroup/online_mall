import json

from django.contrib.auth import authenticate,logout,login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render,redirect
from django.urls import reverse
from django.views import View
import re
from django.http import HttpResponseForbidden
from django.conf import settings

from meiduo_mall.utils.my_carts import merge_cart_cookie_to_redis
from meiduo_mall.utils.my_email import *
from meiduo_mall.utils.my_loginrequired import MyloginRequiredMixin
from users.models import User
from django import http
from django_redis import get_redis_connection
from .models import Address
from meiduo_mall.utils.response_code import RETCODE




# 1,注册类视图
class UserRegisterView(View):
    def get(self,request):
        return render(request,'register.html')

    def post(self,request):
        #1,获取参数
        username = request.POST.get("user_name")
        password = request.POST.get("pwd")
        repassword = request.POST.get("cpwd")
        phone = request.POST.get("phone")
        msg_code = request.POST.get("msg_code")
        allow = request.POST.get("allow")

        #2,校验参数
        # 2,1校验用户名格式
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$',username):
            return HttpResponseForbidden("用户名格式有误")

        # 2,2密码格式
        if not re.match(r'^[0-9A-Za-z]{8,20}$',password):
            return HttpResponseForbidden("用户名格式有误")

        # 2,3两次密码一致性
        if password != repassword:
            return HttpResponseForbidden("两次密码不一致")

        # 2,4手机号格式
        if not re.match(r'^1[3-9]\d{9}$',phone):
            return HttpResponseForbidden("手机号格式有误")

        # 2,5短信验证码正确性
        redis_conn = get_redis_connection("code")
        redis_sms_code = redis_conn.get("sms_code_%s"%phone)

        # 2,5,1 判断短信验证码是否过期
        if not redis_sms_code:
            return HttpResponseForbidden("短信验证码已过期")

        # 2,5,2 判断正确性
        if msg_code != redis_sms_code.decode():
            return HttpResponseForbidden("短信验证码错误")

        # 2,6是否同意协议
        if allow != 'on':
            return HttpResponseForbidden("必须同意协议")

        #3,数据入库
        user = User.objects.create_user(username=username,password=password,mobile=phone)

        response = redirect(reverse("contents:index"))
        response.set_cookie('username',user.username,max_age=3600*24*15)
        #4,返回响应
        return response

# 2,判断用户名是否存在
class UserCountView(View):
    def get(self,request,username):
        #1,根据username查询用户数量
        count = User.objects.filter(username=username).count()

        #2,返回响应
        return http.JsonResponse({
            "count":count
        })

# 3,判断手机号是否存在
class UserMobileCountView(View):
    def get(self,request,mobile):
        #1,根据手机号查询用户数量
        count = User.objects.filter(mobile=mobile).count()

        #2,返回响应
        return http.JsonResponse({
            "count":count
        })

# 4,用户登录
class UserloginView(View):
    def get(self,request):
        return render(request,'login.html')

    def post(self,request):
        #1,获取参数
        username = request.POST.get("username")
        password = request.POST.get("pwd")
        remembered = request.POST.get("remembered")

        #2,校验参数
        #2,1 为空校验
        if not all([username,password]):
            return http.HttpResponseForbidden("参数不全")

        #2,2 用户名格式校验
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$',username):
            return http.HttpResponseForbidden("用户名格式错误")

        #2,3 密码格式校验
        if not re.match(r'^[0-9A-Za-z]{8,20}$',password):
            return http.HttpResponseForbidden("密码格式错误")

        #2,4 账号密码的校验,校验成功返回用户对象,不成功返回None
        user = authenticate(request,username=username,password=password)

        if not user:
            return http.HttpResponseForbidden("用户名或者密码错误")



        #3,状态保持(明天完成)
        login(request,user)
        response = redirect(reverse("contents:index"))
        if remembered == "on":
            response.set_cookie('username', user.username, max_age=3600*24*15)
            request.session.set_expiry(3600*24*2)

        else:
            request.session.set_expiry(0)
            response.set_cookie('username', user.username, max_age=0)
        # # 4,重定向到首页

        # # 4,返回响应
        response = merge_cart_cookie_to_redis(request, user, response)
        print('haha')
        return response

# 5,用户登出,让网页不再显示用户信息,而网页显示用户信息是因为set_cookies,所以把cookies的username清理掉,前段就没有信息了
class UserLogoutView(View):
    def get(self,request):
        logout(request)
        response = redirect(reverse('contents:index'))
        response.delete_cookie('username')
        return response
        # logout(request) # logout就是把session清理掉
        # response = redirect(reverse('contents:index'))
        # response.delete_cookie('username')
        # request.session.flush()
        # return response


#6  用户中心
class UserInfoView(MyloginRequiredMixin):
    def get(self,request):
        context = {
            'username': request.user.username,
            'mobile':request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active
        }
        print(request.user)
        print(type(request.user))

        # if request.user.is_authenticated:
        #     return render(request,'user_center_info.html')
        # else:
        #     return redirect(reverse('content:index'))

        return render(request, 'user_center_info.html', context=context)

# 7 用户邮箱保存

class UserEmailView(MyloginRequiredMixin):
    def put(self,request):
        """
        获取参数
        校验参数
        数据入库
        返回响应
        :param request:
        :return:
        """
        #获取数据
        data_dict = json.loads(request.body.decode())
        email = data_dict.get("email")
        #验证数据
        if not email:
            return http.JsonResponse({"errmsg": "参数不全", 'code': 5000})
        # if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
        #     return HttpResponseForbidden("邮件格式错误")
        print(email)

        request.user.email = email
        request.user.save()

        from celery_tasks.email.tasks import send_email_url
        verify_url=generate_verify_url(request.user)
        send_email_url.delay(verify_url, email)

        # send_mail(
        #     subject='美多商城',
        #     message='请激活链接%s'%verify_url ,
        #     from_email=settings.EMAIL_FROM,
        #     recipient_list=[email],
        # )

        #添加数据到数据库


        return http.JsonResponse({'errmsg':"设置成功", "code": 0})

# 8 激活邮件
class UserEmailVerificationView(View):
    def get(self,request):
        # 获取数据,token
        token = request.GET.get("token")
        if not token:
            return http.HttpResponseForbidden("token丢失")
        #解密token
        user = decode_token(token)
        if not user:
            return http.HttpResponseForbidden("token失效了,重发邮件")
        #找到用户,修改email属性
        user.email_active = True
        user.save()

        #返回响应
        return http.HttpResponse("邮箱激活成功")

# 9 收货地址视图
class UserAddressView(MyloginRequiredMixin):
    def get(self,request):
        address_list = []
        addresses = request.user.addresses.filter(is_deleted = False).all()
        print(addresses)
        for address in addresses:
            address_dict = {
                "id":address.id,
                "receiver":address.receiver,
                "province":address.province.name,
                "city":address.city.name,
                "district":address.district.name,
                "place":address.place,
                "mobile":address.mobile,
                "tel":address.tel,
                "email":address.email,
                "province_id": address.province_id,
                "city_id": address.city_id,
                "district_id": address.district_id,


            }
            print(address.receiver)
            address_list.append(address_dict)

        context = {"addresses" : address_list,
        "user": request.user}

        return render(request,'user_center_site.html',context=context)

#10 增加地址信息视图
class CreateAddressView(MyloginRequiredMixin):
    def post(self,request):
        count = Address.objects.filter(user_id=request.user.id).count()
        # count = request.user.addresses.count() 简单方法
        from meiduo_mall.utils import my_constants
        if count >= my_constants.USER_ADDRESS_COUNTS_LIMIT:
            return http.JsonResponse({"errmsg":"超过20次", 'code':RETCODE.THROTTLINGERR })
        else:
            data = request.body.decode()
            json_dict = json.loads(data)
            receiver = json_dict.get('receiver')
            province_id = json_dict.get('province_id')
            city_id = json_dict.get('city_id')
            district_id = json_dict.get('district_id')
            place = json_dict.get('place')
            mobile = json_dict.get('mobile')
            tel = json_dict.get('tel')
            email = json_dict.get('email')

    #新增用户地址
            #创建了一个address对象
            address = Address.objects.create(
                user=request.user,
                title = receiver,
                receiver = receiver,
                province_id = province_id,
                city_id = city_id,
                district_id = district_id,
                place =place ,
                mobile =mobile ,
                tel =  tel,
                email=email
            )
            #返回给前段页面数据
            address_dict = {
                "id": address.id,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email,
                "province_id": address.province_id,
                "city_id": address.city_id,
                "district_id": address.district_id}
        return http.JsonResponse({'code':RETCODE.OK, "address":address_dict, "errmsg":"添加成功"})

#11 删除修改地址信息视图
class UpdateDeleteAddressView(MyloginRequiredMixin):
    def delete(self,request,address_id):
        address = Address.objects.get(id=address_id)
        try:
            address.is_deleted = True
            address.save()
        except Exception as e:
            print(e)
            return http.JsonResponse({"code": RETCODE.DBERR, "errmsg": "删除失败"})
        else:
            return http.JsonResponse({"code":RETCODE.OK, "errmsg":"删除成功"})


    def put(self,request,address_id):
        #获取请求体
        data = request.body.decode()
        #获取要修改的数据
        json_dict = json.loads(data)
        print(json_dict)
        #校验数据{'id': 2, 'receiver': '老王', 'province': '广东省', 'city': '广州市', 'district': '海珠区', 'place': '辅警花园', 'mobile': '13660113008', 'tel': '020-34254508', 'email': '123456ovince_id': 440000, 'city_id': 440100, 'district_id': 440105, 'title': '老王'}
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')
        #将校验好的数据导入数据库
        try:
            address = Address.objects.filter(id = address_id).update(
                receiver=receiver,
                province_id =province_id ,
                city_id =city_id ,
                district_id =district_id ,
                place =place ,
                mobile =mobile ,
                tel =tel ,
                email =email

            )

        except Exception as e:
            print('失败')
            print(e)
            return http.JsonResponse({"code": RETCODE.DBERR, "errmsg":"修改失败"})
        else:
            #返回响应
            print('成功')
            address_dict = {
                "id": address.id,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email,
                "province_id": address.province_id,
                "city_id": address.city_id,
                "district_id": address.district_id}

            return http.JsonResponse({"code": RETCODE.OK, "errmsg": "修改成功","address":address_dict})

#12 设置默认地址
class DefaultAddressViews(MyloginRequiredMixin):
    def put(self,request,address_id):
        try:
            # address = Address.objects.get(id = address_id)
            request.user.default_address_id =address_id
        except Exception as e:
            print(e)
            return http.JsonResponse({"code": RETCODE.DBERR, "errmsg": "设置失败"})
        return http.JsonResponse({"code":RETCODE.OK, "errmsg":"设置成功"})


class UpdateTitleAddressView(MyloginRequiredMixin):
    def put(self,request,address_id):
        address = Address.objects.get(id = address_id)
        data = request.body.decode()
        data_dict = json.loads(data)
        title = data_dict.get("title")
        try:
            address.title = title
            address.save()
        except Exception as e:
            print(e)
            return http.JsonResponse({"code": RETCODE.DBERR, "errmsg": "title保存失败"})
        else:
            return http.JsonResponse({"code":RETCODE.OK, "errmsg":"title保存成功"})


class ModifyPassword(MyloginRequiredMixin):
    def get(self,request):
        return render(request,'user_center_pass.html')
    def post(self,request):
        old_pwd = request.POST.get("old_pwd")
        new_pwd = request.POST.get("new_pwd")
        new_cpwd = request.POST.get("new_cpwd")
        if not all([old_pwd,new_pwd,new_cpwd]):
            return http.HttpResponseForbidden("参数不全")
        # 匹配密码格式
        if not re.match(r'^[0-9A-Za-z]{8,20}', old_pwd):
            return http.HttpResponseForbidden("格式错误")



        # 查询原始密码是否存在
        try:
            request.user.check_password(old_pwd)
        except Exception as e:
            print(e)
            return http.HttpResponseForbidden("密码错误")

        # 没有,返回错误
        # 有,判断新密码和确认新密码是否一直
        else:
            if not re.match(r'^[0-9A-Za-z]{8,20}', new_pwd):
                return http.HttpResponseForbidden("格式错误")
            if not re.match(r'^[0-9A-Za-z]{8,20}', new_cpwd):
                return http.HttpResponseForbidden("格式错误")
            if new_pwd != new_cpwd:
                return http.HttpResponseForbidden("密码不一致")
        # 修改密码,输入数据库
        # 返回响应
        try:
            request.user.set_password(new_pwd)
            request.user.save()
        except Exception as e:
            return http.JsonResponse({"code":RETCODE.DBERR,"errmsg":"密码修改失败"})
        else:
            #
            logout(request)

            response = redirect(reverse('users:relogin'))
            response.delete_cookie("username")

            return response










        return render(request,'user_center_pass.html')