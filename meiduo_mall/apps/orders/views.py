import json
import random
from django import http
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django_redis import get_redis_connection
from meiduo_mall.utils.my_constants import FREIGHT, LIST_ORDER_PER_PAGE
from meiduo_mall.utils.response_code import RETCODE
from .models import OrderInfo,OrderGoods
from django.db import transaction
from django.shortcuts import redirect



# Create your views here.
from goods.models import SKU
from meiduo_mall.utils.my_loginrequired import MyloginRequiredMixin
from users.models import Address

#订单显示
class OrderSettlementView(MyloginRequiredMixin):
    def get(self, request):
        user = request.user
        addresses = request.user.addresses.filter(is_deleted=False).all()
        #找到那些商品是selected
        redis_conn = get_redis_connection('carts')
        cart_dict = redis_conn.hgetall('carts_%s'%user.id)
        sku_id_list = redis_conn.smembers('selected_%s' % user.id)  # 这里获取到用户所有sku_id 并且是被选上的
        sku_list = []
        total_count = 0
        total_amount = 0
        for sku_id, selected_count in cart_dict.items():
            if sku_id in sku_id_list:
                sku = SKU.objects.get(id=sku_id)
                sku_dict = {
                    'name': sku.name,
                    'price':sku.price,
                    'count': int(cart_dict[sku_id]),
                    'amount':str(int(cart_dict[sku_id]) * sku.price),
                    'default_image_url': sku.default_image_url.url
                }
                sku_list.append(sku_dict)
                total_count += int(cart_dict[sku_id])
                total_amount += int(cart_dict[sku_id]) * sku.price
        payment_amount = total_amount + FREIGHT
        context = {"addresses": addresses,
                   'sku_list':sku_list,
                   'total_count': total_count,
                   'total_amount': total_amount,
                   "freight": FREIGHT,
                   "payment_amount":payment_amount }
        return render(request, 'place_order.html', context)

#订单提交
class OrdersCommitView(MyloginRequiredMixin):
    @transaction.atomic
    def post(self,request):
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get("address_id") #知道了用户选择那个地址
        pay_method = json_dict.get("pay_method") #知道了用户选择那种付款方式
        pay_method = int(pay_method)
        user = request.user
        #校验: 1 为空检验, 2 address是否存在 3, 判断支付方式
        if not all([address_id,pay_method]):
            return http.JsonResponse({"code": RETCODE.DBERR, "errmsg":"参数不全"})
        try:
            address = Address.objects.get(id = address_id)
        except Exception as e:
            print(e)
            return http.JsonResponse({"code": RETCODE.DBERR, "errmsg": "地址不存在"})
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.JsonResponse({"code": RETCODE.DBERR, "errmsg":"支付方式错误"})


        #2 数据库入库
        # mysql库 通过ORM操作入库
        #对于订单,涉及两张表格,一份是订单信息,一份是订单产品 即OrderInfo,OrderGoods
        #看看两份表格需要什么必填信息,然后创建
        #订单号的生成方式利用日期+随机9位数
        redis_conn = get_redis_connection('carts')
        # 两种类型数据
        cart_dict = redis_conn.hgetall('carts_%s' % user.id)  # 获取到字典包含sku_id: count
        selected_sku_list = redis_conn.smembers('selected_%s' % user.id)  # 获取到一个列表包含所有selected的sku_id list
        order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + ('%06d'%random.randint(0,999999))
        if int(pay_method) == OrderInfo.PAY_METHODS_ENUM['CASH']:
            status = OrderInfo.ORDER_STATUS_ENUM['UNPAID']
        if int(pay_method) == OrderInfo.PAY_METHODS_ENUM['ALIPAY']:
            status = OrderInfo.ORDER_STATUS_ENUM["UNSEND"]

        # 上传数据
 #创建订单信息表,把orderid,用户,地址,总数量,总金额,运费,付款方式,订单状态录入
        sid = transaction.savepoint()
        order_info = OrderInfo.objects.create(
            order_id = order_id,
            user = request.user,
            address = address,
            total_count = 0,
            total_amount = 0,
            freight = FREIGHT,
            pay_method = pay_method,
            status = status
        )
        # 把订单商品表补充完,包括 订单号,sku,count,价格price录入
        for sku_id,count in cart_dict.items():
            while True:
                if sku_id in selected_sku_list:
                    #获取对象
                    sku = SKU.objects.get(id = sku_id)
                    #判断库存
                    if int(count) > sku.stock:
                        transaction.savepoint_rollback(sid)
                        return http.JsonResponse({"code": RETCODE.NODATAERR, "errmsg": "库存不足"})
                    #库存删,销量增加
                    original_stock = sku.stock
                    new_stock = original_stock - int(count)
                    new_sales = original_stock + int(count)
                    # sku.stock -= int(count)
                    #
                    # sku.sales += int(count)
                    # sku.save()
                    ret = SKU.objects.filter(id = sku_id, stock=original_stock).update(stock= new_stock,sales = new_sales)
                    # 证明影响的行数为0,即意味数据库被修改了
                    if ret == 0:
                        transaction.savepoint_rollback(sid)
                        #continue意味可以如果库存修改不了的话,可以继续循环操作
                        continue
                    OrderGoods.objects.create(
                        order_id=order_info.order_id,
                        sku=sku,
                        count=int(count),
                        price=sku.price
                    )
                    order_info.total_count += int(count)
                    order_info.total_amount += (int(count) * sku.price)
                    order_info.save()
                    transaction.savepoint_commit(sid)
                    break

        #提交订单后,购物车要清空
        #购物车的数据在redis,所以要对redis的数据清空,这里注意要清理的是被选中的产品
        redis_conn.hdel('carts_%s'%user.id, *selected_sku_list)
        redis_conn.srem('selected_%s'%user.id, *selected_sku_list)
        #返回响应
        context = {"code": RETCODE.OK, "order_id": order_id,
                   'payment_amount':order_info.total_amount,
                   'pay_method':pay_method}
        return http.JsonResponse(context)

#订单成功页面
class OrdersSuccessView(MyloginRequiredMixin):
    def get(self,request):
        context = {'order_id' : request.GET.get("order_id"),
        'payment_amount' : request.GET.get("payment_amount"),
        'pay_method' : request.GET.get('pay_method')
        }
        return render(request,'order_success.html',context)

#订单中心
class OrderInfoView(MyloginRequiredMixin):
    def get(self,request,page_num):
        user = request.user
        orders = user.orderinfo_set.all().order_by("order_id")
        for order in orders:
            order.paymethod_name = OrderInfo.PAY_METHOD_CHOICES[order.pay_method -1][1]
            order.status_name = OrderInfo.ORDER_STATUS_CHOICES[order.status - 1][1]
        paginator = Paginator(orders, LIST_ORDER_PER_PAGE)
        page = paginator.page(page_num)
        object_list = page.object_list
        total_page = paginator.num_pages
        current_page = page_num
        context = {
            "current_page": current_page,
            "total_page": total_page,
            "orders": object_list

        }
        return render(request,'user_center_order.html',context=context)

