from decomp.models import Experiment,FileDetail,MotifList,AlphaTable
from urllib import urlopen
from django.views.generic import TemplateView
import simplejson as json
import numpy as np
import requests

def populateExperiment(experimentName,description,resultId,filename): 
    if '\r\n' in resultId and '\r\n' in filename:
        experiment = Experiment.objects.get_or_create(experimentName = experimentName, description=description,
                                                  resultId = resultId,fileNames = filename)
        return True  
    else:
        return False

def populateFileDetail(experimentName,resultId,filename):
        experiment = Experiment.objects.get(experimentName=experimentName)
        res_id = str(experiment.resultId).split('\r\n') 
        filename = str(experiment.fileNames).split('\r\n')
        for res_id,filename in zip(res_id,filename):
            FileDetail.objects.create(experimentName = experiment,resultId= res_id, fileName = filename)
                
def populateMotifList(experimentName):
            experiment = Experiment.objects.get(experimentName=experimentName)

            file = FileDetail.objects.filter(experimentName=experiment)
            index =1
            alpha_value = []
            link ='http://ms2lda.org/decomposition/api/batch_results/{}'.format(file[0].resultId)
            if urlopen(link).getcode() is not 200:
                experiments.delete()
                file.delete()
                return False
            else:
                raw_data = urlopen(link).read()
                url = json.loads(raw_data)            
                url1 = url.get('alpha')
                url2 = url.get('motifset')
                #print url2
                alpha_value = sorted(url1, key=lambda k: k[0], reverse=False)
                motif_list = np.transpose(np.array(alpha_value))[0]
                #print alpha_value
                index =0
                for i in range(len(motif_list)):    
                      MotifList.objects.create(MotifName = motif_list[i],experimentName = experiment,MotifId=i)
                loadAnnotation(experiment,url2)
                return True
        
def populateAlphaMatrix(experimentName):
        experiment = Experiment.objects.get(experimentName = experimentName)
    #for experiment in experiment:
        file = FileDetail.objects.filter(experimentName = experiment)
        Motiflist = MotifList.objects.filter(experimentName = experiment)        
        alpha_value = []
        alpha_values = np.zeros((len(file),len(Motiflist)),np.float)
        #print len(Motiflist)
        for file in file:           
            index =1
            link ='http://ms2lda.org/decomposition/api/batch_results/{}'.format(file.resultId)
            raw_data = urlopen(link).read()
            url = json.loads(raw_data)
            url = url.get('alpha')
            alpha_value = sorted(url, key=lambda k: k[0], reverse=False)   
            for motif,i in zip(Motiflist,range(len(Motiflist))):
                #print i 
                alp = AlphaTable.objects.get_or_create(mass2motif = motif,
                                         fileName = file, value = alpha_value[i][index])
                           
    
def loadAnnotation(experimentName,motifset):
    print "hello"
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
    #print len(annotation)
    print annotation
    experiment = Experiment.objects.get(experimentName = experimentName)   
    print experiment
    for i in range(len(annotation)):
        motiflist = MotifList.objects.filter(experimentName = experiment)
        print motiflist
        for m in motiflist:  
            print m.MotifName
            if m.MotifName == annotation[i][0]:
                m.Annotation = annotation[i][1]                  
                m.save()
                

    
