# coding=utf-8
from __future__ import unicode_literals
import datetime
from sitetree.utils import item
from registration.competition_classes.base import CompetitionScriptBase
from registration.tables import ParticipantTable
from results.tables import ResultChildrenGroupTable


class Brm2015(CompetitionScriptBase):
    competition_index = 1
    BERNU_DISTANCE_ID = 44

    @property
    def groups(self):
        """
        Returns defined groups for each competition type.
        """
        ret = []
        for gender in ('M', 'Z'):
            for year in range(2004, 2013):
                ret.append("%i %s" % (year, gender))

        return {
            self.BERNU_DISTANCE_ID: tuple(sorted(ret)),
        }


    def assign_group(self, distance_id, gender, birthday):
        year = birthday.year
        children_gender_mapping = {'W': 'M', 'M': 'Z'}

        group = "%i %s" % (year, children_gender_mapping.get(gender))

        if group in self.groups.get(self.BERNU_DISTANCE_ID):
            return group

        print 'here I shouldnt be...'
        raise Exception('Invalid group assigning. {0} {1} {2}'.format(gender, distance_id, birthday))



    def build_manager_menu(self):
        return item(unicode(self.competition), '#', url_as_pattern=False, in_menu=self.competition.is_in_menu, access_loggedin=True)


    def build_menu(self):
        current_date = datetime.date.today()
        child_items = [
            item('Atbalstītāji', 'competition:supporters %i' % self.competition.id),
            item('Starta saraksts', 'competition:participant_list %i' % self.competition.id),
        ]
        self.build_flat_pages(self.competition, child_items)
        if self.competition.map_set.count():
            child_items.append(item('Kartes', 'competition:maps %i' % self.competition.id))

        if self.competition.competition_date <= current_date:
            child_items.append(item('Rezultāti', 'competition:result_distance_list %i' % self.competition.id))
        return item(unicode(self.competition), '#', url_as_pattern=False, children=child_items, in_menu=self.competition.is_in_menu)


    def get_result_table_class(self, distance, group=None):
        return ResultChildrenGroupTable

    def get_startlist_table_class(self, distance=None):
        return ParticipantTable


    def get_group_for_number_search(self, distance_id, gender, birthday):
        return self.assign_group(distance_id, gender, birthday)
