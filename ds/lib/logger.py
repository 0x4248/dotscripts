# SPDX-License-Identifier: SEE LICENSE IN LICENSE
# DotScript
# A dotfile scripts system
#
# DotScript/lib/logger.py
# 
# Logger
# Logging system
#
# COPYRIGHT NOTICE
# Copyright (C) 2024 0x4248 - GNU General public licence

import datetime
import os

CONFIG = {}

class COLOUR:
	RED = '\033[91m'
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	BLUE = '\033[94m'
	PURPLE = '\033[95m'
	CYAN = '\033[96m'
	WHITE = '\033[97m'
	GRAY = '\033[90m'
	ENDC = '\033[0m'

class log_internal:
	def write(type, message):
		if os.path.exists(os.path.expanduser("~/.scripts/logs")):
			with open(os.path.expanduser(f"~/.scripts/logs/{datetime.datetime.now().strftime('%Y-%m-%d')}.log"), "a") as f:
				f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\t[{type}]\t{message}\n")

def trace(message):
	if CONFIG["show_trace"]:
		print(f"{COLOUR.GRAY}**>{COLOUR.ENDC} {message}")
	log_internal.write("TRACE", str(message))

def log(message):
	print(f"{COLOUR.CYAN}==>{COLOUR.ENDC} {message}")
	log_internal.write("LOG", message)

def sublog(message):
	print(f" {COLOUR.CYAN}->{COLOUR.ENDC} {message}")
	log_internal.write("SLOG", message)

def warning(message):
	print(f"{COLOUR.YELLOW}=!>{COLOUR.ENDC} {message}")
	log_internal.write("WARN", message)

def error(message):
	print(f"{COLOUR.RED}=X>{COLOUR.ENDC} {message}")
	log_internal.write("ERR", message)