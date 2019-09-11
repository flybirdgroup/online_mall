from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    url(r'^register/$',views.UserRegisterView.as_view()),
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$',views.UserCountView.as_view()),
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$',views.UserMobileCountView.as_view()),
    url(r'^login/$',views.UserloginView.as_view(),name='relogin'),
    url(r'^logout/$',views.UserLogoutView.as_view()),
    url(r'^info/$',views.UserInfoView.as_view(), name='info'),
    url(r'^emails/$',views.UserEmailView.as_view(), name='email'),
    url(r'^emails/verification/$',views.UserEmailVerificationView.as_view(), name='email'),
    url(r'^addresses/$',views.UserAddressView.as_view(), name='addresses'),
    url(r'^addresses/(?P<address_id>\d+)/$',views.UpdateDeleteAddressView.as_view()),
    url(r'^addresses/(?P<address_id>\d+)/default/$',views.DefaultAddressViews.as_view()),
    url(r'^addresses/(?P<address_id>\d+)/title/$',views.UpdateTitleAddressView.as_view()),
    url(r'^addresses/create/$', views.CreateAddressView.as_view()),
    url(r'^password/$',views.ModifyPassword.as_view()),
    url(r'^find_password/$', views.Find_PasswordView.as_view()),
    url(r'^users/(?P<user_id>\d+)/password/$',views.PasswordSettingView.as_view())
]