from django.contrib import admin
from web.models import BibleText

class BibleTextAdmin(admin.ModelAdmin):
    fields = (('verse_id', 'bibleverse', 'translation'), 'text')
    list_display = ('verse_id', 'bibleverse', 'translation', )
    ordering = ('verse_id',)

admin.site.register(BibleText, BibleTextAdmin)
