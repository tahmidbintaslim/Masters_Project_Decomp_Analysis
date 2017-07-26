import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'project.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

import django
django.setup()

from rango.models import Experiment,FileDetail,MotifList,AlphaTable
from urllib import urlopen
from django.views.generic import TemplateView
import simplejson as json
import numpy as np

def populateExperiment():  
    import sys
    experimentName = sys.argv[1]
    resultId = sys.argv[2]
    category = sys.argv[3]
    experiment = Experiment.objects.get_or_create(experimentName = experimentName, resultId = resultId,category = category)

def populateFileDetail():
    experiments = Experiment.objects.all()
    for experiment in experiments:
        res_id = str(experiment.resultId).split(',')
        category = str(experiment.category).split(',')
        for res_id,category in zip(res_id,category):
            FileDetail.objects.create(experimentName = experiment,fileName = res_id,category=category,motif_count=0)
    

def populateMotifs():
    experiments = Experiment.objects.all()
    motif = populateAlpha()
    print len(motif)
    index =0
    for experiment in experiments:
        for i in range(len(motif)):            
            MotifList.objects.create(MotifName = motif[i],experimentName = experiment,MotifId=i)
            
    
    
def populateAlpha():
    file = FileDetail.objects.all()
    index =1
    alpha_value = []
    alpha_values = np.zeros((2,300),np.float)
    for file in file:
            link ='http://ms2lda.org/decomposition/api/batch_results/{}'.format(file.fileName)
            raw_data = urlopen(link).read()
            url = json.loads(raw_data)
            url = url.get('alpha')
            alpha_value = sorted(url, key=lambda k: k[0], reverse=False)
    motif_list = np.transpose(np.array(alpha_value))[0] 
    return motif_list
            
            
def populateAlphaMatrix():
    experiment = Experiment.objects.get(experimentName = "exp1")
    file = FileDetail.objects.filter(experimentName = experiment)
    Motiflist = MotifList.objects.filter(experimentName = experiment)
    alpha_value = []
    alpha_values = np.zeros((2,300),np.float)
    
    
    
    #motif_list = np.zeros((2,300),np.chararray)
    i =0
    for file in file:
            index =1
            link ='http://ms2lda.org/decomposition/api/batch_results/{}'.format(file.fileName)
            raw_data = urlopen(link).read()
            url = json.loads(raw_data)
            url = url.get('alpha')
            alpha_value = sorted(url, key=lambda k: k[0], reverse=False)
           
            
            for motif,i in zip(Motiflist,range(len(motif))):
                 alp = AlphaTable.objects.get_or_create(mass2motif = motif,
                                         fileName = file, value = alpha_value[i][index])
                
                 i +=1
            index +=1
            

if __name__ == '__main__':
        print("Starting Rango population script...")
        populateAlphaMatrix()               
    
