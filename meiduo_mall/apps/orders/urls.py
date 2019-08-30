from django.conf.urls import url
from .import views

urlpatterns = [url(r'^orders/settlement/$', views.OrderSettlementView.as_view()),
               url(r'^orders/commit/$', views.OrdersCommitView.as_view()),
               url(r'^orders/success/$', views.OrdersSuccessView.as_view()),
               url(r'^orders/info/(?P<page_num>\d+)/$', views.OrderInfoView.as_view(),name='info'),

               ]