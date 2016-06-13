import requests
from django.conf import settings
from celery.task import task
from velo.core.tasks import LogErrorsTask


@task(base=LogErrorsTask)
def subscribe(email):
    resp = requests.post("https://sendy.velo.lv/subscribe", data={
        "email": email,
        "list": settings.MAIN_LIST_ID,
        "boolean": True,
    })
    print(resp.content)
