from velo.payment.discount_kinds.family_mtb2019 import FamilyMtb2019


class FamilyUnity2019(FamilyMtb2019):
    COMPETITIONS = [98, ]

    DISCOUNTS_FOR_DISTANCE = {
        102: 0.2,  # Sporta šosejas brauciens
        103: 0.2,  # Kalnu divriteņu brauciens
        104: 0.2,  # Tautas brauciens
        105: 0.2,  # Retro Velo Tūrisma distance
    }
