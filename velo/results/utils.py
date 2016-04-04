from difflib import get_close_matches
from registration.models import Participant
from results.models import LegacyResult


def map_participants_with_legacy_results():
    LegacyResult.objects.filter(competition_id=16).update(participant_2014=None)
    old_ids = {
        32: 21,
        33: 23,
        34: 22
    }
    for participant in Participant.objects.filter(is_participating=True, competition_id=35):
        competition_id = 16
        distance_id = old_ids.get(participant.distance_id)
        LegacyResult.objects.filter(slug=participant.slug, competition_id=competition_id, distance_id=distance_id).update(participant_2014=participant)


def map_participants_with_legacy_results_potential():
    LegacyResult.objects.filter(competition_id=16).update(participant_2014_could_be=None, participant_2014_could_be2=None)
    distance_ids = [32, 33, 34]
    old_ids = {
        32: 21,
        33: 23,
        34: 22
    }
    old_competition_id = 16
    for distance_id in distance_ids:
        old_distance_id = old_ids.get(distance_id)

        participants = Participant.objects.filter(legacyresult__id=None, is_participating=True, distance_id=distance_id)
        global_slugs = [obj.slug for obj in LegacyResult.objects.filter(competition_id=old_competition_id, distance_id=old_distance_id, participant_2014=None)]
        for participant in participants:
            slugs = [obj.slug for obj in LegacyResult.objects.filter(competition_id=old_competition_id, distance_id=old_distance_id, participant_2014=None, year=participant.birthday.year)]
            print participant.slug
            matches = get_close_matches(participant.slug, slugs)
            matches2 = get_close_matches(participant.slug, global_slugs)
            if matches:
                LegacyResult.objects.filter(competition_id=old_competition_id, distance_id=old_distance_id, participant_2014=None, year=participant.birthday.year, slug=matches[0]).update(participant_2014_could_be=participant)
            if matches2:
                LegacyResult.objects.filter(competition_id=old_competition_id, distance_id=old_distance_id, participant_2014=None, slug=matches2[0]).update(participant_2014_could_be2=participant)

