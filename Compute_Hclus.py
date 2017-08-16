import os
import pickle
import numpy as np
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
import django
django.setup()

from sklearn.decomposition import PCA
import scipy.spatial
import matplotlib.pyplot as plt

from rango.models import Experiment,FileDetail,MotifList,AlphaTable

from plotly.offline import plot, iplot, init_notebook_mode
import plotly.graph_objs as go
from plotly.tools import FigureFactory as FF
import simplejson as json
from numpy import *
from scipy import stats
import plotly.figure_factory as FF
import numpy as np
from scipy.spatial.distance import pdist, squareform

if __name__ == '__main__':
    expname = sys.argv[1]
    exp = Experiment.objects.get(experimentName = expname)
    files = FileDetail.objects.filter(experimentName = exp).filter(category__isnull=False)
    print files
  
    ind_file = [f.experimentName for f in files]
    motifs = MotifList.objects.filter(experimentName = ind_file[0])    
    alp_vals = []
    
    i =0
    for individual in ind_file:        
        motifs = individual.motiflist_set.all()  
        alp_vals.append([m.alphatable_set.all()[i].value for m in motifs]) 
        i +=1
    #print alp_vals    
    alpha_values = np.array(alp_vals,np.float) 
    alpha_values /= alpha_values.sum(axis=1)[:,None]

    alpha_v = alpha_values
    norm_alpha = (alpha_v - (np.mean(alpha_v, axis=0)))/np.std(alpha_v, axis=0)
    motifs = MotifList.objects.filter(experimentName = exp) 
    labels =[]
    for m in motifs:
        labels.append(m.MotifName)  
    data_array = norm_alpha.T
    data_array2 = norm_alpha
    figure = FF.create_dendrogram(data_array, orientation='bottom', labels=labels)
    #plot(figure, filename='dendrogram_with_heatmap')
    print len(figure['data'])
    for i in range(len(figure['data'])):
        figure['data'][i]['yaxis'] = 'y2'

    # Create Side Dendrogram
    dendro_side = FF.create_dendrogram(data_array2, orientation='right')
    print len(dendro_side['data'])
    for i in range(len(dendro_side['data'])):
        dendro_side['data'][i]['xaxis'] = 'x2'

    # Add Side Dendrogram Data to Figure
    figure['data'].extend(dendro_side['data'])

    # Create Heatmap
    dendro_leaves = dendro_side['layout']['yaxis']['ticktext']
    dendro_leaves = list(map(int, dendro_leaves))
    data_dist = pdist(data_array)
    heat_data = squareform(data_dist)
    heat_data = heat_data[dendro_leaves,:]
    heat_data = heat_data[dendro_leaves,:]

    heatmap = go.Data([
    go.Heatmap(
        x = dendro_leaves,
        y = dendro_leaves,
        z = heat_data,
        colorscale = 'YIGnBu'
        )
        ])

    heatmap[0]['x'] = figure['layout']['xaxis']['tickvals']
    heatmap[0]['y'] = dendro_side['layout']['yaxis']['tickvals']


    # Add Heatmap Data to Figure
    figure['data'].extend(go.Data(heatmap))
    figure['layout']['yaxis']['ticktext'] = np.asarray(dendro_leaves)
    figure['layout']['yaxis']['tickvals'] = np.asarray(dendro_side['layout']['yaxis']['tickvals'])

    # Edit Layout

    figure['layout'].update({'width':1000, 'height':1000,
                         'showlegend':False, 'hovermode': 'closest',
                         })
    figure['layout']['xaxis'].update({'domain': [.15, 1],
                                  'mirror': False,
                                  'showgrid': False,
                                  'showline': False,
                                  'zeroline': False,
                                  'showticklabels': True,
                                  'ticks':"",
                                  'tickfont': dict(
            family='Old Standard TT, serif',
            size=8,
            color='black'
        )
                                
                                 })
    # Edit xaxis2
    figure['layout'].update({'xaxis2': {'domain': [0, .15],
                                   'mirror': False,
                                   'showgrid': False,
                                   'showline': False,
                                   'zeroline': False,
                                   'showticklabels': False,
                                   'ticks':""}})

    # Edit yaxis
    figure['layout']['yaxis'].update({'domain': [0, .85],
                                  'mirror': False,
                                  'showgrid': False,
                                  'showline': False,
                                  'zeroline': False,
                                  'showticklabels': True,
                                  'ticks': ""})
    # Edit yaxis2
    figure['layout'].update({'yaxis2':{'domain':[.825, .975],
                                   'mirror': False,
                                   'showgrid': False,
                                   'showline': False,
                                   'zeroline': False,
                                   'showticklabels': False,
                                   'ticks':""}})

    # Plot!
    #heat_div = plot(figure, output_type='div')
    #exp.heatmap = heat_div
    #exp.save()
    plot(figure, filename='dendrogram_with_heatmap')
    
     