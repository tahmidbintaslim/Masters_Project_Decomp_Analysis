import os
import datetime
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings

class Experiment(models.Model):
    experimentName = models.TextField(max_length=128, unique=True)
    resultId = models.TextField()
    category = models.TextField()
    pca = models.TextField(null=True)
    hclus = models.TextField(null=True)
    
    def __str__(self):
        return self.experimentName
    
class FileDetail(models.Model):
    experimentName = models.ForeignKey(Experiment)  
    fileName = models.TextField()
    category = models.TextField()
    motif_count = models.IntegerField(null=True, default=300)

    def __str__(self):
        return self.fileName
    
class MotifList(models.Model):
    MotifName = models.TextField()
    experimentName = models.ForeignKey(Experiment)
    MotifId = models.IntegerField(default=1)
    #metadata = models.CharField(max_length=1024 * 1024, null=True)
    
    def __unicode__(self):
        return self.MotifName
    
class AlphaTable(models.Model):
    mass2motif = models.ForeignKey(MotifList)
    fileName = models.ForeignKey(FileDetail)
    value = models.FloatField()        