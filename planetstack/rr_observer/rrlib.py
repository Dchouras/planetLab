import os
import base64
import string
import sys
from sets import Set
if __name__ == '__main__':
    sys.path.append("/opt/planetstack")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "planetstack.settings")

from planetstack.config import Config
from core.models import Service
from requestrouter.models import RequestRouterService, ServiceMap
from util.logger import Logger, logging
import rrlib_config

logger = Logger(level=logging.INFO)

'''
Conventions:
1) All dnsredir backend will listen at port 9000+ servicemap.pk ( where pk is the primary key generated in django model)
'''

class RequestRouterLibrary:

	def __init__(self):
		pass
	
	def gen_slice_info(self, service=None):
        	"""generates sliver information from slice of request router
        	"""

		if (service is None ):
			service = RequestRouterService.objects.get()

		mapping = {}
	
        	for slice in service.service.all():
            		name = slice.name
            		for sliver in slice.slivers.all():
	    			mapping[sliver.name] = str(sliver.ip)

		return mapping

	def gen_servicemap_slice_info(self, servicemap):
                """generates sliver information from slice of servicemap
                """

		wzone = Set(['arizona', 'stanford', 'on.lab', 'housten']) # zone=1 in cooden.conf
		ezone = Set(['princeton', 'atlanta', 'new york', 'georgia tech']) # zone=2 in coodeen.conf

                mapping_zone = {}
		mapping_ip = {}
		slice = servicemap.slice
                name = slice.name
                for sliver in slice.slivers.all():
			mapping_ip[sliver.name] = str(sliver.ip)
			site = sliver.node.site.name
			if(site.lower() in wzone):
				mapping_zone[sliver.name] = str(1)
			else:
				mapping_zone[sliver.name] = str(2)

                return mapping_ip, mapping_zone


	def gen_slice_file(self, service):
                """ generates host file for the slice information
                to be used by ansible to push configuration files
                """

		mapping = self.gen_slice_info(service)

                fn = "/etc/ansible/requestrouter/hosts"
                f = open(fn, "w")

                for (k,v) in mapping.items():
                	f.write("%s\n" % k)


	def get_servicemap_uid(self, servicemap):
		seq = ("service_", str(servicemap.pk));
		return "".join(seq)

	def get_service_port(self, servicemap):
                return str(9000+servicemap.pk)

	def gen_dnsredir_serviceconf(self, servicemap):
		objname = self.get_servicemap_uid(servicemap)
	
		rr_mapping = self.gen_slice_info(None)
	
		#generate dnsredir.conf file parameters to be used in static file.
		mapping = {}
		mapping["port_listen"] = self.get_service_port(servicemap)
		mapping["configdir"] = rrlib_config.DNSREDIR_CONFIGDIR_PREFIX+objname+".d"
		mapping["logdir"] = rrlib_config.DNSREDIR_LOGDIR_PREFIX+objname+".d"
		mapping["pidfile"] = rrlib_config.DNSREDIR_PIDFILE_PREFIX+objname+".pid"
		mapping["domain_name"] = servicemap.prefix		

		#generate dnsredir.conf file 

		fn = "./temp_config/dnsredir/"+objname+".conf"
		f = open(fn, "w")
		f.write("""
[dnsredir]

# specify a name server for the domain name
#
""")
		for (k,v) in rr_mapping.items():
                        f.write(mapping["domain_name"]+" NS "+k+" "+v+" 86400 \n" % mapping)


		f.write("""
# Default TTL for an A record lookup (default: 30)
#
Default_TTL=30

# port on which to listen
#
Port=%(port_listen)s

# configuration directory (default: /etc/dnsredir/config/)
#
ConfigDir=%(configdir)s

# directory in which to create log files (default: ./log)
#
LogDir=%(logdir)s

# directory containing the redirection maps. If dir is relative (doesn't start with '/') it is relative to configDir.
#
MapsDir=mapsd

# port on which HTTP requests are received (default: 80)
#
HttpRequestPort=80

""" % mapping)

		#generate configdirectory
		
		os.mkdir("./temp_config/dnsredir/"+objname+".d")
		
		#geenrate codeen_nodes.conf
		mapping_ip, mapping_zone = self.gen_servicemap_slice_info(servicemap)

		codeen_name = "./temp_config/dnsredir/"+objname+".d/codeen_nodes.conf"
                f = open(codeen_name, "w")
		for (k,v) in mapping_zone.items():
                        f.write(k+" zone="+v+" \n")

		iptxt = "./temp_config/dnsredir/"+objname+".d/node-to-ip.txt"
		f = open(iptxt, "w")
		for (k,v) in mapping_ip.items():
			f.write(k+" "+v+" \n")

		#generate maps directory
		os.mkdir("./temp_config/dnsredir/"+objname+".d/mapsd")

		# redirection map
		map = "./temp_config/dnsredir/"+objname+".d/mapsd/map.conf"
		f = open(map, "w")
		f.write("prefix "+servicemap.prefix+" \n")
		f.write("map 1.2.3.4/24 zone 1 || zone 2 \n")
		f.write("map 1.2.3.4/24 zone 2 || zone 1 \n")


	def gen_dnsdemux_serviceconf(self, servicemap):
		'''
		generates frontend service*.conf file for each of the service
		It assumes that there is a dnsdemux frontend running on the RR istallation and will
		just add a conf file for each service in /etc/dnsdemux/default/backends.d 
		'''
		objname = self.get_servicemap_uid(servicemap)
		#generate dnsdemux.conf file parameters to be used in static file.
		mapping = {}
		mapping["port_listen"] = self.get_service_port(servicemap)
		mapping["domain_name"] = servicemap.prefix	
		#generate service specifc .conf file

		fn = "./temp_config/dnsdemux/"+objname+".conf"
		f = open(fn, "w")
		f.write("""
Forward 127.0.0.1  %(port_listen)s %(domain_name)s 
""" % mapping)

	
	def teardown_temp_configfiles(self, objname):
		os.remove("./temp_config/dnsdemux/"+objname+".conf")
		os.remove("./temp_config/dnsredir/"+objname+".d/mapsd/map.conf")
		os.rmdir("./temp_config/dnsredir/"+objname+".d/mapsd")
		os.remove("./temp_config/dnsredir/"+objname+".d/node-to-ip.txt")
		os.remove("./temp_config/dnsredir/"+objname+".d/codeen_nodes.conf")
		os.rmdir("./temp_config/dnsredir/"+objname+".d")
		os.remove("./temp_config/dnsredir/"+objname+".conf")
