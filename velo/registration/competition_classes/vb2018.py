from difflib import get_close_matches
from io import BytesIO

from django.utils.translation import activate
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from velo.core.pdf import fill_page_with_image, _baseFontNameB
from velo.registration.competition_classes import VB2017
from velo.registration.models import Participant, ChangedName, UCICategory, PreNumberAssign
from velo.results.models import Result, HelperResults
from velo.team.models import Team, Member


class VB2018(VB2017):
    SOSEJAS_DISTANCE_ID = 89
    MTB_DISTANCE_ID = 90
    TAUTAS_DISTANCE_ID = 91
    RETRO_DISTANCE_ID = 92
    competition_index = 1

    @property
    def groups(self):
        """
        Returns defined groups for each competition type.
        """
        return {
            self.SOSEJAS_DISTANCE_ID: ('W-18', 'M-18', 'M CFA', 'M-Elite', 'W', 'M-35', 'M-45', 'M-55', 'M-65'),
            self.MTB_DISTANCE_ID: ('MTB W-18', 'MTB M-18', 'MTB M', 'MTB W', 'MTB M-35', 'MTB M-45', 'MTB M-55', 'MTB M-65', ),
            self.TAUTAS_DISTANCE_ID: ('T M', 'T W', )
        }

    def _update_year(self, year):
        return year + 4


    def number_pdf(self, participant_id):
        participant = Participant.objects.get(id=participant_id)
        activate(participant.application.language if participant.application else 'lv')
        output = BytesIO()

        c = canvas.Canvas(output, pagesize=A4)
        fill_page_with_image("velo/media/competition/vestule/VB2018.jpg", c)

        c.setFont(_baseFontNameB, 18)
        c.drawString(9.0*cm, 21.85*cm, "%s %s" % (participant.full_name.upper(), participant.birthday.year))
        c.drawString(6.4*cm, 19.6*cm, str(participant.distance))

        if participant.primary_number:
            c.setFont(_baseFontNameB, 35)
            c.drawString(16.5*cm, 20.6*cm, str(participant.primary_number))
        else:
            c.setFont(_baseFontNameB, 25)
            c.drawString(16.5*cm, 20.6*cm, "-")

        c.showPage()
        c.save()
        output.seek(0)
        return output

    def create_helper_results(self, participants):
        prev_competition = self.competition.get_previous_sibling()
        prev_prev_competition = prev_competition.get_previous_sibling()

        prev_slugs_road = [obj.participant.slug for obj in Result.objects.filter(competition=prev_competition, participant__distance__kind='V').select_related('participant')]
        prev_slugs_mtb = [obj.participant.slug for obj in Result.objects.filter(competition=prev_competition, participant__distance__kind='S').select_related('participant')]
        prev_slugs_tauta = [obj.participant.slug for obj in Result.objects.filter(competition=prev_competition, participant__distance__kind='T').select_related('participant')]
        prev_slugs_retro = [obj.slug for obj in Participant.objects.filter(competition=prev_competition, distance__kind='R', is_participating=True)]

        for participant in participants:
            competition_use = prev_competition
            changed = ChangedName.objects.filter(new_slug=participant.slug)
            if participant.slug in prev_slugs_retro or (changed and changed[0].slug in prev_slugs_retro):
                competition_use = prev_prev_competition

            results = Result.objects.filter(competition=competition_use, participant__slug=participant.slug, participant__distance__kind=participant.distance.kind).order_by('time')

            if not results:
                try:
                    changed = ChangedName.objects.get(new_slug=participant.slug)
                    results = Result.objects.filter(competition=competition_use, participant__slug=changed.slug, participant__distance__kind=participant.distance.kind).order_by('time')
                except:
                    pass

            helper, created = HelperResults.objects.get_or_create(competition=self.competition, participant=participant)

            if participant.distance_id not in (self.SOSEJAS_DISTANCE_ID, self.MTB_DISTANCE_ID, self.TAUTAS_DISTANCE_ID):
                continue

            if helper.is_manual:
                continue # We do not want to overwrite manually created records

            if results:
                result = results[0]
                helper.calculated_total = result.result_distance
                helper.result_used = result
            else:
                helper.calculated_total = None
                matches = None
                if participant.distance_id == self.SOSEJAS_DISTANCE_ID:
                    matches = get_close_matches(participant.slug, prev_slugs_road, 1, 0.8)
                elif participant.distance_id == self.MTB_DISTANCE_ID:
                    matches = get_close_matches(participant.slug, prev_slugs_mtb, 1, 0.8)
                elif participant.distance_id == self.TAUTAS_DISTANCE_ID:
                    matches = get_close_matches(participant.slug, prev_slugs_tauta, 1, 0.8)

                if matches:
                    helper.matches_slug = matches[0]

            helper.save()

    def pre_competition_run(self):
        t = Team.objects.filter(distance__competition=self.competition)
        members = Member.objects.filter(team__in=t)
        for member in members:
            try:
                p = Participant.objects.get(slug=member.slug, is_participating=True, distance=member.team.distance)
                if p.team_name != member.team.title:
                    print("%i %s %s %s" % (p.id, p.slug, p.team_name, member.team.title))
                    p.team_name = member.team.title
                    p.save()
            except:
                print('Not %s' % member.slug)

        uci = UCICategory.objects.filter(group='Juniori')
        for u in uci:
            x = Participant.objects.filter(is_participating=True, competition_id=self.competition_id, slug__icontains=u.slug, group__in=('MTB W-18', 'MTB M-18'))
            if x:
                PreNumberAssign.objects.get_or_create(competition=self.competition, distance=x[0].distance, participant_slug=x[0].slug, description="UCI Juniors", segment=1 if x[0].gender == 'M' else 2)

