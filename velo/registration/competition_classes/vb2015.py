from io import BytesIO
from difflib import get_close_matches
from velo.registration.competition_classes.base_vb import VBCompetitionBase
from velo.registration.models import Participant, ChangedName
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from velo.core.pdf import fill_page_with_image, _baseFontName, _baseFontNameB
import os.path
from velo.results.models import Result, HelperResults


class VB2015(VBCompetitionBase):
    SOSEJAS_DISTANCE_ID = 45
    MTB_DISTANCE_ID = 46
    TAUTAS_DISTANCE_ID = 47
    competition_index = 1

    @property
    def groups(self):
        """
        Returns defined groups for each competition type.
        """
        return {
            self.SOSEJAS_DISTANCE_ID: ('W-18', 'M-16', 'M-18', 'M-Elite', 'W', 'M-35', 'M-45', 'M-55', 'M-60'),
            self.MTB_DISTANCE_ID: ('MTB W-18', 'MTB M-16', 'MTB M-18', 'MTB M-Elite', 'MTB W', 'MTB M-35', 'MTB M-45', 'MTB M-55', 'MTB M-65', ),
            self.TAUTAS_DISTANCE_ID: ('T M', 'T W', )
        }

    def _update_year(self, year):
        return year + 1

    def assign_group(self, distance_id, gender, birthday, participant=None):
        year = birthday.year
        if distance_id not in (self.SOSEJAS_DISTANCE_ID, self.MTB_DISTANCE_ID, self.TAUTAS_DISTANCE_ID):
            return ''
        elif distance_id == self.SOSEJAS_DISTANCE_ID:
            if gender == 'M':
                if self._update_year(1999) >= year >= self._update_year(1998):
                    return 'M-16'
                elif self._update_year(1997) >= year >= self._update_year(1996):
                    return 'M-18'
                elif self._update_year(1995) >= year >= self._update_year(1980):
                    return 'M-Elite'
                elif self._update_year(1979) >= year >= self._update_year(1970):
                    return 'M-35'
                elif self._update_year(1969) >= year >= self._update_year(1960):
                    return 'M-45'
                elif self._update_year(1959) >= year >= self._update_year(1950):
                    return 'M-55'
                elif year <= self._update_year(1949):
                    return 'M-60'
            else:
                if self._update_year(1999) >= year >= self._update_year(1996):
                    return 'W-18'
                elif year <= self._update_year(1995):
                    return 'W'
        elif distance_id == self.MTB_DISTANCE_ID:
            if gender == 'M':
                if self._update_year(2002) >= year >= self._update_year(1998):
                    return 'MTB M-16'
                elif self._update_year(1997) >= year >= self._update_year(1996):
                    return 'MTB M-18'
                elif self._update_year(1995) >= year >= self._update_year(1980):
                    return 'MTB M-Elite'
                elif self._update_year(1979) >= year >= self._update_year(1970):
                    return 'MTB M-35'
                elif self._update_year(1969) >= year >= self._update_year(1960):
                    return 'MTB M-45'
                elif self._update_year(1959) >= year >= self._update_year(1950):
                    return 'MTB M-55'
                elif year <= self._update_year(1949):
                    return 'MTB M-65'
            else:
                if self._update_year(2001) >= year >= self._update_year(1996):
                    return 'MTB W-18'
                elif year <= self._update_year(1995):
                    return 'MTB W'
        elif distance_id == self.TAUTAS_DISTANCE_ID:
            if gender == 'M':
                return 'T M'
            else:
                return 'T W'

        print('here I shouldnt be...')
        raise Exception('Invalid group assigning. {0} {1} {2}'.format(gender, distance_id, birthday))


    def number_pdf(self, participant_id):
        participant = Participant.objects.get(id=participant_id)
        output = BytesIO()

        c = canvas.Canvas(output, pagesize=A4)
        fill_page_with_image("velo/media/competition/vestule/VBm_2015_vestule_ar_tekstu.jpg", c)

        c.setFont(_baseFontNameB, 18)
        c.drawString(5.5*cm, 20.05*cm, "%s %s" % (participant.full_name.upper(), participant.birthday.year))
        c.drawString(4.2*cm, 18.05*cm, str(participant.distance))


        if participant.primary_number:
            c.setFont(_baseFontNameB, 35)
            c.drawString(15*cm, 18.5*cm, str(participant.primary_number))
        # elif participant.distance_id == self.GIMENU_DISTANCE_ID:
        #     c.setFont(_baseFontNameB, 25)
        #     c.drawString(15*cm, 18.5*cm, "Amway")
        else:
            c.setFont(_baseFontNameB, 25)
            c.drawString(15*cm, 19*cm, "-")

        c.showPage()
        c.save()
        output.seek(0)
        return output

    def generate_diploma(self, result):
        output = BytesIO()
        path = 'velo/results/files/diplomas/%i/%i.jpg' % (self.competition_id, result.participant.distance_id)

        if not os.path.isfile(path):
            raise Exception

        c = canvas.Canvas(output, pagesize=A4)

        fill_page_with_image(path, c)

        c.setFont(_baseFontNameB, 35)
        c.drawCentredString(c._pagesize[0] / 2, 16.3*cm, result.participant.full_name)
        c.setFont(_baseFontName, 25)
        c.drawCentredString(c._pagesize[0] / 2, 15*cm, "%i.vieta" % result.result_distance)
        c.setFont(_baseFontName, 18)
        c.drawCentredString(c._pagesize[0] / 2, 14*cm, "Laiks: %s" % result.time.replace(microsecond=0))
        c.drawCentredString(c._pagesize[0] / 2, 13*cm, "Vidējais ātrums: %s km/h" % result.avg_speed)

        c.showPage()
        c.save()
        output.seek(0)
        return output

    def create_helper_results(self, participants):
        prev_competition = self.competition.get_previous_sibling()

        prev_slugs_road = [obj.participant.slug for obj in Result.objects.filter(competition=prev_competition, participant__distance__kind='V').select_related('participant')]
        prev_slugs_mtb = [obj.participant.slug for obj in Result.objects.filter(competition=prev_competition, participant__distance__kind='S').select_related('participant')]
        prev_slugs_tauta = [obj.participant.slug for obj in Result.objects.filter(competition=prev_competition, participant__distance__kind='T').select_related('participant')]

        for participant in participants:
            results = Result.objects.filter(competition=prev_competition, participant__slug=participant.slug, participant__distance__kind=participant.distance.kind).order_by('time')

            if not results:
                try:
                    changed = ChangedName.objects.get(new_slug=participant.slug)
                    results = Result.objects.filter(competition=prev_competition, participant__slug=changed.slug, participant__distance__kind=participant.distance.kind).order_by('time')
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

    def assign_numbers_special_additional(self):
        # Assign number for women in teams.

        queryset = self.competition.participant_set.filter(is_participating=True,
                                                        distance_id=self.TAUTAS_DISTANCE_ID,
                                                        gender='F').exclude(team_name='').extra(
            select={
                'shoseja_count': 'Select count(*) from registration_participant rp where rp.is_participating=True and distance_id= %s and rp.team_name_slug = registration_participant.team_name_slug',
                'mtb_count': 'Select count(*) from registration_participant rp where rp.is_participating=True and distance_id= %s and rp.team_name_slug = registration_participant.team_name_slug'
            },
            select_params=(self.SOSEJAS_DISTANCE_ID, self.MTB_DISTANCE_ID),
        )
        queryset = queryset.filter(helperresults__competition_id = self.competition.id)
        queryset = queryset.extra(
                select={
                    'calculated_total': 'results_helperresults.calculated_total',
                    'passage_assigned': 'results_helperresults.passage_assigned',
                    },
            ).order_by('team_name_slug', 'calculated_total', 'last_name')
        counter = {}
        total_counter = 0
        passage_info = self.passages().get(self.TAUTAS_DISTANCE_ID)[1]
        for w in queryset:
            if w.shoseja_count >= 2 and w.mtb_count >= 2:
                total_in_team = counter.get(w.team_name_slug, 0)
                if total_in_team >= 4:
                    continue
                counter.update({w.team_name_slug: (total_in_team + 1)})
                total_counter += 1
                number = self.competition.number_set.filter(distance_id=self.TAUTAS_DISTANCE_ID,
                                                            participant_slug='',
                                                            number__gte=passage_info[1],
                                                            number__lte=passage_info[2])[0]
                number.participant_slug = w.slug
                number.save()

                w.primary_number = number
                w.save()

                print("%s, %i, %s, %s, %s, %s" % (number, w.id, w.calculated_total, w.last_name, w.first_name, w.team_name))

        return {2: total_counter}
