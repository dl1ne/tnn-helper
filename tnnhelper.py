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


	def config_load(self):
		self.config.read(self.config_file)
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


	def config_save(self):
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
		with open(self.config_file, 'w') as configfile:
			self.config.write(configfile)


	def checkerror(self, resp):
		if ("message" in resp and resp["message"] != "success") or ("error" in resp):
			print("API responds with error, exiting!")
			print("More:")
			print(resp)
			exit(1)

	def get_nodes(self, raw = False):
		res = requests.get(self.api_url + "/api/node", timeout=self.api_timeout)
		response = res.json()
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
			res = requests.post(self.api_url + "/api/node/", data=payload, headers=headers, timeout=self.api_timeout)
			self.checkerror(res.json())
			self.get_nodes()


	def get_links(self, raw = False):
		updateTNN = False
		res = requests.get(self.api_url + "/api/link/" + self.my_call, timeout=self.api_timeout)
		response = res.json()
		self.checkerror(response)
		if 'data' in response:
			for link in response["data"]:
				if self.my_call == link["callleft"] and link["callleft"] not in self.links:
					self.links[link["callright"]] = 1
					updateTNN = True
				if self.my_call == link["callright"] and link["callright"] not in self.links:
					self.links[link["callleft"]] = 1
					updateTNN = True

			if updateTNN:
				self.tnn_updateax25route()
				self.tnn_updatelinks()

			if raw:
				return response["data"]


	def create_link(self, callsign):
		headers = {'Content-type': 'application/json'}
		mydata = {}
		mydata["callleft"] = self.my_call
		mydata["callright"] = callsign
		payload = json.dumps(mydata)
		res = requests.post(self.api_url + "/api/link", data=payload, headers=headers, timeout=self.api_timeout)
		response = res.json()
		self.checkerror(response)
		self.get_links()


	def get_tnnconfig(self, tnnconfig, linenum):
		with open(tnnconfig) as fp:
			for i, line in enumerate(fp):
				if i == (linenum-1):
					return line.replace('\n','').replace('\r','').replace(' ','').replace('\t','')
		return False


	def cmd_tnn(self, cfgstring):
		cmdstring = urllib.pathname2url(cfgstring)
		res = requests.post("http://" + self.tnn_host + ":" + self.tnn_port + "/cmd?cmd=" + cmdstring, timeout=self.api_timeout, auth=HTTPBasicAuth(self.my_call, ""))
		response = res.text
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


