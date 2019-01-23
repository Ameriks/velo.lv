from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from velo.registration.models import Application


class FamilyMtb2019(object):    # object is application

    COMPETITIONS = [90, 91, 92, 93, 94, 95]
    IS_RULE_FOR_PARTICIPANTS = True
    ADULTS_IN_APPLICATION = 2
    IS_LIMITED_USAGE = True
    DISCOUNTS_FOR_DISTANCE = {  # discount in percents for every distance
        93: 0.2,  # sporta distance
        94: 0.2,  # tautas distance
        95: 0.2,  # mammadaba veselības distance
        96: 0,    # bērnu distance
        97: 0.2,  # mammadaba zēni un meitenes
    }
    IS_DISCOUNT_DECIMAL = True
    IS_DISCOUNT_FOR_INSURANCE = False

    def __init__(self, application=None):
        if not application:
            raise Exception('At least one variable is required.')

        self.application = Application.objects.get(code=application.code)

    def is_valid_for_competition(self):
        return self.application.competition_id in self.COMPETITIONS

    def is_correct_application(self):
        if not self.IS_RULE_FOR_PARTICIPANTS:
            return True
        else:
            adults = self.ADULTS_IN_APPLICATION
            now = timezone.now().date()
            for participant in self.application.participant_set.all():
                birth_date = participant.birthday
                if now.year - birth_date.year > 18 or (now.year-birth_date.year == 18 and now.month - birth_date.month
                                                       >= 0 and now.day - birth_date.day >= 0):
                    adults -= 1
                if adults < 0:
                    return False
            return True

    def get_final_price_for_application(self):
        if not self.is_valid_for_competition():
            return _("Card not valid for this competition")
        if not self.is_correct_application():
            return _("Only two adults can be in application")
        entry_fee = 0
        for participant in self.application.participant_set.all():
            self.get_entry_fee_for_participant(participant)
            entry_fee += self.get_entry_fee_for_participant(participant)
        return entry_fee

    def get_entry_fee_for_participant(self, participant):
        if self.is_valid_for_competition() and self.is_correct_application():
            if self.IS_DISCOUNT_DECIMAL:
                return float(participant.price.price) * (1 - self.DISCOUNTS_FOR_DISTANCE[participant.distance_id])
            else:
                return float(participant.price.price) - self.DISCOUNTS_FOR_DISTANCE[participant.distance_id]
        else:
            return float(participant.price.price)


