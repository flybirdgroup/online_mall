from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [url(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$',views.SKUListView.as_view()),
               url(r'hot/(?P<category_id>\d+)/$', views.HotSkuListView.as_view() ),
               url(r'^detail/(?P<sku_id>\d+)/$', views.DetailView.as_view()),
               url(r'^detail/visit/(?P<category_id>\d+)/$',views.CategoryVisitCountView.as_view()),
               url(r'^browse_histories/$', views.UserBrowseHistory.as_view()),





]