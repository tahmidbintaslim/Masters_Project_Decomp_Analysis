from django.contrib.auth.forms import AuthenticationForm 
from django import forms
from .models import Experiment,FileDetail,MotifList,AlphaTable

# Referenced from tango with django book

# Form to get/Post the categorized sample data
class categoryform(forms.Form):
    group = forms.CharField(widget=forms.TextInput(attrs={'style': 'width:300px'}))
    files = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 80}))   
    
# Form to get/Post new decomposition analysis experiment    
class createExpform(forms.ModelForm):        
    class Meta:
        model = Experiment
        fields = [
            'experimentName','description','resultId','fileNames'
        ]
        widgets = {'experimentName': forms.Textarea(attrs={'rows': 1, 'cols': 50}),
                   'description': forms.Textarea(attrs={'rows': 1, 'cols': 50}),
            'resultId': forms.Textarea(attrs={'rows': 5, 'cols': 50}),
            'fileNames': forms.Textarea(attrs={'rows': 5, 'cols': 50})
            
                  }
        exclude = ('pca','hclus',)
          

