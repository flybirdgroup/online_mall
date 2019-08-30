import base64
import json
import pickle

from django import http
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection

# Create your views here.
from goods.models import SKU
from meiduo_mall.utils.my_loginrequired import MyloginRequiredMixin
from meiduo_mall.utils.response_code import RETCODE

#购物车浏览
class CartView(View):
    def get(self,request):
        # 判断是否登录,如果登录
        user_id = request.user.id
        if request.user.is_authenticated:
            #获取redis数据
            redis_conn = get_redis_connection('carts')
            # hget 设计表的结果是 carts_%s'%user_id, sku_id, count
            cart_dict = redis_conn.hgetall('carts_%s'%user_id)
            selected_list = redis_conn.smembers("selected_%s"%user_id)
            #拼接数据,
            sku_list = []
            for sku_id in cart_dict.keys():
                sku = SKU.objects.get(id = sku_id)
                sku_dict = {
                    "id": sku.id,
                    'name': sku.name,
                    'default_image_url': sku.default_image_url.url,
                    "selected": str(sku_id in selected_list),
                    "price":str(sku.price),
                    "count":int(cart_dict[sku_id]),
                    "amount":str(int(cart_dict[sku_id]) * sku.price)
                }
                sku_list.append(sku_dict)
            return render(request, 'cart.html', context={"sku_list": sku_list})
            # 返回数据
        else:
            #1 假设获取到cookies中的cart数据,注意,get是不会报错的
            cart_cookie = request.COOKIES.get('carts')
            # 2 判断是否有数据
            if cart_cookie: #返回的cookies是一串编译后的字符串,women把它变成byte类型,再用base64转成8位,再用pickle转成字典
                # 3 如果有,把字符串转成字典数据,获取数据, 返回数据,渲染数据
                #4 注意,设置的这里设置的cookies格式是"sku_id":{"count": count, "selected": selected}
                cart_cookie_dict = pickle.loads(base64.b64decode(cart_cookie.encode()))
                sku_list=[]
                for sku_id,selected_count in cart_cookie_dict.items():
                    sku = SKU.objects.get(id = sku_id)
                    sku_dict = {
                        "id": sku.id,
                        'name': sku.name,
                        'default_image_url': sku.default_image_url.url,
                        # "selected": 'selected',
                        #为什么selected 这里直接给值也可以显示
                        "selected":str(selected_count["selected"]),
                        "price": str(sku.price),
                        "count": int(selected_count["count"]),
                        "amount": str(int(selected_count["count"]) * sku.price)

                    }
                    sku_list.append(sku_dict)
            else:
                sku_list=''

        return render(request, 'cart.html', context={"sku_list": sku_list})

    def post(self,request):
        # sku_id: parseInt(this.sku_id),
        # count: this.sku_count 前段给了两个数据women
        #1 接收数据, 因为是axios请求,所以用request.body获取

        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get("sku_id")
        count = json_dict.get("count")
        selected = json_dict.get("selected", True)
        print(sku_id, count)
        # 2 检验数据
        if not all([sku_id,count]):
            return http.JsonResponse({"errmsg": "参数不全"})
        #2.1 判断sku是否存在
        sku = SKU.objects.get(id = sku_id)
        try:
            sku = SKU.objects.get(id=sku_id)
        except Exception as e:
            return http.JsonResponse({"code": RETCODE.NODATAERR, "errmsg": "商品不存在"})
        #2.2 判断库存是否足够
        if sku.stock < count:
            return http.JsonResponse({"code": RETCODE.NODATAERR, "errmsg": "库存不足"})

        # 3 数据入口
        # 3.1 已经登录用户
        # 3.2 没有登录用户
        user_id = request.user.id
        if request.user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            redis_conn.hincrby("carts_%s"%user_id,sku_id,count)
            if selected:
                redis_conn.sadd("selected_%s"%user_id,sku_id)
                return http.JsonResponse({"code": RETCODE.OK})

        else:
            # 获取cookies
            cart_cookies = request.COOKIES.get('carts')
            cart_cookies_dict = {}
            if cart_cookies:
                cart_cookies_dict = pickle.loads(base64.b64decode(cart_cookies.encode())) #把看不懂的cookies转成字典来load值
            #将字符串转换为字典 loads
            if sku_id in cart_cookies_dict:
                count += cart_cookies_dict[sku_id]["count"]
            # 添加新的数据到字典中
            cart_cookies_dict[sku_id] = {"count": count,
                                         "selected": selected}

            # 建立设立cookies,返回reponse
            response = http.JsonResponse({"code": RETCODE.OK} )
            cart_cookie = base64.b64encode(pickle.dumps(cart_cookies_dict)).decode()
            response.set_cookie('carts',cart_cookie)
            return response
       # 4 返回相应

    def put(self,request):
        """获取到的数据有
        sku_id: this.carts[index].id,
                    count:count,
                    selected: this.carts[index].selected
        """
        #获取数据
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected')
        #校验数据
        try:
            sku = SKU.objects.get(id = sku_id)
        except Exception as e:
            return http.JsonResponse({"code": RETCODE.DBERR, "errmsg": "没有该产品"})
        #数据入库 分两种情况,一种是登录用户,一种是未登录用户

        try:
            count = int(count)
        except Exception as e:
            return http.JsonResponse({"code": RETCODE.NODATAERR, "errmsg": "count不是整数"})
        if count > sku.stock:
            return http.JsonResponse({"code": RETCODE.NODATAERR, "errmsg": "库存不足"})

        user_id = request.user.id
        if request.user.is_authenticated:
            #把新的数据放入redis
            #redis入库时候,有两种类型要修改, 一种是hash表, 一种set表
            #hash表的结构是key field value 这里hash表的实际数据是 'cart_%s'%user_id , sku_id, count 就是用户, sku, 数量
            #set表的结构是key value 这里set表的实际数据是 "selected_%s"%user.id, sku_id
            redis_conn = get_redis_connection('carts') #创建reids对象
            # 修改数据 hset
            redis_conn.hset("carts_%s" % user_id, sku_id, count)
            #修改set表,修改方法为s
            if selected:
                redis_conn.sadd("selected_%s"%user_id, sku_id)
            else:
                redis_conn.srem("selected_%s" % user_id, sku_id)
            #返回数据:
            sku = SKU.objects.get(id = sku_id)
            #传入字典,到时方便取值
            sku_dict = {
                "id": sku.id,
                    'name': sku.name,
                    'default_image_url': sku.default_image_url.url,
                    "selected": selected,
                    "price":str(sku.price),
                    "count":int(count),
                    "amount":str(int(count) * sku.price)
            }
            return http.JsonResponse({"code": RETCODE.OK, "cart_sku": sku_dict})


        else:
            cart_cookies = request.COOKIES.get('carts')
            cart_cookies_dict = {}
            if cart_cookies:
                cart_cookies_dict = pickle.loads(base64.b64decode(cart_cookies.encode()))# 把看不懂的cookies转成字典来load值
            #cookies的格式是"sku_id" : {"selected":"selected", 'count' : count}
            cart_cookies_dict[sku_id] = {
                "selected": selected,
                'count': count,
            }
            sku = SKU.objects.get(id = sku_id)
            sku_dict = {
                "id": sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image_url.url,
                "selected": selected,
                "price": str(sku.price),
                "count": count,
                "amount": str(int(count) * sku.price)
            }
            response = http.JsonResponse({"code": RETCODE.OK, "cart_sku": sku_dict})
            # 将字典转为字符串 dumps
            cart_cookies = base64.b64encode(pickle.dumps(cart_cookies_dict)).decode()
            response.set_cookie('carts', cart_cookies)
            return response

    def delete(self,request):
        #sku_id: this.carts[index].id 收到的数据
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get("sku_id")

        #检验参数
        sku = SKU.objects.get(id=sku_id)
        if not sku:
            return http.JsonResponse({"code": RETCODE.NODATAERR, 'errmsg': "没有这个产品"})
        #1 判断用户是否为登录用户
        else:
            user_id = request.user.id
            if request.user.is_authenticated:
                # 1 是登录用户
                # 通过sku_id, 对redis数据库删除
                # redis库有两种类型,一种是hash类型,一种是set类型, 删除分别是hdel, srem两种, hash类型是 key,field, value, set类型是 key, member
                redis_conn = get_redis_connection('carts')
                redis_conn.hdel("carts_%s" % user_id,sku_id)
                redis_conn.srem("selected_%s"%user_id,sku_id)
                return http.JsonResponse({"code": RETCODE.OK, 'errmsg': "删除成功"})

            else:
                # 2 不是登录用户
                # 通过sku_id,对cookies的内容删除
                #获取cookies中的字符串,
                cart_cookies = request.COOKIES.get('carts')
                # 转化为字典
                cart_cookies_dict = pickle.loads(base64.b64decode(cart_cookies.encode()))
                #因为cookies字典的格式 {sku_id : {"selected": selected, "count": count}}
                # 判断sku_id是否在字典里面,如果在,删除
                if sku_id in cart_cookies_dict:
                    del cart_cookies_dict[sku_id]
                #删除后,设置新的cookies,返回数据
                cart_cookies = base64.b64encode(pickle.dumps(cart_cookies_dict)).decode()
                Response = http.JsonResponse({"code": RETCODE.OK, 'errmsg': "删除成功"})
                Response.set_cookie('carts', cart_cookies)
                return Response

#购物车全选
class CartsSelectAllView(View):
    def put(self,request):
        json_dict = json.loads(request.body.decode())
        selected = json_dict.get("selected", True)
        #判断用户是否登录
        user_id = request.user.id
        # 1 登录状态
        # 1.1 登录的,修改redis用户所有sku的selected状态
        # 1.1.1 创建redis对象, 操作redis
        # 1.1.2 对于登录用户,有两个数据操作, 一个是hash 'carts_%s'%user_id, sku_id, count, 第二个数据操作set集合, (selected_%s)%user_id, sku_id
        if request.user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            sku_id_list = redis_conn.hkeys('carts_%s'%user_id)
            # 不能去hkeys,因为得到是列表,添加不进去
            if selected:
                for sku_id in sku_id_list:
                    redis_conn.sadd('selected_%s'%user_id, sku_id)
            else:
                for sku_id in sku_id_list:
                    redis_conn.srem('selected_%s'%user_id, sku_id)
            return http.JsonResponse({"code": RETCODE.OK, "errmsg": "操作成功"})
        else:
            #获取cookies数据
            cart_cookies = request.COOKIES.get('carts')
            #把字符串转成字典
            cart_cookies_dict = pickle.loads(base64.b64decode(cart_cookies.encode()))
            # 修改字典数据
            # 把字典重新变成字符串
            # 设置cookies
            # 返回相应
            if selected:
                # 因为cookies的格式{sku_id : {"selected": selected, "count": count}}, 要去除sku_id, 可以通过字典.keys()取出键值
                sku_id_list = cart_cookies_dict.keys()
                for sku_id in sku_id_list:
                    cart_cookies_dict[sku_id]["selected"] = selected
            else:
                sku_id_list = cart_cookies_dict.keys()
                for sku_id in sku_id_list:
                    cart_cookies_dict[sku_id]["selected"] = None
            cart_cookies = base64.b64encode(pickle.dumps(cart_cookies_dict)).decode()
            response = http.JsonResponse({"code": RETCODE.OK, "errmsg": "操作成功"})
            response.set_cookie("carts", cart_cookies)
            return response

#购物车简单显示
class CartsSimpleView(View):
    def get(self,request):
        #判断是否为登录用户
        #1 如果是登录用户,获取sku_id
        #1.1 提供数据,组成字典(因为是axios,不能直接返回对象)
        #2 如果是没登录用户,获取cookies
        #2.1 把cookies转成字典
        #2.2 获取cookies_dict里面的所有sku_id键
        #返回响应
        user = request.user
        if request.user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            cart_skus_list = []
            for sku_id, count in redis_conn.hgetall('carts_%s'%user.id).items():
                if sku_id in redis_conn.smembers('selected_%s'%user.id):
                    sku = SKU.objects.get(id = sku_id)
                    sku_dict = {
                        "default_image_url": sku.default_image_url.url,
                        "name":sku.name,
                        "count": int(count),
                    }
                    cart_skus_list.append(sku_dict)
        else:
            cart_cookies = request.COOKIES.get('carts')
            #把字符串cookies转换字典
            #cookie的格式就是{'sku_id': {'selected': selected, 'count': count}
            cart_cookies_dict = pickle.loads(base64.b64decode(cart_cookies.encode()))
            cart_skus_list = []
            for sku_id, selected_count in cart_cookies_dict.items():
                if cart_cookies_dict[sku_id]['selected']:
                    sku = SKU.objects.get(id=sku_id)
                    cart_skus_list.append({
                        "default_image_url": sku.default_image_url.url,
                        "name": sku.name,
                        "count": int(selected_count['count']),
                    })
        return http.JsonResponse({"cart_skus": cart_skus_list, "code": RETCODE.OK})




