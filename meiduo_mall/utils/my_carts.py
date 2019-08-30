import base64
import json
import pickle
from django import http
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, user, response):
    #用户登录后
    # 对照cookies里面的carts,
    #cookies中carts里面的数据是{sku_id: {"selected":selected, "count":count}}
    # redis 两类型数据: hash 和 set集合
    #hash: 'carts_%s'user_id, sku_id, count
    #set: 'selected_%s'user_id, selected
    """
     如果cookie中的购物车数据在Redis数据库中已存在，将cookie购物车数据覆盖Redis购物车数据。
    3.3 如果cookie中的购物车数据在Redis数据库中不存在，将cookie购物车数据新增到Redis。
    3.4 最终购物车的勾选状态以cookie购物车勾选状态为准。"""
    #1 先把cookies转成字典
    cart_cookies = request.COOKIES.get('carts')
    if not cart_cookies:
        return response
    #转成字典
    cart_cookies_dict = pickle.loads(base64.b64decode(cart_cookies.encode()))
    # 同步cookie中购物车reids数据
    redis_conn = get_redis_connection('carts')
    sku_id_list = []
    mapping = {}
    for sku_id, selected_count in cart_cookies_dict.items():
        mapping.update({ sku_id : selected_count['count']
        })
        if cart_cookies_dict[sku_id]['selected']:
            redis_conn.sadd('selected_%s'%user.id,sku_id)
        else:
            redis_conn.srem('selected_%s'%user.id,sku_id)
    redis_conn.hmset('carts_%s'%user.id, mapping)
    response.delete_cookie('carts')
    return response
    # hash: 'carts_%s'user_id, sku_id, count
    # set: "selected_%s"%user_id, sku_id
    #也就是把cookies中的sku_id,count同步redis, 李荣hash(name,mapping)批量导入



