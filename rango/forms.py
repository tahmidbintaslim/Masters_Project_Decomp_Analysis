from django.contrib.auth.forms import AuthenticationForm 
from django import forms
#from .models import User,Details

# If you don't do this you cannot use Bootstrap CSS
class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=30, 
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username'}))
    password = forms.CharField(label="Password", max_length=30, 
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'password'}))
    
#class DataForm(forms.ModelForm):
 #    class Meta:
        #model = User
  #      model = Details
   #     fields = ('user','exp','res_id','category')  
    #username = forms.CharField(label='Username', max_length=30)
    #exp = forms.CharField(label='exp', max_length=30)
    #res = forms.CharField(label='res', max_length=30)
    #cat = forms.CharField(label='cat', max_length=30)
        
        
#class RegistrationForm(forms.Form):
 #   username = forms.CharField(label='Username', max_length=30)
 #   email = forms.EmailField(label='Email')
  #  password = forms.CharField(label='Password',
   #                       widget=forms.PasswordInput())

