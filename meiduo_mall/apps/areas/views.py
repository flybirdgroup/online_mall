from django import http
from django.shortcuts import render
from django.views import View
from areas.models import Area
from meiduo_mall.utils.response_code import RETCODE
from django.core.cache import cache

# Create your views here.

class AreaView(View):
    def get(self,request):
        area_id = request.GET.get("area_id")
        if not area_id:
            province_list = cache.get("province_list")
            if province_list:
                context = {"code": RETCODE.OK,
                           'province_list': province_list}
                return http.JsonResponse(context)
            province_list = []
            provinces = Area.objects.filter(parent_id = None).all()
            for province in provinces:
                province_dict = {
                    "id": province.id,
                    "name": province.name
                }
                province_list.append(province_dict)
            context = {"code": RETCODE.OK,
                       'province_list': province_list}
            cache.set("province_list",province_list)
        else:

            area = Area.objects.get(id = area_id)
            sub_list = cache.get("subs_%s"%area_id)
            if sub_list:
                context = {"code": RETCODE.OK,
                           "sub_data": {"subs": sub_list}}
                return http.JsonResponse(context)
            cities = area.subs.all()
            sub_list = []
            for city in cities:
                city_dict = {
                    "id": city.id,
                    "name":city.name
                }
                sub_list.append(city_dict)
            context = {"code":RETCODE.OK,
                       "sub_data":{"subs": sub_list}}
            cache.set("subs_%s"%area_id,sub_list)

        return http.JsonResponse(context)