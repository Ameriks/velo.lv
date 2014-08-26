# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Application'
        db.create_table(u'registration_application', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='created_application_set', null=True, to=orm['core.User'])),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='modified_application_set', null=True, to=orm['core.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Competition'])),
            ('payment_status', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('discount_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['payment.DiscountCode'], null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('code', self.gf('django.db.models.fields.CharField')(default='7177e584-72a2-44d2-b930-9245be8cc2d0', unique=True, max_length=50)),
            ('legacy_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('company_name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('company_vat', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('company_regnr', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('company_address', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('company_juridical_address', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('external_invoice_code', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('external_invoice_nr', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('total_discount', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=20, decimal_places=2)),
            ('total_entry_fee', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=20, decimal_places=2)),
            ('total_insurance_fee', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=20, decimal_places=2)),
            ('final_price', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=20, decimal_places=2)),
        ))
        db.send_create_signal(u'registration', ['Application'])

        # Adding model 'Participant'
        db.create_table(u'registration_participant', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='created_participant_set', null=True, to=orm['core.User'])),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='modified_participant_set', null=True, to=orm['core.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('application', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registration.Application'], null=True, blank=True)),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Competition'])),
            ('distance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Distance'], null=True, blank=True)),
            ('price', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['payment.Price'], null=True, blank=True)),
            ('discount_amount', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=20, decimal_places=2)),
            ('insurance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Insurance'], null=True, blank=True)),
            ('team', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('team_name', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('team_name_slug', self.gf('django.db.models.fields.SlugField')(max_length=50, blank=True)),
            ('is_participating', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_competing', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('birthday', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('is_only_year', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('ssn', self.gf('django.db.models.fields.CharField')(max_length=12, blank=True)),
            ('phone_number', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('send_email', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('send_sms', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('country', self.gf('django_countries.fields.CountryField')(max_length=2, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'+', null=True, to=orm['core.Choices'])),
            ('bike_brand', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'+', null=True, to=orm['core.Choices'])),
            ('occupation', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'+', null=True, to=orm['core.Choices'])),
            ('where_heard', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'+', null=True, to=orm['core.Choices'])),
            ('group', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('registrant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.User'], null=True, blank=True)),
            ('legacy_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('full_name', self.gf('django.db.models.fields.CharField')(max_length=120, blank=True)),
            ('primary_number', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registration.Number'], null=True, blank=True)),
            ('is_temporary', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_sent_number_email', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_sent_number_sms', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('registration_dt', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'registration', ['Participant'])

        # Adding model 'Number'
        db.create_table(u'registration_number', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='created_number_set', null=True, to=orm['core.User'])),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='modified_number_set', null=True, to=orm['core.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('status', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Competition'])),
            ('distance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Distance'])),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
            ('number_text', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('participant_slug', self.gf('django.db.models.fields.SlugField')(max_length=50, blank=True)),
            ('group', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
        ))
        db.send_create_signal(u'registration', ['Number'])

        # Adding unique constraint on 'Number', fields ['competition', 'number', 'group']
        db.create_unique(u'registration_number', ['competition_id', 'number', 'group'])


    def backwards(self, orm):
        # Removing unique constraint on 'Number', fields ['competition', 'number', 'group']
        db.delete_unique(u'registration_number', ['competition_id', 'number', 'group'])

        # Deleting model 'Application'
        db.delete_table(u'registration_application')

        # Deleting model 'Participant'
        db.delete_table(u'registration_participant')

        # Deleting model 'Number'
        db.delete_table(u'registration_number')


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
            'email_validation_code': ('django.db.models.fields.CharField', [], {'default': "'cba2575b-9c00-4dce-87e0-eb42f34b1cf9'", 'max_length': '36'}),
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
            'code': ('django.db.models.fields.CharField', [], {'default': "'23b93653-1f77-4b76-8ddf-fb0dede224b7'", 'unique': 'True', 'max_length': '50'}),
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
            'team': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'team_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'team_name_slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'blank': 'True'}),
            'where_heard': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'+'", 'null': 'True', 'to': u"orm['core.Choices']"})
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
        }
    }

    complete_apps = ['registration']