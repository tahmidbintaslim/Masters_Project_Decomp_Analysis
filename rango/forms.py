from django.contrib.auth.forms import AuthenticationForm 
from django import forms
#from .models import User,Details

# If you don't do this you cannot use Bootstrap CSS
class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=30, 
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username'}))
    password = forms.CharField(label="Password", max_length=30, 
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'password'}))
    
    
class ExpForm(forms.Form):
      exp_name = forms.CharField(label='experiment', max_length=30,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'exp'}))
        
        
        
#class RegistrationForm(forms.Form):
 #   username = forms.CharField(label='Username', max_length=30)
 #   email = forms.EmailField(label='Email')
  #  password = forms.CharField(label='Password',
   #                       widget=forms.PasswordInput())

