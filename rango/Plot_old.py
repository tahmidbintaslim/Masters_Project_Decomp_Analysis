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

def basic():
    init_notebook_mode(connected=True)
    #alpha_value = []
    index = 0
    #alpha_values = np.zeros((1,300),np.float)
    res =[]
    
    # Create your views here.  
    #user_id = User.objects.get(id=1)
    #print Details.objects.all()
    #print Details.objects.filter(id='natasha')
    #print Details.objects.all()
    test_details = Details.objects.all()
    #print test_details
    #user = [t.user for t in test_details]
    res = [t.res_id for t in test_details]
    #alphaDetails(res,alpha_values,motif_list)
    #alpha_PCA(alpha_values,category_seq,motif_list)
    #return HttpResponse("hello")
    ind = ['http://ms2lda.org/decomposition/api/batch_results/{}'.format(i) for i in res]
    index = 0
    alpha_values = np.zeros((len(res),300),np.float)
    motif_list = np.zeros((len(res),300),np.chararray)
    category_seq =[]
    url=[]
    category_seq = [t.category for t in test_details]
    category_seq = np.array(category_seq)
    for file in ind:
        raw_data = urlopen(file).read()
        url = json.loads(raw_data)
        url = url.get('alpha')
        alpha_value = sorted(url, key=lambda k: k[0], reverse=False)       
        alpha_values[index,:] = np.transpose(np.array(alpha_value))[1]
        index += 1   
    motif_list = np.transpose(np.array(alpha_value))[0] 
    #print alpha_values
    alpha_values /= alpha_values.sum(axis=1)[:,None] 
    return alpha_values, test_details,category_seq,motif_list

def plotv1(): 
    alpha_values,test_details,category_seq,motif_list = basic()
    sklearn_pca = PCA(n_components=2,whiten = True)
    sklearn_pca.fit(alpha_values)
    print sklearn_pca.explained_variance_
    alpha_sklearn = sklearn_pca.transform(alpha_values)
    print alpha_sklearn
    data = []
    for lab in (0, 1):
        data.append( go.Scatter(
                        x = alpha_sklearn[category_seq==lab,0],
                        y = alpha_sklearn[category_seq==lab,1],
                        mode = 'markers',
                        marker = dict(
                            size = 10,
                            ),
                    )
                )

    for i in range(len(motif_list)):
               data.append(
                    go.Scatter(
                        x = [0,5*sklearn_pca.components_[0,i]],
                        y = [0,5*sklearn_pca.components_[1,i]],
                       name = motif_list[i],
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
    
    return pca_div

def ploth1():    
    import plotly.plotly as py
    from plotly.tools import FigureFactory as FF
    import numpy as np
    alpha_values,test_details,category_seq,motif_list = basic()
    #X = np.random.rand(30, 15)
    dendro = FF.create_dendrogram(alpha_values.T)
    #dendro['layout'].update({'width':800, 'height':500})
    #py.plot(dendro, filename='simple_dendrogram')
    hclus_div = plot(dendro,output_type='div', include_plotlyjs=False)
    
    return hclus_div