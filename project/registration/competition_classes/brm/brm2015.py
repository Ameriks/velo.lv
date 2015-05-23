# coding=utf-8
from __future__ import unicode_literals
import datetime
from sitetree.utils import item
from registration.competition_classes.base import CompetitionScriptBase
from registration.models import Number, Participant
from registration.tables import ParticipantTable
from results.models import HelperResults
from results.tables import ResultChildrenGroupTable
from results.tasks import update_helper_result_table


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

    def number_ranges(self):
        """
        Returns number ranges for each distance.
        """
        return {
            self.BERNU_DISTANCE_ID: [{'start': 1, 'end': 71, 'group': group} for group in self.groups.get(self.BERNU_DISTANCE_ID)],
        }

    def assign_group(self, distance_id, gender, birthday):
        year = birthday.year

        # If participates younger children, then assign 2012 group
        if year > 2012:
            year = 2012

        children_gender_mapping = {'F': 'M', 'M': 'Z'}

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



    def create_helper_results(self, participants):
        for participant in participants:
            helper, created = HelperResults.objects.get_or_create(competition=self.competition, participant=participant)


    def assign_numbers_continuously(self):
        self.assign_numbers(reassign=False, assign_special=False)


    def assign_numbers(self, reassign=False, assign_special=False):

        # Update helper results before assigning
        update_helper_result_table(self.competition_id, update=True)

        if reassign:
            Number.objects.filter(competition_id__in=self.competition.get_ids()).update(participant_slug='', number_text='')
            Participant.objects.filter(competition_id__in=self.competition.get_ids(), is_participating=True).update(primary_number=None)

        helperresults = HelperResults.objects.filter(competition=self.competition, participant__is_participating=True, participant__primary_number=None).select_related('participant').order_by('participant__registration_dt')

        for result in helperresults:
            participant = result.participant

            group = self.get_group_for_number_search(participant.distance_id, participant.gender, participant.birthday)
            try:
                number = Number.objects.get(participant_slug=participant.slug, distance=participant.distance, group=group)
                if not participant.primary_number:
                    participant.primary_number = number
                    participant.save()
            except:
                next_number = Number.objects.filter(participant_slug='', distance=participant.distance, group=group)

                if participant.gender == 'M':
                    next_number = next_number.order_by('number')
                else:
                    next_number = next_number.order_by('-number')

                if not next_number:
                    raise Exception('No free numbers to assign')
                else:
                    next_number = next_number[0]

                next_number.participant_slug = participant.slug
                print "%s - %s" % (next_number, participant.slug)
                next_number.save()
                participant.primary_number = next_number
                participant.save()
