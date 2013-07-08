from django.conf.urls.defaults import *
from django.contrib import admin
from twitter.weibo import views
admin.autodiscover()
from twitter.settings import MEDIA_ROOT
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^twitter/', include('twitter.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    
    
    
    (r'^addmusic/$',views.addmusic),
    (r'^addvideo/$',views.addvideo),
    (r'^getreview/$',views.getreview),
    (r'^getgoodmessage/$',views.getmessage),
     (r'^attentiongood/$',views.attentiongood),
      (r'^searchgoods/$',views.searchgoods),
      (r'^deletegood/$',views.deletegood),
     (r'^getgoods/$',views.getgoods),
     (r'^addfriend/$',views.addfriend),
     (r'^upgoods/$',views.upgoods),
     (r'^addfollow/$',views.addfollow),
     (r'^addattention/$',views.addattention),
    (r'^deletefollowed/$',views.deletefollowed),
    (r'^deletefollow/$',views.deletefollow),
    (r'^searchtwitter/$',views.searchtwitter),
    (r'^deletetwitter/$',views.deletetwitter),
     (r'^like/$',views.like),
    (r'^friended/(?P<followedid>[0-9]*)$',views.friended),
    (r'^followed/$',views.followed),
    (r'^follow/$',views.follow),
    (r'^text/$',views.text),
    (r'^homepage/$',views.homepage),
    (r'^uppicture/$',views.uppicture),
    (r'^friends/(?P<followid>[0-9]*)$',views.friends),
    (r'^addpost/$',views.addpost),
    (r'^verifypwd/$',views.verifypwd),
    (r'^inbox/$',views.inbox),
    (r'^cancel/$',views.cancel),
    (r'^goods/$',views.goods),
    (r'^settings/$',views.settings),
    (r'^modifydata/$',views.modifydata),
    (r'^profile/(?P<userid>[0-9]*)/$',views.profile),
    (r'^addtext/$',views.addtext),
    (r'^addpicture/$',views.addpicture),
    (r'^post/$',views.create_post),
    (r'^signup/$',views.signup),
    (r'^login/findpassword/$',views.findpassword),
    (r'^login/dopwd/$',views.dopwd),
    (r'^login/newpwd/$',views.newpwd),
    (r'^login/dologin/$',views.dologin),
    (r'^login/modifypwd/(?P<key>[a-zA-Z\-_\d]+)/$',views.modifypwd),
    (r'^login/$',views.login),
    (r'^emailactive/(?P<key>[a-zA-Z\-_\d]+)/$',views.emailactive),
    (r'^checkemail/$',views.checkemail),
    (r'^review/$',views.load_review), 
    (r'^addreview/$',views.add_review), 
    (r'^$',views.login),
    (r'^admin/', include(admin.site.urls)),
    (r'^js/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'home/yu/twitter/static/js'}),
    (r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'home/yu/twitter/static/css'}),
    (r'^images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'home/yu/twitter/static/images'}),
    (r'^face/(?P<path>.*)$', 'django.views.static.serve',{'document_root': MEDIA_ROOT+'/face'}),
    (r'^picture/(?P<path>.*)$', 'django.views.static.serve',{'document_root': MEDIA_ROOT+'/picture'}),
    (r'^goods/(?P<path>.*)$', 'django.views.static.serve',{'document_root': MEDIA_ROOT+'/goods'}),
)
