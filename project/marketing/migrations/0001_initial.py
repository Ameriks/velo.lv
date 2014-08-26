# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SMS'
        db.create_table(u'marketing_sms', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('phone_number', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=160)),
            ('is_processed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('response', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('discount_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['payment.DiscountCode'], null=True, blank=True)),
            ('send_out_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
        ))
        db.send_create_signal(u'marketing', ['SMS'])

        # Adding model 'MailgunEmail'
        db.create_table(u'marketing_mailgunemail', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('code', self.gf('django.db.models.fields.CharField')(default='07df17c8-f93e-4d2a-b821-864e7df1bf62', unique=True, max_length=50)),
            ('em_from', self.gf('django.db.models.fields.CharField')(default=u'Tavs velo.lv <hi@mans.velo.lv>', max_length=85)),
            ('em_to', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('em_cc', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('em_replyto', self.gf('django.db.models.fields.CharField')(default='pieteikumi@velo.lv', max_length=255)),
            ('subject', self.gf('django.db.models.fields.TextField')()),
            ('html', self.gf('django.db.models.fields.TextField')()),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('is_sent', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('mailgun_id', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
        ))
        db.send_create_signal(u'marketing', ['MailgunEmail'])


    def backwards(self, orm):
        # Deleting model 'SMS'
        db.delete_table(u'marketing_sms')

        # Deleting model 'MailgunEmail'
        db.delete_table(u'marketing_mailgunemail')


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
        u'core.user': {
            'Meta': {'object_name': 'User'},
            'bike_brand': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['core.Choices']"}),
            'birthday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['core.Choices']"}),
            'country': ('django_countries.fields.CountryField', [], {'default': "'LV'", 'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'email_status': ('django.db.models.fields.SmallIntegerField', [], {'default': '10'}),
            'email_validation_code': ('django.db.models.fields.CharField', [], {'default': "'07c3f2b0-8eb0-4213-8fe8-51290fd36875'", 'max_length': '36'}),
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
        u'marketing.mailgunemail': {
            'Meta': {'object_name': 'MailgunEmail'},
            'code': ('django.db.models.fields.CharField', [], {'default': "'41413b8c-b135-406d-8cb1-021aca61a355'", 'unique': 'True', 'max_length': '50'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'em_cc': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'em_from': ('django.db.models.fields.CharField', [], {'default': "u'Tavs velo.lv <hi@mans.velo.lv>'", 'max_length': '85'}),
            'em_replyto': ('django.db.models.fields.CharField', [], {'default': "'pieteikumi@velo.lv'", 'max_length': '255'}),
            'em_to': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'html': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mailgun_id': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.TextField', [], {}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        u'marketing.sms': {
            'Meta': {'object_name': 'SMS'},
            'discount_code': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['payment.DiscountCode']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'response': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'send_out_at': ('django.db.models.fields.DateTimeField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '160'})
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

    complete_apps = ['marketing']