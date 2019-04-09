from velo.payment.discount_kinds.family_mtb2019 import FamilyMtb2019


class FamilyRiga2019(FamilyMtb2019):
    COMPETITIONS = [97, ]

    DISCOUNTS_FOR_DISTANCE = {
        98: 0.2,  # sporta brauciens
        99: 0.2,  # tautas brauciens 2 apļi
        100: 0.2,  # ģimeņu brauciens
        101: 0.2,  # bērnu brauciens
    }
