from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import date
from datetime import timedelta

from goods.models import CategoryVisitCount
from meiduo_admin.home.home_serializers import CategoryVisitCountSerializer
from users.models import User


class UserTotalCoutView(APIView):
    # permission_classes = [IsAdminUser]

    def get(self,request):
        total_user_count =User.objects.all().count()
        today_date = date.today()
        return Response({'count':total_user_count,'date':today_date})


class UserDayCountView(APIView):
    def get(self,request):
        #要获取新增用户
        #思路1 今天的用户总数减去昨天的用户总数   用户filter创建用户日期在小于等于今天 减去 昨天的
        Today_date = date.today()
        today_users_total = User.objects.filter(date_joined__gte=Today_date).count()
        return Response ({'count': today_users_total, "date": Today_date})


class UserActiveCountView(APIView):
    def get(self,request):
        today_date = date.today()
        One_day = timedelta(days=1)
        yesterday_date = today_date - One_day
        active_users_count = User.objects.filter(last_login__gt=yesterday_date).count()
        print(active_users_count)
        return Response({'count': active_users_count, 'date':today_date})


class UserDaysOrderView(APIView):
    def get(self,request):
        today_date = date.today()
        today_order_count = User.objects.filter(orderinfo__create_time__gte=today_date).count()
        return Response({'count': today_order_count, 'date':today_date})


class UserMonthCountView(APIView):
    def get(self, request):
        # 获取当前日期
        now_date = date.today()
         # 获取一个月前日期
        start_date = now_date - timedelta(29)
        # 创建空列表保存每天的用户量
        date_list = []

        for i in range(30):
            # 循环遍历获取当天日期
            index_date = start_date + timedelta(days=i)
            # 指定下一天日期
            cur_date = start_date + timedelta(days=i + 1)
            # 查询条件是大于当前日期index_date，小于明天日期的用户cur_date，得到当天用户量
            count = User.objects.filter(date_joined__gte=index_date, date_joined__lt=cur_date).count()

            date_list.append({
                'count': count,
                'date': index_date
            })
        return Response(date_list)

class GoodsDayView(APIView):
    def get(self,request):
        today_date = date.today()
        data = CategoryVisitCount.objects.filter(date=today_date)
        serializer = CategoryVisitCountSerializer(data, many=True)
        return Response(serializer.data)
