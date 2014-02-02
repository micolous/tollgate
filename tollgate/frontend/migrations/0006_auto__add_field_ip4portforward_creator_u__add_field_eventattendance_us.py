# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'IP4PortForward.creator_u'
        db.add_column(u'frontend_ip4portforward', 'creator_u',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='ipv4_port_forwards_created', null=True, to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'EventAttendance.user'
        db.add_column(u'frontend_eventattendance', 'user',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='attendances', null=True, to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'EventAttendance.registrar'
        db.add_column(u'frontend_eventattendance', 'registrar',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='registrations', null=True, to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'QuotaResetEvent.user'
        db.add_column(u'frontend_quotaresetevent', 'user',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='resets_performed', null=True, to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'NetworkHostOwnerChangeEvent.old_owner_u'
        db.add_column(u'frontend_networkhostownerchangeevent', 'old_owner_u',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='old_host_changes', null=True, to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'NetworkHostOwnerChangeEvent.new_owner_u'
        db.add_column(u'frontend_networkhostownerchangeevent', 'new_owner_u',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='new_host_changes', null=True, to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'NetworkHost.owner'
        db.add_column(u'frontend_networkhost', 'owner',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='hosts', null=True, to=orm['auth.User']),
                      keep_default=False)

        # Adding unique constraint on 'NetworkHost', fields ['mac_address']
        db.create_unique(u'frontend_networkhost', ['mac_address'])

    def backwards(self, orm):
        # Removing unique constraint on 'NetworkHost', fields ['mac_address']
        db.delete_unique(u'frontend_networkhost', ['mac_address'])

        # Deleting field 'IP4PortForward.creator_u'
        db.delete_column(u'frontend_ip4portforward', 'creator_u_id')

        # Deleting field 'EventAttendance.user'
        db.delete_column(u'frontend_eventattendance', 'user_id')

        # Deleting field 'EventAttendance.registrar'
        db.delete_column(u'frontend_eventattendance', 'registrar_id')

        # Deleting field 'QuotaResetEvent.user'
        db.delete_column(u'frontend_quotaresetevent', 'user_id')

        # Deleting field 'NetworkHostOwnerChangeEvent.old_owner_u'
        db.delete_column(u'frontend_networkhostownerchangeevent', 'old_owner_u_id')

        # Deleting field 'NetworkHostOwnerChangeEvent.new_owner_u'
        db.delete_column(u'frontend_networkhostownerchangeevent', 'new_owner_u_id')

        # Deleting field 'NetworkHost.owner'
        db.delete_column(u'frontend_networkhost', 'owner_id')

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
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'frontend.event': {
            'Meta': {'ordering': "['start']", 'object_name': 'Event'},
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'start': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'frontend.eventattendance': {
            'Meta': {'ordering': "['event', 'user_profile']", 'object_name': 'EventAttendance'},
            'coffee': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['frontend.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quota_amount': ('django.db.models.fields.BigIntegerField', [], {'default': '157286400L'}),
            'quota_multiplier': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'quota_unmetered': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'quota_used': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'registered_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'registered_by'", 'null': 'True', 'to': u"orm['frontend.UserProfile']"}),
            'registered_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'registrar': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'registrations'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attendances'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'user_profile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['frontend.UserProfile']"})
        },
        u'frontend.ip4portforward': {
            'Meta': {'object_name': 'IP4PortForward'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['frontend.UserProfile']"}),
            'creator_u': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ipv4_port_forwards_created'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'external_port': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'host': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['frontend.NetworkHost']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            'port': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'protocol': ('django.db.models.fields.related.ForeignKey', [], {'default': '6', 'to': u"orm['frontend.IP4Protocol']"})
        },
        u'frontend.ip4protocol': {
            'Meta': {'ordering': "['name']", 'object_name': 'IP4Protocol'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'has_port': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        u'frontend.networkhost': {
            'Meta': {'ordering': "['mac_address']", 'object_name': 'NetworkHost'},
            'computer_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'first_connection': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'mac_address': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '12'}),
            'online': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'hosts'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'user_profile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['frontend.UserProfile']", 'null': 'True', 'blank': 'True'})
        },
        u'frontend.networkhostownerchangeevent': {
            'Meta': {'ordering': "['when']", 'object_name': 'NetworkHostOwnerChangeEvent'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network_host': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['frontend.NetworkHost']"}),
            'new_owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'new_owner'", 'null': 'True', 'to': u"orm['frontend.UserProfile']"}),
            'new_owner_u': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'new_host_changes'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'old_owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'old_owner'", 'null': 'True', 'to': u"orm['frontend.UserProfile']"}),
            'old_owner_u': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'old_host_changes'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'frontend.networkusagedatapoint': {
            'Meta': {'ordering': "['event_attendance', 'when']", 'object_name': 'NetworkUsageDataPoint'},
            'bytes': ('django.db.models.fields.BigIntegerField', [], {}),
            'event_attendance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['frontend.EventAttendance']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'frontend.oui': {
            'Meta': {'ordering': "['hex']", 'object_name': 'Oui'},
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'hex': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '6'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_console': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        u'frontend.quotaresetevent': {
            'Meta': {'ordering': "['when']", 'object_name': 'QuotaResetEvent'},
            'event_attendance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['frontend.EventAttendance']"}),
            'excuse': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'performer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'performer'", 'to': u"orm['frontend.UserProfile']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'resets_performed'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'frontend.userprofile': {
            'Meta': {'ordering': "['user__username']", 'object_name': 'UserProfile'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internet_on': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'maximum_quota_resets': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'maximum_quota_signins': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'theme': ('django.db.models.fields.CharField', [], {'default': "'cake'", 'max_length': '30'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user'", 'unique': 'True', 'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['frontend']