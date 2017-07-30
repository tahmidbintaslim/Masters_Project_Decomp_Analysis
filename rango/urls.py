from django.conf.urls import url
from . import views

urlpatterns =[
      url(r'^register/$', views.register_page), 
      url(r'^search/$', views.search, name='search'),      
      url(r'^index/(?P<expname>[\w\-]+)/$', views.IndexView, name='index'),
      url(r'^$', views.home, name='home'),
      url(r'^plotv/(?P<expname>[\w\-]+)/$', views.PlotView, name='plotv'),
      url(r'^ploth/(?P<expname>[\w\-]+)$', views.ClusterView, name='ploth'),
      url(r'^plotm/(?P<expname>[\w\-]+)/$', views.VarianceView, name='plotm'), 
      #url(r'^plotm/$', views.MotifScoreView.as_view(), name='plotm'),  
]
