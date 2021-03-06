from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class FamilyMtb2019(object):  # object is application

    COMPETITIONS = [90, 91, 92, 93, 94, 95, 96]

    IS_RULE_FOR_PARTICIPANTS = True
    MIN_ADULTS_IN_APPLICATION = 0
    MAX_ADULTS_IN_APPLICATION = 2
    MIN_KIDS_IN_APPLICATION = 0
    MAX_KIDS_IN_APPLICATION = 5

    IS_LIMITED_USAGE = True
    IS_USAGE_TIMES_FOR_PARTICIPANTS = False

    DISCOUNTS_FOR_DISTANCE = {  # discount in percents for every distance
        # MTB
        93: 0.2,  # sporta distance
        94: 0.2,  # tautas distance
        95: 0.2,  # mammadaba veselības distance
        96: 0,    # bērnu distance
        97: 0.2,  # mammadaba zēni un meitenes
    }

    IS_DISCOUNT_DECIMAL = True
    IS_INSURANCE_DISCOUNT_DECIMAL = True
    DISCOUNT_FOR_INSURANCE = 0

    def __init__(self, application=None):
        if not application:
            raise Exception('At least one variable is required.')

        self.application = application

    def is_valid_for_competition(self):
        return self.application.competition_id in self.COMPETITIONS

    def is_correct_application(self):
        if self.IS_RULE_FOR_PARTICIPANTS:
            adults = 0
            kids = 0
            now = timezone.now().date()
            for participant in self.application.participant_set.all():
                birth_date = participant.birthday
                if now.year - birth_date.year > 18 or (now.year - birth_date.year == 18 and now.month - birth_date.month
                                                       >= 0 and now.day - birth_date.day >= 0):
                    adults += 1
                else:
                    kids += 1

            return not any([self.MAX_ADULTS_IN_APPLICATION < adults, self.MIN_ADULTS_IN_APPLICATION > adults,
                            self.MAX_KIDS_IN_APPLICATION < kids, self.MIN_KIDS_IN_APPLICATION > kids])
        else:
            return True

    def get_final_price_for_application(self):
        if not self.is_valid_for_competition():
            return _("Code not valid for this competition")
        if not self.is_correct_application():
            return _("Maximum 2 adults and 5 kids must be in application")
        final_price = 0
        for participant in self.application.participant_set.all():
            final_price += self.get_entry_fee_for_participant(participant)
            if participant.insurance:
                final_price += self.get_insurance_fee_for_participant(participant)
        return final_price

    def get_entry_fee_for_participant(self, participant):
        if self.is_valid_for_competition() and self.is_correct_application():
            if self.IS_DISCOUNT_DECIMAL:
                entry_fee = float(participant.price.price) * (
                        1 - self.DISCOUNTS_FOR_DISTANCE[participant.distance_id])
            else:
                entry_fee = float(participant.price.price) - self.DISCOUNTS_FOR_DISTANCE[participant.distance_id]
        else:
            entry_fee = float(participant.price.price) + float(participant.insurance.price)

        entry_fee = round(entry_fee, 2)
        return entry_fee

    def get_insurance_fee_for_participant(self, participant):
        if self.is_valid_for_competition() and self.is_correct_application():
            if self.IS_INSURANCE_DISCOUNT_DECIMAL:
                insurance_fee = float(participant.insurance.price) * (1 - self.DISCOUNT_FOR_INSURANCE)
            else:
                insurance_fee = float(participant.insurance.price) - self.DISCOUNT_FOR_INSURANCE

        insurance_fee = round(insurance_fee, 2)
        return insurance_fee

    def get_usage_count(self):
        count = 0
        if self.IS_USAGE_TIMES_FOR_PARTICIPANTS:
            for participant in self.application.participant_set.all():
                if self.DISCOUNTS_FOR_DISTANCE.get(participant.distance_id) != 0:
                    count += 1
            return count
        else:
            return 1
