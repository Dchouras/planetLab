import os
from django.db import models
from core.models import PlCoreBase
#from core.models import Deployment
from core.models import Tag
from django.contrib.contenttypes import generic
from geoposition.fields import GeopositionField

class Site(PlCoreBase):
    """
        A logical grouping of Nodes that are co-located at the same geographic location, which also typically corresponds to the Nodes' location in the physical network.
    """
    tenant_id = models.CharField(null=True, blank=True, max_length=200, help_text="Keystone tenant id")
    name = models.CharField(max_length=200, help_text="Name for this Site")
    site_url = models.URLField(null=True, blank=True, max_length=512, help_text="Site's Home URL Page")
    enabled = models.BooleanField(default=True, help_text="Status for this Site")
    location = GeopositionField()
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    login_base = models.CharField(max_length=50, unique=True, help_text="Prefix for Slices associated with this Site")
    is_public = models.BooleanField(default=True, help_text="Indicates the visibility of this site to other members")
    abbreviated_name = models.CharField(max_length=80)

    deployments = models.ManyToManyField('Deployment', blank=True, related_name='sites')
    #deployments = models.ManyToManyField('Deployment', through='SiteDeployments', blank=True)
    tags = generic.GenericRelation(Tag)

    def __unicode__(self):  return u'%s' % (self.name)

    def can_update(self, user):
        if user.is_readonly:
            return False
        if user.is_admin:
            return True
        site_privs = SitePrivilege.objects.filter(user=user, site=self)
        for site_priv in site_privs:
            if site_priv.role.role == 'pi':
                return True
        return False 

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = Site.objects.all()
        else:
            site_ids = [sp.site.id for sp in SitePrivilege.objects.filter(user=user)]
            site_ids.append(user.site.id)
            qs = Site.objects.filter(id__in=site_ids)
        return qs


class SiteRole(PlCoreBase):

    ROLE_CHOICES = (('admin','Admin'),('pi','PI'),('tech','Tech'),('billing','Billing'))
    role = models.CharField(choices=ROLE_CHOICES, unique=True, max_length=30)

    def __unicode__(self):  return u'%s' % (self.role)

class SitePrivilege(PlCoreBase):

    user = models.ForeignKey('User', related_name='site_privileges')
    site = models.ForeignKey('Site', related_name='site_privileges')
    role = models.ForeignKey('SiteRole')

    def __unicode__(self):  return u'%s %s %s' % (self.site, self.user, self.role)

    def save(self, *args, **kwds):
        super(SitePrivilege, self).save(*args, **kwds)

    def delete(self, *args, **kwds):
        super(SitePrivilege, self).delete(*args, **kwds)

    def can_update(self, user):
        return self.site.can_update(user)

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = SitePrivilege.objects.all()
        else:
            sp_ids = [sp.id for sp in SitePrivilege.objects.filter(user=user)]
            qs = SitePrivilege.objects.filter(id__in=sp_ids)
        return qs

class Deployment(PlCoreBase):
    name = models.CharField(max_length=200, unique=True, help_text="Name of the Deployment")
    #sites = models.ManyToManyField('Site', through='SiteDeployments', blank=True)

    def __unicode__(self):  return u'%s' % (self.name)

    @staticmethod
    def select_by_user(user):
        return Deployment.objects.all()

class DeploymentRole(PlCoreBase):

    ROLE_CHOICES = (('admin','Admin'),)
    role = models.CharField(choices=ROLE_CHOICES, unique=True, max_length=30)

    def __unicode__(self):  return u'%s' % (self.role)

class DeploymentPrivilege(PlCoreBase):

    user = models.ForeignKey('User', related_name='deployment_privileges')
    deployment = models.ForeignKey('Deployment', related_name='deployment_privileges')
    role = models.ForeignKey('DeploymentRole')

    def __unicode__(self):  return u'%s %s %s' % (self.deployment, self.user, self.role)

    def can_update(self, user):
        if user.is_readonly:
            return False
        if user.is_admin:
            return True
        dprivs = DeploymentPrivilege.objects.filter(user=user)
        for dpriv in dprivs:
            if dpriv.role.role == 'admin':
                return True
        return False

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = DeploymentPrivilege.objects.all()
        else:
            dpriv_ids = [dp.id for dp in DeploymentPrivilege.objects.filter(user=user)]
            qs = DeploymentPrivilege.objects.filter(id__in=dpriv_ids)
        return qs 

class SiteDeployments(PlCoreBase):
    site = models.ForeignKey(Site)
    deployment = models.ForeignKey(Deployment)
    tenant_id = models.CharField(null=True, blank=True, max_length=200, help_text="Keystone tenant id")    

    @staticmethod
    def select_by_user(user):
        return SiteDeployments.objects.all()

    #class Meta:
    #    db_table = 'core_site_deployments'
    #    #auto_created = Site

