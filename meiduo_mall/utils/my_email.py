from itsdangerous import TimedJSONWebSignatureSerializer
from django.conf import settings
from users.models import User
def generate_verify_url(user):
    # 创建加密对象
    serializer = TimedJSONWebSignatureSerializer(secret_key=settings.SECRET_KEY, expires_in=300)
    #加密的数据
    data = {"user_id": user.id, "email":user.email}

    #加密
    token = serializer.dumps(data)
    token = token.decode()

    #拼接链接
    verify_url = '%s?token=%s'%(settings.EMAIL_VERIFY_URL, token)
    #返回链接
    return verify_url

def decode_token(token):
    serializer = TimedJSONWebSignatureSerializer(secret_key=settings.SECRET_KEY, expires_in=300)
    try:
        data = serializer.loads(token)
        user_id = data.get('user_id')
        user = User.objects.get(id = user_id)
    except Exception as e:
        print(e)
        return None
    return user
