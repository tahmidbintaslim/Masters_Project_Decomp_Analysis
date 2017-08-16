from rango.models import Experiment,FileDetail,MotifList,AlphaTable
from urllib import urlopen
from django.views.generic import TemplateView
import simplejson as json
import numpy as np
import requests

def populateExperiment(experimentName,description,resultId,filename):  
    experiment = Experiment.objects.get_or_create(experimentName = experimentName, description=description,
                                                  resultId = resultId,fileNames = filename)

def populateFileDetail(experimentName,resultId,filename):
    experiments = Experiment.objects.filter(experimentName=experimentName)
    print experiments
    for experiment in experiments:
        res_id = str(experiment.resultId).split('\n')
        filename = str(experiment.fileNames).split('\n')
        for res_id,filename in zip(res_id,filename):
            FileDetail.objects.create(experimentName = experiment,resultId= res_id, fileName = filename,motif_count=0)
                
def populateMotifList(experimentName,resultId,filename):
    experiments = Experiment.objects.filter(experimentName=experimentName)
    
    for experiment in experiments:
        file = FileDetail.objects.filter(experimentName=experiment)
        index =1
        alpha_value = []
        for file,i in zip(file,range(1)):
            #print file.resultId
            link ='http://ms2lda.org/decomposition/api/batch_results/{}'.format(file.resultId)
            raw_data = urlopen(link).read()
            url = json.loads(raw_data)
            
            url1 = url.get('alpha')
            url2 = url.get('motifset')
            print url2
            alpha_value = sorted(url1, key=lambda k: k[0], reverse=False)
        motif_list = np.transpose(np.array(alpha_value))[0]
        print alpha_value
        index =0
        for i in range(len(motif_list)):    
            #print motif_list[i]
            MotifList.objects.create(MotifName = motif_list[i],experimentName = experiment,MotifId=i)
        loadAnnotation(experiments,url2) 
        
def populateAlphaMatrix(experimentName,resultId,filename):
    experiment = Experiment.objects.filter(experimentName = experimentName)
    for experiment in experiment:
        file = FileDetail.objects.filter(experimentName = experiment)
        Motiflist = MotifList.objects.filter(experimentName = experiment)        
        alpha_value = []
        alpha_values = np.zeros((len(file),len(Motiflist)),np.float)
        print len(Motiflist)
        for file in file:           
            index =1
            link ='http://ms2lda.org/decomposition/api/batch_results/{}'.format(file.resultId)
            raw_data = urlopen(link).read()
            url = json.loads(raw_data)
            url = url.get('alpha')
            alpha_value = sorted(url, key=lambda k: k[0], reverse=False)   
            for motif,i in zip(Motiflist,range(len(Motiflist))):
                print i 
                alp = AlphaTable.objects.get_or_create(mass2motif = motif,
                                         fileName = file, value = alpha_value[i][index])
                           
    
def loadAnnotation(experimentName,motifset):
    annotation = []  
    url ='http://ms2lda.org/decomposition/api/get_motifset_annotations/'
    args = {'motifset':motifset}
    response = requests.post(url,args)
    #print response.json()
    #raw_data = urlopen(link).read()
    url = response.json()
    url = url.get('annotations')
    #print url
    annotation = sorted(url, key=lambda k: k[0], reverse=False)
    print len(annotation)
    print annotation
    experiment = Experiment.objects.filter(experimentName = experimentName)    
    for i in range(len(annotation)):
        motiflist = MotifList.objects.filter(experimentName = experiment)
        for motiflist in motiflist:            
            if motiflist.MotifName == annotation[i][0]:
                motiflist.Annotation = annotation[i][1]                  
                motiflist.save()
                

    
