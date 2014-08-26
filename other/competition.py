from marketing.utils import send_smses
from results.tasks import fetch_results


from registration.competition_classes import Seb2014
import time 
self = Seb2014(31)
while True:                                                                                                            
    time.sleep(10)
    fetch_results(2); self.assign_distance_number(); self.assign_group_number(); self.recalculate_standings(); send_smses()
