import os
import sys
import django.core.handlers.wsgi

os.environ['DJANGO_SETTINGS_MODULE'] = 'twitter.settings'
os.environ['PYTHON_EGG_CACHE'] = '/tmp/.python-eggs'
app_apth = "/home/yu"
sys.path.append(app_apth)
application = django.core.handlers.wsgi.WSGIHandler()
'''
import os, sys 
from os.path import abspath, dirname, join 
     
from django.core.handlers.wsgi import WSGIHandler 
sys.path.insert(0, abspath(join(dirname(__file__), "./"))) 
sys.path.insert(0, abspath(join(dirname(__file__), "../"))) 
     
sys.stdout = sys.stderr 
     
os.environ["DJANGO_SETTINGS_MODULE"] = "twitter.settings" 
os.environ["PYTHON_EGG_CACHE"] = "/tmp" 
os.environ["LANG"] = "zh_CN.utf8" 
application = WSGIHandler()'''
