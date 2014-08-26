# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LegacyResult'
        db.create_table(u'results_legacyresult', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Competition'])),
            ('distance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Distance'])),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('year', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, blank=True)),
            ('result_distance', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('points_distance', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('phone_number', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('participant_2014', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registration.Participant'], null=True, blank=True)),
            ('participant_2014_could_be', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='legacyresult_potential_set', null=True, to=orm['registration.Participant'])),
            ('participant_2014_could_be2', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='legacyresult_potential2_set', null=True, to=orm['registration.Participant'])),
        ))
        db.send_create_signal(u'results', ['LegacyResult'])

        # Adding model 'LegacySEBStandingsResult'
        db.create_table(u'results_legacysebstandingsresult', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Competition'])),
            ('distance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Distance'])),
            ('number', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('group', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('year', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, blank=True)),
            ('team_name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('velo', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('group_points1', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('group_points2', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('group_points3', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('group_points4', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('group_points5', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('group_points6', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('group_points7', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('group_total', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('group_place', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('distance_points1', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('distance_points2', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('distance_points3', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('distance_points4', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('distance_points5', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('distance_points6', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('distance_points7', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('distance_total', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('distance_place', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('participant_2014', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registration.Participant'], null=True, blank=True)),
            ('participant_2014_could_be', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='legacysebstandingsresult_potential_set', null=True, to=orm['registration.Participant'])),
            ('participant_2014_could_be2', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='legacysebstandingsresult_potential2_set', null=True, to=orm['registration.Participant'])),
        ))
        db.send_create_signal(u'results', ['LegacySEBStandingsResult'])

        # Adding model 'UrlSync'
        db.create_table(u'results_urlsync', (
            (u'periodictask_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['djcelery.PeriodicTask'], unique=True, primary_key=True)),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Competition'])),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('current_line', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'results', ['UrlSync'])

        # Adding model 'ChipScan'
        db.create_table(u'results_chipscan', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Competition'])),
            ('nr_text', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('time_text', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('nr', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registration.Number'], null=True, blank=True)),
            ('time', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('is_processed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_blocked', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'results', ['ChipScan'])

        # Adding model 'DistanceAdmin'
        db.create_table(u'results_distanceadmin', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Competition'])),
            ('distance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Distance'])),
            ('zero', self.gf('django.db.models.fields.TimeField')(default='00:00:00')),
            ('distance_actual', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'results', ['DistanceAdmin'])

        # Adding model 'LapResult'
        db.create_table(u'results_lapresult', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('result', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['results.Result'])),
            ('index', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('time', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'results', ['LapResult'])

        # Adding model 'Result'
        db.create_table(u'results_result', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Competition'])),
            ('participant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registration.Participant'])),
            ('number', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registration.Number'])),
            ('time', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('zero_time', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('chip_time', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('avg_speed', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('result_group', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('result_distance', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('points_group', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('points_distance', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('standings_content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
            ('standings_object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('leader', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['results.Leader'], null=True, blank=True)),
        ))
        db.send_create_signal(u'results', ['Result'])

        # Adding model 'Leader'
        db.create_table(u'results_leader', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Competition'])),
            ('color', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
        ))
        db.send_create_signal(u'results', ['Leader'])

        # Adding model 'SebStandings'
        db.create_table(u'results_sebstandings', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Competition'])),
            ('distance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Distance'])),
            ('participant_slug', self.gf('django.db.models.fields.SlugField')(max_length=50, blank=True)),
            ('participant', self.gf('django.db.models.fields.related.ForeignKey')(related_name='primary_sebstandings_set', to=orm['registration.Participant'])),
            ('group_points1', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('group_points2', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('group_points3', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('group_points4', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('group_points5', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('group_points6', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('group_points7', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('group_total', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('group_place', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('distance_points1', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('distance_points2', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('distance_points3', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('distance_points4', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('distance_points5', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('distance_points6', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('distance_points7', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('distance_total', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('distance_total_seconds', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('distance_place', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'results', ['SebStandings'])

        # Adding model 'TeamResultStandings'
        db.create_table(u'results_teamresultstandings', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('team', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['team.Team'], unique=True)),
            ('points_total', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('points1', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('points2', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('points3', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('points4', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('points5', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('points6', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('points7', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
        ))
        db.send_create_signal(u'results', ['TeamResultStandings'])


    def backwards(self, orm):
        # Deleting model 'LegacyResult'
        db.delete_table(u'results_legacyresult')

        # Deleting model 'LegacySEBStandingsResult'
        db.delete_table(u'results_legacysebstandingsresult')

        # Deleting model 'UrlSync'
        db.delete_table(u'results_urlsync')

        # Deleting model 'ChipScan'
        db.delete_table(u'results_chipscan')

        # Deleting model 'DistanceAdmin'
        db.delete_table(u'results_distanceadmin')

        # Deleting model 'LapResult'
        db.delete_table(u'results_lapresult')

        # Deleting model 'Result'
        db.delete_table(u'results_result')

        # Deleting model 'Leader'
        db.delete_table(u'results_leader')

        # Deleting model 'SebStandings'
        db.delete_table(u'results_sebstandings')

        # Deleting model 'TeamResultStandings'
        db.delete_table(u'results_teamresultstandings')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'core.choices': {
            'Meta': {'object_name': 'Choices'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'kind': ('django.db.models.fields.SmallIntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'core.competition': {
            'Meta': {'object_name': 'Competition'},
            'alias': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'apply_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'bill_series': ('django.db.models.fields.CharField', [], {'default': "'B'", 'max_length': '20', 'blank': 'True'}),
            'competition_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'competition_date_till': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'complex_discount': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'complex_payment_enddate': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'created_competition_set'", 'null': 'True', 'to': u"orm['core.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_in_menu': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'kind': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'legacy_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'modified_competition_set'", 'null': 'True', 'to': u"orm['core.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'params': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['core.Competition']"}),
            'payment_channel': ('django.db.models.fields.CharField', [], {'default': "'LKDF'", 'max_length': '20'}),
            'place_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'processing_class': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'sitetree': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sitetree.TreeItem']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'skin': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'core.distance': {
            'Meta': {'ordering': "(u'_order',)", 'object_name': 'Distance'},
            '_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'can_have_teams': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Competition']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'created_distance_set'", 'null': 'True', 'to': u"orm['core.User']"}),
            'distance_m': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'distance_text': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'have_results': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'modified_distance_set'", 'null': 'True', 'to': u"orm['core.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'core.insurance': {
            'Meta': {'ordering': "('competition', 'price')", 'object_name': 'Insurance'},
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Competition']"}),
            'complex_discount': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_complex': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'insurance_company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.InsuranceCompany']"}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '20', 'decimal_places': '2'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'core.insurancecompany': {
            'Meta': {'object_name': 'InsuranceCompany'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'term': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'core.user': {
            'Meta': {'object_name': 'User'},
            'bike_brand': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['core.Choices']"}),
            'birthday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['core.Choices']"}),
            'country': ('django_countries.fields.CountryField', [], {'default': "'LV'", 'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'email_status': ('django.db.models.fields.SmallIntegerField', [], {'default': '10'}),
            'email_validation_code': ('django.db.models.fields.CharField', [], {'default': "'77ec6f00-1840-4a83-8d10-56cfe5db5afb'", 'max_length': '36'}),
            'email_validation_expiry': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'legacy_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'send_email': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'ssn': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"})
        },
        u'djcelery.crontabschedule': {
            'Meta': {'ordering': "[u'month_of_year', u'day_of_month', u'day_of_week', u'hour', u'minute']", 'object_name': 'CrontabSchedule'},
            'day_of_month': ('django.db.models.fields.CharField', [], {'default': "u'*'", 'max_length': '64'}),
            'day_of_week': ('django.db.models.fields.CharField', [], {'default': "u'*'", 'max_length': '64'}),
            'hour': ('django.db.models.fields.CharField', [], {'default': "u'*'", 'max_length': '64'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minute': ('django.db.models.fields.CharField', [], {'default': "u'*'", 'max_length': '64'}),
            'month_of_year': ('django.db.models.fields.CharField', [], {'default': "u'*'", 'max_length': '64'})
        },
        u'djcelery.intervalschedule': {
            'Meta': {'ordering': "[u'period', u'every']", 'object_name': 'IntervalSchedule'},
            'every': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'period': ('django.db.models.fields.CharField', [], {'max_length': '24'})
        },
        u'djcelery.periodictask': {
            'Meta': {'object_name': 'PeriodicTask'},
            'args': ('django.db.models.fields.TextField', [], {'default': "u'[]'", 'blank': 'True'}),
            'crontab': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['djcelery.CrontabSchedule']", 'null': 'True', 'blank': 'True'}),
            'date_changed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'exchange': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'expires': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interval': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['djcelery.IntervalSchedule']", 'null': 'True', 'blank': 'True'}),
            'kwargs': ('django.db.models.fields.TextField', [], {'default': "u'{}'", 'blank': 'True'}),
            'last_run_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'queue': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'routing_key': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'task': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'total_run_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'payment.discountcampaign': {
            'Meta': {'object_name': 'DiscountCampaign'},
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Competition']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'payment.discountcode': {
            'Meta': {'object_name': 'DiscountCode'},
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['payment.DiscountCampaign']"}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'created_discountcode_set'", 'null': 'True', 'to': u"orm['core.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'modified_discountcode_set'", 'null': 'True', 'to': u"orm['core.User']"}),
            'usage_times': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'usage_times_left': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        u'payment.price': {
            'Meta': {'ordering': "('distance', 'start_registering')", 'object_name': 'Price'},
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Competition']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'created_price_set'", 'null': 'True', 'to': u"orm['core.User']"}),
            'distance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Distance']"}),
            'end_registering': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'from_year': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'modified_price_set'", 'null': 'True', 'to': u"orm['core.User']"}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '20', 'decimal_places': '2'}),
            'start_registering': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'till_year': ('django.db.models.fields.IntegerField', [], {'default': '2050'})
        },
        u'registration.application': {
            'Meta': {'object_name': 'Application'},
            'code': ('django.db.models.fields.CharField', [], {'default': "'4034d4d2-108b-4591-8a36-79053c46ef6f'", 'unique': 'True', 'max_length': '50'}),
            'company_address': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'company_juridical_address': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'company_regnr': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'company_vat': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Competition']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'created_application_set'", 'null': 'True', 'to': u"orm['core.User']"}),
            'discount_code': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['payment.DiscountCode']", 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'external_invoice_code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'external_invoice_nr': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'final_price': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '20', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'legacy_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'modified_application_set'", 'null': 'True', 'to': u"orm['core.User']"}),
            'payment_status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'total_discount': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '20', 'decimal_places': '2'}),
            'total_entry_fee': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '20', 'decimal_places': '2'}),
            'total_insurance_fee': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '20', 'decimal_places': '2'})
        },
        u'registration.number': {
            'Meta': {'ordering': "(u'distance', u'group', u'number')", 'unique_together': "((u'competition', u'number', u'group'),)", 'object_name': 'Number'},
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Competition']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'created_number_set'", 'null': 'True', 'to': u"orm['core.User']"}),
            'distance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Distance']"}),
            'group': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'modified_number_set'", 'null': 'True', 'to': u"orm['core.User']"}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'number_text': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'participant_slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'blank': 'True'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'})
        },
        u'registration.participant': {
            'Meta': {'ordering': "(u'distance', u'created')", 'object_name': 'Participant'},
            'application': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['registration.Application']", 'null': 'True', 'blank': 'True'}),
            'bike_brand': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'+'", 'null': 'True', 'to': u"orm['core.Choices']"}),
            'birthday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'+'", 'null': 'True', 'to': u"orm['core.Choices']"}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Competition']"}),
            'country': ('django_countries.fields.CountryField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'created_participant_set'", 'null': 'True', 'to': u"orm['core.User']"}),
            'discount_amount': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '20', 'decimal_places': '2'}),
            'distance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Distance']", 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'group': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'insurance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Insurance']", 'null': 'True', 'blank': 'True'}),
            'is_competing': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_only_year': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_participating': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_sent_number_email': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_sent_number_sms': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_temporary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'legacy_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'modified_participant_set'", 'null': 'True', 'to': u"orm['core.User']"}),
            'occupation': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'+'", 'null': 'True', 'to': u"orm['core.Choices']"}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'price': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['payment.Price']", 'null': 'True', 'blank': 'True'}),
            'primary_number': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['registration.Number']", 'null': 'True', 'blank': 'True'}),
            'registrant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.User']", 'null': 'True', 'blank': 'True'}),
            'registration_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'send_email': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'send_sms': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'blank': 'True'}),
            'ssn': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['team.Team']", 'null': 'True', 'blank': 'True'}),
            'team_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'team_name_slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'blank': 'True'}),
            'where_heard': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'+'", 'null': 'True', 'to': u"orm['core.Choices']"})
        },
        u'results.chipscan': {
            'Meta': {'object_name': 'ChipScan'},
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Competition']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_blocked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'nr': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['registration.Number']", 'null': 'True', 'blank': 'True'}),
            'nr_text': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'time_text': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'results.distanceadmin': {
            'Meta': {'object_name': 'DistanceAdmin'},
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Competition']"}),
            'distance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Distance']"}),
            'distance_actual': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'zero': ('django.db.models.fields.TimeField', [], {'default': "'00:00:00'"})
        },
        u'results.lapresult': {
            'Meta': {'object_name': 'LapResult'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'result': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['results.Result']"}),
            'time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'results.leader': {
            'Meta': {'object_name': 'Leader'},
            'color': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Competition']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'results.legacyresult': {
            'Meta': {'object_name': 'LegacyResult'},
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Competition']"}),
            'distance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Distance']"}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'participant_2014': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['registration.Participant']", 'null': 'True', 'blank': 'True'}),
            'participant_2014_could_be': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'legacyresult_potential_set'", 'null': 'True', 'to': u"orm['registration.Participant']"}),
            'participant_2014_could_be2': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'legacyresult_potential2_set'", 'null': 'True', 'to': u"orm['registration.Participant']"}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'points_distance': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'result_distance': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'blank': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'results.legacysebstandingsresult': {
            'Meta': {'object_name': 'LegacySEBStandingsResult'},
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Competition']"}),
            'distance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Distance']"}),
            'distance_place': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'distance_points1': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'distance_points2': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'distance_points3': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'distance_points4': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'distance_points5': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'distance_points6': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'distance_points7': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'distance_total': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'group': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'group_place': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'group_points1': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'group_points2': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'group_points3': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'group_points4': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'group_points5': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'group_points6': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'group_points7': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'group_total': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'participant_2014': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['registration.Participant']", 'null': 'True', 'blank': 'True'}),
            'participant_2014_could_be': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'legacysebstandingsresult_potential_set'", 'null': 'True', 'to': u"orm['registration.Participant']"}),
            'participant_2014_could_be2': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'legacysebstandingsresult_potential2_set'", 'null': 'True', 'to': u"orm['registration.Participant']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'blank': 'True'}),
            'team_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'velo': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'results.result': {
            'Meta': {'object_name': 'Result'},
            'avg_speed': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'chip_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Competition']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'leader': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['results.Leader']", 'null': 'True', 'blank': 'True'}),
            'number': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['registration.Number']"}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['registration.Participant']"}),
            'points_distance': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'points_group': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'result_distance': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'result_group': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'standings_content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'standings_object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'zero_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'results.sebstandings': {
            'Meta': {'object_name': 'SebStandings'},
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Competition']"}),
            'distance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Distance']"}),
            'distance_place': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'distance_points1': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'distance_points2': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'distance_points3': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'distance_points4': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'distance_points5': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'distance_points6': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'distance_points7': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'distance_total': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'distance_total_seconds': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'group_place': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'group_points1': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'group_points2': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'group_points3': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'group_points4': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'group_points5': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'group_points6': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'group_points7': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'group_total': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'primary_sebstandings_set'", 'to': u"orm['registration.Participant']"}),
            'participant_slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'blank': 'True'})
        },
        u'results.teamresultstandings': {
            'Meta': {'object_name': 'TeamResultStandings'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'points1': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'points2': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'points3': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'points4': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'points5': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'points6': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'points7': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'points_total': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'team': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['team.Team']", 'unique': 'True'})
        },
        u'results.urlsync': {
            'Meta': {'object_name': 'UrlSync', '_ormbases': [u'djcelery.PeriodicTask']},
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Competition']"}),
            'current_line': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'periodictask_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['djcelery.PeriodicTask']", 'unique': 'True', 'primary_key': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'sitetree.tree': {
            'Meta': {'object_name': 'Tree'},
            'alias': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'sitetree.treeitem': {
            'Meta': {'unique_together': "(('tree', 'alias'),)", 'object_name': 'TreeItem'},
            'access_guest': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'access_loggedin': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'access_perm_type': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'access_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'access_restricted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'alias': ('sitetree.models.CharFieldNullable', [], {'db_index': 'True', 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'hint': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inbreadcrumbs': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'inmenu': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'insitetree': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'treeitem_parent'", 'null': 'True', 'to': u"orm['sitetree.TreeItem']"}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'tree': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'treeitem_tree'", 'to': u"orm['sitetree.Tree']"}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'urlaspattern': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'})
        },
        u'team.team': {
            'Meta': {'ordering': "(u'distance', u'-is_featured', u'title')", 'object_name': 'Team'},
            'contact_person': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'country': ('django_countries.fields.CountryField', [], {'max_length': '2'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'created_team_set'", 'null': 'True', 'to': u"orm['core.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'distance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Distance']"}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'is_featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'legacy_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'management_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'modified_team_set'", 'null': 'True', 'to': u"orm['core.User']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.User']"}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'shirt_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['results']