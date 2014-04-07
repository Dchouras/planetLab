import ansible.playbook
import ansible.constants as C
import ansible.utils.template
from ansible import errors
from ansible import callbacks
from ansible import utils

def main():
	stats = callbacks.AggregateStats()
	playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
	runner_cb = callbacks.PlaybookRunnerCallbacks(stats, verbose=utils.VERBOSITY)
	pb = ansible.playbook.PlayBook(playbook="ping.yml",
					callbacks=playbook_cb,
            				runner_callbacks=runner_cb,
            				stats=stats
					)
	result = pb.run()
	print result

if __name__ == "__main__":
        main()
