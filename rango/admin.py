from django.contrib import admin
from rango.models import Experiment,FileDetail,MotifList,AlphaTable,MotifSetList


admin.site.register(Experiment)
admin.site.register(FileDetail)
admin.site.register(MotifList)
admin.site.register(AlphaTable)
admin.site.register(MotifSetList)


# Register your models here.
