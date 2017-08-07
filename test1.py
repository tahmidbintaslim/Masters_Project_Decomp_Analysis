import django
import os
import numpy as np
import sys
from rango.models import Experiment,FileDetails,MotifList,AlphaTable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()


experimentName = sys.argv[1]
resultId = sys.argv[2]
category = sys.argv[3]
experiment = Experiment.objects.get_or_create(experimentName = experimentName, resultId = resultId,category = category)
experiment.save()






rows = len(a)
columns= 300
#alpha_values = np.array[:]
alpha_values = np.zeros((rows,columns),np.float)
alpha_values2 = np.zeros((rows,columns),np.float)
motif_list = np.zeros((rows,columns),np.chararray)

i=1
j=0
index=0



url =[]
for file in a:
    api_link = a['file{}'.format(i)][0]
    raw_data = urlopen(api_link[0]).read()
    url = json.loads(raw_data)
    url = url.get('alpha')
    alpha_value = sorted(url, key=lambda k: k[0], reverse=False)
    alpha_values[index,:] = np.transpose(np.array(alpha_value))[1]
    index +=1 
    i +=1
    
motif_list = np.transpose(np.array(alpha_value))[0] 
#print motif_list
alpha_values2 = alpha_values
alpha_values /= alpha_values.sum(axis=1)[:,None]
#print alpha_values.shape
print alpha_values[0][100] 

#print alpha_values[0]
sklearn_pca = PCA(n_components=2,whiten = True)
sklearn_pca.fit(alpha_values)
#print sklearn_pca.explained_variance_
alpha_sklearn = sklearn_pca.transform(alpha_values)

j=1
category_seq =[]
group1_index=[]
group2_index=[]

for i in range(rows):
    category_seq.append(a['file{}'.format(j)][0][1]) 
    if(a['file{}'.format(j)][0][1] == 1):
        group1_index.append(i)
    else:
        group2_index.append(i)
       
    i=i+1
    j=j+1
    
category_seq = np.array(category_seq)

data = []
for lab in (0, 1):
    data.append( Scatter(
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
                    Scatter(
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
plt.plot({'data':data})

m_score = []
arr_t = np.transpose(alpha_values)
for i, alp in enumerate(arr_t):
        a = np.array(alp) 
        g1 = a[group1_index]
        g2 = a[group2_index]
        zscore = (g1.mean() - g2.mean()) / (g1.std() + g2.std())  #or use zscore method????
        t, p = ttest_ind(g1, g2, equal_var=False)
        m_score.append((i, zscore, t, p))

print m_score

import scipy.cluster.hierarchy as hier
import scipy.spatial.distance as dist
#print alpha_values.shape
#Z = hac.linkage(alpha_values.T, 'complete', 'correlation')
#print Z
dataMatrix = np.array(alpha_values.T)
#print dataMatrix

distanceMatrix = dist.pdist(dataMatrix)
distanceSquareMatrix = dist.squareform(distanceMatrix)
linkageMatrix = hier.linkage(distanceSquareMatrix)

heatmapOrder = hier.leaves_list(linkageMatrix)
#print "heatmapOrder"
#print heatmapOrder


orderedDataMatrix = dataMatrix[heatmapOrder,:]

rowHeaders = np.array(motif_list)
#print rowHeaders[heatmapOrder]

orderedRowHeaders = rowHeaders[heatmapOrder]

matrixOutput = []
row = 0
for rowData in orderedDataMatrix:
	col = 0
	rowOutput = []
	for colData in rowData:
		rowOutput.append([colData, row, col])
		col += 1
	matrixOutput.append(rowOutput)
	row += 1

colHeaders = ["file1","file2","file3","file4","file5","file6","file7","file8","file9","file10","file11","file12"]    
#print 'var maxData = ' + str(np.amax(dataMatrix)) + ";"
#print 'var minData = ' + str(np.amin(dataMatrix)) + ";"
#print 'var data = ' + str(matrixOutput) + ";"
#print 'var cols = ' + str(colHeaders) + ";"
#print 'var rows = ' + str([x for x in orderedRowHeaders]) + ";"


# Plot the dendogram
#plot1.figure(figsize=(25, 10))
#plot1.title('Hierarchical Clustering Dendrogram')
#plot1.xlabel('sample index')
#plot1.ylabel('distance')
#hac.dendrogram(
#    Z,
#    leaf_rotation=90.,  # rotates the x axis labels
#    leaf_font_size=8.,  # font size for the x axis labels
#)
#plot1.show()

#import plotly.plotly as py
#import plotly.figure_factory as ff

#import numpy as np

#dendro = ff.create_dendrogram(alpha_values.T)
#dendro['layout'].update({'width':800, 'height':500})
#py.iplot(dendro, filename='simple_dendrogram')
import scipy.spatial
import matplotlib.pyplot as plt
dataMatrix = np.array(alpha_values.T)
distMat = scipy.spatial.distance.pdist( dataMatrix )

# Cluster hierarchicaly using scipy
clusters = scipy.cluster.hierarchy.linkage(distMat, method='complete')
T = scipy.cluster.hierarchy.to_tree( clusters , rd=False )

# Create dictionary for labeling nodes by their IDs
labels = list(motif_list)
id2name = dict(zip(range(len(labels)), labels))

# Draw dendrogram using matplotlib to scipy-dendrogram.pdf
scipy.cluster.hierarchy.dendrogram(clusters, labels=labels, orientation='right')
plt.savefig("scipy-dendrogram.png")

# Create a nested dictionary from the ClusterNode's returned by SciPy
def add_node(node, parent ):
	# First create the new node and append it to its parent's children
	newNode = dict( node_id=node.id, children=[] )
	parent["children"].append( newNode )

	# Recursively add the current node's children
	if node.left: add_node( node.left, newNode )
	if node.right: add_node( node.right, newNode )

# Initialize nested dictionary for d3, then recursively iterate through tree
d3Dendro = dict(children=[], name="Root1")
add_node( T, d3Dendro )

# Label each node with the names of each leaf in its subtree
def label_tree( n ):
	# If the node is a leaf, then we have its name
	if len(n["children"]) == 0:
		leafNames = [ id2name[n["node_id"]] ]
	
	# If not, flatten all the leaves in the node's subtree
	else:
		leafNames = reduce(lambda ls, c: ls + label_tree(c), n["children"], [])

	# Delete the node id since we don't need it anymore and
	# it makes for cleaner JSON
	del n["node_id"]

	# Labeling convention: "-"-separated leaf names
	n["name"] = name = "-".join(sorted(map(str, leafNames)))
	
	return leafNames

label_tree( d3Dendro["children"][0] )

# Output to JSON
json.dump(d3Dendro, open("d3-dendrogram.json", "w"), sort_keys=True, indent=4)


import matplotlib.pyplot as plt
import numpy as np

column_labels = list(range(0,12))
row_labels = list(motif_list)
data = np.array(alpha_values.T)
fig, axis = plt.subplots() # il me semble que c'est une bonne habitude de faire supbplots
heatmap = axis.pcolor(data, cmap=plt.cm.Blues) # heatmap contient les valeurs

axis.set_yticks(np.arange(data.shape[0])+0.5, minor=False)
axis.set_xticks(np.arange(data.shape[1])+0.5, minor=False)

axis.invert_yaxis()

axis.set_yticklabels(row_labels, minor=False)
axis.set_xticklabels(column_labels, minor=False)

fig.set_size_inches(11.03, 3.5)

plt.savefig('test2.png', dpi=100)









        





