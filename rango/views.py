from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse,HttpResponseRedirect
from django.views import generic
from django.shortcuts import render
from braces import views
from . import forms
from . import plots
from django.contrib.auth import authenticate, login, logout
#from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.template import RequestContext 
from django.shortcuts import render_to_response
#from rango.models import User,Details

@login_required(login_url="login/")
def home(request):
    return render(request,"home.html")

#class home(TemplateView):
     #HttpResponseRedirect('index.html')
    #template_name = "home.html"

def add(request):
    #form = forms.DataForm()
    #print request
    #return render(request, 'add.html', {'form': form})
        
    if request.method == "POST":
        form = forms.DataForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            #print request.user
            data.user = request.user
            data.exp = request.POST['exp']
            data.res_id = request.POST['res_id']
            data.category = request.POST['category']
            data.save()
            #return redirect('home')
    else:
        form = forms.DataForm()
    return render(request, 'add.html', {'form': form})    

class IndexView(TemplateView):
    template_name = "index.html"

class PlotView(TemplateView):
    template_name = "plot.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(PlotView, self).get_context_data(**kwargs)
        context['plot'] = plots.plotv()
        return context
    
class ClusterView(TemplateView):
    template_name = "plot.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ClusterView, self).get_context_data(**kwargs)
        context['plot'] = plots.ploth()
        return context 
    
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
