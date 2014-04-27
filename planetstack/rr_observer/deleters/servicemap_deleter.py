import os
import sys
import traceback
from requestrouter.models import ServiceMap
from observer.deleter import Deleter

parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

class ServiceMapDeleter(Deleter):
        model='ServiceMap'

        def __init__(self, **args):
            Deleter.__init__(self, **args)

        def call(self, pk, model_dict):
	    try:
                servicemap = ServiceMap.objects.get(pk=pk)
		print "XXX delete ServiceMap %s", servicemap.name
                return True
            except Exception, e:
                traceback.print_exc()
                logger.exception("Failed to erase map '%s'" % map_name)
                return False

if __name__ == "__main__":
	smap = ServiceMapDeleter()
    	smap.call( 6, {'name': 'Service23'} )
