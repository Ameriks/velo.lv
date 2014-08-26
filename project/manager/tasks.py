import celery
from django.conf import settings
from django.core.mail import send_mail
from legacy.utils import full_sync
from registration.models import Participant
from velo.utils import load_class


@celery.task
def legacy_sync(email):
    full_sync()
    send_mail("Finished sync", "Finished synchronisation", settings.SERVER_EMAIL, [email,],)



@celery.task
def update_results_for_result(result):
    """
    Full result recalculation in case points have changed for participant.
    """
    class_ = load_class(result.competition.processing_class)
    competition_class = class_(competition=result.competition)
    updated = result.set_all()
    if updated:
        print 'points have been updated.'
        result.save()
        competition_class.assign_distance_number()
        competition_class.assign_group_number()
        competition_class.recalculate_standing_for_result(result)
        competition_class.assign_distance_and_group_places()

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