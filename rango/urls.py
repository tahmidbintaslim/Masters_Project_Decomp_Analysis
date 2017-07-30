from django.conf.urls import url
from . import views

urlpatterns =[
      url(r'^register/$', views.register_page), 
      url(r'^index/$', views.IndexView.as_view(), name='index'),
      url(r'^$', views.home, name='home'),
      url(r'^plotv/$', views.PlotView.as_view(), name='plotv'),
      url(r'^ploth/$', views.ClusterView, name='ploth'),
      url(r'^plotm/$', views.VarianceView, name='plotm'), 
      #url(r'^plotm/$', views.MotifScoreView.as_view(), name='plotm'),  
]
