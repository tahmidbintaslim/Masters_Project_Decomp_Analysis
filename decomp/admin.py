from django.contrib import admin
from decomp.models import Experiment,FileDetail,MotifList,AlphaTable

# Referenced from tango with django book
# Register your models here.

admin.site.register(Experiment)
admin.site.register(FileDetail)
admin.site.register(MotifList)
admin.site.register(AlphaTable)

