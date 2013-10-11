from django.contrib import admin
from api.models import ClusterData

class ClusterDataAdmin(admin.ModelAdmin):
    fields = [date, range, num_cluster]

admin.site.register(ClusterData, ClusterDataAdmin)
