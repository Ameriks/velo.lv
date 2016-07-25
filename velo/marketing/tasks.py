import requests
from django.conf import settings
from celery.task import task
from velo.core.tasks import LogErrorsTask
from bs4 import BeautifulSoup
import re
import os
import shutil
from premailer import transform


@task(base=LogErrorsTask)
def subscribe(email):
    resp = requests.post("https://sendy.velo.lv/subscribe", data={
        "email": email,
        "list": settings.MAIN_LIST_ID,
        "boolean": True,
    })
    print(resp.content)


@task(base=LogErrorsTask)
def copy_mc_template(template_id: int, subject: str):
    resp = requests.post("https://%s/login/post" % settings.MC_URL, data={
        "username": settings.MC_USER,
        "password": settings.MC_PASSWORD,
        "enc": "1",
        "user_id": settings.MC_USERID,
    })
    resp2 = requests.get("https://%s/templates/export-template?id=%s" % (settings.MC_URL, template_id), cookies=resp.cookies)

    template_html = resp2.text
    template_html = re.sub(r'/\*@editable\*/', '', template_html)  #  remove "Editable" comment
    template_html = re.sub("(<!--.*?-->)", "", template_html)
    template_html = re.sub(r'\s*/\*[^\*]*\*/\s*', '\n', template_html, flags=re.M)
    template_html = re.sub(r'mc:\w*="\w*"', '', template_html)
    template_html = re.sub(r'mc:\w*', '', template_html)
    template_html = re.sub(r'\*\|LIST:DESCRIPTION\|\*', '', template_html)
    template_html = re.sub(r'\*\|HTML:LIST_ADDRESS_HTML\|\*', '', template_html)
    template_html = re.sub(r'\*\|HTML:REWARDS\|\*', '', template_html)

    template_html = re.sub(r'\*\|MC:SUBJECT\|\*', 'velo.lv', template_html)  # todo: Change to subject

    template_html = re.sub(r'\*\|CURRENT_YEAR\|\*', '[currentyear]', template_html)
    template_html = re.sub(r'\*\|LIST:COMPANY\|\*', 'Igo Japiņa sporta aģentūra', template_html)
    template_html = re.sub(r'\*\|TWITTER:PROFILEURL\|\*', 'https://twitter.com/Velolv', template_html)
    template_html = re.sub(r'\*\|FACEBOOK:PROFILEURL\|\*', 'https://www.facebook.com/velolv/', template_html)
    template_html = re.sub(r'\*\|UNSUB\|\*', '[unsubscribe]', template_html)
    template_html = re.sub(r'\*\|ARCHIVE\|\*', '[webversion]', template_html)

    template_html = re.sub(r'\*\|IFNOT:ARCHIVE_PAGE\|\*[^(\*\|)]*\*\|END:IF\|\*', '', template_html, flags=re.M)
    template_html = re.sub(r'\*\|IF:REWARDS\|\*[^(\*\|)]*\*\|END:IF\|\*', '', template_html, flags=re.M)
    template_html = re.sub(r'monkeyRewards', '', template_html)

    template_html = re.sub(r'unsubscribe from this list', 'Atrakstīties no e-pastu saņemšanas', template_html)

    # I hate those. Replace to regular quotation marks
    template_html = re.sub(r'“', '"', template_html)
    template_html = re.sub(r'”', '"', template_html)

    template_html = re.sub(r'\t', '', template_html)

    os.mkdir("/sendy/%s" % template_id)

    soup = BeautifulSoup(template_html, "lxml")
    for img in soup.find_all("img"):
        src = img.attrs.get('src')
        file_name = os.path.basename(src)
        r = requests.get(src, stream=True)
        if r.status_code == 200:
            with open("/sendy/%s/%s" % (template_id, file_name), 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        img.attrs.update({'src': 'https://sendy.velo.lv/uploads/templates/%s/%s' % (template_id, file_name)})

    for link in soup.find_all("a"):
        src = link.attrs.get('href')
        if not 'gallery.m' in src:
            continue
        file_name = os.path.basename(src)
        r = requests.get(src, stream=True)
        if r.status_code == 200:
            with open("/sendy/%s/%s" % (template_id, file_name), 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        link.attrs.update({'src': 'https://sendy.velo.lv/uploads/templates/%s/%s' % (template_id, file_name)})

    template_html = transform(str(soup))

    resp3 = requests.post("https://sendy.velo.lv/api/campaigns/create.php", data={
        "api_key": settings.SENDY_API_KEY,
        "from_name": "VELO.LV",
        "from_email": "hello@mans.velo.lv",
        "reply_to": "info@velo.lv",
        "subject": subject,
        "html_text": template_html,
        "brand_id": "1",
    })
    print(resp.content)
