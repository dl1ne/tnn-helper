import time
import os
import sys

version = "v0.1"
width = 80
loader_val = 0
loader_char = ["-", "\\", "|", "/", "#"]

class bcolors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

def tr(corner = False, txtLeft = "", txtRight = ""):
        global width
        fillme = width-4
        fillme = fillme - len(txtLeft)
        fillme = fillme - len(txtRight)
        if corner:
                print("+-" + txtLeft + fillme*"-" + txtRight + "-+")
        else:
                print(width*"-")

def menu_title(title):
        global width
        fillme = width-2
        tr(True, version, "by-DL1NE")
        filltxt1 = int((fillme-len(title))/2)
        filltxt2 = fillme-filltxt1-len(title)
        print("|" + filltxt1*" " + title + filltxt2*" " + "|")
        tr(True)

def menu_footer():
        tr(True)

def menu_entry(title):
        global width
        fillme = width-3
        filltxt = fillme-len(title)
        print("| " + title + filltxt*" " + "|")

