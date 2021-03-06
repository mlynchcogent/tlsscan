import sys, datetime, argparse, timeit, signal, os
from TLSScanner import TLSScanner
from  multiprocessing import Process
try:
	from scapy.all import TLS
	from scapy.all import *
except ImportError:
	from scapy_ssl_tls.ssl_tls import *


parser = argparse.ArgumentParser(usage= sys.argv[0]+ ' <website> [options]', 
	description='SSL/TLS website passive analyzer.',
	epilog='''
...            Have fun! ...  
''')

parser.add_argument('website',  type=str, action='store', help='website to scan.')
parser.add_argument('-p', '--port',  type=int, action='store',default=443, help='TCP port to test (default: 443).')
parser.add_argument('--fullscan', action='store_true', help='start a full scan of the website.')
parser.add_argument('--ciphers', action='store_true', help='start a scan of server supported cipher suites.')
parser.add_argument('--suppproto', action='store_true', help='perform only a scan of supported protocols version.')
parser.add_argument('--certscan', action='store_true', help='perform only a scan of the server certificate.')
parser.add_argument('-d', '--delay', type=int, action='store', default=0, help="wait N milliseconds between each request.")
parser.add_argument('-vv', '--verbose', action='store_true', default=False, help="show verbose information.")
parser.add_argument('-w', '--write',  action='store_true', help='write scan output to file.')
parser.add_argument('-s', '--sniff', action='store_true', help='save full packet capture in .pcap format. (NEED SUDO PRIVILEGES)')
parser.add_argument('-t', '--torify', action='store_true', help='make the script running under Tor network.')
parser.add_argument('-i', '--input',  type=argparse.FileType('r'), action='store', help='input file with website list (\\n separated.')
parser.add_argument('-v', '--version', action='version', version='version 0.1', help='show program version.')


def main():
	args = parser.parse_args()
	#print args
	print "\n"
	
	if args.write:
		sys.stdout = open(args.website + "_" + str(datetime.datetime.now()).replace(" ","_")+".txt", 'w')
	
	print "\033c"
	printScreen()


	target = (args.website, int(args.port))
	start_time = timeit.default_timer()
	if args.input != None:
		print "--input not yet supported, working on"

	if args.sniff and args.torify:
		print "Temporary unsupported function. Please use -t and -s one without the other. "
		exit(0)

	scanner = TLSScanner(target=target, time_delay=args.delay, verbose=args.verbose, 
		to_file = args.write, torify=args.torify)
	
	sniffer_process = None
	
	if args.sniff:
		if os.geteuid() != 0:
			exit("You need to have root privileges to run SNIFFING mode.\nExiting.")

		filename = args.write + ".pcap" if args.write else "pcap_"+str(datetime.datetime.now()).replace(" ","_")+".pcap"

		sniffer_process = Process(target=sniffer, args=(filename, scanner.target[0]))
		sniffer_process.start()

	mode = ''
	if args.ciphers:
		mode = TLSScanner.MODE.CIPHERS
	elif args.certscan:
		mode = TLSScanner.MODE.CERTSCAN
	elif args.suppproto:
		mode = TLSScanner.MODE.SUPPROTO
	if args.fullscan:
		mode = TLSScanner.MODE.FULLSCAN

	try:
		scanner.scan(mode)
	except Exception as ex:
		print ex.message
		print "sorry, report the problem."

	if sniffer_process != None:
		sniffer_process.terminate() 
	print "Finished in --- %s seconds ---\n\n" % (timeit.default_timer()-start_time)

def signal_handler(signal, frame):
    raise KeyboardInterrupt

def sniffer(filename, ip):
	filter = "host " + str(ip)
	signal.signal(signal.SIGTERM, signal_handler)
	try:
		wrpcap(filename, sniff(filter=filter))
	except ValueError as ex:
			print ex.message
			print "Sorry, something went wrong with the sniffer process."

def printScreen():
	print(
'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|                                             |
|   ############  ###         #############   |
|   ############  ###         #############   | Scan a website and analyze 
|       ###       ###         ###             | HTTPS configurations and 
|       ###       ###         #############   | certificates.
|       ###       ###         #############   |
|       ###       ###                   ###   |
|       ###       ###                   ###   | Find misconfigurations
|       ###       ##########  #############   | which could lead to 
|       ###       ##########  #############   | potential attacks.
|                                             |
| and SSL for HTTPS  Passive Security Scanner |
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
''')


if __name__ == '__main__':
	main()