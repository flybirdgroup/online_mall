#1,图片验证码有效期
from decimal import Decimal

IMAGE_CODE_EXPIRE = 300

#2,短信验证码有效期
SMS_CODE_EXPIRY = 300

#3,防止短信频繁发送标记
SMS_CODE_SEND_FLAG = 60

#4,状态保持有效期
SESSIOIN_MAX_AGE = 3600*24*2


#用户地址限制数量
USER_ADDRESS_COUNTS_LIMIT = 20

LIST_SKU_PER_COUNT = 4

FREIGHT = 10

LIST_ORDER_PER_PAGE = 5

PageNum = 3