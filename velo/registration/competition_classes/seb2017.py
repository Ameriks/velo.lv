from velo.registration.competition_classes import Seb2016


class Seb2017(Seb2016):
    SPORTA_DISTANCE_ID = 60
    TAUTAS_DISTANCE_ID = 61
    VESELIBAS_DISTANCE_ID = 62
    BERNU_DISTANCE_ID = 63

    STAGES_COUNT = 7

    def _update_year(self, year):
        return year + 3

