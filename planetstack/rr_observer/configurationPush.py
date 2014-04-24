import ansible.playbook
import ansible.constants as C
import ansible.utils.template
from ansible import errors
from ansible import callbacks
from ansible import utils
from subprocess import call
def main():
	'''stats = callbacks.AggregateStats()
	playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
	runner_cb = callbacks.PlaybookRunnerCallbacks(stats, verbose=utils.VERBOSITY)
	pb = ansible.playbook.PlayBook(playbook="playbook/site.yml",
					callbacks=playbook_cb,
            				runner_callbacks=runner_cb,
            				stats=stats
					)
	result = pb.run()
	print result
	'''
	call("ansible-playbook playbook/site.yml --extra-vars \"name=service_1\"", shell=True)
	

if __name__ == "__main__":
        main()
