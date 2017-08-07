from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse,HttpResponseRedirect
from django.views import generic
from django.shortcuts import render
from braces import views
from . import forms
from . import plots
from rango.forms import categoryform
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
#from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.template import RequestContext 
from django.shortcuts import render_to_response
from rango.models import Experiment,FileDetail,MotifList,AlphaTable
from simple_search import search_form_factory
#from .forms import SearchForm
#from rango.models import User,Details

@login_required(login_url="login/")
def home(request):
    return render(request,"home.html") 

def search(request):
    result_list = Experiment.objects.all()
    return render(request, 'search.html', {'result_list': result_list})

def categorySel(request,expname):
    #print expname
    context_dict = {}
    exp = Experiment.objects.get(experimentName = expname)
    result_list = FileDetail.objects.filter(experimentName = exp)
    if request.method == 'POST':
        categoryf = categoryform(request.POST)
        group1 = request.POST.getlist('group1')
        group2 = request.POST.getlist('group2')
        for g1,g2 in zip(group1,group2):
            for result_list in result_list: 
                if g1 == result_list.fileName:
                    result_list.category ='0'
                    result_list.save()  
                else:
                    result_list.category ='1'
                    result_list.save() 
    else:
        context_dict['result_list'] = result_list  
      
    return render(request, 'categorySel.html',context_dict)

def IndexView(request,expname):
    print expname
    return render(request, 'index.html', {'expname': expname})

def PlotView(request,expname):
    
        exp = Experiment.objects.get(experimentName = expname)
        context={
        'plot':plots.plotv(),
        }
       
        return render(request, 'plot.html', context)   
    
    
def ClusterView(request,expname):
        # Call the base implementation first to get a context
     #   context = super(VarianceView, self).get_context_data(**kwargs)
     #   context['variance'] = plots.plotm()
        exp = Experiment.objects.get(experimentName = expname)
        #motif = MotifList.objects.filter(experimentName = exp)
        context={
        'exp':exp,
        }
        return render(request, 'index2.html', context)    

def VarianceView(request,expname):
        # Call the base implementation first to get a context
     #   context = super(VarianceView, self).get_context_data(**kwargs)
     #   context['variance'] = plots.plotm()
        exp = Experiment.objects.get(experimentName = expname)
        motif = MotifList.objects.filter(experimentName = exp)
        context={
        'motif':motif,
        }
        return render(request, 'variance.html', context)

def register_page(request):
    if request.method == 'POST':
        form = forms.RegistrationForm(request.POST)
        if form.is_valid():
            user=User.objects.create_user(username=form.cleaned_data['username'],
                                          password=form.cleaned_data['password1'],
                                          email=form.cleaned_data['email'])
            #user.save()
            return HttpResponseRedirect('/')
    form = forms.RegistrationForm()
    variables = RequestContext(request, {'form': form})
    return render_to_response('register.html',variables)    
