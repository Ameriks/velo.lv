from velo.registration.competition_classes import RM2017


class RM2018(RM2017):
    SPORTA_DISTANCE_ID = 84
    TAUTAS_DISTANCE_ID = 85
    TAUTAS1_DISTANCE_ID = 88
    GIMENU_DISTANCE_ID = 87
    BERNU_DISTANCE_ID = 86

    def _update_year(self, year):
        return year + 4
