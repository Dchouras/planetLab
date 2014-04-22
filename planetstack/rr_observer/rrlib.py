import os
import base64
import string
import sys

if __name__ == '__main__':
    sys.path.append("/opt/planetstack")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "planetstack.settings")

from planetstack.config import Config
from core.models import Service
from requestrouter.models import RequestRouterService
from util.logger import Logger, logging

logger = Logger(level=logging.INFO)

class RequestRouterLibrary:
	
	def __init__(self):
		pass
	
	def gen_slice_file(self, service=None):
        	""" generates host file for the slice of request router
	    	to be used by ansible to push configuration files
        	"""

		if (service is None ):
			service = RequestRouterService.objects.get()


		fn = "./slices"
		f = open(fn, "w")

        	for slice in service.service.all():
            		name = slice.name
            		for sliver in slice.slivers.all():
	    			f.write("%s\n" % sliver.node.name)
	
