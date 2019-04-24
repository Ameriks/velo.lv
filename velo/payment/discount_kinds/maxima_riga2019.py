from velo.payment.discount_kinds.family_mtb2019 import FamilyMtb2019


class MaximaRiga2019(FamilyMtb2019):
    IS_RULE_FOR_PARTICIPANTS = False

    COMPETITIONS = [97, ]

    DISCOUNTS_FOR_DISTANCE = {
        98: 0.3,  # sporta brauciens
        99: 0.3,  # tautas brauciens 2 apļi
        100: 0.3,  # ģimeņu brauciens
        101: 0.3,  # bērnu brauciens
    }

    IS_USAGE_TIMES_FOR_PARTICIPANTS = True
