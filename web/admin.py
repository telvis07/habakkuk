from django.contrib import admin
from web.models import ClusterData, BibleText

class BibleTextAdmin(admin.ModelAdmin):
    fields = (('verse_id', 'bibleverse', 'translation'), 'text')
    list_display = ('verse_id', 'bibleverse', 'translation', )
    ordering = ('verse_id',)

admin.site.register(ClusterData)
admin.site.register(BibleText, BibleTextAdmin)
