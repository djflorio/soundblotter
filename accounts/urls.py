from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^login/$', views.login, name='login'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^register/$', views.register_user, name='register'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^delete_user/$', views.delete_user, name='delete_user'),
    url(r'^forgot_pass/$', views.forgot_pass, name='forgot_pass'),
    url(r'^user_settings/$', views.user_settings, name='user_settings'),
    url(r'^pass_settings/$', views.pass_settings, name='pass_settings'),
    url(r'^activate_user/(?P<key>.+)$', views.activate_user, name='activate_user'),
    url(r'^new_activation_link/(?P<user_id>\d+)$', views.new_activation_link, name="new_activation_link"),
    url(r'^r/(?P<user_id>\d+)/(?P<pwreset_key>.+)$', views.reset_view, name="reset_view"),
]