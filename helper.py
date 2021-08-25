import tnnhelper
import sys
from pythonping import ping
import psutil
import socket

api_protocol = "http"
api_hostname = "rconfig.di0han.as64636.de.ampr.org"
api_port     = "8000"


def logme(msg):
	print("--> " + str(msg))



logme("Checking system settings....")

#
# Checking HamNET connectivity
#
cfg_avail = ping(api_hostname, size=40, count=10)
if cfg_avail.rtt_avg_ms > 100:
	logme(" ")
	logme(" HUUUUUUUUUUUUPS ")
	logme(" ")
	logme("No valid connection to HamNET configuration service!")
	logme("Exiting now.")
	logme(" ")
	sys.exit(-1)


#
# Checking if TNN is running
#
tnnRunning = False
for proc in psutil.process_iter():
	if proc.name().lower() == "tnn":
		tnnRunning = True
if not tnnRunning:
	logme(" ")
	logme(" HUUUUUUUUUUUUPS ")
	logme(" ")
	logme("TheNetNode/TNN is not running!")
	logme("Exiting now.")
	logme(" ")
	sys.exit(-1)


#
# Check if TNN Port 8081 is available
#
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('127.0.0.1', 8081))
if result != 0:
	logme(" ")
	logme(" HUUUUUUUUUUUUPS ")
	logme(" ")
	logme("TheNetNode/TNN is not listening on HTTP 8081!")
	logme("Exiting now.")
	logme(" ")
	sys.exit(-1)



#
# Check if default CALLSIGN is configured for TNN
#
tnn179_f = "/usr/local/tnn/tnn179.pas"
tnn179   = open(tnn179_f, "r")
tnn179_c = tnn179.read()
if "XX0XX" in tnn179_c:
	logme(" ")
	logme(" HUUUUUUUUUUUUPS ")
	logme(" ")
	logme("Default CALLSIGN for TNN detected! Please check your configuration:")
	logme(tnn179_f)
	logme("Exiting now.")
	logme(" ")
	sys.exit(-1)



logme("Connection to API")
tnn = tnnhelper.tnnhelper(api_protocol + "://" + api_hostname + ":" + api_port)

logme("Fetching link data for TNN")
tnn.get_links()

l_measure = {}
latency   = {}
cnt_links = 0
max_links = 5
new_links = []

logme("Trying to measure link quality to known TNN Nodes")
for key, value in tnn.nodes.items():
	if key.upper() != tnn.my_call.upper():
		p = ping(value, size=40, count=10)
		logme("Found Node: " + key + " -> " + value + " -> " + str(p.rtt_avg_ms) + "ms")
		l_measure[key] = p.rtt_avg_ms

logme("Sorting measure results for building links")
sorted_measure = sorted(l_measure, key=l_measure.get)
for w in sorted_measure:
	latency[w] = l_measure[w]


logme("Building links")
for key, value in latency.items():
	if cnt_links < max_links:
		logme("Checking Node " + str(key) + " for existing link")
		new_links.append(str(key).upper())
		if key.upper() in tnn.links:
			logme("Link is already created, nothing to do with node " + key)
		else:
			logme("Creating Link in TNN and API database")
			tnn.create_link(str(key).upper())
	cnt_links = cnt_links + 1


logme("Retrieving again the link data from API")
tnn.get_links()
logme("Cleaning up old links")
for key, value in tnn.links.items():
	logme("Checking Link to Node " + key)
	if key.upper() in new_links:
		logme("Keep link, latency is good")
	else:
		logme("Link should be deleted")
		tnn.delete_link(value)


logme("Saving configuration to TNN")
tnn.cmd_tnn("spa")

logme("Finished.")


