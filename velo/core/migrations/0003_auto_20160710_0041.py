from django.contrib.auth.management import create_permissions
from django.db import migrations
from django.conf import settings
from django.core import serializers
from django.contrib.contenttypes.management import update_contenttypes


def run_sqls(apps, schema_editor):
    User = apps.get_model("core", "User")
    Site = apps.get_model("sites", "Site")

    user, created = User.objects.get_or_create(id=1, defaults={
        'is_superuser': True,
        'is_staff': True,
        'email': 'admin@example.com',
        'password': 'pbkdf2_sha256$24000$56ZHqaQzkzUq$B+DN4PcV/0w7Hf83OuQP3ZjLeNGf2vgGArYBI4KXui0=',
    })
    user.emailaddress_set.get_or_create(email="admin@example.com", defaults={"verified": True, "primary": True})

    site = Site.objects.get(id=settings.SITE_ID)

    site.socialapp_set.get_or_create(provider="facebook", defaults={
        "name": "Facebook",
        "client_id": "175838825855542",
    })
    site.socialapp_set.get_or_create(provider="twitter", defaults={
        "name": "Twitter",
        "client_id": "KOd36nFdR0LSCQCm9EqOBQ",
    })
    site.socialapp_set.get_or_create(provider="draugiem", defaults={
        "name": "Draugiem",
        "client_id": "15007685",
    })

    for _ in ['advert', 'core', 'registration', 'staticpage', 'supporter', 'team', 'gallery', 'news']:
        app = apps.get_app_config(_)
        app.models_module = app.models_module or True
        update_contenttypes(app)
        create_permissions(app)

    with open("fixtures/group.json", 'rb') as fixture:
        objects = serializers.deserialize('json', fixture, ignorenonexistent=True)
        for obj in objects:
            obj.save()

    with open("fixtures/sitetree.json", 'rb') as fixture:
        objects = serializers.deserialize('json', fixture, ignorenonexistent=True)
        for obj in objects:
            obj.save()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20160707_0709'),
        ('sites', '0002_set_site_domain_and_name'),
        ('socialaccount', '0003_extra_data_default_dict'),
        ('marketing', '__first__'),
        ('supporter', '__first__'),
        ('contenttypes', '__first__'),
        ('registration', '__first__'),
        ('staticpage', '__first__'),
        ('supporter', '__first__'),
        ('team', '__first__'),
        ('gallery', '__first__'),
        ('news', '__first__'),
    ]

    operations = [
        migrations.RunPython(run_sqls),
    ]
