# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.core.mail import send_mail
from django.conf import settings
from django.core.files.base import ContentFile

import celery

from velo.core.models import User
from velo.core.tasks import LogErrorsTask
from velo.manager.models import TempDocument
from velo.manager.pdfreports import PDFReports
from velo.registration.models import Participant
from velo.velo.utils import load_class


@celery.task
def update_results_for_result(result):
    """
    Full result recalculation in case points have changed for participant.
    """
    class_ = load_class(result.competition.processing_class)
    competition_class = class_(competition=result.competition)
    updated = result.set_all()
    if updated:
        print('points have been updated.')
        result.save()
        competition_class.assign_result_place()
        competition_class.recalculate_standing_for_result(result)
        competition_class.assign_standing_places()

        if result.participant.team:
            competition_class.recalculate_team_result(team=result.participant.team)


@celery.task
def update_results_for_participant(participant_id):
    """
    Full result recalculation in case points have changed for participant.
    """
    participant = Participant.objects.get(id=participant_id)
    results = participant.result_set.all()
    for result in results:
        update_results_for_result(result)



@celery.task(base=LogErrorsTask)
def generate_pdfreport(competition_id, action, user_id):
    user = User.objects.get(id=user_id)
    pdf_class = PDFReports(competition_id=competition_id)

    if action == 'results_groups':
        pdf_class.results_groups()
    elif action == 'results_groups_top20':
        pdf_class.results_groups(20)
    elif action == 'results_gender':
        pdf_class.results_gender()
    elif action == 'results_distance':
        pdf_class.results_distance()
    elif action == 'results_distance_top20':
        pdf_class.results_distance(20)
    elif action == 'results_standings':
        pdf_class.results_standings()
    elif action == 'results_standings_top20':
        pdf_class.results_standings(20)
    elif action == 'results_standings_groups':
        pdf_class.results_standings_groups()
    elif action == 'results_standings_groups_top20':
        pdf_class.results_standings_groups(20)
    elif action == 'results_standings_gender':
        pdf_class.results_standings_gender()
    elif action == 'results_team':
        pdf_class.results_team()
    elif action == 'results_team_standings':
        pdf_class.results_team_standings()

    elif action == 'RM_results_distance':
        pdf_class.RM_results_distance()
    elif action == 'RM_results_groups':
        pdf_class.RM_results_groups()
    elif action == 'RM_results_distance_top20':
        pdf_class.RM_results_distance(20)
    elif action == 'RM_results_groups_top20':
        pdf_class.RM_results_groups(20)
    elif action == 'RM_results_gender':
        pdf_class.RM_results_gender()
    elif action == 'RM_results_team':
        pdf_class.RM_results_team()

    file_obj = pdf_class.build()

    obj = TempDocument(created_by=user)
    obj.doc.save("%s.pdf" % action, ContentFile(file_obj.read()))
    obj.save()
    file_obj.close()

    send_mail(subject='PDF atskaite %s' % action,
              message='Atskaite atrodama šeit: {0}{1}'.format(settings.MY_DEFAULT_DOMAIN, obj.doc.url),
              from_email=settings.SERVER_EMAIL,
              recipient_list=[user.email, ],
              html_message='Atskaite atrodama šeit: <a href="{0}{1}">{0}{1}</a>'.format(settings.MY_DEFAULT_DOMAIN, obj.doc.url))

    return True
