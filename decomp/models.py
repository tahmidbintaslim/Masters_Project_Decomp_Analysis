import os
import datetime
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings

# Declare tables/models here

# New decomposition experiment details
class Experiment(models.Model):
    experimentName = models.TextField(max_length=128, unique=True)
    description = models.TextField(null=True)
    resultId = models.TextField()
    fileNames = models.TextField()
    pca = models.TextField(null=True)
    hclus = models.TextField(null=True)
    heatmap = models.TextField(null=True)
    
    def __unicode__(self):
        return self.experimentName

# Sample files detail    
class FileDetail(models.Model):
    experimentName = models.ForeignKey(Experiment)
    resultId = models.TextField()
    fileName = models.TextField()
    category = models.TextField(null=True)
    
    def __str__(self):
        return self.fileName

# Available motif in sample and their differential prevalence details   
class MotifList(models.Model):
    MotifName = models.TextField()
    experimentName = models.ForeignKey(Experiment)
    MotifId = models.IntegerField(default=1)
    Annotation = models.TextField(null=True) 
    z_score= models.FloatField(null=True)
    t_value= models.FloatField(null=True)
    p_value= models.FloatField(null=True)
    q_value= models.FloatField(null=True)
    
    def __unicode__(self):
        return self.MotifName

# Motifs and their prevalence values   
class AlphaTable(models.Model):
    mass2motif = models.ForeignKey(MotifList)
    fileName = models.ForeignKey(FileDetail)
    value = models.FloatField()        