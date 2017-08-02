from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse,HttpResponseRedirect
from django.views import generic
from django.shortcuts import render
from braces import views
from . import forms
from . import plots
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
'''    
    print"hello"
    result_list = []
    if request.method == 'POST':
        query = request.POST['query'].strip() 
        if query:
            # Run our Bing function to get the results list!
            result_list = Experiment.objects.filter(experimentName=query)
            #print result_list
            
    
    
   query = request.GET.get('q')
        print query
        if query:
            exp = Experiment.objects.filter(experimentName=query)            
            for exp in exp:
                return render(request, 'index.html', exp.experimentName)
        else:
            print "here"
            return Experiment.objects.all()
     
    


def search(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            expn = Experiment.objects.get(experimentName = request.POST['exp'])
            print expn
            return HttpResponseRedirect('/index/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SearchForm()

    return render(request, 'search.html', {'form': form})

    
    form = SearchForm(request.GET or {})
    if form.is_valid():
        results = form.get_queryset()
    else:
        results = Experiment.objects.none()

    return {
        'form': form,
        'results': results,
    }
    '''
def IndexView(request,expname):
    print expname
    return render(request, 'index.html', {'expname': expname})

def PlotView(request,expname):
    
        exp = Experiment.objects.get(experimentName = expname)
        context={
        'plot':plots.plotv(),
        }
        #context['plot'] = plots.plotv()
        #motif = MotifList.objects.filter(experimentName = exp)
        return render(request, 'plot.html', context)   
    
class ClusterView2(TemplateView):
    template_name = "index2.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ClusterView, self).get_context_data(**kwargs)
        context['index'] = plots.ploth()
        return context
    
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
        
        #exp = Experiment.objects.get(experimentName = "exp1")
        #motif = MotifList.objects.filter(experimentName = exp)
        #return render(request, 'variance.html', {'motif': motif})
        #return context 
    
#class MotifScoreView(TemplateView):
 #   template_name = "variance.html"

 #   def get_context_data(self, **kwargs):
 #       # Call the base implementation first to get a context
 #       context = super(VarianceView, self).get_context_data(**kwargs)
 #       context['plot'] = plots.plotm()
 #       return context     
        
    
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
