from velo.registration.competition_classes import VB2016


class VB2017(VB2016):
    SOSEJAS_DISTANCE_ID = 69
    MTB_DISTANCE_ID = 70
    TAUTAS_DISTANCE_ID = 71
    competition_index = 1


    def _update_year(self, year):
        return year + 3
