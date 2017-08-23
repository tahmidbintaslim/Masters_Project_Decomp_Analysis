from django.conf.urls import url
from . import views

urlpatterns =[
      url(r'^register/$', views.register_page), 
      url(r'^search/$', views.search, name='search'),  
      url(r'^guide/$', views.guide, name='guide'),  
      url(r'^categorySel/(?P<expname>[\w\-]+)/$', views.categorySel, name='categorySel'),
      #url(r'^index/(?P<expname>[\w\-]+)/$', views.IndexView,name='index'),
      url(r'^index/(?P<expname>[\w\-]+)/$', views.IndexView,name='index'),
      url(r'^$', views.home, name='home'),
      url(r'^plotv/(?P<expname>[\w\-]+)/$', views.PcaView, name='plotv'),
      url(r'^ploth/(?P<expname>[\w\-]+)$', views.DendroView, name='ploth'),
      url(r'^plotm/(?P<expname>[\w\-]+)/$', views.ScoreView, name='plotm'), 
      url(r'^plotheat/(?P<expname>[\w\-]+)/$', views.HeatView, name='plotheat'),
      url(r'^loadData/$', views.loadData, name='loadData'),  
]
