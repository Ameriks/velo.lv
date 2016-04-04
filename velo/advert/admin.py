from django.contrib import admin

# Register your models here.
from advert.models import FlashBanner

class FlashBannerAdmin(admin.ModelAdmin):
    list_filter = ('competition', 'status')
    list_display = ('title', 'status', 'competition', 'location', 'ordering', 'url')


admin.site.register(FlashBanner, FlashBannerAdmin)