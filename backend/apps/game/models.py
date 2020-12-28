from django.db import models
from soft_delete_it.models import SoftDeleteModel
from base.models import BaseModel
from user.models import User, Auth


class Game(SoftDeleteModel, BaseModel):
    game_name = models.CharField(max_length=255, verbose_name='游戏名称')
    game_name_cn = models.CharField(max_length=255, verbose_name='游戏名称-cn')
    charge_url = models.CharField(max_length=255, null=True, blank=True, verbose_name='充值接口')
    query_url = models.CharField(max_length=255, null=True, blank=True, verbose_name='查询接口')
    reset_url = models.CharField(max_length=255, null=True, blank=True, verbose_name='撤销接口')

    class Meta:
        db_table = 'A_Game_Table'
        verbose_name = '游戏名表'
        verbose_name_plural = verbose_name


class AuthGame(models.Model):
    auth = models.ForeignKey(Auth, on_delete=models.CASCADE, verbose_name='权限组', related_name='auth_game')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, verbose_name='游戏', related_name='authgame_game')

    class Meta:
        db_table = 'A_AuthGame_Table'
        verbose_name = '权限游戏表'
        verbose_name_plural = verbose_name
        unique_together=("auth","game")


class ChargeType(SoftDeleteModel, BaseModel):
  vip_choice = (
    (0, '普通卡'),
    (1, 'VIP卡'),
  )
  decide_type_choice = (
    (0, '系统设定'),
    (1, '自定义类型'),
  )
  type_name = models.CharField( max_length=255, verbose_name='充值类型')
  type_name_cn = models.CharField( max_length=255, verbose_name='充值类型-cn')
  charge_value = models.IntegerField( null=True, blank=True,  verbose_name='充值金额')
  vip = models.IntegerField( default=0, choices=vip_choice, verbose_name='是否VIP')
  days = models.IntegerField( default=0, verbose_name='充值天数')
  decide_type = models.IntegerField( default=0, choices=decide_type_choice, verbose_name='充值设定类型')

  class Meta:
      db_table = 'A_Charge_Type'
      verbose_name = '充值类型表'
      verbose_name_plural = verbose_name


class Charge(SoftDeleteModel, BaseModel):
  status_choices = (
    (0, '未撤销'),
    (1, '已撤销'),
    (2, '失败'),
  )
  user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='用户', related_name='charge_user')
  game = models.ForeignKey(Game, on_delete=models.PROTECT, verbose_name='游戏', related_name='charge_game')
  chargetype = models.ForeignKey(ChargeType, on_delete=models.PROTECT, verbose_name='充值类型', related_name='charge_type')
  charge_value = models.IntegerField( null=True, blank=True,  verbose_name='充值金额')
  days = models.IntegerField(default=0, verbose_name='充值天数')
  server_id = models.IntegerField(null=True, blank=True,  verbose_name='服务器ID')
  userid = models.CharField(max_length=255, null=True, blank=True,  verbose_name='用户ID')
  charge_time = models.DateTimeField(auto_now_add=True, verbose_name='充值时间')
  reset_time = models.DateTimeField(auto_now=True, verbose_name='撤销时间')
  old_fuzhu_vip = models.IntegerField(null=True, blank=True,  verbose_name='充值前辅助是否VIP')
  old_end_time = models.DateTimeField(null=True, blank=True, verbose_name='充值前辅助到期时间')
  fuzhu_vip = models.IntegerField(null=True, blank=True,  verbose_name='辅助是否VIP')
  end_time = models.DateTimeField(null=True, blank=True, verbose_name='辅助到期时间')
  status = models.IntegerField(default=0, choices=status_choices, verbose_name='是否撤销')
  result = models.CharField(max_length=1000, null=True, blank=True,  verbose_name='充值结果')

  class Meta:
      db_table = 'A_Charge'
      verbose_name = '充值明细表'
      verbose_name_plural = verbose_name

