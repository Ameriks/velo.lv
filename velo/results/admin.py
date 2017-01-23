from django.contrib import admin

from velo.results.models import DistanceAdmin


class DistanceModelAdmin(admin.ModelAdmin):
    list_filter = ('competition', )
    list_display = ('__str__', 'competition', 'distance', 'zero', 'distance_actual')


admin.site.register(DistanceAdmin, DistanceModelAdmin)
