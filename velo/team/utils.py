from difflib import get_close_matches
from velo.core.models import Competition
from velo.registration.models import Participant
from velo.team.models import MemberApplication
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
