import tnnhelper

menu_text = "Manage Node Links"
menu_item = [	["Print Links",			"links.print_links()"],
		["Add Node Link",		"links.add_link()"],
		["Delete Node Link",		"links.delete_link()"],
		["Back to Main Menu",		"menu_set('main')"]]

selected_nodes = []
nodes = {}
links = {}
api = tnnhelper.tnnhelper()

def add_text():
        return menu_text

def add_item():
        return menu_item

def close():
	global api
	api.config_save()

def get_links():
	global selected_nodes
	global links
	links = api.get_links(True)
	mycall = api.get_mycall().upper()
	for link in links:
		if link["callleft"].upper() == mycall and link["callright"] not in selected_nodes:
			selected_nodes.append(link["callright"].upper())
		if link["callright"].upper() == mycall and link["callleft"] not in selected_nodes:
			selected_nodes.append(link["callleft"].upper())


def print_nodes(selected):
	global api
	global nodes
	global selected_nodes
	get_links()
	mycall = api.get_mycall().upper()
	nodes = api.get_nodes(True)
	count = 0
	print("Nr  Link    Call     Ident       IP-Address")
	print("--------------------------------------------------")
	for node in nodes:
		if not node["callsign"].upper() == mycall:
			count = count + 1
			if node["callsign"].upper() in selected_nodes:
				mark = " [x]"
			else:
				mark = " [ ]"
			print("%3d %-7s %-8s %-11s %s" % (count, mark, node["callsign"], node["callident"], node["ipaddr"]))
			'''print(" " + txt + mark + " " + node["callsign"] + ", " + node["callident"] + ", " + node["ipaddr"])'''

def add_link():
	global nodes
	global api
	mycall = api.get_mycall().upper()
	print("Trying to fetch available nodes...\n")
	print_nodes(selected_nodes)
	print("\nPlease enter Node Number you want to link,")
	nodenr = raw_input("or enter 0 for cancel: ")
	if not nodenr:
		return
	if int(nodenr) > len(nodes):
		print("Invalid Number!")
		return
	if int(nodenr) < 1:
		return
	print("\n\nTrying to setup link with selected Node...")
	count = 0
	callsign = ""
	for node in nodes:
		if not node["callsign"].upper() == mycall:
			count = count +1
			if int(nodenr) == count:
				callsign = node["callsign"]
				break
	api.create_link(callsign)
	print(api.get_response())
	print("\n\n")
	print_links()



def delete_link():
	global api
	valid = print_links()
	print("\nPlease enter Link Number you want to delete,")
	linknr = raw_input("or enter 0 for cancel: ")
	if not linknr:
		return
	if linknr < 1:
		return
	if not int(linknr) in valid:
		print("Invalid Link! Valid links:")
		print(valid)
		return
	api.delete_link(linknr)
	print(api.get_response())
	print("\n\n")
	print_links()


def print_links():
	global links
	global api
	print("Trying to fetch configured links...\n")
	get_links()
	valid = []
	print("ID     Link")
	print("---------------------------------------")
	for link in links:
		print(" %3d   %-8s <-------> %8s" % (link["id"], link["callleft"], link["callright"]))
		valid.append(link["id"])
	return valid

