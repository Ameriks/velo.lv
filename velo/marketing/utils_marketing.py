from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.db.models import Count

from io import BytesIO
import csv

from velo.manager.models import TempDocument
from velo.registration.models import Participant, Application


def create_csv_seb(user=None):
    this_year_participates = set(obj.get('email') for obj in Participant.objects.filter(is_participating=True,
                                                                                        competition_id__in=(
                                                                                        38, 39, 40, 41, 42, 43, 44,
                                                                                        45)).exclude(email='').values(
        'email').annotate(c=Count('id')).order_by('-c'))
    this_year_applications = set(obj.get('email') for obj in
                                 Application.objects.filter(participant__is_participating=True, competition_id__in=(
                                 38, 39, 40, 41, 42, 43, 44, 45)).exclude(email='').values('email').annotate(
                                     c=Count('id')).order_by('-c'))
    this_year = this_year_participates.union(this_year_applications)

    sec_stage_participates = set(obj.get('email') for obj in
                                 Participant.objects.filter(is_participating=True, competition_id__in=(40,)).exclude(
                                     email='').values('email').annotate(c=Count('id')).order_by('-c'))
    sec_stage_applications = set(obj.get('email') for obj in
                                 Application.objects.filter(participant__is_participating=True,
                                                            competition_id__in=(40,)).exclude(email='').values(
                                     'email').annotate(c=Count('id')).order_by('-c'))
    sec_stage = sec_stage_participates.union(sec_stage_applications)

    first_stage_participates = set(obj.get('email') for obj in
                                   Participant.objects.filter(is_participating=True, competition_id__in=(39,)).exclude(
                                       email='').exclude(email__in=sec_stage).values('email').annotate(
                                       c=Count('id')).order_by('-c'))
    first_stage_applications = set(obj.get('email') for obj in
                                   Application.objects.filter(participant__is_participating=True,
                                                              competition_id__in=(39,)).exclude(email='').exclude(
                                       email__in=sec_stage).values('email').annotate(c=Count('id')).order_by('-c'))
    not_in_second_stage = first_stage_participates.union(first_stage_applications)

    this_year_not_payed = set(obj.get('email') for obj in
                              Participant.objects.filter(is_participating=False, competition_id__in=(40,)).exclude(
                                  email='').exclude(email__in=not_in_second_stage).values('email').annotate(
                                  c=Count('id')).order_by('-c'))

    last_year_participates = set(obj.get('email') for obj in Participant.objects.filter(
        competition_id__in=(25, 26, 27, 28, 29, 30, 31, 32)).exclude(email='').exclude(email__in=this_year).exclude(
        email__in=this_year_not_payed).values('email').annotate(c=Count('id')).order_by('-c'))
    last_year_applications = set(obj.get('email') for obj in Application.objects.filter(
        competition_id__in=(25, 26, 27, 28, 29, 30, 31, 32)).exclude(email='').exclude(email__in=this_year).exclude(
        email__in=this_year_not_payed).values('email').annotate(c=Count('id')).order_by('-c'))
    last_year = last_year_participates.union(last_year_applications)

    # previously = set(obj.get('participant_email') for obj in Ev68RVeloParticipations.objects.filter(
    #     competition_id__in=(12, 13, 14, 15, 16, 17, 18, 27, 28, 29, 30, 31, 32, 33, 34)).exclude(
    #     participant_email='').exclude(participant_email__in=this_year).exclude(
    #     participant_email__in=this_year_not_payed).exclude(participant_email__in=last_year).values(
    #     'participant_email').annotate(c=Count('id')).order_by('-c'))

    file_obj = BytesIO()
    wrt = csv.writer(file_obj)
    wrt.writerow(['Email'])
    for email in this_year:
        wrt.writerow([email.encode('utf-8')])
    file_obj.seek(0)
    obj = TempDocument(created_by=user)
    obj.doc.save("this_year.csv", ContentFile(file_obj.read()))
    obj.save()
    file_obj.close()

    file_obj = BytesIO()
    wrt = csv.writer(file_obj)
    wrt.writerow(['Email'])
    for email in this_year_not_payed:
        wrt.writerow([email.encode('utf-8')])
    file_obj.seek(0)
    obj1 = TempDocument(created_by=user)
    obj1.doc.save("this_year_not_payed.csv", ContentFile(file_obj.read()))
    obj1.save()
    file_obj.close()

    file_obj = BytesIO()
    wrt = csv.writer(file_obj)
    wrt.writerow(['Email'])
    for email in last_year:
        wrt.writerow([email.encode('utf-8')])
    file_obj.seek(0)
    obj2 = TempDocument(created_by=user)
    obj2.doc.save("last_year.csv", ContentFile(file_obj.read()))
    obj2.save()
    file_obj.close()

    file_obj = BytesIO()
    wrt = csv.writer(file_obj)
    wrt.writerow(['Email'])
    for email in not_in_second_stage:
        wrt.writerow([email.encode('utf-8')])
    file_obj.seek(0)
    obj4 = TempDocument(created_by=user)
    obj4.doc.save("not_in_sec_stage.csv", ContentFile(file_obj.read()))
    obj4.save()
    file_obj.close()

    html = """this_year_not_payed: <a href="{0}{1}">{0}{1}</a><br>
last_year: <a href="{0}{2}">{0}{2}</a><br>
this_year_participates: <a href="{0}{3}">{0}{3}</a><br>
not_in_sec_stage: <a href="{0}{4}">{0}{4}</a><br>
    """.format(settings.MY_DEFAULT_DOMAIN, obj1.doc.url, obj2.doc.url,  obj.doc.url, obj4.doc.url)

    txt = """this_year_not_payed: {0}{1}
last_year: {0}{2}
this_year_participates: {0}{3}
not_in_sec_stage: {0}{4}
    """.format(settings.MY_DEFAULT_DOMAIN, obj1.doc.url, obj2.doc.url, obj.doc.url, obj4.doc.url)

    send_mail(subject='Emails for marketing',
              message=txt,
              from_email=settings.SERVER_EMAIL,
              recipient_list=[user.email, ],
              html_message=html)
