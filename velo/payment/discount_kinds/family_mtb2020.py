from velo.payment.discount_kinds.family_mtb2019 import FamilyMtb2019


class FamilyMtb2020(FamilyMtb2019):
    COMPETITIONS = [100, 101, 102, 103, 104, 105, 106]

    DISCOUNTS_FOR_DISTANCE = {  # discount in percents for every distance
        # MTB
        106: 0.2,  # sporta distance
        107: 0.2,  # tautas distance
        108: 0.2,  # mammadaba veselības distance
        109: 0,  # bērnu distance
        110: 0.2,  # mammadaba zēni un meitenes
    }
