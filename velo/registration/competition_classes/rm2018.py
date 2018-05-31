from io import BytesIO

from django.utils.timezone import activate
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from velo.core.pdf import fill_page_with_image, _baseFontNameB
from velo.registration.competition_classes import RM2017
from velo.registration.models import Participant, PreNumberAssign, UCICategory


class RM2018(RM2017):
    SPORTA_DISTANCE_ID = 84
    TAUTAS_DISTANCE_ID = 85
    TAUTAS1_DISTANCE_ID = 88  # OUT
    GIMENU_DISTANCE_ID = 87
    BERNU_DISTANCE_ID = 86

    def _update_year(self, year):
        return year + 4

    def number_ranges(self):
        """
        Returns number ranges for each distance.
        """
        return {
            self.SPORTA_DISTANCE_ID: [{'start': 201, 'end': 400, 'group': ''}, ],
            self.TAUTAS_DISTANCE_ID: [{'start': 2001, 'end': 3700, 'group': ''}, ],
            self.GIMENU_DISTANCE_ID: [{'start': 7001, 'end': 7900, 'group': ''}, ],
        }

    @property
    def groups(self):
        """
        Returns defined groups for each competition type.
        """
        return {
            self.SPORTA_DISTANCE_ID: ('M-18', 'M', 'M-35', 'M-45', 'M-55', 'M-65', 'W'),
            self.TAUTAS_DISTANCE_ID: ('T M', 'T W', 'T M-14', 'T W-14', 'T M-16', 'T W-16', 'T M-18', 'T W-18', ),
        }

    def assign_group(self, distance_id, gender, birthday, participant=None):
        year = birthday.year
        if distance_id not in (self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID):
            return ''
        elif distance_id == self.SPORTA_DISTANCE_ID:
            if gender == 'M':
                if self._update_year(1997) >= year >= self._update_year(1996):
                    return 'M-18'
                elif self._update_year(1995) >= year >= self._update_year(1980):
                    return 'M'
                elif self._update_year(1979) >= year >= self._update_year(1970):
                    return 'M-35'
                elif self._update_year(1969) >= year >= self._update_year(1960):
                    return 'M-45'
                elif self._update_year(1959) >= year >= self._update_year(1950):
                    return 'M-55'
                elif year <= self._update_year(1949):
                    return 'M-65'
            else:
                return 'W'

        elif distance_id == self.TAUTAS_DISTANCE_ID:
            if gender == 'M':
                if self._update_year(2001) >= year >= self._update_year(2000):
                    return 'T M-14'
                elif self._update_year(1999) >= year >= self._update_year(1998):
                    return 'T M-16'
                elif self._update_year(1997) >= year >= self._update_year(1996):
                    return 'T M-18'
                elif year <= self._update_year(1995):
                    return 'T M'
            else:
                if self._update_year(2001) >= year >= self._update_year(2000):
                    return 'T W-14'
                elif self._update_year(1999) >= year >= self._update_year(1998):
                    return 'T W-16'
                elif self._update_year(1997) >= year >= self._update_year(1996):
                    return 'T W-18'
                elif year <= self._update_year(1995):
                    return 'T W'

        print('here I shouldnt be...')
        raise Exception('Invalid group assigning. {0} {1} {2}'.format(gender, distance_id, birthday))

    def passages(self):
        return {
            self.SPORTA_DISTANCE_ID: [(1, 1, 500, 0), ],
            self.TAUTAS_DISTANCE_ID: [
                                    (1, 2001, 2200, 20),
                                    (2, 2201, 2400, 20),
                                    (3, 2401, 2600, 15),
                                    (4, 2601, 2800, 10),
                                    (5, 2801, 3000, 10),
                                    (6, 3001, 3200, 10),
                                    (7, 3201, 3700, 0),
                                    ],
            self.GIMENU_DISTANCE_ID: [
                (1, 7001, 7901, 0),
            ],
        }

    def number_pdf(self, participant_id):
        # activate('lv')
        participant = Participant.objects.get(id=participant_id)
        output = BytesIO()

        c = canvas.Canvas(output, pagesize=A4)
        fill_page_with_image("velo/media/competition/vestule/RVm_2018_vestule_ar_tekstu.jpg", c)

        c.setFont(_baseFontNameB, 18)
        c.drawString(5*cm, 20.4*cm, "%s %s" % (participant.full_name.upper(), participant.birthday.year))
        c.drawString(4*cm, 18.4*cm, str(participant.distance))

        if participant.primary_number:
            c.setFont(_baseFontNameB, 35)
            c.drawString(15*cm, 19.4*cm, str(participant.primary_number))
        # elif participant.distance_id == self.GIMENU_DISTANCE_ID:
        #     c.setFont(_baseFontNameB, 25)
        #     c.drawString(14*cm, 19.4*cm, "Ģimeņu br.")
        else:
            c.setFont(_baseFontNameB, 25)
            c.drawString(15.5*cm, 19.4*cm, "-")

        c.showPage()
        c.save()
        output.seek(0)
        return output

    def assign_numbers(self, reassign=False, assign_special=False):
        # TODO: Need to find all participants that have started in sport distance and now are in other distances.
        prev_participants = [p.slug for p in Participant.objects.filter(is_participating=True, competition=self.competition, distance_id=65)]
        now_participants = Participant.objects.filter(distance_id=self.TAUTAS_DISTANCE_ID, is_participating=True, slug__in=prev_participants)
        for now in now_participants:
            try:
                PreNumberAssign.objects.get(competition=self.competition, participant_slug=now.slug)
            except:
                PreNumberAssign.objects.create(competition=self.competition, distance=now.distance, participant_slug=now.slug, segment=1)

        # All juniors in 2nd segment
        juniors = Participant.objects.filter(competition=self.competition, distance_id=self.TAUTAS_DISTANCE_ID,
                                             is_participating=True, group__in=('T M-16', )).order_by('id')
        for _ in juniors:
            if UCICategory.objects.filter(first_name__icontains=_.first_name, last_name__icontains=_.last_name):
                try:
                    PreNumberAssign.objects.get(competition=self.competition, participant_slug=_.slug)
                except:
                    PreNumberAssign.objects.create(competition=self.competition, distance=_.distance, participant_slug=_.slug, segment=2)

        # All juniors in 3rd segment
        juniors = Participant.objects.filter(competition=self.competition, distance_id=self.TAUTAS_DISTANCE_ID,
                                             is_participating=True, group__in=('T W-18', 'T W-16', 'T M-14')).order_by('id')
        for _ in juniors:
            if UCICategory.objects.filter(first_name__icontains=_.first_name, last_name__icontains=_.last_name):
                try:
                    PreNumberAssign.objects.get(competition=self.competition, participant_slug=_.slug)
                except:
                    PreNumberAssign.objects.create(competition=self.competition, distance=_.distance, participant_slug=_.slug, segment=3)

        # All juniors in 4th segment
        juniors = Participant.objects.filter(competition=self.competition, distance_id=self.TAUTAS_DISTANCE_ID,
                                             is_participating=True, group__in=('T W-14', )).order_by('id')
        for _ in juniors:
            if UCICategory.objects.filter(first_name__icontains=_.first_name, last_name__icontains=_.last_name):
                try:
                    PreNumberAssign.objects.get(competition=self.competition, participant_slug=_.slug)
                except:
                    PreNumberAssign.objects.create(competition=self.competition, distance=_.distance, participant_slug=_.slug, segment=4)

        super(RM2017, self).assign_numbers(reassign, assign_special)
