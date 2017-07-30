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

if __name__ == '__main__':
    expname = sys.argv[1]
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