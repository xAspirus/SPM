#!/usr/bin/env python3

# Scratch Package Manager
# -----------------------
# Modular project development for Scratch
# - Written by Aspirus

"""
[bold]Commands:[/bold]
  [blue]Setup project for use with SPM[/blue]
   > spm /path/to/main init
  [blue]Add package to main, if already added: package is updated[/blue]
   > spm /path/to/main SpriteName add /path/to/package
  [blue]Remove package from main[/blue]
  [blue]If only package name is provided: SPM looks inside ./spm-modules/[/blue]
   > spm /path/to/main SpriteName add PackageName
  [blue]Remove package by name[/blue]
   > spm /path/to/main SpriteName remove PackageName
"""


import json
import os
import sys
import tempfile

from rich import print as rprint
from collections import defaultdict


class Zip:
	@staticmethod
	def unzip(in_path: str, out_path: str):
		os.system(f"unzip -o '{in_path}' -d '{out_path}' > /dev/null")
	
	@staticmethod
	def zip(in_path: str, out_path: str):
		os.system(f"zip -rj '{out_path}' '{in_path}' > /dev/null")


class Package:
	def __init__(
	self,
	sb3_path: str,
	name: str = '',
	description: str = '',
	version: str = None):
		self.name = name
		self.description = description
		self.version = '0.0.0' if version is None else version
		self.sprites = {}
		self.unpacked = tempfile.TemporaryDirectory().name
		self.json = {}
		self.load_sb3(sb3_path)
	
	def __del__(self):
		os.system(f'rm -rf \'{self.unpacked}\'')

	def load_sb3(self, sb3_path: str):
		if not os.path.isfile(sb3_path):
			raise FileNotFoundError(f'"{sb3_path}" does not exist')
		if sb3_path.split('.')[-1] != 'sb3':
			raise FileNotFoundError(f'"{sb3_path} is not a scratch project"')
		Zip.unzip(sb3_path, self.unpacked)
		# Load project.json
		with open(f'{self.unpacked}/project.json', 'r') as fp:
			self.json = json.loads(fp.read())
		# Load package data
		self.stage = [i for i in self.json['targets'] if i['name'] == 'Stage'][0]
		if 'package.json' in self.stage['comments']:
			package_json = json.loads(self.stage['comments']['package.json']['text'])
			self.name = package_json['name']
			self.description = package_json['description']
			self.version = package_json['version']
		else:
			package_json = {
				'sprites': {}
			}
			self.update_package_json()
		# Load sprites
		self.sprites = {
			target['name']: Sprite(
				self,
				target,
				dependencies=defaultdict(dict, package_json['sprites'])[target['name']]
			)
			for target in self.json['targets'] if target['name'] != 'Stage'
		}
		return self
	
	def update_package_json(self):
		self.stage['comments']['package.json'] = {
			'blockId': None,
			'x': 0,
			'y': 0,
			'width': 1000,
			'height': 1000,
			'minimized': False,
			'text': json.dumps(
				{
					'name': self.name,
					'description': self.description,
					'version': self.version,
					'sprites': {
						sprite.name: sprite.dependencies
						for sprite in self.sprites.values()
					}
				},
				indent=2
			)
		}

	def export_sb3(self, sb3_path: str):
		self.update_package_json()		
		with open(f'{self.unpacked}/project.json', 'w') as fp:
			fp.write(json.dumps(self.json))
		Zip.zip(self.unpacked, sb3_path)
		return self


class Sprite:
	def __init__(self, package: Package, json: dict, dependencies: dict):
		self.json = json
		self.name = self.json['name']
		self.package = package
		self.dependencies = dependencies
		self.track()

	def track(self):
		OMEGA = 'Ω'
		tag = self.package.name + OMEGA
		self.json['variables'] = {
			variable[0]: variable
			for variable in self.json['variables'].values()
		}
		self.json['blocks'] = {
			(tag+key) if key.count(OMEGA) == 0 else key: value
			for key, value in self.json['blocks'].items()
		}
		for block in self.json['blocks'].values():
			# I am not going to bother refactor this...
			if type(block) is list:
				block[2] = block[1]
				continue
			if block['next'] is not None and block['next'].count(OMEGA) == 0:
				block['next'] = tag+block['next']
			if block['parent'] is not None and block['parent'].count(OMEGA) == 0:
				block['parent'] = tag+block['parent']
			for input in block['inputs'].values():
				if input[0] in (1,2,3) and type(input[1]) is str and input[1].count(OMEGA) == 0:
					input[1] = tag+input[1]
				if input[0] == 3 and type(input[1]) is list and input[1][0] == 12:
					input[1][2] = input[1][1]
			if ( block['opcode'] == 'procedures_definition'
				 and block['inputs']['custom_block'][1].count(OMEGA) == 0 ):
				block['inputs']['custom_block'][1] = tag+block['inputs']['custom_block'][1]
			elif block['opcode'] in ('procedures_prototype', 'procedures_call'):
				block['mutation']['argumentids'] = str([
					tag+x if x.count(OMEGA) == 0 else x
					for x in eval(block['mutation']['argumentids'])
				]).replace("'", '"') # FIXME?
				block['inputs'] = {
					(tag+key) if key.count(OMEGA) == 0 else key: value
					for key, value in block['inputs'].items()
				}
				if block['opcode'] == 'procedures_prototype':
					for input in block['inputs'].values():
						if input[1].count(OMEGA) == 0:
							input[1] = tag+input[1]
		return self
	
	def get_package_blocks(self) -> dict:
		blocks = {
			block_id: block
			for block_id, block in self.json['blocks'].items()
			# Remove blocks with '#' in name:
			if block_id.startswith(self.package.name)
				and not (
					block['opcode'] == 'procedures_definition'
					and '#' in self.json['blocks']
					[block['inputs']['custom_block'][1]]['mutation']['proccode']
				)
		}
		for block in blocks.values():
			# Stack all blocks on top of each other:
			# if block['topLevel']:
			# 	block['x'] = 0
			# 	block['y'] = 0
			# Hide blocks with '_' in name:
			if block['opcode'] == 'procedures_definition':
				if '_' in blocks[block['inputs']['custom_block'][1]]['mutation']['proccode']:
					block['shadow'] = True
		return blocks

	def remove_package(self, package: Package):
		try:
			self.dependencies.pop(package.name)
		except KeyError:
			pass
		self.json['blocks'] = {
			block_id: block
			for block_id, block in self.json['blocks'].items()
			if not block_id.startswith(package.name)
		}
		return self

	def add_package(self, package: Package):
		self.remove_package(package)
		try:
			sprite = package.sprites['Main']
		except KeyError:
			raise KeyError(f'"{package.name}" does not have a Main sprite, is it a SPM package?')
		self.dependencies[package.name] = package.version
		self.json['variables'] = {
			**self.json['variables'],
			**sprite.json['variables']
		}
		self.json['blocks'] = {
			**sprite.get_package_blocks(),
			**self.json['blocks']
		}
		def has_costume(costume1):
			for self_costumes in self.json['costumes']:
				if costume['name'] == self_costumes['name']:
					return True
			return False
		diff_costumes = []
		for costume in sprite.json['costumes']:
			if not has_costume(costume):
				diff_costumes.append(costume)
		self.json['costumes'] += diff_costumes
		for costume in diff_costumes:
			os.system(f'cp -f \'{package.unpacked}/{costume["md5ext"]}\' \'{self.package.unpacked}\'')
		return self


class Interface():
	def __init__(self):
		try:
			self.run()
		except KeyError as e:
			rprint(f'[yellow]Error:[/yellow] "{e}"')
			exit(1)
		except Exception as e:
			rprint(f'[yellow]{type(e).__name__}:[/yellow] {e}')
			exit(1)

	def run(self=None):
		arg = sys.argv[1:]
		if len(arg) > 0:
			if len(arg) > 1:
				if arg[1] == 'init':
					Interface.init(arg[0])
				elif len(arg) > 2:
					if arg[2] == 'add':
						if len(arg) > 3:
								Interface.add(arg[0], arg[3], arg[1])
						else:
							rprint(f'[yellow]Missing package path[/yellow]')
					elif arg[2] == 'remove':
						if len(arg) > 3:
							Interface.remove(arg[0], arg[3], arg[1])
						else:
							rprint(f'[yellow]Missing package name[/yellow]')
					else:
						rprint('[yellow]Possible commands are[/yellow] add, remove ')
				else:
					Interface.usage()
					exit(1)
			else:
				Interface.usage()
				exit(1)
		else:
			Interface.usage()
			exit(1)

	@staticmethod
	def usage():
		rprint(__doc__)

	@staticmethod
	def init(main_path: str):
		Package(main_path).export_sb3(main_path)
	
	@staticmethod
	def add(main_path: str, package_path: str, sprite_name: str):
		if not '.sb3' in package_path and not '/' in package_path:
			package_path = f'spm-modules/{package_path}.sb3'
			rprint(f'Resolving to [green]{package_path}[/green] for package path')
		main = Package(main_path)
		try:
			sprite = main.sprites[sprite_name]
		except KeyError:
			raise KeyError(f'"main.name" does not have the sprite {sprite_name}')
		sprite.add_package(Package(package_path))
		main.export_sb3(main_path)
	
	@staticmethod
	def remove(main_path: str, package_name: str, sprite_name: str):
		main = Package(main_path)
		try:
			sprite = main.sprites[sprite_name]
		except KeyError:
			raise KeyError(f'"main.name" does not have the sprite {sprite_name}')
		sprite.remove_package(package_name)
		main.export_sb3(main_path)


if __name__ == '__main__':
	Interface()
