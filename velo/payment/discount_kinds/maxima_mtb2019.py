from velo.payment.discount_kinds.family_mtb2019 import FamilyMtb2019


class MaximaMTB2019(FamilyMtb2019):
    IS_RULE_FOR_PARTICIPANTS = False

    DISCOUNTS_FOR_DISTANCE = {  # discount in percents for every distance
        # MTB
        93: 0.3,  # sporta distance
        94: 0.3,  # tautas distance
        95: 0.3,  # mammadaba veselības distance
        96: 0,    # bērnu distance
        97: 0.3,  # mammadaba zēni un meitenes
    }

    IS_USAGE_TIMES_FOR_PARTICIPANTS = True
