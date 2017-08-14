import os
import datetime
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings

class MotifSetList(models.Model):
    motifset = models.TextField(max_length=128, unique=True,default=1)
       
    def __str__(self):
        return self.motifset

    
class Experiment(models.Model):
    experimentName = models.TextField(max_length=128, unique=True)
    description = models.TextField(null=True)
    resultId = models.TextField()
    fileNames = models.TextField()
    motifset = models.ForeignKey(MotifSetList,default=1)
    pca = models.TextField(null=True)
    hclus = models.TextField(null=True)
    heatmap = models.TextField(null=True)
    
    def __unicode__(self):
        return self.experimentName
    
class FileDetail(models.Model):
    experimentName = models.ForeignKey(Experiment)
    resultId = models.TextField()
    fileName = models.TextField()
    category = models.TextField(null=True)
    motif_count = models.IntegerField(null=True, default=300)

    def __str__(self):
        return self.fileName
    
class MotifList(models.Model):
    MotifName = models.TextField()
    experimentName = models.ForeignKey(Experiment)
    MotifId = models.IntegerField(default=1)
    Annotation = models.TextField(null=True) 
    z_score= models.FloatField(null=True)
    t_value= models.FloatField(null=True)
    p_value= models.FloatField(null=True)
    
    def __unicode__(self):
        return self.MotifName
    
class AlphaTable(models.Model):
    mass2motif = models.ForeignKey(MotifList)
    fileName = models.ForeignKey(FileDetail)
    value = models.FloatField()        