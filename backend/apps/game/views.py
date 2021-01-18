import datetime
import requests
from django.db.models import F, Q
from django.db.models import Count, Sum
from django.db import connection
import django_filters
from rest_framework import serializers, status, generics, mixins, viewsets
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from utils.utils import jwt_decode_handler,jwt_encode_handler,jwt_payload_handler,jwt_payload_handler,jwt_response_payload_handler,google_otp,VisitThrottle,getDistance,NormalObj
from utils.jwtAuth import JWTAuthentication
from utils.pagination import Pagination
from utils.permissions import JWTAuthPermission, AllowAllPermission, BaseAuthPermission, AdminGetPermission
from .models import *
from .serializers import *
from .filters import *
from user.models import User


class GameViewset(ModelViewSet):
    '''
    修改局部数据
    create:  创建游戏
    retrieve:  检索某个游戏
    update:  更新游戏
    destroy:  删除游戏
    list:  获取游戏列表
    '''
    queryset = Game.objects.all().order_by('-update_time')
    authentication_classes = (JWTAuthentication,)
    permission_classes = [BaseAuthPermission, ]
    serializer_class = GameSerializer
    pagination_class = Pagination
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
    search_fields = ('game_name', 'game_name_cn')


class AuthGameViewset(ModelViewSet):
    queryset = AuthGame.objects.all()
    authentication_classes = (JWTAuthentication,)
    # permission_classes = [BaseAuthPermission, ]
    serializer_class = AuthGameSerializer
    pagination_class = Pagination

    def get_queryset(self):
        if self.request.user.group.group_type in ['SuperAdmin']:
            queryset = AuthGame.objects.all().order_by('auth_id')
            return queryset
        else:
            return AuthGame.objects.filter(auth_id=self.request.user.auth_id)


class ChargeTypeViewset(ModelViewSet):
    queryset = ChargeType.objects.all()
    authentication_classes = (JWTAuthentication,)
    permission_classes = [BaseAuthPermission, ]
    serializer_class = ChargeTypeSerializer
    pagination_class = Pagination
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
    search_fields = ('type_name', 'type_name_cn')
    ordering_fields = ('sort',)

    def get_queryset(self):
        queryset = ChargeType.objects.all().order_by('sort')
        return queryset


class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    '''
    用于查询条件包含在数组的方式
    https://www.cnblogs.com/MarsMercury/p/11316244.html
    https://django-filter.readthedocs.io/en/master/ref/filters.html#baseinfilter
    '''
    pass


class ChargeFilter(django_filters.rest_framework.FilterSet):
    """自定义充值的过滤类,会先经过ChargeViewset中的get_queryset，然后才到这里"""
    '''
    对于 django_filters.DateTimeFilter 在执行 SQL 时会把前端的时间参数当成是东八区时间然后转为 UTC 时区时间
    查询url为http://127.0.0.1:8000/charge/?start_time=2020-12-22 00:00:00&end_time=2020-12-23 00:00:00
    上面的和下面的效果一样http://127.0.0.1:8000/charge/?start_time=2020-12-22&end_time=2020-12-23 00:00:00
    '''
    start_time = django_filters.DateTimeFilter(field_name="charge_time",lookup_expr="gte")
    # end_time = django_filters.DateTimeFilter(field_name="charge_time",lookup_expr="lte")
    user_id = NumberInFilter(field_name="user", lookup_expr='in')


    '''
    下面的方式是自定义查询的方式，目的将end_tim加一天。
    要不然这种情况http://127.0.0.1:8000/charge/?start_time=2020-12-22&end_time=2020-12-22就查询不到2020-12-22的数据
    '''
    end_time = django_filters.DateTimeFilter(field_name="charge_time", method='filter_end_time')
    # user_id = django_filters.CharFilter(field_name="user", method='filter_user')
    def filter_end_time(self, queryset, name, value):
        end_time = value + datetime.timedelta(days=1)
        return queryset.filter(Q(charge_time__lte = end_time))

    def filter_user(self, queryset, name, value):
        # 自定义的多选user查询，但是不是很好，采用上面的NumberInFilter才是更好的方法
        arr_user_id_str = value.split(',')
        arr_user_id_int = []
        for i in arr_user_id_str:
            arr_user_id_int.append(int(i))
        return queryset.filter(Q(user_id__in = arr_user_id_int))


    class Meta:
        model = Charge  # 关联的表
        fields = ['start_time', 'end_time', 'status', 'game', 'server_id', 'userid', 'chargetype', 'user', 'user_id']  # 过滤的字段


class ChargeViewset(ModelViewSet):
    '''
    修改局部数据
    create:  创建充值记录
    retrieve:  检索某个充值记录
    update:  更新充值记录
    destroy:  删除充值记录
    list:  获取充值记录列表
    '''
    queryset = Charge.objects.all()
    authentication_classes = (JWTAuthentication,)
    permission_classes = [BaseAuthPermission, ]
    serializer_class = ReturnChargeSerializer
    pagination_class = Pagination
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
    filter_class  = ChargeFilter
    search_fields = ( 'server_id', 'userid',) # 搜索功能对应的字段,查询参数为search，http://127.0.0.1:8000/charge/?search=30 模糊匹配 # '^' Starts-with search；'=' Exact matches.
    filter_fields = ('charge_value', 'days', 'server_id', 'userid',) # 用于精确搜索的字段，DjangoFilterBackend提供的功能, 因为前面用了自定义filter_class，这里就不生效了。自定义的filter_class生效
    ordering_fields = ('update_time', 'create_time',)
    '''
    如果有ordering_fields
        url输入的是该字段，就按该字段排序（ordering_fields必须是可以参与order_by()的字段，否则会报错）否则不排序
    
    如果ordering_fields = '__all__':
        1. 如 url:/ordering = -sdfsfd，则 ordering = None，不排序
        2. 如 url:/ordering = -update_time, 则 ordering = -update_time，按-update_time
    
    如果没有指定ordering_fields,
        1. 不参与序列化，如：sdsadf。则 ordering = None，不排序
        2. 参与序列化且是表字段，如：price，则 ordering = price, 按price排序，
        3. 参与序列化不是表字段，如：brand_name, 则 ordering = brand_name,报错（order_by(brand_name)出错）
    '''


    def get_serializer_class(self):
        print('ChargeViewset')
        if self.action in ['create']:
            print('ChargeViewset-add')
            return AddChargeSerializer
        if self.action in ['update', 'partial_update']:
            print('ChargeViewset-update')
            return UpdateChargeSerializer
        return ReturnChargeSerializer

    def get_queryset(self):
        '''
        因为搜索这里如果是超级管理员，需要能够进行搜索全部用户的，
        Admin用户能够搜索自己有权限游戏的所有记录
        而代理只能搜索自己的记录
        '''
        if bool(self.request.auth) and self.request.user.group.group_type == 'SuperAdmin':
            if bool(self.request.query_params.get('user')):
                user_id = self.request.query_params.get('user')
                queryset = Charge.objects.filter(user_id=user_id).order_by('-charge_time')
            else:
                queryset = Charge.objects.all().order_by('-charge_time')
        elif bool(self.request.auth) and self.request.user.group.group_type == 'Admin':
                '''
                找出该用户的auth_id，然后再从AuthGame中找出该auth_id对应的game_id
                '''
                qs_game = AuthGame.objects.filter(auth_id=self.request.user.auth_id).values('game_id')
                queryset = Charge.objects.filter(game_id__in = qs_game).order_by('-charge_time')
        elif bool(self.request.auth):
            queryset = Charge.objects.filter(user_id=self.request.user.id).order_by('-charge_time')
        else:
            queryset = []
        # 如果不用filter_class自定义时间过滤，也可以通过下面的方法进行过滤
        # start_time = self.request.query_params.get('start_time', None)
        # end_time = self.request.query_params.get('end_time', None)
        # if start_time and end_time:
        #     queryset = queryset.filter(create_time__range=[start_time, end_time])
        return queryset
    '''
    '''
    # 下面这个方法写与不写结果都一样， CreateModelMixin 中的create方法和这个差不多
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # serializer.validated_data 和 AddChargeSerializer 中的validate返回的结果一样
        # print(serializer.validated_data)
        self.perform_create(serializer)
        if (serializer.data['status'] == 0):
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif (serializer.data['status'] == 2):
            return Response({"errorCode": 1, "message": serializer.data['result']}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"errorCode": 1, "message": '充值响应异常，请在充值页面查询是否已经充值成功'}, status=status.HTTP_403_FORBIDDEN)


    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        if (serializer.data['status'] == 1):
            return Response(serializer.data)
        else:
            return Response({"errorCode": 1, "message": instance.message})


from rest_framework.viewsets import ReadOnlyModelViewSet
from drf_renderer_xlsx.mixins import XLSXFileMixin
from drf_renderer_xlsx.renderers import XLSXRenderer
class ChargeExportViewset(XLSXFileMixin, ReadOnlyModelViewSet):
    queryset = Charge.objects.all()
    authentication_classes = (JWTAuthentication,)
    permission_classes = [JWTAuthPermission, ]
    serializer_class = ExportChargeSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class  = ChargeFilter
    renderer_classes = (XLSXRenderer,)
    filename = 'charge_export.xlsx'


    def get_queryset(self):
        '''
        因为搜索这里如果是超级管理员，需要能够进行搜索全部用户的，
        Admin用户能够搜索自己有权限游戏的所有记录
        而代理只能搜索自己的记录
        '''
        if bool(self.request.auth) and self.request.user.group.group_type == 'SuperAdmin':
            if bool(self.request.query_params.get('user')):
                user_id = self.request.query_params.get('user')
                queryset = Charge.objects.filter(user_id=user_id).order_by('-charge_time')
            else:
                queryset = Charge.objects.all().order_by('-charge_time')
        elif bool(self.request.auth) and self.request.user.group.group_type == 'Admin':
                '''
                找出该用户的auth_id，然后再从AuthGame中找出该auth_id对应的game_id
                '''
                qs_game = AuthGame.objects.filter(auth_id=self.request.user.auth_id).values('game_id')
                queryset = Charge.objects.filter(game_id__in = qs_game).order_by('-charge_time')
        elif bool(self.request.auth):
            queryset = Charge.objects.filter(user_id=self.request.user.id).order_by('-charge_time')
        else:
            queryset = Charge.objects.filter(id=0)
        return queryset
    
    column_header = {
        'height': 20,
        'column_width': [10, 14, 14, 14, 14, 14, 14, 14, 14, 14, 22, 22, 14, 22, 14, 22,],
    }

    body = {
        'style': {
            # 'fill': {
            #     'fill_type': 'solid',
            #     'start_color': 'FFCCFFCC',
            # },
            # 'alignment': {
            #     'horizontal': 'left',
            #     'vertical': 'center',
            #     'wrapText': True,
            #     'shrink_to_fit': True,
            # },
            # 'border_side': {
            #     'border_style': 'thin',
            #     'color': 'FF000000',
            # },
            # 'font': {
            #     'name': 'Arial',
            #     'size': 12,
            #     'bold': False,
            #     'color': 'FF000000',
            # }
        },
        'height': 20,
    }


class ChargeSumView(mixins.ListModelMixin, generics.GenericAPIView):
    '''
    根据时间段汇总充值数据
    '''
    serializer_class = ChargeSumViewSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = [JWTAuthPermission, ]
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
    # filter_class  = ChargeFilter  # 这里因为没有用get_query_set，所有没起作用

    def get(self, request, *args, **kwargs):
        # return self.list(request, *args, **kwargs)
        try:
            query_res = self.query()
            return Response({"message": "查询成功", "errorCode": 0, "data": query_res})
        except Exception as e:
            print('发生错误：',e)
            return Response({"message": "出现了无法预料的view视图错误：%s" % e, "errorCode": 1, "data": {}})

    def query(self):
        '''
        1. 超级管理员能够查看所有的
        2. 管理员能够查看自己管理游戏的所有用户的
        3. 普通用户只能查看自己管理的所有游戏的
        4. 如果不传时间，默认查询7天的
        '''
        today = datetime.date.today()
        start_time = self.request.query_params.get('start_time', today - datetime.timedelta(days=7))
        has_end_time = self.request.query_params.get('end_time', None)
        if has_end_time:
            # 这里加一天，要不然必须输入2020-12-27，2020-12-28才能查询出2020-12-27的数据
            end_time = datetime.datetime.strptime(self.request.query_params.get('end_time'), '%Y-%m-%d') + datetime.timedelta(days=1)
        else:
            end_time = today
        game_id = self.request.query_params.get('game_id', None)
        user_id = self.request.query_params.get('user_id', None)
        select = {'day': connection.ops.date_trunc_sql('day', 'charge_time')} # 按天统计归档
        queryset = Charge.objects.filter(charge_time__range=[start_time, end_time]).extra(select=select)
        if game_id:
            arr_game_id_str = game_id.split(',')
            arr_game_id_int = []
            for i in arr_game_id_str:
                arr_game_id_int.append(int(i))
            queryset = queryset.filter(game_id__in=arr_game_id_int)
        if user_id:
            arr_user_id_str = user_id.split(',')
            arr_user_id_int = []
            for i in arr_user_id_str:
                arr_user_id_int.append(int(i))
            queryset = queryset.filter(user_id__in=arr_user_id_int)
        if bool(self.request.auth) and self.request.user.group.group_type == 'SuperAdmin':
            # 这里的双下划线超厉害。比如下面的user__username就直接可以把对应的user_id在user表中对应的username查询出来。
            queryset = queryset.values("game__game_name_cn","user__username", "day").annotate(charge_value=Sum('charge_value'))
        elif bool(self.request.auth) and self.request.user.group.group_type == 'Admin':
            qs_game = AuthGame.objects.filter(auth_id=self.request.user.auth_id).values('game_id')
            queryset = queryset.filter(game_id__in = qs_game).values("game__game_name_cn","user__username", "day").annotate(charge_value=Sum('charge_value'))
        elif bool(self.request.auth):
            queryset = queryset.filter(user_id=self.request.user.id).values("game__game_name_cn","user__username", "day").annotate(charge_value=Sum('charge_value'))
        else:
            queryset = []
        return queryset


class QueryGameUserView(generics.GenericAPIView):
    serializer_class = QueryGameUserViewSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = [JWTAuthPermission, ]

    # 这里定义的为get，就只能用get方法;如果想要支持post方法，就得定义对应的函数post
    def get(self, request):
        try:
            serializer = self.get_serializer(data=request.query_params)
            if not serializer.is_valid():
                return Response({"message": str(serializer.errors), "errorCode": 4, "data": {}})
            data = (serializer.data)
            userid = data.get('userid')
            server_id = data.get('server_id')
            game = serializer.validated_data['game']
            data['game_name'] = game.game_name
            query_res = self.query(game, userid, server_id)
            if query_res['code'] == 200:
                return Response({"message": query_res['message'], "errorCode": 0, "data": query_res['data']})
            else:
                return Response({"message": query_res['message'], "errorCode": 1 })
        except Exception as e:
            print('发生错误：',e)
            return Response({"message": "出现了无法预料的view视图错误：%s" % e, "errorCode": 1, "data": {}})

    def query(self, game, userid, server_id):
        url = game.query_url
        print('url', url)
        params = {
            'server_id': server_id,
            'userid': userid,
            'account': self.request.user.username
        }
        try:
            res = requests.get(url, params=params, timeout=5)
            res.raise_for_status()
            return  res.json()
        except requests.HTTPError as e:
            print(e)
        except Exception as e:
            print(e)


class UserOfAuthView(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = [AdminGetPermission, ]

    def get(self, request):
        try:
            auth_id = request.user.auth.id
            qs1 = AuthGame.objects.filter(auth_id = auth_id).values('game_id')
            qs2 = AuthGame.objects.filter(game_id__in = qs1).values('auth_id')
            qs3 = User.objects.filter(auth_id__in = qs2).values('username', 'id')
            return Response({"message": '操作成功', "errorCode": 0, "data": qs3})
        except Exception as e:
            return Response({"message": "出现了无法预料的view视图错误：%s" % e, "errorCode": 1, "data": {}})
