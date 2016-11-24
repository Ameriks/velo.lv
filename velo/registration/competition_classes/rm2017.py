from velo.registration.competition_classes import RM2016


class RM2017(RM2016):
    SPORTA_DISTANCE_ID = 65
    TAUTAS_DISTANCE_ID = 66
    TAUTAS1_DISTANCE_ID = 67
    GIMENU_DISTANCE_ID = 68

    def _update_year(self, year):
        return year + 3