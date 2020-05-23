import requests
from requests.auth import HTTPBasicAuth
import urllib
import json
import os
import time
from datetime import datetime
import configparser

class tnnhelper:
	api_url     = "http://192.168.101.135:8000"
	api_timeout = 4

	config = configparser.RawConfigParser()
	config_file = "./tnnhelper.ini"

	my_call = ""
	my_ident = ""
	my_callid = -1

	tnn_host = "127.0.0.1"
	tnn_port = "8081"
	tnn_pas  = "/usr/local/tnn/tnn179.pas"
	tnn_ax25ip = -1

	nodes = {}
	links = {}

	http_response = ""

	msg = {}
	msg[0] = "Could not connect to API, please make sure\nthat you have active hamnet connection running."
	msg[1] = "Could not read configuration file!\nMaybe there is an bad file permission setting?"
	msg[2] = "Could not write configuration file!\nPlease check file system permissions!"
	msg[3] = "API responds with an error,\nmore information:\n"
	msg[4] = "Could not read TheNetNode configuration file!\nPlease check file permissions and path..."
	msg[5] = "Could not connect to TheNetNode WebUI API!\nPlease check that tnn is running and WebUI is enabled.\nFurther, please check port settings..."

	def __init__(self, api_url = ""):
		if api_url != "":
			self.api_url = api_url
		self.config_load()
		if self.my_call == "":
			self.my_call = self.get_tnnconfig(self.tnn_pas, 16)
		if self.my_ident == "":
			self.my_ident = self.get_tnnconfig(self.tnn_pas, 13)
		self.create_node()
		if self.tnn_ax25ip < 0:
			self.tnn_ax25ip = int(self.tnn_hwport("AX25IP"))

	def get_mycall(self):
		return self.my_call

	def get_response(self):
		return self.http_response


	def config_load(self):
		try:
			self.config.read(self.config_file)
		except:
			self.returnmsg("def config_load():\n" + self.msg[1])
		if 'general' in self.config:
			self.api_url = self.config["general"]["api_url"]
			self.my_call = self.config["general"]["my_call"]
			self.my_callid = self.config["general"]["my_callid"]
			self.my_ident = self.config["general"]["my_ident"]
		if 'tnn' in self.config:
			self.tnn_host = self.config["tnn"]["host"]
			self.tnn_port = self.config["tnn"]["port"]
			self.tnn_pas  = self.config["tnn"]["pas"]
			self.tnn_ax25ip = self.config["tnn"]["ax25ip_port"]
		if 'nodes' in self.config:
			for node in self.config["nodes"]:
				self.nodes[node] = self.config["nodes"][node]
		if 'links' in self.config:
			for link in self.config["links"]:
				self.links[link] = self.config["links"][link]


	def config_save(self, cleanup = False):
		if cleanup:
			if 'links' in self.config:
				self.config.remove_section('links')
			if 'nodes' in self.config:
				self.config.remove_section('nodes')
		if not 'general' in self.config:
			self.config.add_section('general')
		if not 'tnn' in self.config:
			self.config.add_section('tnn')
		if not 'nodes' in self.config:
			self.config.add_section('nodes')
		if not 'links' in self.config:
			self.config.add_section('links')
		self.config.set('general', 'api_url', self.api_url)
		self.config.set('general', 'my_call', self.my_call)
		self.config.set('general', 'my_callid', self.my_callid)
		self.config.set('general', 'my_ident', self.my_ident)
		self.config.set('tnn', 'host', self.tnn_host)
		self.config.set('tnn', 'port', self.tnn_port)
		self.config.set('tnn', 'pas', self.tnn_pas)
		self.config.set('tnn', 'ax25ip_port', self.tnn_ax25ip)
		for node in self.nodes:
			self.config.set('nodes', node, self.nodes[node])
		for link in self.links:
			self.config.set('links', link, self.links[link])
		try:
			with open(self.config_file, 'w') as configfile:
				self.config.write(configfile)
		except:
			self.returnmsg("def config_save():\n" + msg[2])


	def checkerror(self, resp):
		self.http_response = resp
		if ("message" in resp and (resp["message"] != "success" and resp["message"] != "deleted")) or ("error" in resp):
			self.returnmsg("def checkerror():\n" + msg[3] + resp)
			exit(1)


	def returnmsg(self, msg):
		print("\n\n")
		print(msg)
		print("\n\n")
		exit(1)


	def get_nodes(self, raw = False):
		try:
			res = requests.get(self.api_url + "/api/node", timeout=self.api_timeout)
			response = res.json()
		except:
			self.returnmsg("def get_nodes():\n" + msg[0])
		self.checkerror(response)
		for node in response["data"]:
			self.nodes[node["callsign"]] = node["ipaddr"]
			if self.my_call.upper() == node["callsign"].upper():
				self.my_callid = node["id"]
		if raw:
			return response["data"]

	def create_node(self):
		self.get_nodes()
		if self.my_callid < 0:
			headers = {'Content-type': 'application/json'}
			mydata = {}
			mydata["callsign"] = self.my_call
			mydata["callident"] = self.my_ident
			payload = json.dumps(mydata)
			try:
				res = requests.post(self.api_url + "/api/node/", data=payload, headers=headers, timeout=self.api_timeout)
				self.checkerror(res.json())
				self.get_nodes()
			except:
				self.returnmsg("def create_node()\n" + self.msg[0])


	def get_links(self, raw = False):
		updateTNN = False
		try:
			res = requests.get(self.api_url + "/api/link/" + self.my_call, timeout=self.api_timeout)
			response = res.json()
		except:
			self.returnmsg("def get_links()\n" + self.msg[0])
		self.checkerror(response)
		newlinks = {}
		cleanup = False
		if 'data' in response:
			for link in response["data"]:
				if self.my_call == link["callleft"] and link["callleft"] not in self.links:
					newlinks[link["callright"]] = 1
					updateTNN = True
				if self.my_call == link["callright"] and link["callright"] not in self.links:
					newlinks[link["callleft"]] = 1
					updateTNN = True


			for linkold in self.links:
				if linkold not in newlinks:
					updateTNN = True
					cleanup = True
					break

			if updateTNN:
				self.links = newlinks
				self.tnn_updateax25route()
				self.tnn_updatelinks()
				self.tnn_updateconv()
				self.config_save(cleanup)

			if raw:
				return response["data"]


	def create_link(self, callsign):
		headers = {'Content-type': 'application/json'}
		mydata = {}
		mydata["callleft"] = self.my_call
		mydata["callright"] = callsign
		payload = json.dumps(mydata)
		try:
			res = requests.post(self.api_url + "/api/link", data=payload, headers=headers, timeout=self.api_timeout)
			response = res.json()
		except:
			self.returnmsg("def create_link():\n" + self.msg[0])
		self.checkerror(response)
		self.get_links()


	def delete_link(self, linkid):
                headers = {'Content-type': 'application/json'}
		try:
	                res = requests.delete(self.api_url + "/api/link/" + str(linkid), headers=headers, timeout=self.api_timeout)
	                response = res.json()
		except:
			self.returnmsg("def delete_link():\n" + self.msg[0])
                self.checkerror(response)
                self.get_links()


	def get_tnnconfig(self, tnnconfig, linenum):
		try:
			with open(tnnconfig) as fp:
				for i, line in enumerate(fp):
					if i == (linenum-1):
						return line.replace('\n','').replace('\r','').replace(' ','').replace('\t','')
		except:
			self.returnmsg("def get_tnnconfig():\n" + self.msg[4])
		return False


	def cmd_tnn(self, cfgstring):
		cmdstring = urllib.pathname2url(cfgstring)
		try:
			res = requests.post("http://" + self.tnn_host + ":" + self.tnn_port + "/cmd?cmd=" + cmdstring, timeout=self.api_timeout, auth=HTTPBasicAuth(self.my_call, ""))
			response = res.text
		except:
			self.returnmsg("def cmd_tnn():\n" + self.msg[5])
		return response


	def tnn_hwport(self, hw = "AX25IP"):
		r = self.cmd_tnn("port")
		for line in r.splitlines():
			if hw in line:
				fields = line.split()
				return fields[0]
		return False

	def tnn_l7port(self, l7 = "HTTPD"):
		r = self.cmd_tnn("port")
		for line in r.splitlines():
			if l7 in line:
				fields = line.split()
				return fields[-1]


	def tnn_updatelinks(self):
		r = self.cmd_tnn("links")
		for link in self.links:
			addLink = True
			for line in r.splitlines():
				if not self.my_call in line and not "----" in line and not "pre>" in line:
					f = line.split()
					c = f[2].split(':')[1]
					if c == link:
						addLink = False
			if addLink:
				self.cmd_tnn("links + i " + str(self.tnn_ax25ip) + " " + link[-3:].lower() + ":" + link)
				"""self.links[link] = self.links[link] + 1"""

		for line in r.splitlines():
			if not self.my_call in line and not "----" in line and not "pre>" in line:
				f = line.split()
				c = f[2].split(':')[1]
				if not c in self.links:
					rm = self.cmd_tnn("links - i " + str(self.tnn_ax25ip) + " " + f[2])


	def tnn_updateax25route(self):
		r = self.cmd_tnn("axip")
		for link in self.links:
			addRoute = True
			for line in r.splitlines():
				if "UDP" in line and not "UDP-Port" in line:
					f = line.split()
					c = f[0]
					if c == link:
						addRoute = False
			if addRoute:
				self.cmd_tnn("axip r + " + link + " " + self.nodes[link.lower()] + " udp 10093")
				"""self.links[link] = self.links[link] + 1"""

		for line in r.splitlines():
			if "UDP" in line and not "UDP-Port" in line:
				f = line.split()
				c = f[0]
				if not c in self.links:
					rm = self.cmd_tnn("axip r - " + c)



	def tnn_updateconv(self):
		r = self.cmd_tnn("conv c")
		for link in self.links:
			addConv = True
			for line in r.splitlines():
				if "Connected" in line:
					f = line.split()
					c = f[0]
					if c == link:
						addConv = False
			if addConv:
				self.cmd_tnn("conv c " + link)


		for line in r.splitlines():
			if "Connected" in line or "Disconnected" in line:
				f = line.split()
				c = f[0]
				if not c in self.links:
					rm = self.cmd_tnn("conv c - " + c)
