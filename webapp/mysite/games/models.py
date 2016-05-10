#!coding=utf-8
from django.db import models

# Create your models here.
class AppOverview(models.Model):
	platform = models.CharField(max_length=45)
	app_id = models.CharField(max_length=500)
	company = models.CharField(max_length=500)
	app_name = models.CharField(max_length=500)
	type_name = models.CharField(max_length=45)
	payamount = models.FloatField()
	payment_user = models.FloatField(default=0)
	payment_rate = models.FloatField()
	dau = models.FloatField()
	avg_new_user = models.FloatField()
	retain_d1_rate = models.FloatField()
	retain_d7_rate = models.FloatField()
	retain_d14_rate = models.FloatField()
	retain_d30_rate = models.FloatField()
	ltv_d15 = models.FloatField()
	oneday_user_rate = models.FloatField(verbose_name=u'一日玩家')
	logintimes = models.FloatField()
	duration = models.FloatField()
	last_update_time = models.DateTimeField(blank=True, null=True)
	
	def __unicode__(self):
		return self.app_name

	class Meta:
		managed = False
		db_table = 'app_overview'
		verbose_name = u'平台游戏概述'
		verbose_name_plural = u'平台游戏概述'
	


GAMEPLAY = ((u'RPG-ARPG-大型多人在线', 'RPG-ARPG-大型多人在线'),
	(u'RPG-ARPG-地牢式副本', 'RPG-ARPG-地牢式副本'),
	(u'RPG-TRPG-自动回合制', 'RPG-TRPG-自动回合制'),
	(u'RPG-TRPG-半即时回合', 'RPG-TRPG-半即时回合'),
	(u'RPG-TRPG-传统回合制', 'RPG-TRPG-传统回合制'),
	(u'RPG-IRPG-点击放置', 'RPG-IRPG-点击放置'),
	(u'RPG-IRPG-自动放置', 'RPG-IRPG-自动放置'),
	(u'RPG-SRPG-自动战棋', 'RPG-SRPG-自动战棋'),
	(u'RPG-SRPG-传统战棋', 'RPG-SRPG-传统战棋'),
	(u'ACT-横版格斗', 'ACT-横版格斗'),
	(u'ACT-动作冒险', 'ACT-动作冒险'),
	(u'CAG-CRPG-平面回合制卡牌', 'CAG-CRPG-平面回合制卡牌'),
	(u'CAG-CRPG-动作微操卡牌', 'CAG-CRPG-动作微操卡牌'),
	(u'CAG-CRPG-复合型卡牌', 'CAG-CRPG-复合型卡牌'),
	(u'CAG-TCG/CCG-集换式卡牌', 'CAG-TCG/CCG-集换式卡牌'),
	(u'CAG-TCG/CCG-收集式卡牌', 'CAG-TCG/CCG-收集式卡牌'),
	(u'SLG-RTS-即时战略', 'SLG-RTS-即时战略'),
	(u'SLG-RTS-半即时战略', 'SLG-RTS-半即时战略'),
	(u'SLG-RTS-即时战术', 'SLG-RTS-即时战术'),
	(u'SLG-TBS', 'SLG-TBS'),
	(u'SLG-TD-休闲塔防', 'SLG-TD-休闲塔防'),
	(u'SLG-TD-策略塔防', 'SLG-TD-策略塔防'),
	(u'FTG', 'FTG'),
	(u'MOBA', 'MOBA'),
	(u'STG-FPS', 'STG-FPS'),
	(u'STG-TPS', 'STG-TPS'),
	(u'STG', 'STG'),
	#(u'STG-TPS-自由移动', 'STG-TPS-自由移动'),
	#(u'STG-TPS-固定位置', 'STG-TPS-固定位置'),
	#(u'STG-TPS-掩体转移', 'STG-TPS-掩体转移'),
	#(u'STG-STG-动作射击', 'STG-STG-动作射击'),
	#(u'STG-STG-飞行弹幕射击', 'STG-STG-飞行弹幕射击'),
	#(u'STG-STG-其它', 'STG-STG-其它'),
	(u'SIM-模拟经营', 'SIM-模拟经营'),
	(u'SIM-模拟仿真', 'SIM-模拟仿真'),
	(u'SIM-其它', 'SIM-其它'),
	(u'EDU-恋爱养成', 'EDU-恋爱养成'),
	(u'EDU-宠物养成', 'EDU-宠物养成'),
	(u'EDU-换装养成', 'EDU-换装养成'),
	(u'EDU-其它', 'EDU-其它'),
	(u'AVG-文字冒险', 'AVG-文字冒险'),
	(u'AVG-图形解谜', 'AVG-图形解谜'),
	(u'AVG-其它', 'AVG-其它'),
	(u'PUZ-消除类', 'PUZ-消除类'),
	(u'PUZ-跑酷类', 'PUZ-跑酷类'),
	(u'PUZ-敏捷类', 'PUZ-敏捷类'),
	(u'PUZ-益智类', 'PUZ-益智类'),
	(u'PUZ-儿童教育', 'PUZ-儿童教育'),
	(u'PUZ-社交类', 'PUZ-社交类'),
	(u'PUZ-其它', 'PUZ-其它'),
	(u'TAB-棋牌类', 'TAB-棋牌类'),
	(u'TAB-桌游类', 'TAB-桌游类'),
	(u'MUG-音乐节奏类', 'MUG-音乐节奏类'),
	(u'MUG-舞蹈类', 'MUG-舞蹈类'),
	(u'RCG', 'RCG'),
	(u'SPG', 'SPG'),
	(u'MUD', 'MUD'),
	(u'ETC', 'ETC'))
		
	
THEME = ((u'IP-历史名著-三国', 'IP-历史名著-三国'),
	(u'IP-历史名著-隋唐', 'IP-历史名著-隋唐'),
	(u'IP-历史名著-其它', 'IP-历史名著-其它'),
	(u'IP-传统文学-武侠', 'IP-传统文学-武侠'),
	(u'IP-传统文学-西游', 'IP-传统文学-西游'),
	(u'IP-传统文学-封神', 'IP-传统文学-封神'),
	(u'IP-传统文学-水浒', 'IP-传统文学-水浒'),
	(u'IP-传统文学-童话', 'IP-传统文学-童话'),
	(u'IP-传统文学-其它', 'IP-传统文学-其它'),
	(u'IP-网络文学', 'IP-网络文学'),
	(u'IP-动漫作品-动画', 'IP-动漫作品-动画'),
	(u'IP-动漫作品-漫画', 'IP-动漫作品-漫画'),
	(u'IP-动漫作品-虚拟形象', 'IP-动漫作品-虚拟形象'),
	(u'IP-经典游戏-背景改编', 'IP-经典游戏-背景改编'),
	(u'IP-经典游戏-跨平台移植', 'IP-经典游戏-跨平台移植'),
	(u'IP-经典游戏-迭代续作', 'IP-经典游戏-迭代续作'),
	(u'IP-经典游戏-玩偶形象', 'IP-经典游戏-玩偶形象'),
	(u'IP-影视作品-电影', 'IP-影视作品-电影'),
	(u'IP-影视作品-电视剧', 'IP-影视作品-电视剧'),
	(u'IP-影视作品-网络剧', 'IP-影视作品-网络剧'),
	(u'IP-影视作品-人物肖像', 'IP-影视作品-人物肖像'),
	(u'IP-娱乐综艺', 'IP-娱乐综艺'),
	(u'IP-体育赛事', 'IP-体育赛事'),
	(u'历史-远古时期', '历史-远古时期'),
	(u'历史-春秋战国', '历史-春秋战国'),
	(u'历史-秦汉', '历史-秦汉'),
	(u'历史-隋唐', '历史-隋唐'),
	(u'历史-元明清', '历史-元明清'),
	(u'历史-中国近代', '历史-中国近代'),
	(u'历史-日本战国', '历史-日本战国'),
	(u'历史-西方古代史', '历史-西方古代史'),
	(u'历史-欧洲中世纪', '历史-欧洲中世纪'),
	(u'历史-大航海时期', '历史-大航海时期'),
	(u'历史-美国西部', '历史-美国西部'),
	(u'历史-其它', '历史-其它'),
	(u'东方玄奇-仙侠', '东方玄奇-仙侠'),
	(u'东方玄奇-玄幻', '东方玄奇-玄幻'),
	(u'东方玄奇-神话', '东方玄奇-神话'),
	(u'东方玄奇-武侠', '东方玄奇-武侠'),
	(u'西方幻想-西方神话', '西方幻想-西方神话'),
	(u'西方幻想-西方魔幻', '西方幻想-西方魔幻'),
	(u'日式幻想-蒸汽幻想', '日式幻想-蒸汽幻想'),
	(u'日式幻想-泛幻想', '日式幻想-泛幻想'),
	(u'战争军事-二战军事', '战争军事-二战军事'),
	(u'战争军事-现代战争', '战争军事-现代战争'),
	(u'科幻-生化', '科幻-生化'),
	(u'科幻-星际', '科幻-星际'),
	(u'科幻-末世', '科幻-末世'),
	(u'科幻-未来', '科幻-未来'),
	(u'体育-足球', '体育-足球'),
	(u'体育-篮球', '体育-篮球'),
	(u'体育-其它', '体育-其它'),
	(u'都市-商战', '都市-商战'),
	(u'都市-现代生活', '都市-现代生活'),
	(u'复合-历史', '复合-历史'),
	(u'复合-游戏', '复合-游戏'),
	(u'复合-神话', '复合-神话'),
	(u'复合-动漫', '复合-动漫'),
	(u'复合-影视', '复合-影视'))

NETWORK_TYPE = ((u'单机', '单机'), (u'网游', '网游'))
SCREEN_TYPE = (('2D', '2D'), ('3D', '3D'))

class GameDetail(models.Model):
	name = models.CharField(max_length=500, verbose_name = u'游戏名称', default=u'unknown')
	author = models.CharField(max_length=200, verbose_name = u'厂商名称', default=u'unknown', blank=True)
	network_type = models.CharField(max_length=50, verbose_name=u'联网方式', choices=NETWORK_TYPE, default=u'unknown')
	screen_type = models.CharField(max_length=50, verbose_name=u'画面类型', choices=SCREEN_TYPE, default=u'---')
	img = models.CharField(max_length=500, verbose_name=u'图片')

	gameplay = models.CharField(max_length=200, verbose_name=u'玩法类型', choices=GAMEPLAY, default=u'RPG-ARPG-大型多人在线')
	theme = models.CharField(max_length=200, verbose_name=u'游戏题材', choices=THEME, default=u'IP-历史名著-三国')

	def admin_image(self):
		return '<img src="%s" width="400" height="250"/>' % self.img
	admin_image.allow_tags = True

	def __unicode__(self):
		return self.name

	class Meta:
		verbose_name = u'名称补充'
		verbose_name_plural = u'名称补充'

class ADVGameSummary(models.Model):
	#gid = models.IntegerField(primary_key=True)
	gid = models.AutoField(primary_key=True)
	name = models.CharField(max_length=500, verbose_name = u'游戏名称', default=u'unknown')
	prefix = models.CharField(max_length=50, verbose_name = u'游戏名称首字母', default=u'-')
	company = models.CharField(max_length=200, verbose_name = u'厂商名称', default=u'unknown', blank=True)
	network_type = models.CharField(max_length=50, verbose_name=u'联网方式', choices=NETWORK_TYPE, default=u'unknown')
	screen_type = models.CharField(max_length=50, verbose_name=u'画面类型', choices=SCREEN_TYPE, default=u'---')

	gameplay = models.CharField(max_length=200, verbose_name=u'玩法类型', choices=GAMEPLAY, default=u'RPG-ARPG-大型多人在线')
	theme = models.CharField(max_length=200, verbose_name=u'游戏题材', choices=THEME, default=u'IP-历史名著-三国')

	def __unicode__(self):
		return "%s\t%s" % (self.prefix, self.name)

	class Meta:
		verbose_name = u'游戏信息'
		verbose_name_plural = u'游戏信息'


class ADVToGame(models.Model):

	adv_game_id = models.IntegerField(default=-1)
	name = models.CharField(max_length=200, default=u'unknown', verbose_name=u'市场推荐位名称')
	img = models.CharField(max_length=500, verbose_name=u'图片')
	def admin_image(self):
		return '<img src="%s" width="300" height="200"/>' % self.img
	admin_image.allow_tags = True
	admin_image.short_description = u'图片'
	game_summary = models.ForeignKey(ADVGameSummary, default=-1, verbose_name=u'前缀拼音 + 游戏名')
	def spe_name(self):
		return u'<span style="color:red;font-weight:bold">%s</span>' % self.game_summary
	spe_name.allow_tags = True
	spe_name.short_description = u'前缀拼音 + 游戏名'

	is_valid = models.BooleanField(default=False, verbose_name=u'有效游戏')
	
	def __unicode__(self):
		return self.name

	class Meta:
		verbose_name_plural = u'市场推荐位匹配'
