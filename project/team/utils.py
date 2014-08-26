from difflib import get_close_matches
from core.models import Competition
from registration.models import Participant
from team.models import MemberApplication
from velo.utils import load_class



def match_participant_to_applied(participant):
    results = participant.result_set.all()
    for result in results:
        ma = MemberApplication.objects.filter(competition=result.competition, participant=None, member__slug=participant.slug)
        if ma:
            ma1 = ma.get()
            ma1.participant = participant
            ma1.save()
            participant.team = ma1.member.team
            participant.save()
            # Recalculate points
            class_ = load_class(result.competition.processing_class)
            _competition_class = class_(result.competition.id)
            _competition_class.recalculate_team_result(team=ma1.member.team)

# TODO: Rebuild this
def match_applied_to_participants(competition_id, update_participant_team=False):
    competition = Competition.objects.get(id=competition_id)
    ms = MemberApplication.objects.filter(competition=competition, participant=None)
    ids = competition.get_ids()
    slugs = {distance.id: [obj.slug for obj in Participant.objects.filter(competition_id=ids, distance=distance)] for
             distance in competition.get_distances().filter(can_have_teams=True)}
    for m in ms:
        slug = m.member.slug
        m.participant_potential = None
        m.participant_unpaid = None
        participants = Participant.objects.filter(competition_id__in=ids, slug=slug, is_participating=True,
                                                  distance=m.member.team.distance)
        if participants:
            participant = participants[0]
            m.participant = participant
            if update_participant_team:
                participant.team = m.member.team
                participant.save()
            m.save()
        else:
            participants = Participant.objects.filter(competition_id__in=ids, slug=slug,
                                                      distance=m.member.team.distance).order_by('-id')
            if participants:
                m.participant_unpaid = participants[0]
            else:
                matches = get_close_matches(slug, slugs.get(m.member.team.distance_id), 1, 0.5)
                if matches:
                    participants = Participant.objects.filter(competition_id__in=ids, slug=matches[0],
                                          distance=m.member.team.distance).order_by('-id')
                    if participants:
                        m.participant_potential = participants[0]
            m.save()