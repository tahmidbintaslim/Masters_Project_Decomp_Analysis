from django.conf.urls import url
from . import views

urlpatterns =[
      url(r'^$', views.home, name='home'),
      url(r'^register/$', views.register_page), 
      url(r'^index/$', views.IndexView.as_view(), name='index'),
      url(r'^add/', views.add, name='add'),
      url(r'^plotv/$', views.PlotView.as_view(), name='plotv'),
      url(r'^ploth/$', views.ClusterView.as_view(), name='ploth'),
]
