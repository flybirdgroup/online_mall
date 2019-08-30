from django.conf import settings
from django.core.mail import send_mail

from celery_tasks.main import app
from meiduo_mall.libs.yuntongxun.sms import CCP
from meiduo_mall.utils.my_email import generate_verify_url


@app.task(bind=True,name="send_email_url")
def send_email_url(self,verify_url,email):
    #1,发送短信
    try:
        result = send_mail(
            subject='美多商城',
            message='请激活链接%s'%verify_url ,
            from_email=settings.EMAIL_FROM,
            recipient_list=[email],

        )

    except Exception as e:
        result = -1

    #2,判断短信是否发送成功
    if result == -1:
        #exc: 发送失败之后的异常,  countdown:间隔的时间  max_retries:重试的次数
        self.retry(exc=Exception("邮件发送失败啦!"),countdown=5,max_retries=3)
