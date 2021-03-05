from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from base.serializers import BaseModelSerializer
from user.serializers import ReturnBriefUserSerializer
from rest_framework.utils import model_meta
from .models import *
from user.models import Auth
import json
import requests
import datetime

# 游戏序列化器
class GameSerializer(serializers.ModelSerializer):
    game_name = serializers.CharField(label="游戏名称代码", help_text="游戏名称代码", required=True, allow_blank=False,
                                      validators=[UniqueValidator(queryset=Game.objects.all(), message="该游戏名称代码已经存在")])
    game_name_cn = serializers.CharField(label="游戏名称", help_text="游戏名称", required=True, allow_blank=False,
                                         validators=[UniqueValidator(queryset=Game.objects.all(), message="该游戏名称已经存在")])

    class Meta:
        model = Game
        exclude = ('deleted', 'sort_time', 'create_time', 'update_time',)


# 游戏权限序列化器
class AuthGameSerializer(serializers.ModelSerializer):
    # 这里定义一个game_details的作用就是避免使用game，这样post也可以使用同样这个序列化器，否则得写两个序列化器。
    # game_details = GameSerializer(source='game', read_only=True)
    # auth_details = ReturnBriefAuthSerializer(source='auth', read_only=True)
    game_name_cn = serializers.SerializerMethodField()
    game_name = serializers.SerializerMethodField()
    auth_type = serializers.SerializerMethodField()

    class Meta:
        model = AuthGame
        exclude = ()

    def get_game_name_cn(self, obj):
        return obj.game.game_name_cn

    def get_game_name(self, obj):
        return obj.game.game_name

    def get_auth_type(self, obj):
        return obj.auth.auth_type


# 游戏价格序列化器
class PriceSerializer(serializers.ModelSerializer):
    game_name_cn = serializers.SerializerMethodField()
    charge_type_name_cn = serializers.SerializerMethodField()

    class Meta:
        model = Price
        exclude = ()

    def get_game_name_cn(self, obj):
        return obj.game.game_name_cn

    def get_charge_type_name_cn(self, obj):
        return obj.charge_type.type_name_cn


class GameListSerializer(serializers.ModelSerializer):

    class Meta:
        model = AuthGame
        exclude = ('deleted',)
        # fields = ('id','game_name','game_name_cn',)


# 充值类型序列化器
class ChargeTypeSerializer(serializers.ModelSerializer):
    type_name = serializers.CharField(label="充值类型代码", help_text="充值类型代码", required=True, allow_blank=False,
                                      validators=[UniqueValidator(queryset=ChargeType.objects.all(), message="该充值类型代码已经存在")])
    type_name_cn = serializers.CharField(label="充值类型", help_text="充值类型", required=True, allow_blank=False,
                                         validators=[UniqueValidator(queryset=ChargeType.objects.all(), message="该充值类型已经存在")])

    class Meta:
        model = ChargeType
        exclude = ('deleted', 'sort_time', 'create_time', 'update_time',)
        # 如果上面ChargeTypeSerializer中继承了BaseModelSerializer， exclude中就不能包含'sort_time', 'create_time', 'update_time'


# 充值序列化器
class AddChargeSerializer(serializers.ModelSerializer):
    # game_details = GameSerializer(source='game', read_only=True)

    class Meta:
        model = Charge
        exclude = ('deleted', 'user', 'sort_time', 'create_time', 'update_time',)
        # 这里必须把user排除掉，因为充值的时候没有在数据中传递用户信息

    # 这里把user添加到参数中，让请求中能够有user信息。这里的attrs中有game和chargeType的Object
    def validate(self, attrs):
        attrs['user'] = self.context['request'].user
        if attrs['chargetype'].decide_type == 0:
            attrs['charge_value'] = attrs['chargetype'].charge_value
            attrs['days'] = attrs['chargetype'].days
            attrs['fuzhu_vip'] = attrs['chargetype'].vip
        else:
            attrs['fuzhu_vip'] = self.context['request'].data['fuzhu_vip']
        return attrs

    def create(self, validated_data):
        # result = [
        #   "充值30天成功！",
        #   "ID    ：5586624",
        #   "区服  ：741",
        #   "原到期时间：2030-11-11 11:11:11",
        #   "新到期时间：2030-12-11 11:11:11"
        # ]
        # result=json.dumps(result, ensure_ascii=False)
        # validated_data['result'] = result
        charge_res = self.charge(validated_data)
        res_data = charge_res['data']

        # 判断是否改游戏和充值类型是否有单独定价
        game_id = validated_data.get('game').id
        charge_type_id = validated_data.get('chargetype').id
        price = Price.objects.filter(game_id = game_id, charge_type_id = charge_type_id).first()
        if price:
            charge_value = price.charge_value
        else:
            charge_value = validated_data.get('charge_value')

        if charge_res['code'] == 100:
            validated_data['status'] = 3
            validated_data['charge_value'] = 0
            validated_data['days'] = 0
        elif charge_res['code'] == 200:
            validated_data['old_fuzhu_vip'] = res_data['old_fuzhu_vip']
            validated_data['fuzhu_vip'] = res_data['fuzhu_vip']
            validated_data['old_end_time'] = res_data['old_end_time']
            validated_data['end_time'] = res_data['end_time']
            validated_data['result'] = res_data['result']
            validated_data['charge_value'] = charge_value
            validated_data['days'] = validated_data.get('days')
        else:
            validated_data['result'] = res_data['result']
            validated_data['status'] = 2
            validated_data['charge_value'] = 0
            validated_data['days'] = 0
        charge = Charge.objects.create(**validated_data)
        return charge

    def charge(self, validated_data):
        server_id = validated_data.get('server_id')
        userid = validated_data.get('userid')
        days = validated_data.get('days')
        vip = validated_data.get('fuzhu_vip')
        url = validated_data.get('game').charge_url
        account = validated_data.get('user').username
        params = {
            'server_id': server_id,
            'userid': userid,
            'days': days,
            'vip': vip,
            'account': account
        }
        try:
            res = requests.post(url, data=params, timeout=10)
            res.raise_for_status()
            return  res.json()
        # except requests.HTTPError as e:
        #     print(e)
        except Exception as e:
            res = {
                'code': 100,
                'data': {}
            }
            return res
            print(e)



# 更新充值记录 序列化器
class UpdateChargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Charge
        exclude = ('deleted', 'user', 'result', 'sort_time', 'create_time', 'update_time',)
        # 这里必须把user排除掉，因为充值的时候没有在数据中传递用户信息


    # 这里把user添加到参数中，让请求中能够有user信息。
    def validate(self, attrs):
        now = datetime.datetime.now()
        this_week_start = now - datetime.timedelta(days=now.weekday())
        this_week_start_date = this_week_start.date()
        if self.instance.status == 1:
            raise serializers.ValidationError("已经撤回的记录,无法撤回。")
        elif self.instance.status == 2:
            raise serializers.ValidationError("充值失败的记录无法撤回。")
        elif self.instance.charge_time.date() < this_week_start_date:
            raise serializers.ValidationError("只能撤回本周的记录。")
        # elif self.instance.user_id != self.context['request'].user.id:
        #     raise serializers.ValidationError("只能撤回自己的记录。")
        return attrs

    def update(self, instance, validated_data):
        reset_res = self.reset(instance)
        instance.message = reset_res['message']  # 这里是为了将撤销返回的消息传递到view中
        if reset_res['code'] == 200:
            setattr(instance, 'status', 1)
            setattr(instance, 'charge_value', 0)
            setattr(instance, 'reset_user', self.context['request'].user)
            instance.save()
        return instance

    def reset(self, instance):
        url = instance.game.reset_url
        params = {
            'server_id': instance.server_id,
            'userid': instance.userid,
            'old_end_time': instance.old_end_time,
            'old_fuzhu_vip': instance.old_fuzhu_vip,
            'account': instance.user.username
        }
        try:
            res = requests.post(url, data=params, timeout=5)
            res.raise_for_status()
            return  res.json()
        except requests.HTTPError as e:
            print(e)
        except Exception as e:
            print(e)


# 返回充值信息
class ReturnChargeSerializer(serializers.ModelSerializer):
    '''
    下面两种返回的方式，第一种会直接返回单个字段，第二种会返回整个对象
    '''
    game = serializers.ReadOnlyField(source='game.game_name_cn')
    user = serializers.ReadOnlyField(source='user.username')
    chargetype = serializers.ReadOnlyField(source='chargetype.type_name_cn')
    reset_user = serializers.ReadOnlyField(source='reset_user.username')
    # 下面这种方式会返回game的对象
    # game = GameSerializer()
    # user = ReturnBriefUserSerializer()
    # chargetype = ChargeTypeSerializer()
    # reset_user = ReturnBriefUserSerializer()

    class Meta:
        model = Charge
        exclude = ('deleted', 'sort_time', 'create_time', 'update_time',)

class ChargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Charge
        exclude = ('deleted', 'sort_time', 'create_time', 'update_time',)


# 导出充值信息
class ExportChargeSerializer(serializers.ModelSerializer):
    game_name_cn = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    chargetype = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Charge
        exclude = ('deleted', 'sort_time', 'create_time', 'update_time', 'sort', 'result', 'user', 'game')

    def get_game_name_cn(self, obj):
        return obj.game.game_name_cn

    def get_username(self, obj):
        return obj.user.username

    def get_chargetype(self, obj):
        return obj.chargetype.type_name_cn

    def get_status(self, obj):
        return obj.get_status_display()


# 查询单个用户的辅助信息表单验证
class QueryGameUserViewSerializer(serializers.Serializer):
    '''
    采用这种方式的话，这里只是起校验字段的作用
    在view中需要采用如下方式去查询game
    game_id = serializer.data.get('game_id')
    game = Game.objects.filter(Q(id=game_id)).first()
    '''
    # game_id = serializers.IntegerField()
    '''
    关于外键的serializers
    其实，外键的field也比较简单，如果我们直接使用serializers.Serializer，那么直接用PrimaryKeyRelatedField就解决了。
    因为QueryGameUserViewSerializer不是ModelSerializer，没有对应的model，这里反序列化在view中获取的方法为
    game = serializer.validated_data['game']
    '''
    game = serializers.PrimaryKeyRelatedField(queryset=Game.objects.all(), required=True)
    server_id = serializers.IntegerField()
    userid = serializers.CharField()


class ChargeSumViewSerializer(serializers.Serializer):

    class Meta:
        model = Charge
        exclude = ('deleted', 'sort_time', 'update_time',)





