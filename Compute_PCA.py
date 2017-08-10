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
from scipy.stats import ttest_ind

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
    
    #------CALCULATE MOTIF SCORE-------#
    category_seq =[]
    m_score=[]
    group1_index=[]
    group2_index=[]
    for i,files in zip(range(12),files):
        category_seq.append(str(files.category))  
        if files.category =='0':
            group1_index.append(i)
        else:
            group2_index.append(i)
    category_seq = np.array(category_seq)
    Motiflist = MotifList.objects.filter(experimentName = exp)
    for i,alp in enumerate(alpha_values.T):
        #for motifs in Motiflist:
            a = np.array(alp)            
            g1 = a[group1_index]
            g2 = a[group2_index]
            zscore = (g1.mean() - g2.mean()) / (g1.std() + g2.std())  #or use zscore method????
            t, p = ttest_ind(g1, g2, equal_var=False)
            m_score.append((zscore, t, p))
    i =0        
    for motifs,score in zip(Motiflist,m_score):
    #     mscore_str = motifs.MotifName + " " + 
            motifs.z_score = m_score[i][0]
            motifs.t_value = m_score[i][1]
            motifs.p_value = m_score[i][2]
            i +=1
            motifs.save()       
    #exp.motif_score = mscore
    #m_score_str =[]
    #for motifs,i in zip(Motiflist,range(len(m_score))):
     #        m_score_str.append(motifs.MotifName + " " + str(m_score[i]) + "\n")
   
    #motifs.motif_score = m_score_str   
    sklearn_pca = PCA(n_components = 2,whiten = True)
    sklearn_pca.fit(alpha_values)
    var = sklearn_pca.explained_variance_ratio_
    #print len(var)
    pc1 = str(var[0:1] * 100)
    pc2 = str(var[1:2] * 100)
    #exp.alpha_variance = "PC2" + " " + str(var[0:1]) + "\n" + "PC1" + " " + str(var[1:2])
    alpha_sklearn = sklearn_pca.transform(alpha_values)
    
    #print alpha_sklearn.shape
    #print alpha_sklearn
    
    data = []
    #category_seq =[]
    #for files in files:
     #   category_seq.append(str(files.category))  
    #category_seq = np.array(category_seq)
    motifs = MotifList.objects.filter(experimentName = ind_file[0])  
    for lab,names in zip(('0', '1'),('healthy','diagnose')):
         data.append(go.Scatter(
                        x = alpha_sklearn[category_seq==lab,0],
                        y = alpha_sklearn[category_seq==lab,1],
                        mode = 'markers',
                        name = names, 
                        marker = dict(
                            size = 10,
                            ),
                    )
                )
            
    for i,motifs in zip(range(len(motifs)),motifs):
               #motifs = MotifList.objects.filter(experimentName = exp) 
               data.append(
                    go.Scatter(
                        x = [0,5*sklearn_pca.components_[0,i]],
                        y = [0,5*sklearn_pca.components_[1,i]],
                        name = motifs.MotifName,
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
            title= 'PC1' + " " + pc1 + "%",          
            domain=[0, 0.85],
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            title='PC2' + " " + pc2 + "%",
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
    
    
    