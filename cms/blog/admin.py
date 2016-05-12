from django.contrib import admin
from feincms.admin import item_editor

from cms.blog.models import BlogEntry



class EntryAdmin(item_editor.ItemEditor):

    model = BlogEntry

    ordering = ['-published_on']
    list_display = ['title', 'published', 'published_on']
    list_filter = ['published']
    search_fields = ['title', 'slug']

    prepopulated_fields = {
        'slug': ('title',)
    }

    raw_id_fields = []

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(BlogEntry, EntryAdmin)
