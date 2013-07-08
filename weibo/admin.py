from django.contrib import admin
from twitter.weibo.models import User,Twitter,FriendShip,Event
from twitter.weibo.models import Music,Video,Review,Text,Goods,Picture

class UserAdmin(admin.ModelAdmin):
	list_display=('username','password','email','website','face','created_date')

class TwitterAdmin(admin.ModelAdmin):
	list_display=('content','created','file','good','content_num','tags')
class VideoAdmin(admin.ModelAdmin):
	list_display=('video_url',)
class MusicAdmin(admin.ModelAdmin):
	list_display=('music_url',)
	
class TextAdmin(admin.ModelAdmin):
	list_display=('text_url',)
	
class PictureAdmin(admin.ModelAdmin):
	list_display=('picture_url',)
	
class ReviewAdmin(admin.ModelAdmin):
	list_display=('owner','reviewer','content','newreview','created')
	
class FriendShipAdmin(admin.ModelAdmin):
	list_display=('user','follower')
	
class GoodsAdmin(admin.ModelAdmin):
	list_display=('user','description','tags')
admin.site.register(User)
admin.site.register(Twitter,TwitterAdmin)
admin.site.register(Music,MusicAdmin)
admin.site.register(Video,VideoAdmin)
admin.site.register(Picture,PictureAdmin)
admin.site.register(Review,ReviewAdmin)
admin.site.register(FriendShip,FriendShipAdmin)
admin.site.register(Goods,GoodsAdmin)
admin.site.register(Event)
