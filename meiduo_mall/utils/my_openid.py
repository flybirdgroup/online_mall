from itsdangerous import TimedJSONWebSignatureSerializer
from django.conf import settings

#1 加密opennid

def encode_openid(openid):
    #1,创建加密对象
    serializer = TimedJSONWebSignatureSerializer(secret_key=settings.SECRET_KEY,expires_in=300)

    #2
    token = serializer.dumps({"openid": openid})

    #3 返回加密的open
    return token.decode()

def decode_openid(token):
    serializer = TimedJSONWebSignatureSerializer(secret_key=settings.SECRET_KEY, expires_in=300)
    try:
        data_dict = serializer.loads(token)
    except Exception as e:
        print(e)
        return None
    else:
        openid = data_dict.get('openid')
        return openid
