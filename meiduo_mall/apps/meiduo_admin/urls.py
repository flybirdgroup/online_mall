from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token
from meiduo_admin.home import home_views
from meiduo_admin.user import user_views
from meiduo_admin.items import items_views, sku_views, spu_views, option_views, goodschannel_views, goodsbrands_views, \
    image_views

urlpatterns = [url(r'^authorizations/$', obtain_jwt_token),
               url(r'^statistical/total_count/$', home_views.UserTotalCoutView.as_view()),
               url(r'^statistical/day_increment/$', home_views.UserDayCountView.as_view()),
               url(r'^statistical/day_active/$', home_views.UserActiveCountView.as_view()),
               url(r'^statistical/day_orders/$', home_views.UserDaysOrderView.as_view(), name="用户订单"),
               url(r'^statistical/month_increment/$', home_views.UserMonthCountView.as_view()),
               url(r'^statistical/goods_day_views/$', home_views.GoodsDayView.as_view()),
               url(r'^users/$',user_views.UserView.as_view()),
               url(r"^skus/categories/$", items_views.SkuCategoriesView.as_view()),
               url(r'^goods/simple/$', items_views.SpuSimpleView.as_view()),
               url(r'^goods/(?P<spu_id>\d+)/specs/$', sku_views.SkuSpuSpecificationView.as_view()),
               url(r'^goods/channel/categories/$', spu_views.SPUCategoriesView.as_view()),
               url(r'^goods/channel/categories/(?P<sid>\d+)', spu_views.SPUSubCategories.as_view()),
               url(r'^goods/brands/simple/$', spu_views.SPUBrand.as_view()),
               url(r'^goods/images/$', spu_views.SPUImageView.as_view()),
               url(r'goods/specs/simple/$',option_views.SpecificationOptionView.as_view()),
               url(r'^goods/categories/$', goodschannel_views.ChannelCategoriesView.as_view(), name="一级类别显示"),
               url(r'^goods/channel_types/$', goodschannel_views.GoodsChannelGroupView.as_view(), name="频道组"),
               url(r'^skus/simple/$', image_views.ImageSKUView.as_view(),name='图片管理下的显示SKU功能')
]

router = DefaultRouter()
router.register(r'skus/images', viewset=image_views.SKUImageView,base_name="SKU图片管理")
urlpatterns += router.urls

router = DefaultRouter()
router.register(r'skus', viewset=items_views.SKUView,base_name='SKU路由注册')
urlpatterns += router.urls
print(router.urls)

router = DefaultRouter()
router.register(r'specs/options', viewset=option_views.OptionView,base_name='规格选项注册')
urlpatterns += router.urls

router = DefaultRouter()
router.register(r'goods/brands', viewset=goodsbrands_views.GoodsBrandView,base_name='品牌注册')
urlpatterns += router.urls

router = DefaultRouter()
router.register(r'goods/channels', viewset=goodschannel_views.GoodsChannelView, base_name='频道注册')
urlpatterns += router.urls

router = DefaultRouter()
router.register(r'goods/specs',spu_views.SPUspecificationView,base_name="规格管理注册")
urlpatterns += router.urls


router = DefaultRouter()
router.register(r'goods', viewset=spu_views.SPUView,base_name='SPU路由注册')
urlpatterns += router.urls








