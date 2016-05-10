from django.contrib import admin

# Register your models here.
from games.models import GameDetail, AppOverview, ADVGameSummary, ADVToGame


class AppAdmin(admin.ModelAdmin):
	#list_display = ('platform', 'type_name', 'app_name')
	list_display = [field.name for field in AppOverview._meta.fields if field.name != "id" and field.name !="last_update_time"]
	list_filter = ('type_name', 'platform',)
	search_fields = ['type_name', 'app_name',  'app_id',  ]
	list_per_page = 20

class AdvAdmin(admin.ModelAdmin):
	list_display = ('name', 'author','network_type', 'screen_type', 'gameplay', 'theme', 'admin_image')
	search_fields = ['name', 'img',  ]
	list_per_page = 20

class GameSummaryAdmin(admin.ModelAdmin):
	list_display = [field.name for field in ADVGameSummary._meta.fields if field.name != "gid" and field.name!='prefix']
	#list_display = ('name', 'company', 'spe_name',)
	search_fields = ['name',]
	ordering = ('prefix',)
	list_per_page = 20

class ADVToGameAdmin(admin.ModelAdmin):
	list_display = ('name', 'spe_name', 'is_valid','admin_image',)
	#search_fields = ('game_summary__id', )
	readonly_fields = ('name', 'adv_game_id', 'img', )
	ordering = ('-id',)
	#list_editable = ('name', )
	list_filter = ('is_valid',)
	list_per_page = 20

admin.site.register(AppOverview, AppAdmin)
admin.site.register(ADVGameSummary, GameSummaryAdmin)
admin.site.register(ADVToGame, ADVToGameAdmin)
#admin.site.register(GameDetail, AdvAdmin)

