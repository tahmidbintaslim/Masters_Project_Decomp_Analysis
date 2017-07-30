from django.shortcuts import render
from django.http import HttpResponse
import numpy as np
from urllib import urlopen
from django.views.generic import TemplateView
import simplejson as json
from sklearn.decomposition import PCA
#from rango.models import User,Details
from plotly.offline import plot, iplot, init_notebook_mode
import plotly.graph_objs as go
from rango.models import Experiment,FileDetail,MotifList,AlphaTable
import sys
#from django.contrib.auth.models import User

def plotv():
    #expname = sys.argv[1]
    exp = Experiment.objects.get(experimentName = "exp1")
    return exp.pca

#def ploth():
#    exp = Experiment.objects.get(experimentName = "exp1")
#    return exp.hclus
    
#def plotm():
#    exp = Experiment.objects.get(experimentName = "exp1")
#    return exp.alpha_variance, exp.motif_score


    
    
    
                              
        
