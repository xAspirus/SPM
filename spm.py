#!/bin/python3

from rich import print as rprint
import os
import json
import sys


class Project:
	def __init__(self, name: str):
		self.name = name
		self.dir_path = str()
		self.json = dict()
	
	def load_project_dir(self, dir_path: str):
		if os.path.isfile(f'./{dir_path}/{self.name}.sb3'):
			pass
		else:
			raise Exception(" Invalid project folder ")
		self.dir_path = dir_path
		rprint(f"[blue] ** Unzipping {self.name}.sb3 [/blue]")
		os.system(f"unzip -o ./{self.dir_path}/{self.name}.sb3 -d ./{self.dir_path}/__unpacked__")
		with open(f"./{self.dir_path}/__unpacked__/project.json", "r") as f:
			self.json = json.loads(f.read())

	def package(self, output: str = None):
		if output is None: output = self.name
		with open(f"./{self.dir_path}/__unpacked__/project.json", "w") as f:
			f.write(json.dumps(self.json))
		rprint(f"[blue] ** Zipping project into {output}.sb3 [/blue]")
		os.system(f"zip -rj ./{self.dir_path}/{output}.sb3 ./{self.dir_path}/__unpacked__")
	
	def print_json(self):
		rprint(f"[green] ** {self.name}'s json contents: [/green]")
		rprint(self.json)
	
	def get_sprite(self, sprite_name: str):
		for sprite in self.json["targets"]:
			if sprite["name"] == sprite_name:
				return sprite
		raise Exception(f"Sprite {sprite_name} is not found")

	def unify_block_ids(self):
		main_sprite = self.get_sprite("Main")
		
		# Append self.name to all block ids
		main_sprite["blocks"] = {(self.name + ":" if not key.startswith(self.name+':') else '') + key: value for key, value in main_sprite["blocks"].items()}
		
		for _, block in main_sprite["blocks"].items():
			# custom block prototypes
			if block["opcode"] == "procedures_definition" and not block["inputs"]["custom_block"][1].startswith(self.name+':'):
				block["inputs"]["custom_block"][1]=self.name+":"+block["inputs"]["custom_block"][1]
			if block["opcode"] == "procedures_prototype":
				block["mutation"]["argumentids"] = str([
					x
						if x.startswith(self.name+':')
					else
						(self.name+':'+x)
				for x in eval(block["mutation"]["argumentids"])
				]).replace("'", '"')
			# Update next pointers
			if not block["next"] is None and not block["next"].startswith(self.name+':'):
				block["next"] = self.name + ":" + block["next"]
			# Update parent pointers
			if not block["parent"] is None and not block["parent"].startswith(self.name+':'):
				block["parent"] = self.name + ":" + block["parent"]
			# Update pointers in block inputs
			keys = []
			for key, input in block["inputs"].items():
				if block["opcode"] == "procedures_prototype":
					keys.append(key)
					if input[0] == 1:
						if type(input[1]) is str and not input[1].startswith(self.name+':'):
							input[1] = self.name + ":" + input[1]
				elif input[0] == 3:
					if type(input[1]) is str and not input[1].startswith(self.name+':'):
						input[1] = self.name + ":" + input[1]
					if type(input[2]) is str and not input[2].startswith(self.name+':'):
						input[2] = self.name + ":" + input[2]
				elif input[0] == 2:
					if type(input[1]) is str and not input[1].startswith(self.name+':'):
						input[1] = self.name + ':' + input[1]
			for i in keys:
				if not i.startswith(self.name+':'):
					block["inputs"][self.name+":"+i] = block["inputs"].pop(i)

	def add(self, modl: "Project"):
		# Fix block-id collisions
		self.unify_block_ids()
		modl.unify_block_ids()
		# Add blocks from modl to self
		main_sprite = self.get_sprite("Main")
		modl_sprite = modl.get_sprite("Main")
		main_sprite["blocks"] = {**main_sprite["blocks"], **modl_sprite["blocks"]}

	def remove(self, name):
		main_sprite = self.get_sprite("Main")
		for i in list(main_sprite["blocks"].keys()):
			if i.startswith(name+':'):
				main_sprite["blocks"].pop(i)
	
	def add_module(self, modl: "Project"):
		self.remove(modl.name)
		self.add(modl)


main_name = os.getcwd().split('/')[-1]

if os.path.isfile(main_name+'.sb3'):
	pass
else:
	rprint(f'[red] Current folder does not contain {main_name}.sb3 [/red]')
	exit(1)



sys.argv = sys.argv[1:]

if len(sys.argv) >= 1:
	main = Project("MainProject")
	main.load_project_dir(".")
	if sys.argv[0] == "add":
		if len(sys.argv) >= 2:
			modl = Project(sys.argv[1])
			try:
				modl.load_project_dir(modl.name)
			except:
				rprint("[red] Module folder not found or does not have .sb3 [/red]")
				exit(1)
			main.add_module(modl)
			main.package()
		else:
			rprint("[red] Please enter a module name [/red]")
			exit(1)
	elif sys.argv[0] == "remove":
		if len(sys.argv) >= 2:
			main.remove(sys.argv[1])
			main.package()
		else:
			rprint("[red] Please enter a module name [/red]")
			exit(1)
else:
	rprint("[red] Please enter a command {add,remove} [/red]")
	exit(1)
