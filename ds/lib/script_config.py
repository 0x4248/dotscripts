# SPDX-License-Identifier: SEE LICENSE IN LICENSE
# DotScript
# A dotfile scripts system
#
# DotScript/lib/consent.py
# 
# Script Config
# Script configuration system
#
# COPYRIGHT NOTICE
# Copyright (C) 2024 0x4248 - GNU General public licence

import inspect
import json
import os

def get_config(defconfig):
	caller = inspect.stack()[1].filename
	caller = caller.split("/")[-1].split(".")[0]

	if os.path.exists(os.path.expanduser(f"~/.scripts/config/{caller}-config.json")):
		with open(os.path.expanduser(f"~/.scripts/config/{caller}-config.json")) as f:
			config = json.load(f)
	else:
		with open(os.path.expanduser(f"~/.scripts/config/{caller}-config.json"), "w") as f:
			json.dump(defconfig, f, indent=4)
		config = defconfig
	
	return config