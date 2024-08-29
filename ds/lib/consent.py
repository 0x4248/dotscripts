# SPDX-License-Identifier: SEE LICENSE IN LICENSE
# DotScript
# A dotfile scripts system
#
# DotScript/lib/consent.py
# 
# Consent
# Yes no consent prompt
#
# COPYRIGHT NOTICE
# Copyright (C) 2024 0x4248 - GNU General public licence

class COLOUR:
	YELLOW = '\033[93m'
	ENDC = '\033[0m'

def askyn(message, default=""):
	while True:
		if default == "y":
			response = input(f"{COLOUR.YELLOW}=?>{COLOUR.ENDC} {message} [Y/n] ")
		elif default == "n":
			response = input(f"{COLOUR.YELLOW}=?>{COLOUR.ENDC} {message} [y/N] ")
		else:
			response = input(f"{COLOUR.YELLOW}=?>{COLOUR.ENDC} {message} [y/n] ")

		if response == "":
			if default == "y":
				return True
			if default == "n":
				return False
			if default == "":
				while True:
					print("Please enter a valid response (y/n)")
					response = input(f"{COLOUR.YELLOW}=?>{COLOUR.ENDC} {message} [y/n] ")
					if response.lower() == "y" or response.lower() == "yes":
						return True
					if response.lower() == "n" or response.lower() == "no":
						return
		
		if response.lower() == "y" or response.lower() == "yes":
			return True
		if response.lower() == "n" or response.lower() == "no":
			return False