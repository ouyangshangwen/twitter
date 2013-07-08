# -*- coding: utf-8 -*-
import time
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models.signals import post_save
from twitter.settings import MEDIA_ROOT
# Create your models here.
def upload(instance,filename):
    return '/'.join([instance.user.username,filename])
class User(models.Model):
    username = models.CharField(max_length=30,blank=True, null=True)
    address = models.CharField(blank=True, null=True,max_length=100)
    password = models.CharField(max_length=300,blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now = True)
    bigface = models.ImageField('头像',upload_to='bigfaces/%Y/%m/%d',default='',blank=True, null=True)
    smallface= models.ImageField('头像',upload_to='smallfaces/%Y/%m/%d',default='',blank=True, null=True)
    def __unicode__(self):
        return self.username
    
class Twitter(models.Model):
    user = models.ForeignKey(User) 
    title= models.CharField(blank=True,max_length=140)
    content = models.CharField(blank=True,max_length=140) # 内容，最多140字
    created = models.DateTimeField(auto_now_add=True)
    events = generic.GenericRelation('Event')  
    file = models.FileField(upload_to=upload)
    good = models.IntegerField(default=0) 
    cont_type = models.IntegerField(default=0)
    content_num = models.IntegerField(default=0)  
    tags=models.CharField(max_length=100)

    class Meta:
        ordering = ['-created',]
         
    def __unicode__(self):
        return self.content
    
    
class Review(models.Model):
    owner = models.ForeignKey(Twitter)
    me= models.ForeignKey(User,related_name='user')
    reviewer = models.ForeignKey(User,related_name='reviewer')
    content = models.CharField(max_length=140)

    created = models.DateTimeField(auto_now_add=True)
    newreview=models.IntegerField(default=0)
class Reply(models.Model):
    owner = models.ForeignKey(Twitter)
    me = models.ForeignKey(User,related_name='me')
    reply = models.ForeignKey(User,related_name='replyer')
    content = models.CharField(max_length=140)

    created = models.DateTimeField(auto_now_add=True)
    newreview=models.IntegerField(default=0)

class Goods(models.Model):
    user=models.ForeignKey(User)
    title=models.CharField(blank=True,max_length=100)
    goods_url=models.ImageField('物品',upload_to='/goods/',default='',blank=True, null=True)
    description=models.CharField(max_length=200)
    tags=models.CharField(max_length=100)
class RelationGoods(models.Model):
    user=models.ForeignKey(User)
    other=models.ForeignKey(User,related_name='other')
    good=models.ForeignKey(Goods)
    new=models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
class Text(Twitter):
    text_url=models.URLField(verify_exists=False)

class Picture(Twitter): 
    picture_url = models.URLField(verify_exists=False)
        
class Music(Twitter):
    music_url = models.URLField(verify_exists=False)

class Video(Twitter):
    flashurl=models.URLField(verify_exists=False)
    video_url = models.URLField(verify_exists=False)

class Event(models.Model):
    user = models.ForeignKey(User)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    event_object = generic.GenericForeignKey('content_type', 'object_id')

class FriendShip(models.Model):
    user = models.ForeignKey(User, related_name='owner')
    follower = models.ForeignKey(User, related_name='follower')
    
def postsave(sender, instance, **kwargs):
    obj = instance
    event = Event(user=obj.user, event_object=obj)
    event.save()
post_save.connect(postsave, sender=Music, dispatch_uid="my_unique_identifier")
post_save.connect(postsave, sender=Twitter, dispatch_uid="my_unique_identifier")
post_save.connect(postsave, sender=Video, dispatch_uid="my_unique_identifier")
post_save.connect(postsave, sender=Text, dispatch_uid="my_unique_identifier")


















    
