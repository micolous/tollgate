# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'UserProfile'
        db.create_table('frontend_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user', unique=True, to=orm['auth.User'])),
            ('internet_on', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('theme', self.gf('django.db.models.fields.CharField')(default='cake', max_length=30)),
        ))
        db.send_create_signal('frontend', ['UserProfile'])

        # Adding model 'NetworkHost'
        db.create_table('frontend_networkhost', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mac_address', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('ip_address', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('computer_name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('first_connection', self.gf('django.db.models.fields.DateTimeField')()),
            ('user_profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['frontend.UserProfile'], null=True, blank=True)),
            ('online', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('frontend', ['NetworkHost'])

        # Adding model 'Event'
        db.create_table('frontend_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('start', self.gf('django.db.models.fields.DateTimeField')()),
            ('end', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('frontend', ['Event'])

        # Adding model 'EventAttendance'
        db.create_table('frontend_eventattendance', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['frontend.Event'])),
            ('user_profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['frontend.UserProfile'])),
            ('quota_used', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('quota_multiplier', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            ('quota_amount', self.gf('django.db.models.fields.PositiveIntegerField')(default=52428800L)),
            ('quota_unmetered', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('coffee', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('registered_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='registered_by', null=True, to=orm['frontend.UserProfile'])),
            ('registered_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('frontend', ['EventAttendance'])

        # Adding model 'QuotaResetEvent'
        db.create_table('frontend_quotaresetevent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('when', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('event_attendance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['frontend.EventAttendance'])),
            ('performer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='performer', to=orm['frontend.UserProfile'])),
            ('excuse', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('frontend', ['QuotaResetEvent'])

        # Adding model 'NetworkHostOwnerChangeEvent'
        db.create_table('frontend_networkhostownerchangeevent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('when', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('old_owner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='old_owner', null=True, to=orm['frontend.UserProfile'])),
            ('new_owner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='new_owner', null=True, to=orm['frontend.UserProfile'])),
            ('network_host', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['frontend.NetworkHost'])),
        ))
        db.send_create_signal('frontend', ['NetworkHostOwnerChangeEvent'])

        # Adding model 'NetworkUsageDataPoint'
        db.create_table('frontend_networkusagedatapoint', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('when', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('event_attendance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['frontend.EventAttendance'])),
            ('bytes', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('frontend', ['NetworkUsageDataPoint'])

        # Adding model 'Oui'
        db.create_table('frontend_oui', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hex', self.gf('django.db.models.fields.CharField')(unique=True, max_length=6)),
            ('full_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('is_console', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('frontend', ['Oui'])

        # Adding model 'IP4Protocol'
        db.create_table('frontend_ip4protocol', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('has_port', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('frontend', ['IP4Protocol'])

        # Adding model 'IP4PortForward'
        db.create_table('frontend_ip4portforward', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('host', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['frontend.NetworkHost'])),
            ('protocol', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['frontend.IP4Protocol'])),
            ('port', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('external_port', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['frontend.UserProfile'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('frontend', ['IP4PortForward'])


    def backwards(self, orm):

        # Deleting model 'UserProfile'
        db.delete_table('frontend_userprofile')

        # Deleting model 'NetworkHost'
        db.delete_table('frontend_networkhost')

        # Deleting model 'Event'
        db.delete_table('frontend_event')

        # Deleting model 'EventAttendance'
        db.delete_table('frontend_eventattendance')

        # Deleting model 'QuotaResetEvent'
        db.delete_table('frontend_quotaresetevent')

        # Deleting model 'NetworkHostOwnerChangeEvent'
        db.delete_table('frontend_networkhostownerchangeevent')

        # Deleting model 'NetworkUsageDataPoint'
        db.delete_table('frontend_networkusagedatapoint')

        # Deleting model 'Oui'
        db.delete_table('frontend_oui')

        # Deleting model 'IP4Protocol'
        db.delete_table('frontend_ip4protocol')

        # Deleting model 'IP4PortForward'
        db.delete_table('frontend_ip4portforward')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'frontend.event': {
            'Meta': {'ordering': "['start']", 'object_name': 'Event'},
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'start': ('django.db.models.fields.DateTimeField', [], {})
        },
        'frontend.eventattendance': {
            'Meta': {'ordering': "['event', 'user_profile']", 'object_name': 'EventAttendance'},
            'coffee': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['frontend.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quota_amount': ('django.db.models.fields.PositiveIntegerField', [], {'default': '52428800L'}),
            'quota_multiplier': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'quota_unmetered': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'quota_used': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'registered_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'registered_by'", 'null': 'True', 'to': "orm['frontend.UserProfile']"}),
            'registered_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user_profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['frontend.UserProfile']"})
        },
        'frontend.ip4portforward': {
            'Meta': {'object_name': 'IP4PortForward'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['frontend.UserProfile']"}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'external_port': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'host': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['frontend.NetworkHost']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'port': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'protocol': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['frontend.IP4Protocol']"})
        },
        'frontend.ip4protocol': {
            'Meta': {'ordering': "['name']", 'object_name': 'IP4Protocol'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'has_port': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        'frontend.networkhost': {
            'Meta': {'ordering': "['mac_address']", 'object_name': 'NetworkHost'},
            'computer_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'first_connection': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'mac_address': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'online': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'user_profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['frontend.UserProfile']", 'null': 'True', 'blank': 'True'})
        },
        'frontend.networkhostownerchangeevent': {
            'Meta': {'ordering': "['when']", 'object_name': 'NetworkHostOwnerChangeEvent'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network_host': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['frontend.NetworkHost']"}),
            'new_owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'new_owner'", 'null': 'True', 'to': "orm['frontend.UserProfile']"}),
            'old_owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'old_owner'", 'null': 'True', 'to': "orm['frontend.UserProfile']"}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'frontend.networkusagedatapoint': {
            'Meta': {'ordering': "['event_attendance', 'when']", 'object_name': 'NetworkUsageDataPoint'},
            'bytes': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'event_attendance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['frontend.EventAttendance']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'frontend.oui': {
            'Meta': {'ordering': "['hex']", 'object_name': 'Oui'},
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'hex': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '6'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_console': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'frontend.quotaresetevent': {
            'Meta': {'ordering': "['when']", 'object_name': 'QuotaResetEvent'},
            'event_attendance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['frontend.EventAttendance']"}),
            'excuse': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'performer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'performer'", 'to': "orm['frontend.UserProfile']"}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'frontend.userprofile': {
            'Meta': {'ordering': "['user__username']", 'object_name': 'UserProfile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internet_on': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'theme': ('django.db.models.fields.CharField', [], {'default': "'cake'", 'max_length': '30'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user'", 'unique': 'True', 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['frontend']
