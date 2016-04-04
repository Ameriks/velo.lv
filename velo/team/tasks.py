from difflib import get_close_matches
from celery.schedules import crontab
from celery.task import periodic_task, task
import datetime
from django.utils import timezone
from core.models import Competition
from registration.models import Participant
from team.models import MemberApplication


@task
def match_team_members_to_participants(competition_id, participant_id=None, participant=None):
    competition = Competition.objects.get(id=competition_id)

    if MemberApplication.objects.filter(competition=competition).count() == 0:
        return False

    if participant_id:
        participant = Participant.objects.get(id=participant_id)

    # Cleanup
    # If participant have been inactivated, then we should remove it from team as well
    members = MemberApplication.objects.filter(competition=competition, participant__is_participating=False)
    for member in members:
        member.participant.team = None
        member.participant.save()
        member.participant = None
        member.save()

    slugs = None

    members = MemberApplication.objects.filter(competition=competition, participant=None).select_related('member', 'member__team', 'member__team__distance')

    if participant:
        members = members.filter(member__slug=participant.slug)

    for member in members:
        if member.participant_unpaid and member.participant_unpaid.is_participating:
            participant = member.participant_unpaid
            member.participant = participant
            member.participant_unpaid = None
            participant.team = member.member.team
            participant.save()
            member.save()
            continue

        participants = Participant.objects.filter(competition_id__in=competition.get_ids(), slug=member.member.slug, distance=member.member.team.distance)
        participants_payed = participants.filter(is_participating=True)
        if participants_payed:
            member.participant = participants_payed[0]
            participants_payed[0].team = member.member.team
            participants_payed[0].save()
            member.participant_potential = member.participant_unpaid = None
            member.save()
        elif participants:
            member.participant_unpaid = participants[0]
            member.participant_potential = None
            member.save()
        else:
            if not slugs:
                slugs = {distance.id: [obj.slug for obj in Participant.objects.filter(competition_id=competition.get_ids(),
                                                                              distance=distance, is_participating=True)] for distance in competition.get_distances().filter(can_have_teams=True)}
            matches = get_close_matches(member.member.slug, slugs.get(member.member.team.distance_id), 1, 0.5)
            if matches:
                participants = Participant.objects.filter(competition_id__in=competition.get_ids(), slug=matches[0],
                                              distance=member.member.team.distance).order_by('-id')
                member.participant_potential = participants[0]
                member.save()


def check_participant_team_is_filled(competition_id):
    competition = Competition.objects.get(id=competition_id)

    if MemberApplication.objects.filter(competition=competition).count() == 0:
        return False

    members = MemberApplication.objects.filter(competition=competition, participant__team=None).exclude(participant=None)
    for member in members:
        member.participant.team = member.member.team
        member.participant.save()


@periodic_task(run_every=crontab(minute="4", ))
def master_match_team_members_to_participants(participant_id=None):
    competitions = Competition.objects.filter(competition_date__gte=(timezone.now() - datetime.timedelta(days=1))).exclude(participant=None)
    for competition in competitions:
        match_team_members_to_participants(competition_id=competition.id, participant_id=participant_id)
        if not participant_id:
            check_participant_team_is_filled(competition_id=competition.id)