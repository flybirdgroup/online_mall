import json


from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime
from django import http

# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from goods.models import SKU, GoodsCategory, CategoryVisitCount
from meiduo_mall.utils.my_category import get_categories
from meiduo_mall.utils.my_constants import LIST_SKU_PER_COUNT
from meiduo_mall.utils.my_loginrequired import MyloginRequiredMixin
from meiduo_mall.utils.response_code import RETCODE


class SKUListView(View):
    def get(self,request,category_id,page_num):
        sort = request.GET.get("sort")
        if sort == "price":
            sort_field = "price"
        elif sort == "hot":
            sort_field = "-sales"
        else:
            sort_field = "stock"
            sort = "default"
        categories = get_categories()
        category = GoodsCategory.objects.get(id = category_id)
        SKUs = SKU.objects.filter(category_id= category_id).order_by(sort_field).all()
        paginator = Paginator(SKUs,LIST_SKU_PER_COUNT)
        totalPage = paginator.num_pages
        currentPage = paginator.page(page_num).number
        sku_list = paginator.page(page_num).object_list



        context = {
            "SKUs":sku_list,
            "category": category,
            "categories": categories,
            "totalPage": totalPage,
            "currentPage":currentPage,
            "sort": sort
        }
        return render(request, 'list.html', context=context)



class HotSkuListView(View):
    def get(self,request,category_id):

        #找到热销商品数据
        SKUs = SKU.objects.filter(category_id=category_id).order_by("-sales")[:3]
        hot_sku_list = []
        #数据转换
        for sku in SKUs:
            sku_dict = {
                "name" : sku.name,
                'price': sku.price,
                'id' : sku.id,
                'default_image_url':sku.default_image_url.url
            }
            hot_sku_list.append(sku_dict)


        return JsonResponse({"hot_sku_list":hot_sku_list})

#产品详细页面
class DetailView(View):
    def get(self,request,sku_id):
        categories = get_categories()

        sku = SKU.objects.get(id = sku_id)
        category = sku.category
        sku_specs = sku.specs.order_by('spec_id')
        sku_key = []
        for spec in sku_specs:
            sku_key.append(spec.option.id)
        # 获取当前商品的所有SKU
        skus = sku.spu.sku_set.all()
        # 构建不同规格参数（选项）的sku字典
        spec_sku_map = {}
        for s in skus:
            # 获取sku的规格参数
            s_specs = s.specs.order_by('spec_id')
            # 用于形成规格参数-sku字典的键
            key = []
            for spec in s_specs:
                key.append(spec.option.id)
            # 向规格参数-sku字典添加记录
            spec_sku_map[tuple(key)] = s.id
        # 获取当前商品的规格信息
        goods_specs = sku.spu.specs.order_by('id')
        # 若当前sku的规格信息不完整，则不再继续
        if len(sku_key) < len(goods_specs):
            return
        for index, spec in enumerate(goods_specs):
            # 复制当前sku的规格键
            key = sku_key[:]
            # 该规格的选项
            spec_options = spec.options.all()
            for option in spec_options:
                # 在规格参数sku字典中查找符合当前规格的sku
                key[index] = option.id
                option.sku_id = spec_sku_map.get(tuple(key))
            spec.spec_options = spec_options
        context = {
            "categories": categories,
            "category": category,
            "sku":sku,
            "specs": goods_specs

        }

        return render(request,'detail.html',context=context)


class CategoryVisitCountView(View):
    def post(self,request,category_id):
        today = datetime.today()
        try:
            category_visit = CategoryVisitCount.objects.get(date=today, category_id=category_id)
        except Exception as e:
            category_visit = CategoryVisitCount()


        category_visit.date = today
        category_visit.category_id = category_id
        category_visit.count += 1
        category_visit.save()

        return http.HttpResponse({"code":RETCODE.OK},status=200)


class UserBrowseHistory(MyloginRequiredMixin):
    def get(self, request):
        """获取用户浏览记录"""
        # 获取Redis存储的sku_id列表信息
        redis_conn = get_redis_connection('history')
        sku_ids = redis_conn.lrange('history_%s' % request.user.id, 0, 4)

        # 根据sku_ids列表数据，查询出商品sku信息
        skus = []
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            skus.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image_url.url,
                'price': sku.price,

            })

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'skus': skus})
        #JsonResponse返回的值不能是对象,如果渲染需要遍历,最好用列表,列表里面嵌套字典就可以取值

    def post(self,request):
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        print(json_dict)
        print('haha')
        print(request.user)
        print('haha')
        try: #找是否有这个sku
            SKU.objects.get(id = sku_id)
        except Exception as e:
            print(e)
            return http.HttpResponseForbidden('没有这个sku')

        redis_conn = get_redis_connection("history")
        pl = redis_conn.pipeline()
        user_id = request.user.id
        pl.lrem('history_%s'%user_id, 0 , sku_id)
        pl.lpush('history_%s'%user_id,sku_id)
        pl.ltrim('history_%s' % user_id, 0, 4)
        pl.execute()

        return http.JsonResponse({'code': RETCODE.OK,'errmsg':"OK"})



