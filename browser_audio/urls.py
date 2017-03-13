from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.audio, name='audio'),
    url(r'^create_file/$', views.create_file, name='create_file'),
    url(r'^delete_file/$', views.delete_file, name='delete_file'),
    url(r'^rename_audio/$', views.rename_audio, name='rename_audio'),
]