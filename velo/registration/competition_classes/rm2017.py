from django.utils.translation import activate
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from velo.core.pdf import fill_page_with_image, _baseFontNameB
from velo.registration.competition_classes import RM2016
from velo.registration.models import UCICategory, Participant


class RM2017(RM2016):
    SPORTA_DISTANCE_ID = 65
    TAUTAS_DISTANCE_ID = 66
    TAUTAS1_DISTANCE_ID = 77
    GIMENU_DISTANCE_ID = 68
    BERNU_DISTANCE_ID = 67

    def _update_year(self, year):
        return year + 3

    @property
    def groups(self):
        """
        Returns defined groups for each competition type.
        """
        return {
            self.SPORTA_DISTANCE_ID: ('M-18', 'M', 'Masters', 'M 19-34 CFA', ),
            self.TAUTAS_DISTANCE_ID: ('T M-16', 'T W-16', 'T M', 'T W', 'T M-35', 'T M-45', 'T M-55', 'T M-65'),
            self.TAUTAS1_DISTANCE_ID: ('T1 M', 'T1 W',)
        }

    def number_ranges(self):
        """
        Returns number ranges for each distance.
        """
        return {
            self.SPORTA_DISTANCE_ID: [{'start': 1, 'end': 500, 'group': ''}, ],
            self.TAUTAS_DISTANCE_ID: [{'start': 2001, 'end': 3400, 'group': ''}, ],
            self.TAUTAS1_DISTANCE_ID: [{'start': 3401, 'end': 4000, 'group': ''}, ],
        }

    def assign_group(self, distance_id, gender, birthday, participant=None):
        year = birthday.year
        if distance_id not in (self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID, self.TAUTAS1_DISTANCE_ID):
            return ''
        elif distance_id == self.SPORTA_DISTANCE_ID:
            if gender == 'M':
                if participant and (self._update_year(1995) >= year >= self._update_year(1980)) and UCICategory.objects.filter(category="CYCLING FOR ALL", slug=participant.slug):
                    return 'M 19-34 CFA'
                if self._update_year(1997) >= year >= self._update_year(1996):
                    return 'M-18'
                elif year <= self._update_year(1979):
                    return 'Masters'
                else:
                    return 'M'
            else:
                return 'W'

        elif distance_id == self.TAUTAS_DISTANCE_ID:
            if gender == 'M':
                if self._update_year(1999) >= year >= self._update_year(1998):
                    return 'T M-16'
                elif self._update_year(1997) >= year >= self._update_year(1980):
                    return 'T M'
                elif self._update_year(1979) >= year >= self._update_year(1970):
                    return 'T M-35'
                elif self._update_year(1969) >= year >= self._update_year(1960):
                    return 'T M-45'
                elif self._update_year(1959) >= year >= self._update_year(1950):
                    return 'T M-55'
                elif year <= self._update_year(1949):
                    return 'T M-65'
            else:
                if self._update_year(1999) >= year >= self._update_year(1998):
                    return 'T W-16'
                elif year <= self._update_year(1997):
                    return 'T W'

        elif distance_id == self.TAUTAS1_DISTANCE_ID:
            if gender == 'M':
                return 'T1 M'
            else:
                return 'T1 W'

        print('here I shouldnt be...')
        raise Exception('Invalid group assigning. {0} {1} {2}'.format(gender, distance_id, birthday))

    def passages(self):
        return {
            self.SPORTA_DISTANCE_ID: [(1, 1, 200, 0), (2, 201, 500, 0)],
            self.TAUTAS_DISTANCE_ID: [
                                    (1, 2001, 2200, 20),
                                    (2, 2201, 2400, 20),
                                    (3, 2401, 2600, 15),
                                    (4, 2601, 2800, 10),
                                    (5, 2801, 3000, 10),
                                    (6, 3001, 3200, 5),
                                    (7, 3201, 3400, 5),
                                    ],
            self.TAUTAS1_DISTANCE_ID: [
                (1, 3401, 3600, 5),
                (2, 3601, 3800, 5),
                (3, 3801, 4000, 5),
            ],
        }

    def number_pdf(self, participant_id):
        activate('lv')
        participant = Participant.objects.get(id=participant_id)
        output = BytesIO()

        c = canvas.Canvas(output, pagesize=A4)
        fill_page_with_image("velo/media/competition/vestule/RVm_2017_vestule_ar_tekstu.jpg", c)

        c.setFont(_baseFontNameB, 18)
        c.drawString(5*cm, 19.7*cm, "%s %s" % (participant.full_name.upper(), participant.birthday.year))
        c.drawString(5*cm, 17.7*cm, str(participant.distance))


        if participant.primary_number:
            c.setFont(_baseFontNameB, 35)
            c.drawString(15*cm, 18.6*cm, str(participant.primary_number))
        elif participant.distance_id == self.GIMENU_DISTANCE_ID:
            c.setFont(_baseFontNameB, 25)
            c.drawString(14.5*cm, 18.6*cm, "Ģimeņu br.")
        else:
            c.setFont(_baseFontNameB, 25)
            c.drawString(15*cm, 18.6*cm, "-")

        c.showPage()
        c.save()
        output.seek(0)
        return output
