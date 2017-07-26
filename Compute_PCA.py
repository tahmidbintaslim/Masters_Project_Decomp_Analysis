import os
import pickle
import numpy as np
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
import django
django.setup()

from sklearn.decomposition import PCA

from rango.models import Experiment,FileDetail,MotifList,AlphaTable
import jsonpickle
from plotly.offline import plot, iplot, init_notebook_mode
import plotly.graph_objs as go

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
            print s
            nav = [a / s for a in av]
            
            new_alp_vals.append(nav)
        alp_vals = new_alp_vals 
      
    alpha_values = np.array(alp_vals)
   
    sklearn_pca = PCA(n_components = 2,whiten = True)
    sklearn_pca.fit(alpha_values)
    alpha_sklearn = sklearn_pca.transform(alpha_values)
    print alpha_sklearn.shape
    print alpha_sklearn
    
    data = []
    category_seq =[]
    for files in files:
        category_seq.append(str(files.category))  
    category_seq = np.array(category_seq)
    for lab in ('0', '1'):
         data.append(go.Scatter(
                        x = alpha_sklearn[category_seq==lab,0],
                        y = alpha_sklearn[category_seq==lab,1],
                        mode = 'markers',
                        marker = dict(
                            size = 10,
                            ),
                    )
                )
            
    for i in range(len(motifs)):
               motifs = MotifList.objects.filter(experimentName = exp) 
               data.append(
                    go.Scatter(
                        x = [0,5*sklearn_pca.components_[0,i]],
                        y = [0,5*sklearn_pca.components_[1,i]],
                        name = [motifs.MotifName for motifs in motifs],
                        mode = 'lines',
                        line = dict(
                            color = ('rgba(200,0,0,0.1)'),
                            ),
                          showlegend = False,
                        )
                    )   
    layout = go.Layout(
        showlegend=False,
        autosize=False,
        width=800,
        height=700,
        xaxis=dict(
            domain=[0, 0.85],
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            domain=[0, 0.85],
            showgrid=False,
            zeroline=False
        ),
        margin=dict(
            t=50
        ),
        hovermode='closest',
        bargap=0,
       
    )
    fig = go.Figure(data=data, layout=layout)
    pca_div = plot(fig,output_type='div', include_plotlyjs=False)
    exp.pca = pca_div
    exp.save()
    
    