import requests
import json
import os
import sys
import time
from datetime import datetime
import argparse
import tnnhelper
import stuff
import links

width = 80
version = "v0.1"


menu_cur = "main"
menu_wait = True
menu_text = {}
menu_item = {}
menu_exec = {}

menu_text["main"] = "Main Menu"
menu_item["main"] = [["Manage Node Links",        "menu_set('links')"]]

menu_text["links"] = links.add_text()
menu_item["links"] = links.add_item()

parser = argparse.ArgumentParser()
parser.add_argument('-c', action='store_true', default=False, dest='configmode', help='Run in configuration mode')


def menu_set(pos):
        global menu_cur
        global menu_wait
        menu_wait = False
        menu_cur = pos

def menu_display(topic):
        global menu_cur
        global menu_wait
        menu_wait = True
        os.system('clear')
        print(" ")
        stuff.menu_title(menu_text[topic])
        counter = 0
        for entry in menu_item[topic]:
                counter = counter + 1
                stuff.menu_entry(str(counter) + ". " + str(entry[0]))
        stuff.menu_entry("0. Exit from Script")
        stuff.menu_footer()
        choice = raw_input("Enter your choice [0-" + str(counter) + "]: ")
        if choice:
                try:
                        choice_num = int(choice)
                except:
                        choice_num = 999999
                if choice_num == 0:
                        print(" ")
                        sys.exit()
                if choice_num > -1 and choice_num < (counter+1):
                        exec_menu = menu_item[topic][choice_num-1][1]
                        print(" ")
                        eval(exec_menu)
                else:
                        print("Wrong menu selection...")
        else:
                print("Wrong menu selection...")



myargs = parser.parse_args()

if myargs.configmode:
	while True:
	        menu_display(menu_cur)
        	if menu_wait:
	                print(" ")
	                print(" ")
	                b = raw_input("Press Return to continue....")


tnn = tnnhelper.tnnhelper()
tnn.get_links()
