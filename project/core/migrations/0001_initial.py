# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Choices'
        db.create_table(u'core_choices', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('kind', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'core', ['Choices'])

        # Adding model 'User'
        db.create_table(u'core_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=75)),
            ('email_status', self.gf('django.db.models.fields.SmallIntegerField')(default=10)),
            ('email_validation_code', self.gf('django.db.models.fields.CharField')(default='6fcfd16a-367d-4b96-8a28-9c4534c8c5dc', max_length=36)),
            ('email_validation_expiry', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('country', self.gf('django_countries.fields.CountryField')(default='LV', max_length=2, null=True, blank=True)),
            ('ssn', self.gf('django.db.models.fields.CharField')(max_length=12, blank=True)),
            ('birthday', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['core.Choices'])),
            ('bike_brand', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['core.Choices'])),
            ('phone_number', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('send_email', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('legacy_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('full_name', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('is_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_joined', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'core', ['User'])

        # Adding M2M table for field groups on 'User'
        m2m_table_name = db.shorten_name(u'core_user_groups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm[u'core.user'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(m2m_table_name, ['user_id', 'group_id'])

        # Adding M2M table for field user_permissions on 'User'
        m2m_table_name = db.shorten_name(u'core_user_user_permissions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm[u'core.user'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(m2m_table_name, ['user_id', 'permission_id'])

        # Adding model 'Competition'
        db.create_table(u'core_competition', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('alias', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='created_competition_set', null=True, to=orm['core.User'])),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='modified_competition_set', null=True, to=orm['core.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('place_name', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('competition_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('competition_date_till', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('kind', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('complex_payment_enddate', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('complex_discount', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('bill_series', self.gf('django.db.models.fields.CharField')(default='B', max_length=20, blank=True)),
            ('payment_channel', self.gf('django.db.models.fields.CharField')(default='LKDF', max_length=20)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name='children', null=True, to=orm['core.Competition'])),
            ('processing_class', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('legacy_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('sitetree', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sitetree.TreeItem'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('is_in_menu', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('skin', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('logo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('apply_image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('params', self.gf('jsonfield.fields.JSONField')(null=True, blank=True)),
            (u'lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'core', ['Competition'])

        # Adding model 'Distance'
        db.create_table(u'core_distance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='created_distance_set', null=True, to=orm['core.User'])),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='modified_distance_set', null=True, to=orm['core.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Competition'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('distance_text', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('distance_m', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('can_have_teams', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('have_results', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('_order', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'core', ['Distance'])

        # Adding model 'InsuranceCompany'
        db.create_table(u'core_insurancecompany', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('term', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'core', ['InsuranceCompany'])

        # Adding model 'Insurance'
        db.create_table(u'core_insurance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('status', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('insurance_company', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.InsuranceCompany'])),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Competition'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('price', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=20, decimal_places=2)),
            ('in_complex', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('complex_discount', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
        ))
        db.send_create_signal(u'core', ['Insurance'])

        # Adding model 'CustomSlug'
        db.create_table(u'core_customslug', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('birthday', self.gf('django.db.models.fields.DateField')()),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, blank=True)),
        ))
        db.send_create_signal(u'core', ['CustomSlug'])

        # Adding model 'Log'
        db.create_table(u'core_log', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.User'], null=True, blank=True)),
            ('action', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('params', self.gf('jsonfield.fields.JSONField')(null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['Log'])

        # Adding model 'Map'
        db.create_table(u'core_map', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Competition'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('ordering', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'core', ['Map'])


    def backwards(self, orm):
        # Deleting model 'Choices'
        db.delete_table(u'core_choices')

        # Deleting model 'User'
        db.delete_table(u'core_user')

        # Removing M2M table for field groups on 'User'
        db.delete_table(db.shorten_name(u'core_user_groups'))

        # Removing M2M table for field user_permissions on 'User'
        db.delete_table(db.shorten_name(u'core_user_user_permissions'))

        # Deleting model 'Competition'
        db.delete_table(u'core_competition')

        # Deleting model 'Distance'
        db.delete_table(u'core_distance')

        # Deleting model 'InsuranceCompany'
        db.delete_table(u'core_insurancecompany')

        # Deleting model 'Insurance'
        db.delete_table(u'core_insurance')

        # Deleting model 'CustomSlug'
        db.delete_table(u'core_customslug')

        # Deleting model 'Log'
        db.delete_table(u'core_log')

        # Deleting model 'Map'
        db.delete_table(u'core_map')


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
        u'core.customslug': {
            'Meta': {'object_name': 'CustomSlug'},
            'birthday': ('django.db.models.fields.DateField', [], {}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'blank': 'True'})
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
        u'core.log': {
            'Meta': {'object_name': 'Log'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'params': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.User']", 'null': 'True', 'blank': 'True'})
        },
        u'core.map': {
            'Meta': {'ordering': "('competition', 'ordering')", 'object_name': 'Map'},
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Competition']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
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
            'email_validation_code': ('django.db.models.fields.CharField', [], {'default': "'dc273f01-7d67-4358-9ca1-9904a842f125'", 'max_length': '36'}),
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

    complete_apps = ['core']