from django.contrib import admin
from velo.registration.models import UCICategory


class UCICategoryAdmin(admin.ModelAdmin):
    list_display = ('category', 'first_name', 'last_name', 'issued', 'code', 'birthday', 'valid_until')
    list_filter = ('category', 'issued', 'valid_until')
    search_fields = ['code', 'first_name', 'last_name']


admin.site.register(UCICategory, UCICategoryAdmin)
