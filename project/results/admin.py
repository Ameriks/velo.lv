from django.contrib import admin

# Register your models here.
from results.models import DistanceAdmin

class DistanceModelAdmin(admin.ModelAdmin):
    list_filter = ('competition', )
    list_display = ('__unicode__', 'competition', 'distance', 'zero', 'distance_actual')


admin.site.register(DistanceAdmin, DistanceModelAdmin)
