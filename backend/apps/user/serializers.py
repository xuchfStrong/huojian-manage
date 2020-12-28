from django.db.models import fields
from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from rest_framework.validators import UniqueValidator
from base.serializers import BaseModelSerializer
from rest_framework.utils import model_meta
from .models import *
import time
import datetime
import threading



# 新增权限菜单约束使用
class AddAuthPermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = AuthPermission
        fields = ['id','object_name', 'object_name_cn','auth_list','auth_create','auth_update','auth_destroy']

# 下面这个代码不知道啥作用，注释了也不影响。
# def del_worker(datas):
#     for item in datas:
#         item.delete()
# def save_worker(instance, datas):
#     for item in datas:
#         AuthPermission.objects.create(auth=instance, **item)

# 新增权限使用
class AddAuthSerializer(serializers.ModelSerializer, BaseModelSerializer):
    auth_type = serializers.CharField(label="权限名称", help_text="权限名称", required=True, allow_blank=False,
                                       validators=[UniqueValidator(queryset=Auth.objects.all(), message="该权限已经存在")])
    # 反向取权限，通过related_name
    # 一对多，一个auth下有多个权限，一定要设定many=True
    auth_permissions = AddAuthPermissionSerializer(many=True)

    class Meta:
        model = Auth
        exclude = ('deleted',)

    def create(self, validated_data):
        auth_permissions_data = validated_data.pop('auth_permissions')
        auth_per = Auth.objects.create(**validated_data)
        # 创建权限菜单的方法
        for item in auth_permissions_data:
            # 这里的auth就是AuthPermission表的外键，所以这里用的就前面创建的auth_per对象
            AuthPermission.objects.create(auth=auth_per, **item)
        return auth_per

    def update(self, instance, validated_data):
        # print('查看auth_permissions：', validated_data.get('auth_permissions'))
        if validated_data.get('auth_permissions'):
            auth_permissions_data = validated_data.pop('auth_permissions')
            # 修改时创建权限菜单的方法
            need_dels = AuthPermission.objects.filter(auth_id=instance.id)
            for item in need_dels:
                item.delete()
            for item in auth_permissions_data:
                # print('查看：', item)
                # print('查看id：', item.get('id'))
                AuthPermission.objects.create(auth=instance, **item)
            # 开多线程优化代码
            # del_work = threading.Thread(target=del_worker,args=(need_dels,))
            # del_work.start()
            # save_work = threading.Thread(target=save_worker,args=(instance,auth_permissions_data,))
            # save_work.start()
            # save_work.join()

        # 继承自父类的方法
        info = model_meta.get_field_info(instance)
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                field = getattr(instance, attr)
                field.set(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


# 返回权限使用
class ReturnAuthSerializer(serializers.ModelSerializer, BaseModelSerializer):
    auth_permissions = AddAuthPermissionSerializer(read_only=True, many=True)

    class Meta:
        model = Auth
        exclude = ('deleted',)


# 返回简要权限使用
class ReturnBriefAuthSerializer(serializers.ModelSerializer):

    class Meta:
        model = Auth
        fields = ('id','auth_type',)


# 登录view的表单验证
class LoginViewSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    # test = serializers.DictField(child=serializers.CharField(required=True))


# 新增用户使用
class AddUserSerializer(serializers.ModelSerializer, BaseModelSerializer):

    class Meta:
        model = User
        exclude = ('deleted',)


# ReturnUserSerializer 使用的group序列化器
class UserUseGroupSerializer(serializers.ModelSerializer, BaseModelSerializer):

    class Meta:
        model = Group
        exclude = ('deleted',) 


# 返回用户使用 userinfo
class ReturnUserSerializer(serializers.ModelSerializer, BaseModelSerializer):
    group = UserUseGroupSerializer()
    auth = ReturnAuthSerializer()

    class Meta:
        model = User
        exclude = ('deleted', 'password',)

# 返回简要user数据
class ReturnBriefUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username',)
