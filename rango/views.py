from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse,HttpResponseRedirect
from django.views import generic
from django.shortcuts import render,redirect
from braces import views
import numpy as np
from . import forms
from . import Load_data
from rango.forms import categoryform
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
#from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.template import RequestContext 
from django.shortcuts import render_to_response
from rango.models import Experiment,FileDetail,MotifList,AlphaTable
from simple_search import search_form_factory
from sklearn.decomposition import PCA
import simplejson as json
from rango.models import Experiment,FileDetail,MotifList,AlphaTable
import jsonpickle
from plotly.offline import plot, iplot, init_notebook_mode
import plotly.graph_objs as go
from scipy.stats import ttest_ind
from plotly.tools import FigureFactory as FF
import scipy
from scipy.spatial.distance import pdist,squareform
#from .forms import SearchForm
#from rango.models import User,Details

#@login_required(login_url="login/")
def home(request):
    return render(request,"base.html") 

def loadData(request):
    context_dict = {}
    if request.method == "POST":
        decompform = forms.createExpform(request.POST)
        if decompform.is_valid():
            '''
            data = decompform.save(commit=False)
            data.experimentName = request.POST['experimentName']
            data.resultId= request.POST['resultId']
            data.fileNames = request.POST['fileNames']
            #data.save()
            '''
            print request.POST['experimentName']
            Load_data.populateExperiment(request.POST['experimentName'],request.POST['resultId'],request.POST['fileNames'])
            Load_data.populateFileDetail(request.POST['experimentName'],request.POST['resultId'],request.POST['fileNames'])
            Load_data.populateMotifList(request.POST['experimentName'],request.POST['resultId'],request.POST['fileNames'])
            Load_data.populateAlphaMatrix(request.POST['experimentName'],request.POST['resultId'],request.POST['fileNames'])
            
        else:
            context_dict['decompform'] = decompform   
    else:
        decompform = forms.createExpform()
        context_dict['decompform'] = decompform  
    return render(request, 'add.html', {'form': decompform}) 

def search(request):
    result_list = Experiment.objects.all()
    return render(request, 'search.html', {'result_list': result_list})

def categorySel(request,expname):
    #print expname
    context_dict = {}
    exp = Experiment.objects.get(experimentName = expname)
    result_list = FileDetail.objects.filter(experimentName = exp)
    print result_list
    print request.method
    if request.method == 'POST':
        categoryf = categoryform(request.POST)
        group1 = request.POST.getlist('group1')
        group2 = request.POST.getlist('group2')
        print group1
        print group2
        for g1,g2 in zip(group1,group2):
            for i in range(len(result_list)): 
                if g1 == str(result_list[i].fileName):                     
                    result_list[i].category ='0'
                    print result_list[i].category 
                    result_list[i].save()  
                if g2 == str(result_list[i].fileName):   
                    result_list[i].category ='1'
                    result_list[i].save()
        #context_dict['result_list'] = result_list
        context_dict['expname'] = exp            
        return render(request, 'index.html',context_dict)        
    else:
        print "hello"
        context_dict['result_list'] = result_list
        context_dict['exp'] = exp
      
    return render(request, 'categorySel.html',context_dict)

def IndexView(request,expname):
    return render(request, 'index.html', {'expname': expname})

def HeatView(request,expname): 
    exp = Experiment.objects.get(experimentName = expname)
    files = FileDetail.objects.filter(experimentName = exp)
    ind_file = [f.experimentName for f in files]
    #motifs = MotifList.objects.filter(experimentName = ind_file[0])    
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
        if m.Annotation == "":
            labels.append(m.MotifName)  
        else:
            labels.append(m.Annotation)  
    print labels        
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
    heat_div = plot(figure, output_type='div')
    exp.heatmap = heat_div
    exp.save()
    context={
    'plot':exp.heatmap,
    'Name': 'Dendrogram Heatmap'     
     }
       
    return render(request, 'plot.html', context)
       
def PlotView(request,expname):   
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
    #print alp_vals    
    alpha_values = np.array(alp_vals,np.float) 
    alpha_values /= alpha_values.sum(axis=1)[:,None]
    category_seq =[]
    fileNames=[]
    m_score=[]
    fileColor =[]
    group1_index=[]
    group2_index=[]
    for i,files in zip(range(len(files)),files):
        fileNames.append(str(files.fileName))
        category_seq.append(str(files.category))  
        if files.category =='0':
            group1_index.append(i)
            fileColor.append('steelblue')
        else:
            group2_index.append(i)
            fileColor.append('red')
    category_seq = np.array(category_seq)
    grp = group1_index + group2_index
    print category_seq
    Motiflist = MotifList.objects.filter(experimentName = exp)
  
    sklearn_pca = PCA(n_components = 2,whiten = True)
    sklearn_pca.fit(alpha_values)
    var = sklearn_pca.explained_variance_ratio_
    pc1 = str(var[0:1] * 100)
    pc2 = str(var[1:2] * 100)
    y = np.array(fileNames)
    alpha_sklearn = sklearn_pca.transform(alpha_values)
    data = []
    motifs = MotifList.objects.filter(experimentName = ind_file[0]) 
    array = np.array(sklearn_pca.components_)
    import pandas as pd
    print pd.DataFrame(alpha_sklearn.T,columns=fileNames,index = ['PC-1','PC-2'])
    #for names in fileNames:
    for name,color in zip(fileNames,fileColor):
        #print name
        #print y
           data.append(go.Scatter(
                        x = alpha_sklearn[(y==name),0],
                        y = alpha_sklearn[(y==name),1],
                        mode = 'markers',
                        name =name,
                        marker = dict(
                            size = 10,
                            color = color
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
    context={
    'plot':exp.pca,
    'Name': 'Prinicipal Component Analysis'    
     }
       
    return render(request, 'plot.html', context)   
    
    
def DendroView(request,expname):
        # Call the base implementation first to get a context
     #   context = super(VarianceView, self).get_context_data(**kwargs)
     #   context['variance'] = plots.plotm()
    exp = Experiment.objects.get(experimentName = expname)
    files = FileDetail.objects.filter(experimentName = exp)
    ind_file = [f.experimentName for f in files]
    motifs = MotifList.objects.filter(experimentName = ind_file[0])    
    alp_vals = []
    names = []
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
    motifs = MotifList.objects.filter(experimentName = exp)
    for motifs in motifs:
         names.append(motifs.MotifName)
    
    dendro = FF.create_dendrogram(alpha_values.T,orientation='left',labels = names)
    dendro['layout'].update({'width':500, 'height':500})
    #plot(dendro)
    
    
#------D3 Dendrogram------#
    print alpha_values.shape
    dataMatrix = np.array(alpha_values.T)
    distMat = scipy.spatial.distance.pdist( dataMatrix )

    # Cluster hierarchicaly using scipy
    clusters = scipy.cluster.hierarchy.linkage(distMat, method='single')


    # Create dictionary for labeling nodes by their IDs
    labels = list(names)
    id2name = dict(zip(range(len(labels)), labels))

    # Draw dendrogram using matplotlib to scipy-dendrogram.pdf
    #scipy.cluster.hierarchy.dendrogram(clusters, labels=labels, orientation='right')
    #plt.savefig("scipy-dendrogram.png")

# Create a nested dictionary from the ClusterNode's returned by SciPy
    def add_node(node, parent ):
        # First create the new node and append it to its parent's children
    
        newNode = dict( node_id=node.id, children=[] )
        #print newNode
        parent["children"].append( newNode )
        #print parent
        # Recursively add the current node's children
        if node.left : add_node( node.left, newNode )
        if node.right: add_node( node.right, newNode )

    # Initialize nested dictionary for d3, then recursively iterate through tree
    T = scipy.cluster.hierarchy.to_tree( clusters , rd=False )

    d3Dendro = dict(children=[], name="Root1")
    add_node( T, d3Dendro )

    # Label each node with the names of each leaf in its subtree
    def label_tree( n ):
    # If the node is a leaf, then we have its name
        if len(n["children"]) == 0:
            leafNames = [ id2name[n["node_id"]] ]
            #print "0"
            #print  leafNames 
            # If not, flatten all the leaves in the node's subtree
            #elif len(n["children"]) ==2: 
             #   leafNames = ""
        else:
            leafNames = reduce(lambda x, y: x + label_tree(y), n["children"], [])
            #print "not"
            #print leafNames
            # Delete the node id since we don't need it anymore and
            # it makes for cleaner JSON
        del n["node_id"]

        #Labeling convention: "-"-separated leaf names
        n["name"] = name = "-".join(sorted(map(str, leafNames)))

        return leafNames

    label_tree( d3Dendro["children"][0] )
# Output to JSON
    json.dump(d3Dendro, open("d3-dendrogram.json", "w"), sort_keys=True, indent=4)
    exp.hclus = open("d3-dendrogram.json", "r")
    with open("d3-dendrogram.json",'r') as f:
        exp.hclus = json.load(f)

    
    #hclus_div = plot(dendro,output_type='div', include_plotlyjs=False)
    #exp.hclus = hclus_div
    exp.save()
    context={
        'exp':exp,
        }
    return render(request, 'index2.html', context)    

def VarianceView(request,expname):
        # Call the base implementation first to get a context
     #   context = super(VarianceView, self).get_context_data(**kwargs)
     #   context['variance'] = plots.plotm()
        exp = Experiment.objects.get(experimentName = expname)
        motif = MotifList.objects.filter(experimentName = exp)
        context={
        'motif':motif,
        }
        return render(request, 'variance.html', context)

def register_page(request):
    if request.method == 'POST':
        form = forms.RegistrationForm(request.POST)
        if form.is_valid():
            user=User.objects.create_user(username=form.cleaned_data['username'],
                                          password=form.cleaned_data['password1'],
                                          email=form.cleaned_data['email'])
            #user.save()
            return HttpResponseRedirect('/')
    form = forms.RegistrationForm()
    variables = RequestContext(request, {'form': form})
    return render_to_response('register.html',variables)    
