# coding=utf-8
from __future__ import unicode_literals

from celery.task import task
import datetime
from celery.schedules import crontab
from celery.task import periodic_task
from django.conf import settings
import requests
from io import StringIO
from urllib.parse import urlencode
import uuid

from django.db.models import Count

from velo.core.models import Log, Competition
from velo.core.tasks import LogErrorsTask
from velo.marketing.models import SMS
from velo.marketing.utils import send_smses

from velo.registration.models import Number, Participant
from velo.results.models import Result, UrlSync, ChipScan
from velo.velo.utils import load_class
import traceback
from django.utils import timezone


@task(base=LogErrorsTask)
def temp_url_sync_task(urlsync_id):
    from velo.registration.competition_classes import Seb2014
    obj = UrlSync.objects.get(id=urlsync_id)
    _class = Seb2014(obj.competition.id)

    fetch_results(2)
    _class.assign_result_place()
    _class.recalculate_all_standings()
    send_smses()

    temp_url_sync_task.apply_async((urlsync_id, ), countdown=10)


@task(base=LogErrorsTask)
def send_test_sms():
    sms = {
        'page': 'message/send',
        'username': settings.SMS_USERNAME,
        'password': settings.SMS_PASSWORD,
        'destinationAddress': '37126461101',
        'text': 'tests %s' % str(uuid.uuid4()),
    }

    requests.get('%s/?%s' % (settings.SMS_GATEWAY, urlencode(sms)))
    return True



@task(base=LogErrorsTask)
def create_result_sms(result_id):
    send_out = timezone.now()
    result = Result.objects.select_related('competition', 'participant').get(id=result_id)

    #distance_result = Result.objects.filter(competition=result.competition, number__distance=result.number.distance, time__lte=result.time).exclude(time=None).exclude(participant__is_competing=False).count()
    #group_result = Result.objects.filter(competition=result.competition, participant__group=result.participant.group, time__lte=result.time).exclude(time=None).exclude(participant__is_competing=False).count()

    sms_text = result.competition.sms_text % {
        'number': result.number.number,
        'time': str(result.time.replace(microsecond=0)),
        'group_result': result.result_group,
        'group': result.participant.group,
        'distance_result': result.result_distance,
    }

    phone_numbers = result.participant.phone_number.replace('+371', '').replace(' ', '').replace('00371', '').replace('+', '')
    phone_number = phone_numbers.split(';')

    for number in phone_number:
        if len(number) == 0:
            print('NO NUMBER')
            continue
        if number[0:3] == '371':
            number = number[3:]
        if len(number) == 8 and number[0] != '2':
            print('Not sending to %s' % number)
            continue
        elif len(number) == 8:
            number = '371%s' % number

        if len(number) < 8:
            print('TOO SHORT NUMBER')
            continue
        print('Sending to %s' % number)
        print(sms_text)

        SMS.objects.create(send_out_at=send_out, phone_number=number, text=sms_text)

    return True


@task(base=LogErrorsTask)
def process_chip_result(_id):
    scan = ChipScan.objects.select_related('competition').get(id=_id)

    class_ = load_class(scan.competition.processing_class)
    processing_class = class_(scan.competition.id)

    if not scan.is_processed:
        if scan.competition.processing_class:
            processing_class.process_chip_result(scan.id)

@task(base=LogErrorsTask)
def recalculate_standing_for_result(competition_id, _id):
    competition = Competition.objects.get(id=competition_id)
    result = Result.objects.get(id=_id)

    class_ = load_class(competition.processing_class)
    processing_class = class_(competition.id)

    processing_class.recalculate_standing_for_result(result)


@task(base=LogErrorsTask)
def fetch_results(_id):
    url_data = UrlSync.objects.get(id=_id)

    processed_line = url_data.current_line

    class_ = load_class(url_data.competition.processing_class)
    processing_class = class_(url_data.competition.id)
    try:
        resp = requests.get(url_data.url)

        if resp.status_code != 200:
            return

        buf = StringIO(resp.text)
        file_lines = tuple(buf.readlines())
        lines_to_process = file_lines[processed_line:]
        for line in lines_to_process:
            print(line)
            if len(line.strip()) == 0:
                print('empty line')
                continue
            number, time_text = line.strip().split(',')
            if number == '0':
                print('skipping 0 number')
                continue
            scan, created = ChipScan.objects.get_or_create(competition=url_data.competition, nr_text=number, time_text=time_text, url_sync=url_data)
            scan.time = time_text
            try:
                scan.nr = Number.objects.get(competition_id__in=url_data.competition.get_ids(), number=number, group='')
            except:
                print('number not found')
                continue
            finally:
                scan.save()
            process_chip_result.delay(scan.id)
            # processing_class.process_chip_result(scan.id)

        url_data.current_line = len(file_lines)
        url_data.save()

        # TODO: This should be removed after process review
        processing_class.recalculate_all_standings()
        send_smses()

    except:
        error = traceback.format_exc()
        Log.objects.create(content_object=url_data, action="Error processing file", params={
            'error': error,
        })
        raise Exception('Error processing external chip file')


@task(base=LogErrorsTask)
def update_helper_result_table(competition_id, update=False, participant_id=None):
    competition = Competition.objects.get(id=competition_id)

    participants = Participant.objects.filter(competition_id__in=competition.get_ids(), is_participating=True).order_by('distance', 'registration_dt')

    if not update:
        participants = participants.extra(
            where=[
                "(Select hr1.calculated_total from results_helperresults hr1 where hr1.participant_id=registration_participant.id and hr1.competition_id = %s) is null"
            ], params=[competition_id, ],)

    if participant_id:
        participants = participants.filter(id=participant_id)

    if participants:
        class_ = load_class(competition.processing_class)
        competition_class = class_(competition=competition)

        competition_class.create_helper_results(participants)


@periodic_task(run_every=crontab(minute="2", ))
def master_update_helper_result_table(update=False, participant_id=None):
    competitions = Competition.objects.filter(competition_date__gte=(timezone.now() - datetime.timedelta(days=1)))\
        .exclude(participant=None)\
        .exclude(competition_date__lte=datetime.date.today())\
        .filter(complex_payment_enddate=None)
    for competition in competitions:
        update_helper_result_table(competition_id=competition.id, update=update, participant_id=participant_id)


@task(base=LogErrorsTask)
def merge_standings(competition_id):
    """
    Function searches for double created standings in provided competition.
    Such cases could appear if user had grammar error in his name and is fixed after standing has been created.

    This function is invoked from Participant model on save method if participant slug has been changed.

    :param competition_id: competition id that should be searched and merged
    :return: Nothing is being returned
    """
    competition = Competition.objects.get(id=competition_id)
    doubles = competition.sebstandings_set.order_by('distance', 'participant_slug').values('distance', 'participant_slug').annotate(count=Count('participant_slug')).filter(count__gt=1)

    if not doubles:
        return

    if competition.processing_class:
        class_ = load_class(competition.processing_class)
        competition_class = class_(competition=competition)

    for double in doubles:
        print(double)
        standings = list(competition.sebstandings_set.filter(distance_id=double.get('distance'), participant_slug=double.get('participant_slug')).order_by('-distance_total'))
        standing = standings.pop(0)
        for st in standings:
            for _ in range(1, 8):
                if getattr(st, "distance_points%s" % _) > getattr(standing, "distance_points%s" % _):
                    setattr(standing, "distance_points%s" % _, getattr(st, "distance_points%s" % _))
                    setattr(standing, "group_points%s" % _, getattr(st, "group_points%s" % _))
            for result in st.results:
                result.standings_object = standing
                result.save()
            st.delete()
        if competition.processing_class:
            competition_class.recalculate_standing_points(standing)
        standing.save()
