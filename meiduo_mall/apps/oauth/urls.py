from django.conf.urls import url
from .import views

urlpatterns = [url(r'^qq/login/$', views.QQLoginVIEW.as_view()),
               url(r'^oauth_callback/$', views.OAuthCallBackView.as_view()),
               url(r'^sina/login/$', views.SinaLoginView.as_view()),
               url(r'^sina_callback/$', views.SinaCallBackView.as_view())
               ]