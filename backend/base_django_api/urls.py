from base.views import UploadFile, Tests, BeginCelery
from user.views import LoginView, UserViewset, UserInfo, AuthViewset, UserDictExportViewset
from game.views import GameViewset, AuthGameViewset, ChargeTypeViewset, ChargeViewset, QueryGameUserView, ChargeSumView, ChargeExportViewset,UserOfAuthView
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# 新版swagger
from django.conf.urls import url
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
schema_view = get_schema_view(
    openapi.Info(
        title="Django RESTfulAPI",
        default_version='v2',
        description="Ddescription",
        terms_of_service="https://blog.csdn.net/haeasringnar",
        contact=openapi.Contact(email="aeasringnar@163.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
# 使用 viewset 路由管理
router = DefaultRouter()
# 账号管理
router.register(r'user', UserViewset, base_name='账号管理')
router.register(r'exportUser', UserDictExportViewset, base_name='账号导出')
# 权限管理
router.register(r'auth', AuthViewset, base_name='权限管理')
from flow.views import FlowGroupViewset, ApprovalFlowViewset, FlowBodyViewset, FlowGroupListViewset, FlowBodyNeedFlowViewset, ObjectFlowView
# 审批组管理
router.register(r'flowgroup', FlowGroupViewset, base_name='审批组管理')
router.register(r'getflowgroup', FlowGroupListViewset, base_name='获取审批组')
# 审批设置管理
router.register(r'approvalflow', ApprovalFlowViewset, base_name='审批设置管理')
# 审批主体管理
router.register(r'flowbody', FlowBodyViewset, base_name='审批主体管理')
router.register(r'needflowbody', FlowBodyNeedFlowViewset, base_name='待审批列表')
# 游戏管理
router.register(r'game', GameViewset, base_name='游戏管理')
router.register(r'authGame', AuthGameViewset, base_name='游戏权限管理')
router.register(r'chargetype', ChargeTypeViewset, base_name='充值类型管理')
router.register(r'charge', ChargeViewset, base_name='充值管理')
router.register(r'exportCharge', ChargeExportViewset, base_name='充值导出')


urlpatterns = [
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', include(router.urls)),
    path('adminlogin/', LoginView.as_view(), name='后台登录'),
    path('uploadfile/', UploadFile.as_view(), name='文件长传'),
    path('tests/', Tests.as_view(), name='测试接口'),
    path('userinfo/', UserInfo.as_view(), name='获取用户信息'),
    path('celery/', BeginCelery.as_view(), name='测试celery'),
    path('toflow/', ObjectFlowView.as_view(), name='审批操作'),
    path('querGameUser/', QueryGameUserView.as_view(), name='查询单个用户辅助信息'),
    path('chargeSum/', ChargeSumView.as_view(), name='查询单个用户辅助信息'),
    path('userofauth/', UserOfAuthView.as_view(), name='根据管理的游戏查询对应的用户'),
]
