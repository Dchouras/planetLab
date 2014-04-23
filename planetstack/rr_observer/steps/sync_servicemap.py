#!/usr/bin/python

import os
import sys
import base64
import traceback
from django.db.models import F, Q
from planetstack.config import Config
from observer.syncstep import SyncStep
from core.models import Service
from requestrouter.models import ServiceMap
from util.logger import Logger, logging

parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

from rrlib import RequestRouterLibrary

logger = Logger(level=logging.INFO)

class SyncServiceMap(SyncStep, RequestRouterLibrary):
    provides=[ServiceMap]
    requested_interval=0

    def __init__(self, **args):
        SyncStep.__init__(self, **args)
	RequestRouterLibrary.__init__(self)

    def fetch_pending(self):
	try:
        	ret = ServiceMap.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))
        	return ret
	except Exception, e:
        	traceback.print_exc()
            	return None

    def sync_record(self, servicemap):
	try:
		print "sync! %s " % self.get_servicemap_uid(servicemap)
		self.gen_dnsredir_serviceconf(servicemap)
		self.gen_dnsdemux_serviceconf(servicemap)
        	# TODO: finish this
	except Exception, e:
                traceback.print_exc()
                return False

if __name__ == "__main__":
    sv = SyncServiceMap()

    recs = sv.fetch_pending()

    for rec in recs:
        sv.sync_record( rec )
