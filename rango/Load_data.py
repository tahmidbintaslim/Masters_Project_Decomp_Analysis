from rango.models import Experiment,FileDetail,MotifList,AlphaTable
from urllib import urlopen
from django.views.generic import TemplateView
import simplejson as json
import numpy as np
import requests

def populateExperiment(experimentName,resultId,filename):  
    experiment = Experiment.objects.get_or_create(experimentName = experimentName, resultId = resultId,fileNames = filename)

def populateFileDetail(experimentName,resultId,filename):
    experiments = Experiment.objects.filter(experimentName=experimentName)
    print experiments
    for experiment in experiments:
        res_id = str(experiment.resultId).split(',')
        filename = str(experiment.fileNames).split(',')
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
            url = url.get('alpha')
            alpha_value = sorted(url, key=lambda k: k[0], reverse=False)
        motif_list = np.transpose(np.array(alpha_value))[0]
        index =0
        for i in range(len(motif_list)):            
            MotifList.objects.get_or_create(MotifName = motif_list[i],experimentName = experiment,MotifId=i)

            
            
def populateAlphaMatrix(experimentName,resultId,filename):
    experiment = Experiment.objects.filter(experimentName = experimentName)
    for experiment in experiment:
        file = FileDetail.objects.filter(experimentName = experiment)
        Motiflist = MotifList.objects.filter(experimentName = experiment)
        alpha_value = []
        alpha_values = np.zeros((len(file),len(Motiflist)),np.float)
        print alpha_values
        i =0
        for file in file:
            index =1
            link ='http://ms2lda.org/decomposition/api/batch_results/{}'.format(file.resultId)
            raw_data = urlopen(link).read()
            url = json.loads(raw_data)
            url = url.get('alpha')
            alpha_value = sorted(url, key=lambda k: k[0], reverse=False)            
            for motif,i in zip(Motiflist,range(len(Motiflist))):
                 alp = AlphaTable.objects.get_or_create(mass2motif = motif,
                                         fileName = file, value = alpha_value[i][index])
                
                 i +=1
            index +=1
    
def loadAnnotation(experimentName,resultId,filename):
    annotation = []
    print "hello"
    url ='http://ms2lda.org/decomposition/api/get_motifset_annotations/'
    args = {'motifset':'massbank_motifset'}
    response = requests.post(url,args)
    #print response.json()
    #raw_data = urlopen(link).read()
    url = response.json()
    url = url.get('annotations')
    #print url
    annotation = sorted(url, key=lambda k: k[0], reverse=False)
    print len(annotation)
    print annotation
    motiflist = MotifList.objects.all()
    for i in range(len(annotation)):
        motiflist = MotifList.objects.all()
        for motiflist in motiflist:            
            if motiflist.MotifName[5:] == annotation[i][0]:
                motiflist.Annotation = annotation[i][1]                  
                motiflist.save()
                

    
