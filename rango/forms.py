from django.contrib.auth.forms import AuthenticationForm 
from django import forms

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

class createExpform(forms.ModelForm):
     
    class Meta:
        model = Experiment
        #labels = {'experimentName' : 'Experiment','resultId':'Result Ids','fileNames':'File Names'}
        fields = [
            'experimentName','resultId','fileNames',
        ]
        widgets = {'experimentName': forms.Textarea(attrs={'rows': 1, 'cols': 50}),
            'resultId': forms.Textarea(attrs={'rows': 8, 'cols': 50}),
            'fileNames': forms.Textarea(attrs={'rows': 8, 'cols': 50})
            
                  }
        exclude = ('pca','hclus',)
        #fields = ('experimentName','resultId','fileNames') 
'''    
    
    exp_name = forms.CharField(label='Experiment Name', max_length=50,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'expname'}))
    filenames = forms.CharField(label='File Names', max_length=50,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'file'})) 
    resultids = forms.CharField(label='Result Ids', max_length=50,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'resid'}))   
'''    

