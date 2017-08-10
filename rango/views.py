from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse,HttpResponseRedirect
from django.views import generic
from django.shortcuts import render
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
import scipy.spatial
#from .forms import SearchForm
#from rango.models import User,Details

#@login_required(login_url="login/")
def home(request):
    return render(request,"base.html") 

def loadData(request):
    Load_data.populateExperiment
    return render(request, 'search.html', context)

def search(request):
    result_list = Experiment.objects.all()
    return render(request, 'search.html', {'result_list': result_list})

def categorySel(request,expname):
    #print expname
    context_dict = {}
    exp = Experiment.objects.get(experimentName = expname)
    print exp
    result_list = FileDetail.objects.filter(experimentName = exp)
    if request.method == 'POST':
        categoryf = categoryform(request.POST)
        group1 = request.POST.getlist('group1')
        group2 = request.POST.getlist('group2')
        for g1,g2 in zip(group1,group2):
            for i in range(len(result_list)): 
                if g1 == result_list[i].fileName:
                    result_list[i].category ='0'
                    result_list[i].save()  
                else:
                    result_list[i].category ='1'
                    result_list[i].save() 
    else:
        context_dict['result_list'] = result_list
        context_dict['exp'] = exp
      
    return render(request, 'categorySel.html',context_dict)

def IndexView(request,expname):
    return render(request, 'index.html', {'expname': expname})

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
        new_alp_vals = []
        for av in alp_vals:
            s = sum(av)            
            nav = [a / s for a in av]            
            new_alp_vals.append(nav)
        alp_vals = new_alp_vals 
      
    alpha_values = np.array(alp_vals)
    category_seq =[]
    m_score=[]
    group1_index=[]
    group2_index=[]
    for i,files in zip(range(len(files)),files):
        category_seq.append(str(files.category))  
        if files.category =='0':
            group1_index.append(i)
        else:
            group2_index.append(i)
    category_seq = np.array(category_seq)
    Motiflist = MotifList.objects.filter(experimentName = exp)
  
    sklearn_pca = PCA(n_components = 2,whiten = True)
    sklearn_pca.fit(alpha_values)
    var = sklearn_pca.explained_variance_ratio_
    pc1 = str(var[0:1] * 100)
    pc2 = str(var[1:2] * 100)
    alpha_sklearn = sklearn_pca.transform(alpha_values)
    data = []
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
    context={
    'plot':exp.pca,
     }
       
    return render(request, 'plot.html', context)   
    
    
def ClusterView(request,expname):
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
    dendro['layout'].update({'width':2000, 'height':3000})
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
