from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse,HttpResponseRedirect
from django.views import generic
from django.shortcuts import render,redirect
from braces import views
import numpy as np
from . import forms
from . import Load_data
from decomp.forms import categoryform
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.template import RequestContext 
from django.shortcuts import render_to_response
from decomp.models import Experiment,FileDetail,MotifList,AlphaTable
from sklearn.decomposition import PCA
import simplejson as json
import jsonpickle
from plotly.offline import plot, iplot, init_notebook_mode
import plotly.graph_objs as go
from scipy.stats import ttest_ind
from plotly.tools import FigureFactory as FF
import scipy
from scipy.spatial.distance import pdist,squareform
from django.contrib import messages
from operator import itemgetter, attrgetter
#import pdb; pdb.set_trace()

#@login_required(login_url="login/")
def home(request):
    return render(request,"base.html") 

def guide(request):
    return render(request,"guide.html") 

def loadData(request):
    context_dict = {}    
    if request.method == "POST":
        decompform = forms.createExpform(request.POST)        
        if decompform.is_valid():              
            responseLoad = Load_data.populateExperiment(request.POST['experimentName'],request.POST['description'],
                                         request.POST['resultId'],request.POST['fileNames'])
            if responseLoad is True:
                    Load_data.populateFileDetail(request.POST['experimentName'],
                                         request.POST['resultId'],request.POST['fileNames'])
                    responseLoad = Load_data.populateMotifList(request.POST['experimentName'])
                                           
                    if responseLoad is True:
                            Load_data.populateAlphaMatrix(request.POST['experimentName'])                                                    
                            return HttpResponseRedirect(reverse('decomp:search'))
                    else:
                        context_dict['decompform'] = decompform 
                        messages.error(request, "Some Fields are missing or Invalid!!")    
            else:
                context_dict['decompform'] = decompform 
                messages.error(request, "Invalid input format!!")
        else:
            context_dict['decompform'] = decompform 
            messages.error(request, "Some Fields are missing or Invalid!!")
    else:
        decompform = forms.createExpform()
        context_dict['decompform'] = decompform  
        
    return render(request, 'loadData.html', context_dict) 

def search(request):
    context_dict ={}
    context_dict['result_list'] = Experiment.objects.all()
    return render(request, 'search.html', context_dict)

def categorySel(request,expname):
    #print expname
    context_dict = {}
    #expn = str(expname)
    exp = Experiment.objects.get(experimentName = expname)
    exp.hclus = None
    exp.pca = None
    exp.heatmap=None
    exp.save()
    result_list = FileDetail.objects.filter(experimentName = exp)
    motifs = MotifList.objects.filter(experimentName = exp) 
    for files in result_list:  
        files.category=None
        files.save()
    for m in motifs:  
        m.z_score=None
        m.t_value=None
        m.p_value=None
        m.q_value=None
        m.save()
    #result_list = FileDetail.objects.filter(experimentName = exp)
    if request.method == 'POST':
        categoryf = categoryform(request.POST)
        group1 = request.POST.getlist('group1')
        group2 = request.POST.getlist('group2')
        for g1 in group1:
            for f in result_list: 
                if g1 == f.fileName: 
                    f.category ='0' 
                    f.save()             
        for g2 in group2:
            for f in result_list: 
                if g2 == f.fileName: 
                    f.category ='1' 
                    f.save()    
                
        return HttpResponseRedirect(reverse('decomp:index', args=(exp,)))
        #return redirect('index',exp)
               
    else:
        print "hello"
        context_dict['result_list'] = result_list
        context_dict['exp'] = exp
      
    return render(request, 'categorySel.html',context_dict)

def IndexView(request,expname): 
    context_dict ={}
    context_dict['expname']=expname
    
    return render(request, 'index.html',context_dict )

def HeatView(request,expname): 
    exp = Experiment.objects.get(experimentName = expname)
  
    if exp.heatmap is None:
        files = FileDetail.objects.filter(experimentName = exp).filter(category__isnull=False)
        individual = files[1].experimentName
    
        #ind_file = [f.experimentName for f in files]
        motifs = MotifList.objects.filter(experimentName = individual) 
    
        alp_vals = []
        i =0
        for i in range(len(files)):        
        #motifs = individual.motiflist_set.all() 
            alp_vals.append([m.alphatable_set.all()[i].value for m in motifs]) 
        alpha_values = np.array(alp_vals)
        alpha_values /= alpha_values.sum(axis=1)[:,None]
        alpha_v = alpha_values
    
        #Normalize alpha - zscore
        norm_alpha = (alpha_v - (np.mean(alpha_v, axis=0)))/np.std(alpha_v, axis=0) 
    
        labels =[]
        for m in motifs:
            if m.Annotation is None:
                labels.append(m.MotifName)  
            else:
                labels.append(m.Annotation)         
        data_array = norm_alpha.T
        data_array2 = norm_alpha
    
        # Create Up Dendrogram
        figure = FF.create_dendrogram(data_array, orientation='bottom', labels=labels)
        for i in range(len(figure['data'])):
            figure['data'][i]['yaxis'] = 'y2'

        # Create Side Dendrogram
        dendro_side = FF.create_dendrogram(data_array2, orientation='right')
        for i in range(len(dendro_side['data'])):
            dendro_side['data'][i]['xaxis'] = 'x2'
    
        figure['data'].extend(dendro_side['data'])

        # Create Heatmap
        dendro_leaves = dendro_side['layout']['yaxis']['ticktext']
        dendro_leaves = list(map(int, dendro_leaves))
        data_dist = pdist(data_array)
        heat_data = squareform(data_dist)
        heat_data = heat_data[dendro_leaves,:]
        heat_data = heat_data[dendro_leaves]
        filelabel =[]
        filelab =[]
        for files in files:
            filelabel.append(files.fileName)
    
        for dendro_leaves in dendro_leaves:
            filelab.append(filelabel[dendro_leaves])
        
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
        # Edit xaxis
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
                                  'ticks': "",
                                  'ticktext': filelab})
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
        'exp':exp.experimentName,    
        'Name': 'Dendrogram Heatmap'     
         }
    else:
        print "here"
        context={
        'plot':exp.heatmap,
        'exp':exp.experimentName,    
        'Name': 'Dendrogram Heatmap'     
         }
    return render(request, 'plotlyPCA_HeatMap.html', context)
       
def PcaView(request,expname):   
    exp = Experiment.objects.get(experimentName = expname)
    files = FileDetail.objects.filter(experimentName = exp).filter(category__isnull=False)
    individual = files[1].experimentName
    
    #ind_file = [f.experimentName for f in files]
    motifs = MotifList.objects.filter(experimentName = individual) 
    
    alp_vals = []
    i =0
    for i in range(len(files)):        
        alp_vals.append([m.alphatable_set.all()[i].value for m in motifs]) 
        '''
        i +=1
        new_alp_vals = []
        for av in alp_vals:
            s = sum(av)            
            nav = [a / s for a in av]            
            new_alp_vals.append(nav)
        alp_vals = new_alp_vals 
        '''
    alpha_values = np.array(alp_vals)
    alpha_values /= alpha_values.sum(axis=1)[:,None]
    fileNames=[]
    m_score=[]
    fileColor =[]
    group1_index=[]
    group2_index=[]
    for i,files in zip(range(len(files)),files):
        fileNames.append(str(files.fileName)) 
        if files.category =='0':
            group1_index.append(i)
            fileColor.append('steelblue')
        elif files.category =='1':
            group2_index.append(i)
            fileColor.append('red')
    
    sklearn_pca = PCA(n_components = 2,whiten = True)
    sklearn_pca.fit(alpha_values)
    var = sklearn_pca.explained_variance_ratio_
    pc1 = var[0:1] * 100
    pc2 = var[1:2] * 100
    y = np.array(fileNames)
    alpha_sklearn = sklearn_pca.transform(alpha_values)
    data = []
    #motifs = MotifList.objects.filter(experimentName = ind_file[0]) 
    #array = np.array(sklearn_pca.components_)
    
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
        width=1000,
        height=800,
        
        xaxis=dict(
            title= 'PC1' + "(" + str(round(float(pc1),2)) + "% of variance)",          
            domain=[0, 0.85],
            showgrid=True,
            zeroline=True
            
        ),
        yaxis=dict(
            title='PC2' + "(" + str(round(float(pc2),2)) + "% of variance)", 
            domain=[0, 0.85],
            showgrid=True,
            zeroline=True
            
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
    'exp':exp.experimentName,    
    'Name': 'Prinicipal Component Analysis'    
     }
     
    return render(request, 'plotlyPCA_HeatMap.html', context)    
    
    
def DendroView(request,expname):
        # Call the base implementation first to get a context
     #   context = super(VarianceView, self).get_context_data(**kwargs)
     #   context['variance'] = plots.plotm()
    exp = Experiment.objects.get(experimentName = expname)
    files = FileDetail.objects.filter(experimentName = exp).filter(category__isnull=False)
    #ind_file = [f.experimentName for f in files]
    #motifs = MotifList.objects.filter(experimentName = ind_file[0])    
    alp_vals = []
    names = []
    i =0
    individual = files[1].experimentName
    
    #ind_file = [f.experimentName for f in files]
    motifs = MotifList.objects.filter(experimentName = individual) 
    print motifs
    
    alp_vals = []
    i =0
    for i in range(len(files)):        
        #motifs = individual.motiflist_set.all() 
        alp_vals.append([m.alphatable_set.all()[i].value for m in motifs]) 
        '''
        i +=1
        new_alp_vals = []
        for av in alp_vals:
            s = sum(av)            
            nav = [a / s for a in av]            
            new_alp_vals.append(nav)
        alp_vals = new_alp_vals 
        '''
    alpha_values = np.array(alp_vals)
    alpha_values /= alpha_values.sum(axis=1)[:,None]
    motifs = MotifList.objects.filter(experimentName = exp)
    
    for motifs in motifs:
         names.append(motifs.MotifName)
    
    dendro = FF.create_dendrogram(alpha_values.T,orientation='left',labels = names)
    dendro['layout'].update({'width':5000, 'height':5000})
    #plot(dendro)
    
    
#------D3 Dendrogram------#
    print alpha_values.shape
    dataMatrix = np.array(alpha_values.T)
    distMat = scipy.spatial.distance.pdist( dataMatrix )

    # Cluster hierarchicaly using scipy
    clusters = scipy.cluster.hierarchy.linkage(distMat, method='complete')
    import sys
    sys.setrecursionlimit(10000)

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
    return render(request, 'Dendrogram.html', context)    

def ScoreView(request,expname):
        exp = Experiment.objects.get(experimentName = expname)
        files = FileDetail.objects.filter(experimentName = exp).filter(category__isnull=False)
        #print files
        individual = files[1].experimentName
    
        #ind_file = [f.experimentName for f in files]
        motifs = MotifList.objects.filter(experimentName = individual) 
        #print motifs
    
        alp_vals = []
        i =0
        for i in range(len(files)):        
           #motifs = individual.motiflist_set.all() 
            alp_vals.append([m.alphatable_set.all()[i].value for m in motifs]) 
        alpha_values = np.array(alp_vals)
        alpha_values /= alpha_values.sum(axis=1)[:,None]
        #print alpha_values
        #------CALCULATE MOTIF SCORE-------#
        category_seq =[]
        m_score=[]
        group1_index=[]
        group2_index=[]
        for i,files in zip(range(len(files)),files):
            category_seq.append(str(files.category))  
            if files.category =='0':
                group1_index.append(i)
            elif files.category =='1':
                group2_index.append(i)
        #category_seq = np.array(category_seq)
        #print group1_index, group2_index
        #Motiflist = MotifList.objects.filter(experimentName = exp)
        alpha2= np.array(alpha_values.T,np.float)
        print alpha2
        #print alpha_values
        for i,alp in enumerate(alpha2):
            #for m in motifs:
                a = np.array(alp) 
                g1 = a[group1_index]  
                g2 = a[group2_index]
                zscore = (g1.mean() - g2.mean()) / (g1.std() + g2.std())  #or use zscore method????
                t, p = ttest_ind(g1, g2, equal_var=False)
                m_score.append((i,zscore,t,p)) 
                #m_score.append((m.MotifName,zscore,t,p)) 
        s = np.array(m_score)
        print s
        sortm = np.array(sorted(m_score,key=itemgetter(3)))  
        print sortm
        #i =0 
        
        qval=[]
        score_list =[]
        for i in range(len(sortm)):
            a = float(sortm[i][3]) * len(sortm)
            b = a/(i+1)
            score_list.append((sortm[i][0],sortm[i][1],sortm[i][2],sortm[i][3],b))
        #print score_list
        
        score = np.array(sorted(score_list,key=itemgetter(0))) 
        print score
        i=0
        for m in motifs:
            m.z_score = score[i][1]
            m.t_value = score[i][2]
            m.p_value = score[i][3]
            m.q_value = score[i][4]
            i +=1
            m.save() 
       
        #motif_list.append([m.alphatable_set.all()[1].value for m in motif])
        #print np.array(motif_list)    
        #motif_matrix = sorted(motif_list, key=lambda k: k[2], reverse=False)
        #motif_matrix = np.array(motif_matrix)
        #print motif_matrix
        context={
        'motif':motifs,
        'exp':exp.experimentName,    
        }
        
        return render(request, 'score.html', context)

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
