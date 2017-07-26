import os
import pickle
import numpy as np
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
import django
django.setup()

from sklearn.decomposition import PCA

from rango.models import Experiment,FileDetail,MotifList,AlphaTable

from plotly.offline import plot, iplot, init_notebook_mode
import plotly.graph_objs as go
from plotly.tools import FigureFactory as FF

if __name__ == '__main__':
    expname = sys.argv[1]
    exp = Experiment.objects.get(experimentName = expname)
    files = FileDetail.objects.filter(experimentName = exp)
    ind_file = [f.experimentName for f in files]
    motifs = MotifList.objects.filter(experimentName = ind_file[0])    
    alp_vals = []
    i =0
    for individual in ind_file:        
        motifs = individual.motiflist_set.all() 
        alp_vals.append([m.alphatable_set.all()[i].value for m in motifs]) 
        i +=1
        new_alp_vals = []
        for av in alp_vals:
            s = sum(av)
            nav = [a / s for a in av]
            
            new_alp_vals.append(nav)
        alp_vals = new_alp_vals 
      
    alpha_values = np.array(alp_vals)
    dendro = FF.create_dendrogram(alpha_values.T)
    hclus_div = plot(dendro,output_type='div', include_plotlyjs=False)
    exp.hclus = hclus_div
    exp.save()