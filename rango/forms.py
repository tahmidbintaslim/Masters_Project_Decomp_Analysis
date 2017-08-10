from django.contrib.auth.forms import AuthenticationForm 
from django import forms
from simple_search import search_form_factory
from .models import Experiment,FileDetail,MotifList,AlphaTable

# If you don't do this you cannot use Bootstrap CSS
'''
class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=30, 
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username'}))
    password = forms.CharField(label="Password", max_length=30, 
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'password'}))
'''    

class categoryform(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style': 'width:300px'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 80}))   

class decompform(forms.Form):
    exp_name = forms.CharField(label='experiment', max_length=100,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'exp'})) 
    resultids = forms.CharField(label='experiment', max_length=100,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'exp'}))   
    
#class ExpForm(forms.Form):
#      exp_name = forms.CharField(label='experiment', max_length=30,
#                                widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'exp'}))
        
#SearchForm = search_form_factory(Experiment.objects.all(),
#                                 ['^experimentName'])   
#SearchForm = search_form_factory(Experiment.objects.get(),
#                                 ['^experimentName'])   
#class SearchForm(forms.Form):
 #   exp_name = forms.CharField(label='experiment', max_length=100)
        
#class RegistrationForm(forms.Form):
 #   username = forms.CharField(label='Username', max_length=30)
 #   email = forms.EmailField(label='Email')
  #  password = forms.CharField(label='Password',
   #                       widget=forms.PasswordInput())

