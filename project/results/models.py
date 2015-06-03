import datetime
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.template.defaultfilters import slugify
from djcelery.models import PeriodicTask, PeriodicTasks, CrontabSchedule
from django.db.models import signals
from easy_thumbnails.fields import ThumbnailerImageField
import os
import time
from django.utils.translation import ugettext_lazy as _
import math
import uuid
from core.models import Log
from results.helper import time_to_seconds
from velo.mixins.models import TimestampMixin
from velo.utils import load_class


def _get_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    filename = str(uuid.uuid4())
    return os.path.join("competition", "leader", "%s%s" % (filename, ext))

def _get_gpx_upload_path(instance, filename):
    folder = str(uuid.uuid4())
    return os.path.join("competition", "gpx", folder, filename)



class LegacyResult(models.Model):
    competition = models.ForeignKey('core.Competition')
    distance = models.ForeignKey('core.Distance')
    first_name = models.CharField(max_length=60, blank=True)
    last_name = models.CharField(max_length=60, blank=True)
    year = models.IntegerField(blank=True, null=True)
    slug = models.SlugField(blank=True)
    result_distance = models.IntegerField(blank=True, null=True)
    points_distance = models.IntegerField(blank=True, null=True)

    phone_number = models.CharField(max_length=60, blank=True)
    email = models.CharField(max_length=60, blank=True)

    participant_2014 = models.ForeignKey('registration.Participant', blank=True, null=True)
    participant_2014_could_be = models.ForeignKey('registration.Participant', related_name='legacyresult_potential_set', blank=True, null=True)
    participant_2014_could_be2 = models.ForeignKey('registration.Participant', related_name='legacyresult_potential2_set', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            if self.year and self.first_name and self.last_name:
                self.slug = slugify('%s-%s-%i' % (self.first_name, self.last_name, self.year))
            else:
                self.slug = ''

        return super(LegacyResult, self).save(*args, **kwargs)



class LegacySEBStandingsResult(models.Model):
    competition = models.ForeignKey('core.Competition')
    distance = models.ForeignKey('core.Distance')
    number = models.IntegerField(blank=True, null=True)
    group = models.CharField(max_length=20, blank=True)

    first_name = models.CharField(max_length=60, blank=True)
    last_name = models.CharField(max_length=60, blank=True)
    year = models.IntegerField(blank=True, null=True)
    slug = models.SlugField(blank=True)
    team_name = models.CharField(max_length=100, blank=True)
    velo = models.CharField(max_length=100, blank=True)

    group_points1 = models.IntegerField(blank=True, null=True)
    group_points2 = models.IntegerField(blank=True, null=True)
    group_points3 = models.IntegerField(blank=True, null=True)
    group_points4 = models.IntegerField(blank=True, null=True)
    group_points5 = models.IntegerField(blank=True, null=True)
    group_points6 = models.IntegerField(blank=True, null=True)
    group_points7 = models.IntegerField(blank=True, null=True)

    group_total = models.IntegerField(blank=True, null=True)
    group_place = models.IntegerField(blank=True, null=True)

    distance_points1 = models.IntegerField(blank=True, null=True)
    distance_points2 = models.IntegerField(blank=True, null=True)
    distance_points3 = models.IntegerField(blank=True, null=True)
    distance_points4 = models.IntegerField(blank=True, null=True)
    distance_points5 = models.IntegerField(blank=True, null=True)
    distance_points6 = models.IntegerField(blank=True, null=True)
    distance_points7 = models.IntegerField(blank=True, null=True)

    distance_total = models.IntegerField(blank=True, null=True)
    distance_place = models.IntegerField(blank=True, null=True)

    participant_2014 = models.ForeignKey('registration.Participant', blank=True, null=True)
    participant_2014_could_be = models.ForeignKey('registration.Participant', related_name='legacysebstandingsresult_potential_set',blank=True, null=True)
    participant_2014_could_be2 = models.ForeignKey('registration.Participant', related_name='legacysebstandingsresult_potential2_set',blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            if self.year and self.first_name and self.last_name:
                self.slug = slugify('%s-%s-%i' % (self.first_name, self.last_name, self.year))
            else:
                self.slug = ''

        return super(LegacySEBStandingsResult, self).save(*args, **kwargs)


class UrlSync(PeriodicTask):
    competition = models.ForeignKey('core.Competition')
    # expires = models.DateTimeField()
    url = models.CharField(max_length=255)
    current_line = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        self.name = "Sync_%f" % time.time()
        self.task = "results.tasks.fetch_results"
        self.crontab, created = CrontabSchedule.objects.get_or_create(minute='*', hour='*', day_of_week="*", day_of_month="*", month_of_year="*")
        super(UrlSync, self).save(*args, **kwargs)
        self.args = "[%i]" % self.id
        return super(UrlSync, self).save(*args, **kwargs)

signals.pre_delete.connect(PeriodicTasks.changed, sender=UrlSync)
signals.pre_save.connect(PeriodicTasks.changed, sender=UrlSync)


class ChipScan(models.Model):
    competition = models.ForeignKey('core.Competition')
    nr_text = models.CharField(max_length=20)
    time_text = models.CharField(max_length=20)
    nr = models.ForeignKey('registration.Number', blank=True, null=True)
    time = models.TimeField(blank=True, null=True)

    is_processed = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)


class DistanceAdmin(models.Model):
    competition = models.ForeignKey('core.Competition')
    distance = models.ForeignKey('core.Distance')
    zero = models.TimeField(default='00:00:00', help_text='HH:MM:SS')
    distance_actual = models.IntegerField(blank=True, null=True)
    gpx = models.FileField(upload_to=_get_gpx_upload_path, blank=True, null=True)

    def __unicode__(self):
        return '%s - %s' % (self.competition.get_full_name, self.distance)


class LapResult(models.Model):
    result = models.ForeignKey('results.Result')
    index = models.IntegerField(default=0, db_index=True)
    time = models.TimeField(_('Time'), blank=True, null=True)


class Result(models.Model):
    STATUSES = (
        ('DSQ', 'DSQ'),
        ('DNS', 'DNS'),
        ('DNF', 'DNF'),
    )
    competition = models.ForeignKey('core.Competition')
    participant = models.ForeignKey('registration.Participant')
    number = models.ForeignKey('registration.Number')

    time = models.TimeField(_('Time'), blank=True, null=True)

    zero_time = models.TimeField(_('Time'), blank=True, null=True)  # not used for SEB
    chip_time = models.TimeField(_('Time'), blank=True, null=True)  # not used for SEB

    # lap_count = models.IntegerField(default=0)  # not used for SEB
    # loses_group = models.TimeField(_('Loses Group'), blank=True, null=True)
    # loses_distance = models.TimeField(_('Loses Distance'), blank=True, null=True)

    avg_speed = models.FloatField(_('Average Speed'), blank=True, null=True)

    result_group = models.IntegerField(_('Result Group'), blank=True, null=True)
    result_distance = models.IntegerField(_('Result Distance'), blank=True, null=True)

    points_group = models.IntegerField(_('Points Group'), default=0)
    points_distance = models.IntegerField(_('Points Distance'), default=0)

    status = models.CharField(_('Status'), max_length=20, choices=STATUSES, blank=True)

    standings_content_type = models.ForeignKey(ContentType, null=True, blank=True)
    standings_object_id = models.PositiveIntegerField(null=True, blank=True)
    standings_object = generic.GenericForeignKey('standings_content_type', 'standings_object_id')

    leader = models.ForeignKey('results.Leader', blank=True, null=True)

    _competition_class = None

    class Meta:
        unique_together = (('competition', 'participant', 'number', ), )

    # def set_loses_distance(self):
    #     r = Result.objects.filter(competition=self.competition, number__distance=self.number.distance).order_by('time')
    #     if r:
    #         zero_time = datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0, 0, 0))
    #         delta = datetime.datetime.combine(datetime.date.today(), r[0].time) - zero_time
    #         self.loses_distance = datetime.datetime.combine(datetime.date.today(), self.time) - delta
    #     else:
    #         self.loses_distance = '00:00:00'
    #
    # def set_loses_group(self):
    #     r = Result.objects.filter(competition=self.competition, number__distance=self.number.distance, participant__group=self.participant.group).order_by('time')
    #     if r:
    #         zero_time = datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0, 0, 0))
    #         delta = datetime.datetime.combine(datetime.date.today(), r[0].time) - zero_time
    #         self.loses_group = datetime.datetime.combine(datetime.date.today(), self.time) - delta
    #     else:
    #         self.loses_group = '00:00:00'

    def set_avg_speed(self):
        avg_speed = self.avg_speed
        if self.time:
            admin = DistanceAdmin.objects.get(competition=self.competition, distance=self.number.distance)
            seconds = datetime.timedelta(hours=self.time.hour, minutes=self.time.minute, seconds=self.time.second).seconds
            self.avg_speed = round((float(admin.distance_actual) / float(seconds))*3.6, 1)
            if avg_speed != self.avg_speed:
                return True
        return False

    def get_competition_class(self):
        if not self._competition_class:
            class_ = load_class(self.competition.processing_class)
            self._competition_class = class_(self.competition.id)
        return self._competition_class

    def set_points_distance(self):
        points_distance = self.points_distance
        self.points_distance = self.get_competition_class().calculate_points_distance(self)
        if points_distance != self.points_distance:
            return True
        return False

    def set_points_group(self):
        points_group = self.points_group
        self.points_group = self.get_competition_class().calculate_points_group(self)
        if points_group != self.points_group:
            return True
        return False

    def set_all(self):
        # self.set_loses_distance()
        # self.set_loses_group()
        avg = self.set_avg_speed()
        pd = self.set_points_distance()
        pg = self.set_points_group()
        if avg or pd or pg:
            return True  # if any of variables is updated, then return true
        return False


class Leader(models.Model):
    COLORS = (
        ('blue', 'blue'),
        ('red', 'red'),
        ('green', 'green'),
        ('sea', 'sea'),
        ('orange', 'orange'),
        ('yellow', 'yellow'),
    )
    competition = models.ForeignKey('core.Competition')
    color = models.CharField(max_length=50, choices=COLORS)
    text = models.CharField(max_length=50)
    image = ThumbnailerImageField(upload_to=_get_upload_path, blank=True)

    def __unicode__(self):
        return '%s - %s' % (self.competition, self.text)


class SebStandings(models.Model):
    competition = models.ForeignKey('core.Competition')
    distance = models.ForeignKey('core.Distance')

    participant_slug = models.SlugField(blank=True)
    participant = models.ForeignKey('registration.Participant', related_name='primary_%(class)s_set', )  # Should be automatically updated to first participant in competition series.

    group_points1 = models.IntegerField('1.', blank=True, null=True)
    group_points2 = models.IntegerField('2.', blank=True, null=True)
    group_points3 = models.IntegerField('3.', blank=True, null=True)
    group_points4 = models.IntegerField('4.', blank=True, null=True)
    group_points5 = models.IntegerField('5.', blank=True, null=True)
    group_points6 = models.IntegerField('6.', blank=True, null=True)
    group_points7 = models.IntegerField('7.', blank=True, null=True)

    group_total = models.IntegerField(blank=True, null=True)
    group_place = models.IntegerField(blank=True, null=True)

    distance_points1 = models.IntegerField('1.', blank=True, null=True)
    distance_points2 = models.IntegerField('2.', blank=True, null=True)
    distance_points3 = models.IntegerField('3.', blank=True, null=True)
    distance_points4 = models.IntegerField('4.', blank=True, null=True)
    distance_points5 = models.IntegerField('5.', blank=True, null=True)
    distance_points6 = models.IntegerField('6.', blank=True, null=True)
    distance_points7 = models.IntegerField('7.', blank=True, null=True)

    distance_total = models.IntegerField(blank=True, null=True)
    distance_total_seconds = models.FloatField(blank=True, null=True)
    distance_place = models.IntegerField(blank=True, null=True)

    @property
    def results(self):
        ctype = ContentType.objects.get_for_model(self.__class__)
        return Result.objects.filter(standings_content_type__pk=ctype.id, standings_object_id=self.id)

    def set_points(self):
        stages = [1, 2, 3, 4, 5, 6, 7]
        mapping = {obj.id: index for index, obj in enumerate(self.competition.get_children(), start=1)}

        results = self.results

        for result in results:
            setattr(self, "group_points%i" % mapping.get(result.competition_id), result.points_group)
            setattr(self, "distance_points%i" % mapping.get(result.competition_id), result.points_distance)
            try:
                stages.remove(mapping.get(result.competition_id))
            except:
                print "Multiple results in stage %s" % result.competition  # TODO: Remove print
                Log.objects.create(content_object=self, message="Multiple results in stage %s" % result.competition)
        for stage in stages:
            setattr(self, "group_points%i" % stage, 0)
            setattr(self, "distance_points%i" % stage, 0)

    def set_distance_total_seconds(self):
        self.distance_total_seconds = sum((time_to_seconds(obj.time) for obj in self.results))

    def get_total_seconds(self):
        return sum((time_to_seconds(obj.time) for obj in self.results))


class TeamResultStandings(models.Model):
    team = models.OneToOneField('team.Team')

    points_total = models.IntegerField(_('Points Total'), default=0, db_index=True)

    points1 = models.IntegerField('1.', blank=True, null=True, db_index=True)
    points2 = models.IntegerField('2.', blank=True, null=True, db_index=True)
    points3 = models.IntegerField('3.', blank=True, null=True, db_index=True)
    points4 = models.IntegerField('4.', blank=True, null=True, db_index=True)
    points5 = models.IntegerField('5.', blank=True, null=True, db_index=True)
    points6 = models.IntegerField('6.', blank=True, null=True, db_index=True)
    points7 = models.IntegerField('7.', blank=True, null=True, db_index=True)


class HelperResults(TimestampMixin, models.Model):
    """
    This is helper table to calculate number and passage assigning for participants.
    """
    competition = models.ForeignKey('core.Competition')
    participant = models.ForeignKey('registration.Participant')

    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    result_used = generic.GenericForeignKey('content_type', 'object_id')  # Can be standing or result

    calculated_total = models.FloatField(blank=True, null=True, db_index=True)

    passage_assigned = models.IntegerField(blank=True, null=True, db_index=True)

    is_manual = models.BooleanField(default=False)  # Manually added records will not be overwritten

    matches_slug = models.SlugField(blank=True)