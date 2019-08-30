from django.conf.urls import url
from .import views

urlpatterns = [
               url(r'^payment/(?P<order_id>\d+)/$', views.ALIPayView.as_view(), name='alipay'),
               url(r'^payment/status/$', views.PayStatus.as_view(), name='alipay_status')

               ]