import os
import sys
from requestrouter.models import ServiceMap
from observer.deleter import Deleter

parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

class ServiceMapDeleter(Deleter):
        model='ServiceMap'

        def __init__(self, **args):
            Deleter.__init__(self, **args)

        def call(self, pk, model_dict):
            print "XXX delete ServiceMap", model_dict
