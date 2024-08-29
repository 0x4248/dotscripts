# SPDX-License-Identifier: SEE LICENSE IN LICENSE
# DotScript
# A dotfile scripts system
#
# DotScript/__main__.py
# 
# Main
# Main entry point
#
# COPYRIGHT NOTICE
# Copyright (C) 2024 0x4248 - GNU General public licence


# Scripts are located in ~/.scripts/scripts
# Configuration is located in ~/.scripts/config
# Logs are located in ~/.scripts/logs
# binaries are located in ~/.scripts/bin

# ds compile - Compile all scripts and creates links to bin
# in bin lets say we have test.py
# we make ./test
# which contins
# #!/bin/bash
# python3 -m ds
# you can also call programs using ds 
# ds run test
# scripts can also be listed
# ds list # basic list
# ds list a # all info
# All scripts are hashed to prevent tampering
# ds hash rehash
# ds hash checkall
# ds hash check <script>
# ds init # creates .scripts folder

import argparse
import os
import shutil
import time
import hashlib
import importlib
import subprocess
import json

from ds.lib import logger
from ds.lib import consent

DEFCONFIG = {
	"show_all_logs": False,
	"show_running_script_log": False,
	"show_trace": False,
}

HELP_STRING = """
init - Initialize DotScript
repair - Repair DotScript
compile - Compile scripts
"""


CONFIG = DEFCONFIG
logger.CONFIG = CONFIG


class ds:
	def init():
		if os.path.exists(os.path.expanduser("~/.scripts")):
			logger.log("DotScript has already been initialized")
			yn = consent.askyn("Show repair options?")
			if yn == True:
				ds.repair()
				return
			else:
				logger.warning("DotScript has already been initialized and repair options were not shown")
				return
		logger.log("Initializing DotScript")
		logger.sublog("Creating .scripts")

		os.mkdir(os.path.expanduser("~/.scripts"))
		logger.sublog("Creating .scripts/scripts")
		os.mkdir(os.path.expanduser("~/.scripts/scripts"))
		logger.sublog("Creating .scripts/config")
		os.mkdir(os.path.expanduser("~/.scripts/config"))
		logger.sublog("Creating .scripts/logs")
		os.mkdir(os.path.expanduser("~/.scripts/logs"))
		logger.sublog("Creating .scripts/etc")
		os.mkdir(os.path.expanduser("~/.scripts/etc"))
		logger.sublog("Creating .scripts/etc/packages")
		os.mkdir(os.path.expanduser("~/.scripts/etc/packages"))
		logger.sublog("Creating .scripts/bin")
		os.mkdir(os.path.expanduser("~/.scripts/bin"))

		logger.sublog("DS => Creating global executable in bin")
		with open(os.path.expanduser("~/.scripts/bin/ds"), "w") as f:
			f.write("#!/bin/bash\npython3 -m ds $@")
		logger.sublog("DS => Chmoding global executable")
		os.chmod(os.path.expanduser("~/.scripts/bin/ds"), 0o755)
		logger.log("DotScript can now be called by using ds")

		logger.sublog("ETC => init_time create")
		with open(os.path.expanduser("~/.scripts/etc/init_time"), "w") as f:
			f.write(str(time.time()))

		logger.log("DotScript has been initialized")

	def repair():
		logger.log("Showing repair options")
		logger.warning("Repairing DotScript could lead to loosing configs or installed scripts")
		logger.warning("Please make sure you have a backup of your scripts and configs before proceeding")
		yn = consent.askyn("Would you like to create a copy of .scripts at ~/.scripts.bak?")
		if yn == True:
			logger.sublog("Creating backup")
			if os.path.exists(os.path.expanduser("~/.scripts.bak")):
				logger.warning("A backup already exists, please remove it before creating a new one")
				return
			shutil.copytree(os.path.expanduser("~/.scripts"), os.path.expanduser("~/.scripts.bak"))
		else:
			logger.warning("A backup was not done")
		print("To repair DotScript, you can either:")
		print("1. [DESTRUCTIVE] Remove ~/.scripts and reinitialize DotScript")
		print("2. rebuild bin")
		print("3. [DESTRUCTIVE] Remove all config")
		print("4. Rehash all scripts")
		print("5. Check all hashes")
		print("6. Exit")

		while True:
			choice = input("Choice: ")
			if choice == "1":
				logger.warning("Removing ~/.scripts")
				shutil.rmtree(os.path.expanduser("~/.scripts"))
				ds.init()
				break
			elif choice == "2":
				logger.warning("Rebuilding bin")
				shutil.rmtree(os.path.expanduser("~/.scripts/bin"))
				os.mkdir(os.path.expanduser("~/.scripts/bin"))
				logger.log("Bin has been rebuilt")
				break
			elif choice == "3":
				logger.warning("Removing all config")
				shutil.rmtree(os.path.expanduser("~/.scripts/config"))
				os.mkdir(os.path.expanduser("~/.scripts/config"))
				logger.log("Config has been removed")
				break
			elif choice == "4":
				ds.rehash()
				break
			elif choice == "5":
				ds.checkhashes()
				break
			elif choice == "6":
				break

	def compile():
		logger.log("Compiling scripts")
		logger.sublog("Cleaing bin")
		shutil.rmtree(os.path.expanduser("~/.scripts/bin"))
		os.mkdir(os.path.expanduser("~/.scripts/bin"))
		logger.sublog("Cleaning etc/scripts")
		if os.path.exists(os.path.expanduser("~/.scripts/etc/scripts")):
			os.remove(os.path.expanduser("~/.scripts/etc/scripts"))
		logger.sublog("Searching for installed packages")
		if not os.path.exists(os.path.expanduser("~/.scripts/etc/packages")):
			logger.error("No packages found")
			exit()
		for file in os.listdir(os.path.expanduser("~/.scripts/etc/packages")):
			if not file.endswith(".json"):
				continue
			logger.log(f"Found package {file}")
			with open(os.path.expanduser(f"~/.scripts/etc/packages/{file}")) as f:
				data = json.load(f)
			for script in data["scripts"]:
				logger.sublog(f"Compiling {script}")
				with open(os.path.expanduser(f"~/.scripts/scripts/{script}"), "rb") as f:
					hash = hashlib.sha256(f.read()).hexdigest()
				with open(os.path.expanduser("~/.scripts/etc/scripts"), "a") as f:
					f.write(f"{script},{os.path.expanduser(f'~/.scripts/scripts/{script}')},{hash},{data['script-types'][0]}\n")
				with open(os.path.expanduser(f"~/.scripts/bin/{script.split('.')[0]}"), "w") as f:
					f.write(f"#!/bin/bash\npython3 -m ds run {script} $@")
				os.chmod(os.path.expanduser(f"~/.scripts/bin/{script.split('.')[0]}"), 0o755)
		logger.log("Scripts have been compiled")
		logger.log("Adding ds binary")
		with open(os.path.expanduser("~/.scripts/bin/ds"), "w") as f:
			f.write("#!/bin/bash\npython3 -m ds $@")
		os.chmod(os.path.expanduser("~/.scripts/bin/ds"), 0o755)
		logger.log("Binaries have been compiled")
		
	def run(args):
		logger.trace("Running script")
		if len(args.arguments) == 0:
			logger.error("No script provided")
			exit()
		
		if not os.path.exists(os.path.expanduser(f"~/.scripts/scripts/{args.arguments[0]}")):
			logger.error("Script does not exist")
			exit()
	
		logger.trace("Looking up script in etc/scripts")
		with open(os.path.expanduser("~/.scripts/etc/scripts")) as f:
			lines = f.readlines()

		for line in lines:
			if line.split(",")[0] == args.arguments[0]:
				break
		else:
			logger.error("Script not found in etc/scripts if it is installed please recompile the script index with ds compile")
			exit()
		
		logger.trace(f"Checking hash of {args.arguments[0]}")
		with open(os.path.expanduser(f"~/.scripts/scripts/{args.arguments[0]}"), "rb") as f:
			hash = hashlib.sha256(f.read()).hexdigest()
		
		if hash != line.split(",")[2]:
			logger.warning("DS => The script you are running appears to be tampered with")
			logger.warning("DS => To remove this warning, you must recompile")
			yn = consent.askyn("DS => Run anyway?")
			if yn == False:
				exit()
		
		if line.split(",")[3].replace("\n","") == "Python":
			logger.log("DS => Running Python script")
			subprocess.run(["python3", line.split(",")[1], *args.arguments[1:]])
		elif line.split(",")[3].replace("\n","")  == "Shell":	
			logger.log("DS => Running Shell script")
			subprocess.run(["sh", line.split(",")[1], *args.arguments[1:]])
		elif line.split(",")[3].replace("\n","")  == "Bash":	
			logger.log("DS => Running Bash script")
			subprocess.run(["bash", line.split(",")[1], *args.arguments[1:]])
		elif line.split(",")[3].replace("\n","")  == "Fish":
			logger.log("DS => Running Fish script")
			subprocess.run(["fish", line.split(",")[1], *args.arguments[1:]])
		elif line.split(",")[3].replace("\n","")  == "Zsh":
			logger.log("DS => Running Zsh script")
			subprocess.run(["zsh", line.split(",")[1], *args.arguments[1:]])

	def install(args):
		if args.arguments[0] == ".":
			if not os.path.exists("package.json"):
				logger.error("package.json not found")
				exit()
			if not os.path.exists("scripts"):
				logger.error("scripts/ folder not found")
				exit()
			
			with open("package.json") as f:
				packageinfo = json.load(f)
			
			if not "scripts" in packageinfo:
				logger.error("No scripts found in package.json")
				exit()
			
			if not "script-types" in packageinfo:
				logger.error("No script-types found in package.json")
				exit()
			
			if not "name" in packageinfo:
				logger.error("No name found in package.json")
				exit()
			
			if not "version" in packageinfo:
				logger.error("No version found in package.json")
				exit()
			
			print("You are about to install the package:"+ packageinfo["name"] + " v" + packageinfo["version"])
			print("Scripts:")
			for script in packageinfo["scripts"]:
				print(script)
			yn = consent.askyn("Do you want to install this package?")
			if yn == True:
				pass
			else:
				logger.warning("Installation aborted")
				exit()
			logger.log(f"Installing package {packageinfo['name']} v{packageinfo['version']}")
			logger.sublog("Moving package.json to ~/.scripts/etc/packages")
			shutil.copyfile("package.json", os.path.expanduser(f"~/.scripts/etc/packages/package-{packageinfo['name']}.json"))
			logger.sublog("Moving scripts to ~/.scripts/scripts")
			for script in packageinfo["scripts"]:
				shutil.copyfile("scripts/"+script, os.path.expanduser(f"~/.scripts/scripts/{script}"))
			logger.log("Package installed")
			yn = consent.askyn("Do you want to recompile the scripts folder?")
			if yn == True:
				ds.compile()
		else:
			logger.error("Only the current directory can be installed")
	
	def uninstall(args):
		if not os.path.exists(os.path.expanduser(f"~/.scripts/etc/packages/package-{args.arguments[0]}.json")):
			logger.error("Package not found")
			exit()

		with open(os.path.expanduser(f"~/.scripts/etc/packages/package-{args.arguments[0]}.json")) as f:
			packageinfo = json.load(f)
		
		logger.log(f"Uninstalling package {packageinfo['name']} v{packageinfo['version']}")
		logger.sublog("Removing scripts")
		for script in packageinfo["scripts"]:
			os.remove(os.path.expanduser(f"~/.scripts/scripts/{script}"))
		logger.sublog("Removing package.json")
		os.remove(os.path.expanduser(f"~/.scripts/etc/packages/package-{packageinfo['name']}.json"))
		logger.log("Package uninstalled")
		yn = consent.askyn("Do you want to recompile the scripts folder?")
		if yn == True:
			ds.compile()
		
	def list(args):
		if args.arguments[0] == "a":
			logger.log("Listing all scripts")
			with open(os.path.expanduser("~/.scripts/etc/scripts")) as f:
				lines = f.readlines()
			for line in lines:
				print(f"Name: {line.split(',')[0]}")
				print(f"Path: {line.split(',')[1]}")
				print(f"Hash: {line.split(',')[2]}")
				print(f"Type: {line.split(',')[3]}")
		else:
			logger.log("Listing scripts")
			with open(os.path.expanduser("~/.scripts/etc/scripts")) as f:
				lines = f.readlines()
			for line in lines:
				print(f"Name: {line.split(',')[0]}")
				print(f"Type: {line.split(',')[3]}")
	
	def rehash():
		logger.log("Rehashing all scripts")
		with open(os.path.expanduser("~/.scripts/etc/scripts")) as f:
			lines = f.readlines()
		for line in lines:
			with open(line.split(",")[1], "rb") as f:
				hash = hashlib.sha256(f.read()).hexdigest()
			with open(os.path.expanduser("~/.scripts/etc/scripts"), "w") as f:
				f.write(f"{line.split(',')[0]},{line.split(',')[1]},{hash},{line.split(',')[3]}")
		logger.log("All scripts have been rehashed")
	
	def checkhashes():
		logger.log("Checking all hashes")
		with open(os.path.expanduser("~/.scripts/etc/scripts")) as f:
			lines = f.readlines()
		for line in lines:
			with open(line.split(",")[1], "rb") as f:
				hash = hashlib.sha256(f.read()).hexdigest()
			if hash != line.split(",")[2]:
				logger.warning(f"Hash for {line.split(',')[0]} does not match")
		logger.log("All hashes have been checked")
		
if __name__ == "__main__":
	logger.trace("DotScript call at: " + str(time.time()))
	args = argparse.ArgumentParser(description="DotScript")
	args.add_argument("command", help=HELP_STRING)
	args.add_argument("arguments", nargs="*", help="Arguments for the command")
	args = args.parse_args()

	logger.trace("Command: " + args.command)
	logger.trace("Arguments: " + str(args.arguments))

	logger.trace("Checking for .scripts folder")
	logger.trace(f"Checking for .scripts/ =  {os.path.exists(os.path.expanduser('~/.scripts'))}")
	if not os.path.exists(os.path.expanduser("~/.scripts")):
		logger.warning("DotScript has not been initialized")
		logger.warning("Please run ds init to initialize DotScript")

	if args.command == "init":
		logger.trace("Initializing DotScript")
		ds.init()
	
	elif args.command == "repair":
		logger.trace("Repairing DotScript")
		ds.repair()
	
	elif args.command == "compile":
		logger.trace("Compile scripts was called")
		ds.compile()
	
	elif args.command == "run":
		logger.trace("Running script")
		ds.run(args)
	
	elif args.command == "install":
		logger.trace("Installing package")
		ds.install(args)
	
	elif args.command == "uninstall":
		logger.trace("Uninstalling package")
		ds.uninstall(args)
	
	elif args.command == "list":
		logger.trace("Listing scripts")
		ds.list(args)
	
	else:
		logger.error("Command not found")
		exit()