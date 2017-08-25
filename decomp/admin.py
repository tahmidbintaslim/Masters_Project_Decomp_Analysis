from django.contrib import admin
from decomp.models import Experiment,FileDetail,MotifList,AlphaTable

# Register your models here.

admin.site.register(Experiment)
admin.site.register(FileDetail)
admin.site.register(MotifList)
admin.site.register(AlphaTable)

