from django.core.paginator import Paginator
from django.shortcuts import render
from django.views import View
from collections import OrderedDict
from  goods.models import *

# Create your views here.

#创建首页
from contents.models import ContentCategory
from goods.models import GoodsChannel

#产品首页数据库的结构是需要组号,频道,商品分类,一级分类,二级分类,三级分类,名字
from meiduo_mall.utils.my_category import get_categories


class IndexView(View):
    def get(self,request):
        categories = get_categories()

        # 定义字典
        # 获取频道
        #遍历频道
        #获取频道的组好

        #组装数据
        #bian'li
 # # 商品频道及分类菜单[先查询一级分类[分组]，接着查询二级，最后是三级]
 #        categories = {}
 #        # 创建一个字典,categories ={} 表示频道和分类
 #        #分类频道组,
 #        channels = GoodsChannel.objects.order_by('group_id','sequence')
 #        for channel in channels:
 #            group_id = channel.group_id # 找到当前频道组
 #        #找到当前组
 #            if group_id not in categories: #如果categories里面没有这个组,就创建频道组字典
 #                categories[group_id] ={"channels":[], "sub_cats":[]}
 #                #因为一级分类和频道有各自需要的信息,所以channels里面的内容需要两者结合
 #            categories[group_id]['channels'].append({
 #                "id":channel.category.id,
 #                "name":channel.category.name,
 #                'url':channel.url
 #            })
 #            for cat2 in channel.category.subs.all():#查询所有子类
 #                cat2.sub_cats=[]#添加一个属性关于子类的
 #                for cat3 in cat2.subs.all():
 #                    cat2.sub_cats.append(cat3)
 #                categories[group_id]['sub_cats'].append(cat2)

        contents = {}
        content_category = ContentCategory.objects.order_by('id')
        for category in content_category:
            contents[category.key] = category.content_set.all()
        context = {
                "categories": categories,
                "contents":contents
            }

        return render(request,'index.html',context=context)





