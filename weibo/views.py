#!/usr/bin/python   
# -*- coding: utf-8 -*-
from django.http import HttpResponse,HttpResponseRedirect
from django.template.loader import get_template
from django.template import Template,Context
from django.shortcuts import render_to_response
from django.template import loader,Context
from twitter.weibo.models import User,Twitter,Review,Picture,Music
from twitter.weibo.models import Video,Event,FriendShip,Text,Goods,RelationGoods
from twitter.settings import EMAIL_HOST_USER
import md5
from django.utils import simplejson
from django.core import serializers
import sys,os
import time
from StringIO import StringIO
from PIL import Image
from twitter.settings import *
import ImageFilter




def homepage(request):
	if islogin(request):
		
		try:
			t = loader.get_template('selfpage.html')
			user=User.objects.get(id=user_id(request))
			follow=FriendShip.objects.filter(follower=user).count()
			followed=FriendShip.objects.filter(user=user).count()
			c=Context({'user':user,'followers':follow,'followered':followed})
			return HttpResponse(t.render(c))
		except:
			return render_to_response('selfpage.html')
	else:
		return HttpResponseRedirect('/login/')

def load_review(request):
    if islogin(request):
	    if request.method=='POST':
			t = loader.get_template('review_bar.html')
			twitterid=int(request.POST['twitter_id'])
			owner=Twitter.objects.get(id=twitterid)
			reviews=Review.objects.filter(owner=owner)
			items=[]
			for review in reviews:			
				user=review.owner.user
				x={"content":review.content,'url':review.reviewer.smallface.url,'id':user.id}
				items.append(x)


			c=Context({'items':items})
			result={'html':t.render(c)}
			result=simplejson.dumps(result)
			return HttpResponse(result, mimetype='application/json')			
	    else:	    			
			return render_to_response('404.html')
	
    else:
		return HttpResponseRedirect('/login/')
def create_post(request):
    if islogin(request):
	    t = loader.get_template('selftemplate.html')
	    items=list()

	    users=Twitter.objects.all()
	    user=User.objects.get(id=user_id(request))
	    followers = [entry.user for entry in FriendShip.objects.filter(follower=user)]
	    followers=Twitter.objects.filter(user__in=followers)		
	    for user in followers:
	    	print user.created
	    	flashurl=''																																						    	
	    	outurl=''
	    	pic_url=''
	    	if user.cont_type==1:
	    		outurl=''
	    	if user.cont_type==2:
	    		music=user
	    		outurl=Music.objects.get(twitter_ptr=user.id).music_url
	    	if user.cont_type==3:
	    		outurl=Video.objects.get(twitter_ptr=user.id).video_url
	    		flashurl=getflashurl(url='http://'+outurl)
	    	if user.cont_type==4:
	    		picture=Picture.objects.get(twitter_ptr=user.id)

	    		outurl=picture.picture_url
	    		if picture.file:
	    			pic_url=dowithurl(picture.file.url)
	    		else:
	    			pic_url=''
	    	id=str(user.id)
	        container_id='note_container_'+id
	        review_box_id='review_box_'+id
	        
	        if user.user.smallface:
	        	smallface="background-image:url("+user.user.smallface.url+")"
	        else:
	        	smallface="background-image:url(/images/smallface.png)"
	        if user.file:
	        	picture_url=dowithurl(user.file.url)
	        else:
	        	picture_url = ''

	    	c={'review_box_id':review_box_id,
		        'twitter_id':id,
		        'showreview_id':'showreview_'+id,
		        'notes_id': 'notes_'+id,
		        'note_container_id':container_id,
		        'usrname': user.user.username,
		        'review_count': Review.objects.filter(owner=user).count(),
		        'like_id':'like_id_'+id,
				'content':user.content,
				'url':smallface,
				'pictureurl':picture_url,
				'tags':user.tags.split('#'),
				'outurl':outurl,
				'flashurl':flashurl,
				'myid':user_id(request),	
				'id':user.user.id,
				'title':user.title,
		        }

	    	items.append(c)
	    	#print user.file.url
	    c=Context({'items':items})
	    result={'html':t.render(c)}
	    result=simplejson.dumps(result)
	    return HttpResponse(result, mimetype='application/json')
    else:
		return HttpResponseRedirect('/login/')    	

   	
def add_review(request):
    if islogin(request):
	    t = loader.get_template('review_bar.html')
	    id=int(request.POST['postid'])
	    owner=Twitter.objects.get(id=id)
	    print owner
	    reviewer=user_id(request)
	    reviewer=User.objects.get(id=user_id(request))
	    
	    review_content=request.POST['review_content']
	    review=Review(owner=owner,me=owner.user,reviewer=reviewer,content=review_content,newreview=1)
	    review.save()
	    reviewcount=Review.objects.filter(owner=owner).count()
	    x=list()
	    x=[{"content":review_content,'url':reviewer.smallface.url,'id':reviewer.id}]
	    c=Context({'items':x})
	    mydata={'html':t.render(c),'reviewcount':reviewcount}


	    json=simplejson.dumps(mydata)
	
	    return HttpResponse(json,mimetype='application/json')
    else:
    	return HttpResponseRedirect('/login/')


def checkemail(request):
	if request.method=='POST':
		try:
			aemail=request.POST['email']
			User.objects.get(email=aemail)
			data={'email':'true'}
			
		except User.DoesNotExist:
			data={'email':'false'}
	json=simplejson.dumps(data)
	return HttpResponse(json,mimetype='application/json')	
def signup(request):
	if request.method=='POST':
		request.session['email']=request.POST['email']
		request.session['username']=request.POST['username']
		request.session['password']=md5_encode(request.POST['password'])
		request.session['md5email']=md5_encode(request.POST['email'])
		send_regist_success_mail(title=u'注册成功',url='emailactive',
								
								md_encoding=request.session['md5email'],
								email=request.session['email']
								)
		return render_to_response('prompt.html')
	return render_to_response('signup.html')




from django.core.mail import send_mail




def send_regist_success_mail(title,url,md_encoding,email):
    subject = title
    body = u'''<p><a href="http://127.0.0.1/%s/%s">请点击此链接</a></p>'''% (url,md_encoding)
    
    recipient_list= [email,]  
                      

    send_mail(subject,body,'iminic@163.com', recipient_list,fail_silently=True)   


def md5_encode(str):

    return md5.new(str).hexdigest()
def emailactive(request,key):
	if key==request.session['md5email']:
		print request.session['md5email']
		user=User(
				username=request.session.get('username'),
				password=request.session.get('password'),
				email=request.session.get('email'),
				smallface='/images/smallface.png',
				bigface='/images/bigface.png',
				
				)
		user.save()
		return HttpResponseRedirect('/login/')
	return HttpResponseRedirect('/login/')
	
def login(request):
	return render_to_response('login.html')
def dologin(request):
	if request.method=='POST':
		try:
			myemail=request.POST['email']
			user=User.objects.get(email=myemail)
			
			if user.password==md5_encode(request.POST['password']):
				request.session['id']=user.id

				request.session['email']=myemail
				request.session['islogin']=True
				return HttpResponseRedirect('/homepage/')
			else:
				return HttpResponseRedirect('/login/')
		except User.DoesNotExist:
			return  HttpResponseRedirect('/login/')

def findpassword(request):
	return render_to_response('findpassword.html')

def dopwd(request):
	if request.method=='POST':
		try:
			aemail=request.POST['email']			
			user=User.objects.get(email=aemail)
			request.session['email']=user.email
			send_regist_success_mail(title=u'密码修改',
									url='login/modifypwd',
								
								md_encoding=md5_encode(user.email),
								email=user.email
								)
			return  HttpResponseRedirect('/login/')
			
		except User.DoesNotExist:
			return render_to_response('404.html')
def modifypwd(request,key):
    try:
	    aemail=request.session['email']
	    pwd=User.objects.get(email=aemail).password
	    if key==md5_encode(aemail):
		    return render_to_response('modifypassword.html')
    except User.DoesNotExist:
	    return render_to_response('404.html')
	   
def newpwd(request):
	if request.method=='POST':
	    try:
	        myemail=request.session['email']
	        user=User.objects.get(email=myemail)
	        user.password=md5_encode(request.POST['password'])
	        user.save()
	        return  HttpResponseRedirect('/login/')
	    except User.DoesNotExist:
		    return render_to_response('404.html')
	return render_to_response('404.html')
		
def islogin(request):
	return request.session.get('islogin',False)

def user_id(request):
	return request.session['id']
def user_email(request):
	return request.session.get('email','')
def addtext(request):
	if islogin(request):
	    if request.method=='POST':
	    	title=request.POST.get('texttitle','')
	    	contents=request.POST.get('textcontents','')
	    	tags=request.POST.get('texttags','')
	    	texturl=request.POST.get('texturl','')
	    	a_user=User.objects.get(email=request.session.get('email'))
	    	twitter=Text(
							user=a_user,
							content=contents,
							tags=tags,
							text_url=texturl,
							title=title,
							cont_type=1,

							)
	    	twitter.save()
	    	if twitter.user.smallface:
	    		smallface="background-image:url("+twitter.user.smallface.url+")"
	    	else:
	    		smallface="background-image:url(/images/smallface.png)"
	    	t = loader.get_template('selftemplate.html')
	    	id=str(twitter.id)
	    	container_id='note_container_'+id
	    	review_box_id='review_box_'+id


	    	items= [{
		        		'twitter_id':id,
		        		'showreview_id':'showreview_'+id,
		        		'notes_id': 'notes_'+id,
		        		'note_container_id':container_id,
		        		'usrname': twitter.user.username,
		        		'review_count': Review.objects.filter(owner=twitter).count(),
		        		'like_id':'like_id_'+id,
						'content':twitter.content,
						'url':smallface,
						'tags':twitter.tags.split('#'),
						'title':title,
						'myid':'tt',	
						'id':twitter.user.id,
		          },]
	    	c=Context({'items':items})
	    	result={'html':t.render(c)}
	    	result=simplejson.dumps(result)
	    	return HttpResponse(result, mimetype='application/json')
	    else:
			return render_to_response('404.html')
pictureurl=''		
def addpicture(request):
	if islogin(request):
	    if request.method=='POST':
	    	title=request.POST.get('picturetitle','')
	    	contents=request.POST.get('picturecontents','')
	    	tags=request.POST.get('picturetags','')
	    	url=request.POST.get('pictureurl','')
	    	url=website(url)
	    	
	    	a_user=User.objects.get(email=request.session.get('email'))
	    	a_file=request.FILES.get('picturefile')

	    	global pictureurl

	    	

	    	
	    	twitter=Picture(
						title=title,
						   user=a_user,
						   content=contents,
						   tags=tags,
						   picture_url=url,
							file=pictureurl,
							cont_type=4,

							)
	    	twitter.save()
	    	if twitter.file:
	    		pic_url=dowithurl(twitter.file.url)
	    	else:
	    		pic_url=''
	    	t = loader.get_template('selftemplate.html')
	    	id=str(twitter.id)
	    	container_id='note_container_'+id
	    	review_box_id='review_box_'+id
	    	pictureurl=''
	    	if twitter.user.smallface:
	    		url="background-image:url("+twitter.user.smallface.url+")"
	    	else:
	    		url="background-image:url(/images/smallface.png)"



	    	items= [{
		        		'twitter_id':id,
		        		'showreview_id':'showreview_'+id,
		        		'notes_id': 'notes_'+id,
		        		'note_container_id':container_id,
		        		'usrname': twitter.user.username,
		        		'review_count': Review.objects.filter(owner=twitter).count(),
		        		'like_id':'like_id_'+id,
						'content':twitter.content,
						'url':url,
						'pictureurl':pic_url,
						'tags':twitter.tags.split('#'),
						'title':title,
						'outurl':twitter.picture_url,
						'myid':'tt',	
						'id':twitter.user.id,
		          },]

	    	c=Context({'items':items})
	    	result={'html':t.render(c)}
	    	

	    	result=simplejson.dumps(result)	
	    	return HttpResponse(result, mimetype='application/json')
	    else:

			return render_to_response('404.html')
def addvideo(request):
	if islogin(request):
	    if request.method=='POST':
	    	title=request.POST.get('videotitle','')
	    	contents=request.POST.get('videocontents','')
	    	tags=request.POST.get('videotags','')
	    	url=request.POST.get('videourl','')
	    	url=website(url)
	    	flashurl=getflashurl(url='http://'+url)
	    	
	    	a_user=User.objects.get(email=request.session.get('email'))
	    	
	    		    	
	    	twitter=Video(
						title=title,
						   user=a_user,
						   content=contents,
						   tags=tags,
						   video_url=url,
						   cont_type=3,


							)
	    	twitter.save()
	    	if twitter.file:
	    		pic_url=dowithurl(twitter.file.url)
	    	else:
	    		pic_url=''
	    	t = loader.get_template('selftemplate.html')
	    	id=str(twitter.id)
	    	container_id='note_container_'+id
	    	review_box_id='review_box_'+id
	    	pictureurl=''
	    	if twitter.user.smallface:
	    		url="background-image:url("+twitter.user.smallface.url+")"
	    	else:
	    		url="background-image:url(/images/smallface.png)"



	    	items= [{
		        		'twitter_id':id,
		        		'showreview_id':'showreview_'+id,
		        		'notes_id': 'notes_'+id,
		        		'note_container_id':container_id,
		        		'usrname': twitter.user.username,
		        		'review_count': Review.objects.filter(owner=twitter).count(),
		        		'like_id':'like_id_'+id,
						'content':twitter.content,
						'url':url,
#						'pictureurl':twitter.video_url,
						'tags':twitter.tags.split('#'),
						'myid':'tt',
						'title':title,
						'flashurl':flashurl,
						'outurl':twitter.video_url,	
						'id':twitter.user.id,
		          },]
	    	

	    	c=Context({'items':items})
	    	result={'html':t.render(c)}
	    	result=simplejson.dumps(result)	
	    	return HttpResponse(result, mimetype='application/json')
	    else:

			return render_to_response('404.html')
def addmusic(request):
	if islogin(request):
	    if request.method=='POST':
	    	title=request.POST.get('musictitle','')
	    	contents=request.POST.get('musiccontents','')
	    	tags=request.POST.get('musictags','')
	    	url=request.POST.get('musicurl','')
	    	url=website(url)
	    	a_user=User.objects.get(email=request.session.get('email'))
	    	
	    		    	
	    	twitter=Music(
							title=title,
						   user=a_user,
						   content=contents,
						   tags=tags,
						   music_url=url,
						   cont_type=2,


							)
	    	twitter.save()
	    	if twitter.file:
	    		pic_url=dowithurl(twitter.file.url)
	    	else:
	    		pic_url=''
	    	t = loader.get_template('selftemplate.html')
	    	id=str(twitter.id)
	    	container_id='note_container_'+id
	    	review_box_id='review_box_'+id
	    	pictureurl=''
	    	if twitter.user.smallface:
	    		url="background-image:url("+twitter.user.smallface.url+")"
	    	else:
	    		url="background-image:url(/images/smallface.png)"



	    	items= [{
		        		'twitter_id':id,
		        		'showreview_id':'showreview_'+id,
		        		'notes_id': 'notes_'+id,
		        		'note_container_id':container_id,
		        		'usrname': twitter.user.username,
		        		'review_count': Review.objects.filter(owner=twitter).count(),
		        		'like_id':'like_id_'+id,
						'content':twitter.content,
						'url':url,
#						'pictureurl':twitter.video_url,
						'tags':twitter.tags.split('#'),
						'myid':'tt',
						'title':title,
						'outurl':twitter.music_url,	
						'id':twitter.user.id,
		          },]
	    	

	    	c=Context({'items':items})
	    	result={'html':t.render(c)}
	    	result=simplejson.dumps(result)	
	    	return HttpResponse(result, mimetype='application/json')
	    else:

			return render_to_response('404.html')
def uppicture(request):
	id=int(request.POST['id'])
	user=User.objects.get(id=id)
	file_path = '%s/picture/' % (MEDIA_ROOT)
	filename=time.strftime('%m%d%H%M%S%Y')
	print filename
	data=request.FILES['Filedata']

	url=thumbnail(data,file_path,maxwidth=470,maxheight=1000)
	global pictureurl
	pictureurl=url
	result=simplejson.dumps({})
	return HttpResponse(result, mimetype='application/json')

def profile(request,userid):
	if islogin(request):
	    if request.method=='GET':
			
		    if str(request.session['id'])==str(userid):
		    			    	
				request.session['userid']=userid
				t = loader.get_template('myedit.html')
		    else:
	    		request.session['userid']=userid
	    		t = loader.get_template('myedit.html')		    	
		    user=User.objects.get(id=userid)
		    follow=FriendShip.objects.filter(follower=user).count()
		    followed=FriendShip.objects.filter(user=user).count()
		    c=Context({'user':user,'followers':follow,'followered':followed})
		    return HttpResponse(t.render(c))
	    else:
	    	return render_to_response('404.html')		
	else:			
		return  HttpResponseRedirect('/login/')					
def addpost(request):
	if islogin(request):
		if request.method=='POST':
			userid=request.session['userid']
			if str(request.session['id'])==str(userid):
				t = loader.get_template('editertemplate.html')
			else:
				t = loader.get_template('selftemplate.html')
			
			items=list()

		
			users=Twitter.objects.filter(user=userid)
			for user in users:
				flashurl=''				
				outurl=''
				pic_url=''
				if user.cont_type==1:
					outurl=''
				if user.cont_type==2:
					outurl=Music.objects.get(twitter_ptr=user.id).music_url
				if user.cont_type==3:
					outurl=Video.objects.get(twitter_ptr=user.id).video_url
					flashurl=getflashurl(url=('http://'+outurl))
				if user.cont_type==4:
					picture=Picture.objects.get(twitter_ptr=user.id)
					outurl=picture.picture_url
					
					if user.file:
						pic_url=dowithurl(user.file.url)

					else:
						pic_url=''
				
									
				
				id=str(user.id)
				
				if user.user.smallface:
					smallface="background-image:url("+user.user.smallface.url+")"
				else:
					smallface="background-image:url(/images/smallface.png)"
				
				container_id='note_container_'+id
				review_box_id='review_box_'+id
				
				c={'review_box_id':review_box_id,
					'twitter_id':id,
		       		'notes_id': 'notes_'+id,
		        	'note_container_id':container_id,
		        	'usrname': user.user.username,
		        	'review_count': Review.objects.filter(owner=user).count(),
		        	'like_id':'like_id_'+id,
		        	'showreview_id':'showreview_'+id,
		        	'content':user.content,
					'url':smallface,
					'tags':user.tags.split('#'),
					'outurl':outurl,
					'pictureurl':pic_url,
					'flashurl':flashurl,
					'myid':'tt',	
					'id':user.user.id,
					'title':user.title,
				}
				
				items.append(c)
			
			c=Context({'items':items})
			
			result={'html':t.render(c)}
			result=simplejson.dumps(result)
			return HttpResponse(result, mimetype='application/json')
		else:
			return render_to_response('404.html')
	else:
		return  HttpResponseRedirect('/login/')	

def settings(request,user=None):
	if islogin(request):
		t = loader.get_template('settings.html')
		user=User.objects.get(id=user_id(request))
		print user.id
		c=Context({'user':user})
		return HttpResponse(t.render(c))
	else:
		return  HttpResponseRedirect('/login/')


def upload_face(data):    
	if data.size > 0:

		base_im = Image.open(data)		


		size24 = (64,64)

		size120 = (120,120)

		size_array = (size120,size24)

		# generate file name and the file path
		file_name = time.strftime('%H%M%S') + '.png'
		file_root_path = '%s/face/' % (MEDIA_ROOT)
		file_sub_path = '%s' % (str(time.strftime("%Y/%m/%d/")))
		face=list()

		# make different sizes photos
		for size in size_array:
			file_middle_path = '%d/' % size[0]

			file_path = os.path.abspath(file_root_path + file_middle_path + file_sub_path)

			im = base_im
			im = make_thumbnail(im,size[0])

			# check path exist
			if not os.path.exists(file_path):
				os.makedirs(file_path)

			im.save('%s/%s' % (file_path,file_name),'PNG')
			url='/face/'+ file_middle_path+file_sub_path+file_name
			face.append(url)

		
	return face

def make_thumbnail(im, size):            
    width, height = im.size
    if width == height:
        region = im
    else:
        if width > height:
            delta = (width - height)/2
            box = (delta, 0, delta+height, height)
        else:
            delta = (height - width)/2
            box = (0, delta, width, delta+width)            
        region = im.crop(box)

    thumb = region.resize((size,size), Image.ANTIALIAS)
    return thumb


		
			
def modifydata(request):
	if request.method=='POST':
		if islogin(request):
			data=request.FILES.get('file',None)
			username=request.POST['username']
			school= request.POST['school']
			password=request.POST['password']
			password=md5_encode(password)
			

				
			try:
				user=User.objects.get(id=user_id(request))
				if data:
					url=upload_face(data)
					smallface=url[1]
					bigface=url[0]
				else:
					smallface=user.smallface
					bigface=user.bigface
				
				user.username=username
				user.address=school
				user.bigface=bigface
				user.smallface=smallface
				user.save()
						
				return settings(request,user)
			except User.DoesNotExist:
				return render_to_response('404.html')
		else:
			return  HttpResponseRedirect('/login/')
	else:
		
		return render_to_response('settings.html')
def verifypwd(request):
	if request.method=='POST':
		try:
			password=request.POST['password']
			user=User.objects.get(id=user_id(request))
			if user.password==md5_encode(password):
				data='true'
			else:
				data='false'
		except User.DoesNotExist:
			return render_to_response('404.html')
	json=simplejson.dumps(data)
	return HttpResponse(json,mimetype='application/json')

def friended(request,followedid):
	request.session['followedid']=int(followedid)
	if islogin(request):
		return render_to_response('followed.html')
	else:
		return  HttpResponseRedirect('/login/')
def addfollow(request):
	if islogin(request):
		if request.method=='POST':
			addattention=int(request.POST['addfriendid'])
			user=FriendShip.objects.get(id=addattention).user
			follower=User.objects.get(id=user_id(request))
			friend=FriendShip(user=user,follower=follower)
			message=u'您以成功关注：'+user.username
			result={'html':message}
			result=simplejson.dumps(result)
			return HttpResponse(result, mimetype='application/json')
		else:
			return render_to_response('404.html')
	else:
		return  HttpResponseRedirect('/login/')	
def followed(request):
	if islogin(request):
		if request.method=='POST':
			followedid=request.session['followedid']
			if request.session['id']==followedid:
				t = loader.get_template('myfollowed.html')
			else:
				t = loader.get_template('otherfollowed.html')
			
			items=list()
			friends=FriendShip.objects.filter(user=followedid)
			for friend in friends:
				userid=str(friend.follower.id)
				followedid=friend.id
				if friend.user.bigface:
					bigface="background-image:url("+friend.follower.bigface.url+")"
				else:
					bigface="background-image:url(/images/bigface.png)"

				c={

					'url':bigface,
					'username':friend.follower.username,
					'userid':userid,

					'followedid':followedid,
				}
				items.append(c)
			c=Context({'items':items})
			result={'html':t.render(c)}
			result=simplejson.dumps(result)
			return HttpResponse(result, mimetype='application/json')
		else:
			return render_to_response('404.html')
	else:
		return  HttpResponseRedirect('/login/')	

def deletefollowed(request):
	if islogin(request):
		if request.method=='POST':
			followedid=int(request.POST['followedid'])
			followed=FriendShip.objects.get(id=followedid).delete()
			result={}
			result=simplejson.dumps(result)
			return HttpResponse(result, mimetype='application/json')
		else:
			return render_to_response('404.html')
	else:
		return  HttpResponseRedirect('/login/')

def cancel(request):
	if islogin(request):
		request.session['islogin']=False
		return login(request)
	else:
		return render_to_response('404.html')

def goods(request):
	if islogin(request):
		return render_to_response('goods.html')
	else:
		return  HttpResponseRedirect('/login/')

def inbox(request):
	if islogin(request):
		t = loader.get_template('inbox.html')
		try:
			reviewcount=Review.objects.filter(me=user_id(request),newreview=1).count()
		except:
			reviewcount=0
		try:
			goodscount=RelationGoods.objects.filter(user=user_id(request),new=1).count()
		except:
			goodscount=0
		try:
			replycount=Reply.objects.filter(user=user_id(request),new=1).count()
		except:
			replycount=0
		c=Context({'reviewcount':reviewcount,'goodscount':goodscount,'replycount':replycount})
		return HttpResponse(t.render(c))
	else:
		return  HttpResponseRedirect('/login/')

def friends(request,followid):
	request.session['followid']=int(followid)
	if islogin(request):
		return render_to_response('friends.html')
	else:
		return  HttpResponseRedirect('/login/')

def follow(request):
	if islogin(request):
		if request.method=='POST': 
			followid=request.session['followid']
			if request.session['id']==followid:
				t = loader.get_template('myfollow.html')
			else:
				t = loader.get_template('otherfollow.html')
			
			items=list()
			friends=FriendShip.objects.filter(follower=followid)
			for friend in friends:
				userid=str(friend.user.id)
				followid=friend.id
				if friend.user.bigface:
					bigface="background-image:url("+friend.user.bigface.url+")"
				else:
					bigface="background-image:url(/images/bigface.png)"

				c={

					'url':bigface,
					'username':friend.user.username,
					'userid':userid,

					'followid':followid,
				}
				items.append(c)
			c=Context({'items':items})
			result={'html':t.render(c)}
			result=simplejson.dumps(result)
			return HttpResponse(result, mimetype='application/json')
		else:
			return render_to_response('404.html')
	else:
		return  HttpResponseRedirect('/login/')	

def deletefollow(request):
	if islogin(request):
		if request.method=='POST':
			followid=int(request.POST['followid'])
			follow=FriendShip.objects.get(id=followid).delete()
			result={}
			result=simplejson.dumps(result)
			return HttpResponse(result, mimetype='application/json')
		else:
			return render_to_response('404.html')
	else:
		return  HttpResponseRedirect('/login/')

def like(request):
	if islogin(request):
		if request.method=='POST':
			id=str(request.POST['twitterid'])
			twitter=Twitter.objects.get(id=id)
			twitter.good += 1
			twitter.save()
			result={}
			result=simplejson.dumps(result)
			return HttpResponse(result, mimetype='application/json')
		else:
			return render_to_response('404.html')
	else:
		return  HttpResponseRedirect('/login/')

def deletetwitter(request):
	if islogin(request):
		if request.method=='POST':
			id=int(request.POST['twitter_id'])
			twitter=Twitter.objects.get(id=id).delete()
			
			result={}
			result=simplejson.dumps(result)
			return HttpResponse(result, mimetype='application/json')
		else:
			return render_to_response('404.html')
	else:
		return  HttpResponseRedirect('/login/')
def searchtwitter(request):
	if islogin(request):
		if request.method=='POST':
			t = loader.get_template('selftemplate.html')
			tag=request.POST['searchtwitter']

	
			twitters=Twitter.objects.filter(tags__contains=tag)
			
			items=[]
			for user in twitters:
				flashurl=''
				outurl=''
				pic_url=''
				if user.cont_type==1:
					outurl=''
				if user.cont_type==2:
					outurl=Music.objects.get(twitter_ptr=user.id).music_url
					
				if user.cont_type==3:
					outurl=Video.objects.get(twitter_ptr=user.id).video_url
					flashurl=getflashurl(url=('http://'+outurl))
				if user.cont_type==4:
					picture=Picture.objects.get(twitter_ptr=user.id)
					outurl=picture.picture_url
					if picture.file:
						pic_url=dowithurl(picture.file.url)
					else:
						pic_url=''
				id=str(user.id)
				container_id='note_container_'+id
				review_box_id='review_box_'+id
				
				if user.file:
					pic_url=dowithurl(user.file.url)

				else:
					pic_url=''

				c={'review_box_id':review_box_id,
					'twitter_id':id,
		        	'showreview_id':'showreview_'+id,
		       		'notes_id': 'notes_'+id,
		        	'note_container_id':container_id,
		        	'usrname': user.user.username,
		        	'review_count': Review.objects.filter(owner=user).count(),
		        	'like_id':'like_id_'+id,
					'content':user.content,
					'url':"background-image:url("+user.user.smallface.url+")",
					'pictureurl':pic_url,
					'tags':user.tags.split('#'),
					'outurl':outurl,
					'flashurl':flashurl,
					'myid':user_id(request),	
					'id':user.user.id,
					}
				items.append(c)
			c=Context({'items':items})
			result={'html':t.render(c)}
			result=simplejson.dumps(result)
			return HttpResponse(result, mimetype='application/json')
		else:
			return render_to_response('404.html')
	else:
		return  HttpResponseRedirect('/login/')
def addattention(request):
	if islogin(request):
		if request.method=='POST':
			addattention=int(request.POST['addfriendid'])
			user=FriendShip.objects.get(id=addattention).user
			follower=User.objects.get(id=user_id(request))
			friend=FriendShip(user=user,follower=follower)
			message=u'您以成功关注：'+user.username
			result={'html':message}
			result=simplejson.dumps(result)
			return HttpResponse(result, mimetype='application/json')
		else:
			return render_to_response('404.html')
	else:
		return  HttpResponseRedirect('/login/')	
def text(request):
	file_ext = str(request.FILES['Filedata'].name).split('.')[-1]	
	a_user=User.objects.all()[0]	
	file_upload = open( ('sss'+'.'+file_ext), 'w')
	file_upload.write(request.FILES['Filedata'].read())
	file_upload.close()	
	picture=Picture.objects.all()
	
	
	
	
	file_upload.write(request.FILES['Filedata'].read())
	file_upload.close()	
	request.session['pictureurl']=url
	return HttpResponse(picture.picture_url)
def xppicture(request):
	id=str(request.POST['id'])	
	user=User.objects.get(id=id)	
	file_type = str(request.FILES['Filedata'].name).split('.')[-1].lower()
	file_path = '%s/picture/' % (MEDIA_ROOT)

	filename=time.strftime('%m%d%H%M%S%Y')
	if not os.path.exists(file_path):
		os.makedirs(file_path)
	filename=filename+'.'+'jpg'
	
	img=open('%s/%s' % (file_path,filename),'w')
	img.write(request.FILES['Filedata'].read())
	img.close()
#	file_path = os.path.abspath(file_path)
#	url=file_path+filename	
#	thumbnail(url,270,1000)	
	
	global fileurl
	fileurl=file_path+filename


	result=simplejson.dumps({})
	return HttpResponse(result, mimetype='application/json')

			
def dowithurl(url):
	url=str(url)

	if url:
		url=url
		url= url.split('/')
		return '/'+url[-2]+'/'+url[-1]
	return ''
def deletegood(request):
	if islogin(request):
		if request.method=='POST':
			id=int(request.POST['goodid'])
			
			good=Goods.objects.get(id=id)
			name=good.title
			good.delete()
			message=u'您以成功删除：'+name
			result={'html':message}
			result=simplejson.dumps(result)
			return HttpResponse(result, mimetype='application/json')
		else:
			return render_to_response('404.html')
	else:
		return  HttpResponseRedirect('/login/')		

def getgoods(request):
	if islogin(request):
		if request.method=='POST': 			
			try:
				t = loader.get_template('mygood.html')
				user=User.objects.get(id=user_id(request))
			
				items=list()
				goods=Goods.objects.filter(user=user)
				for good in goods:
					good_id=good.id
					if good.goods_url:
						url=dowithurl(good.goods_url)
					else:
						url=""
					c={

						'url':url,
						'title':good.title,
						'good_id':good_id,
						'tags':good.tags.split('#'),

						'description':good.description,
					}
					items.append(c)
				c=Context({'items':items})

				result={'html':t.render(c) ,'flag':'true'}				
				result=simplejson.dumps(result)
				return HttpResponse(result, mimetype='application/json')
			except:
				result={'html':'', 'flag':'false'}
				result=simplejson.dumps(result)
				return HttpResponse(result, mimetype='application/json')
				
		
		else:
			return render_to_response('404.html')
	else:
		return  HttpResponseRedirect('/login/')	

def upgoods(request):
	if islogin(request):
		if request.method=='POST':
			title=request.POST.get('goodstitle','')
			contents=request.POST.get('goodscontents','')
			tags=request.POST.get('goodstags','')
			data=request.FILES['file']
			path = '%s/goods/' % (MEDIA_ROOT)
			url=thumbnail(data,path,maxwidth=300,maxheight=400)
			user=User.objects.get(id=user_id(request))
			good=Goods(
					user=user,
					title=title,
					tags=tags,
					goods_url=url,
					description=contents,
					)

			good.save()
			return HttpResponseRedirect('/goods/')

		else:
			return render_to_response('404.html')
	else:
		return  HttpResponseRedirect('/login/')
	
def addfriend(request):
	if islogin(request):
		if request.method=='POST':
			addattention=int(request.POST['addfriendid'])
			user=User.objects.get(id=addattention)
			follower=User.objects.get(id=user_id(request))
			friend=FriendShip(user=user,follower=follower)
			follower=User.objects.get(id=user_id(request))
			friend=FriendShip(user=user,follower=follower)
			friend.save()
			message=u'您以成功关注：'+user.username
			result={'html':message}
			result=simplejson.dumps(result)
			return HttpResponse(result, mimetype='application/json')
		else:
			return render_to_response('404.html')
	else:
		return  HttpResponseRedirect('/login/')	
	
def searchgoods(request):
	if islogin(request):
		if request.method=='POST':
			t = loader.get_template('othergood.html')
			tag=request.POST['tag']
	
			goods=Goods.objects.filter(tags__contains=tag)
			items=[]
			for good in goods:
				good_id=good.id
				if good.goods_url:
					url=dowithurl(good.goods_url)
				else:
					url=""
				c={

					'url':url,
					'title':good.title,
					'good_id':good_id,
					'tags':good.tags.split('#'),
					'description':good.description,
					}
				items.append(c)
			c=Context({'items':items})
			result={'html':t.render(c)}
			result=simplejson.dumps(result)
			return HttpResponse(result, mimetype='application/json')
		else:
			return render_to_response('404.html')
	else:
		return  HttpResponseRedirect('/login/')	
def attentiongood(request):
	if islogin(request):
		if request.method=='POST':
			goodid=request.POST['goodid']
			user=User.objects.get(id=user_id(request))
			good=Goods.objects.get(id=goodid)
			relationgood=RelationGoods(user=user,good=good,new=1,other=user)
			relationgood.save()
			message=u'您已成功关注：'+good.title
			result={'message':message}
			result=simplejson.dumps(result)
			return HttpResponse(result, mimetype='application/json')
		else:
			return render_to_response('404.html')
	else:	
		return  HttpResponseRedirect('/login/')
def getreview(request):
	if islogin(request):
		
#		try:
			t = loader.get_template('inboxreview.html')
			reviews=Review.objects.filter(me=user_id(request),newreview=1)
			items=[]
			for review in reviews:
				username=review.reviewer.username
				
				reviewid=str(review.id)
				url="background-image:url("+review.reviewer.smallface.url+")"
				review_box_id='review_box_' + reviewid
				userid=str(review.reviewer.id)
				content=review.content
				title=review.owner.title
				if title:
					title=''
				
				c={
				'flag':True,
					'username':username,
					'reviewid':reviewid,
					'review_box_id':review_box_id,
					'userid':userid,
					'url':url,
					'content':content,
					'title':title,
				}
				items.append(c)
			c=Context({'items':items})
			result={'html':t.render(c)}
			result=simplejson.dumps(result)
			return HttpResponse(result, mimetype='application/json')

				
			
#		except:
#			return HttpResponseRedirect('/inbox/')
			


	else:	
		return  HttpResponseRedirect('/login/')
	
def getmessage(request):
	if islogin(request):
		
#		try:
			t = loader.get_template('inboxreview.html')
			reviews=RelationGoods.objects.filter(other=user_id(request),new=1)
			items=[]
			for review in reviews:
				username=review.user.username
				
				reviewid=str(review.id)
				url="background-image:url("+review.user.smallface.url+")"
				review_box_id='review_box_' + reviewid
				userid=str(review.user.id)
				email=review.user.email
				title=review.good.title
				if title:
					title=''
				
				c={
					'flag':False,
					'username':username,
					'reviewid':reviewid,
					'review_box_id':review_box_id,
					'userid':userid,
					'url':url,
					'email':email,

					'title':title,
				}
				items.append(c)
			c=Context({'items':items})
			result={'html':t.render(c)}
			result=simplejson.dumps(result)
			return HttpResponse(result, mimetype='application/json')

				
			
#		except:
#			return HttpResponseRedirect('/inbox/')
			


	else:	
		return  HttpResponseRedirect('/login/')

def website(url):
	
	url=url.lower().split('www')[-1]
	return 'www'+url


	
	url=url.lower().split('www')[-1]
	return 'www'+url

def thumbnail(data,path,maxwidth=470,maxheight=1000):
	
	file_path=path
	path = os.path.abspath(path)
	if not os.path.exists(path):
		os.makedirs(path)	

	
	img= Image.open(data)

	width,height = img.size	
	
	ratio = 0

	if width > maxwidth:		
		ratio = float(maxwidth) / width
	
		width=maxwidth
		height = int(height * ratio)


	if height > maxheight:
		ratio = float(maxheight) / height
		height=maxheight
		width = int(width * ratio)

	im=img.resize(	(width,height), Image.ANTIALIAS)
	name=time.strftime('%m%d%H%M%S%Y')
	url=path+'/'+name+'.jpg'


	im.save(url)
	return file_path +name+'.jpg'
import HTMLParser
import urllib
import sys
import re
class MyParaser(HTMLParser.HTMLParser):

  
    def __init__(self,url):
        HTMLParser.HTMLParser.__init__(self)
        self.url=url
        self.result=''
    def matchswf(self,value):
        patterns=['swf','height']
        flag=False
        if re.search('swf'.decode('utf8'),value,re.M|re.S):
			if re.search('embed'.decode('utf8'),value,re.M|re.S):
				flag=False
			else:
				flag=True


        return flag
            
    def start_do_url(self):

        self.feed(urllib.urlopen(self.url).read().decode("UTF-8"))
 
        self.close()         
    def handle_starttag(self,tag,attrs):
        if 'input'==tag:
            for name,value in attrs:
            	if value:
            		
					
            		if self.matchswf(value.split('.')[-1]):
						self.result=value
						return
            			 
import threading
class ThreadUrl(threading.Thread):
    def __init__(self,a_paraser):
        self.a_paraser=a_paraser
        self.result=''
        threading.Thread.__init__(self)
        

    def run(self):
        self.a_paraser.start_do_url()
        self.result=self.a_paraser.result

def getflashurl(url):
	threadurl=ThreadUrl(MyParaser(url=url))
	threadurl.start()
	threadurl.join()
	return threadurl.result
	
	videourl=MyParaser(url)
	videourl.start_do_url()
	return videourl.result

		


