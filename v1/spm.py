#!/usr/bin/env python3

import json
import os
import sys

from rich import print as rprint
from pathlib import Path

AnyPath = str
OMEGA = 'Ω'


class Zip:
	def unzip(in_path: AnyPath, out_path: AnyPath):
		os.system(f"unzip -o '{in_path}' -d '{out_path}' > /dev/null")
	
	def zip(in_path: AnyPath, out_path: AnyPath):
		os.system(f"zip -rj '{out_path}' '{in_path}' > /dev/null")


class Project:
	def __init__(self, sb3_path: AnyPath):
		if not os.path.isfile(sb3_path):
			raise FileNotFoundError(f'Project file "{sb3_path}" does not exist')
		if not Path(sb3_path).suffix == '.sb3':
			raise Exception(f'"{sb3_path}" is not a scratch project file.')
		self.name = Path(sb3_path).stem
		self.ver = [0,0,0]
		self.desc = ''
		self.id = self.name + OMEGA
		self.sb3_path = sb3_path
		self.json = {}
		self.db = {
			'name': self.name,
			'version': '.'.join(self.ver),
			'description': self.desc,
			'readme': 'This comment is managed by SPM, don\'t edit or delete it!',
			'modules': []
		}
		Zip.unzip(self.sb3_path, f'./__{self.name}__')
		with open(f'./__{self.name}__/project.json', 'r') as fp:
			self.json = json.loads(fp.read())
		self.fetch_database()
	
	def fetch_database(self):
		comments = self.get_sprite('Stage')['comments']
		try:
			self.sb = json.loads(comments['package.json']['text'])
		except KeyError:
			pass
		self.desc = self.db['description']
		self.ver = self.db['version'].split('.')
	
	def store_database(self):
		comments = self.get_sprite('Stage')['comments']
		self.db['version'] = self.ver
		self.db['description'] = self.desc
		comments['package.json'] = {
			'blockId': None,
			'x': 0,
			'y': 0,
			'width': 100,
			'height': 100,
			'minimized': True,
			'text': json.dumps(self.db, indent=2, sort_keys=True)
		}
	
	def __del__(self):
		try:
			os.system(f"rm -rf './__{self.name}__'")
		except:
			pass

	def package_sb3(self, output_file: AnyPath = None) -> 'Project':
		if output_file is None: output_file = self.sb3_path
		self.store_database()
		with open(f'./__{self.name}__/project.json', 'w') as fp: fp.write(json.dumps(self.json))
		Zip.zip(f'./__{self.name}__', output_file)
		return self
	
	def get_sprite(self, sprite_name: str) -> dict:
		for sprite in self.json['targets']:
			if sprite['name'] == sprite_name: return sprite
		raise KeyError(f'Sprite "{sprite_name}" does not exist')

	def get_stage(self):
		return self.get_sprite('Stage')

	def make_block_ids_trackable(self) -> 'Project':
		"""
		assuming that block-ids will be random strings
		if not already starting with self.id: append self.id to block-id
		"""
		sprite = self.get_sprite('Main')
		# make = make block-id trackable
		# make variables
		sprite['variables'] = {
			value[0]: value
			for key, value in sprite['variables'].items()
		}
		# make for keys
		sprite['blocks'] = {
			(self.id+key) if key.count(OMEGA) == 0 else key: value
			for key, value in sprite['blocks'].items()
		}
		for block in sprite['blocks'].values():
			if type(block) is list:
				block[2] = block[1]
				continue
			# make for next, parent
			if block['next'] is not None and block['next'].count(OMEGA) == 0:
				block['next'] = self.id+block['next']
			if block['parent'] is not None and block['parent'].count(OMEGA) == 0:
				block['parent'] = self.id+block['parent']
			# make for block inputs
			for input in block['inputs'].values():
				if input[0] in (1,2,3) and type(input[1]) is str and input[1].count(OMEGA) == 0:
					input[1] = self.id+input[1]
				if input[0] == 3 and type(input[1]) is list and input[1][0] == 12:
					input[1][2] = input[1][1]
			# make for custom blocks
			if ( block['opcode'] == 'procedures_definition'
				 and block['inputs']['custom_block'][1].count(OMEGA) == 0 ):
				block['inputs']['custom_block'][1] = self.id+block['inputs']['custom_block'][1]
			elif block['opcode'] in ('procedures_prototype', 'procedures_call'):
				block['mutation']['argumentids'] = str([
					self.id+x if x.count(OMEGA) == 0 else x
					for x in eval(block['mutation']['argumentids'])
				]).replace("'", '"') # FIXME?
				block['inputs'] = {
					(self.id+key) if key.count(OMEGA) == 0 else key: value
					for key, value in block['inputs'].items()
				}
				if block['opcode'] == 'procedures_prototype':
					for input in block['inputs'].values():
						if input[1].count(OMEGA) == 0:
							input[1] = self.id+input[1]
		return self

	def get_module_blocks(self) -> dict:
		blocks = self.get_sprite('Main')['blocks']
		blocks = {
			key: block
			for key, block in blocks.items()
			if key.startswith(self.id)
			and not (
				block['opcode'] == 'procedures_definition'
				and '!' in blocks[block['inputs']['custom_block'][1]]['mutation']['proccode']
			)
		}
		for block in blocks.values():
			if block['topLevel']:
				block['x'] = 0
				block['y'] = 0
			if block['opcode'] == 'procedures_definition':
				if '_' in blocks[block['inputs']['custom_block'][1]]['mutation']['proccode']:
					block['shadow'] = True
		return blocks

	def get_blocks_except_module(self, module_name: str) -> dict:
		return {
			key: value
			for key, value in self.get_sprite('Main')['blocks'].items()
			if not key.startswith(module_name)
		}

	def add_module(self, module: 'Project') -> 'Project':
		self.list_modules().append(module.name)
		sprite = self.get_sprite('Main')
		module_sprite = module.get_sprite('Main')
		sprite['variables'] = {**sprite['variables'], **module_sprite['variables']}
		sprite['blocks'] = {**self.get_blocks_except_module(module.id), **module.get_module_blocks()}
		return self
	
	def remove_module(self, module_name: str) -> 'Project':
		""" module_name: Name of module without extension (not full path) """
		self.db['modules'].remove(module_name)
		sprite = self.get_sprite('Main')
		sprite['blocks'] = self.get_blocks_except_module(module_name)
		return self
	
	def list_modules(self) -> list:
		return self.db['modules']


class Interface:
	def __init__(self):
		try:
			self.interface()
		except Exception as e:
			rprint(f'[bold][red]{type(e).__name__}[/red][/bold]: {e}')
			exit(1)


	def interface(self):
		arg = sys.argv[1:]
		if len(arg) > 0:
			if len(arg) > 1:
				if arg[1] == 'info':
					self.info(arg[0])
				elif len(arg) > 2:
					if   arg[1] == 'add':
						self.add(arg[0], arg[2])
					elif arg[1] == 'remove':
						self.remove(arg[0], arg[2])
					else:
						rprint(f'[bold][red] {arg[1]} is not a valid command')
						exit(1)
				else:
					rprint('[bold][red] Missing module')
					exit(1)
		else:
			rprint('[bold][red] Please enter a command[/red] (See manual)')
			exit(1)
	
	def info(self, project_path):
		project = Project(project_path)
		project_modules = project.list_modules()
		if len(project_modules) == 0:
			rprint(f'[bold][yellow]{project.name}[/yellow][/bold] contains no modules')
			return
		rprint(f"[bold][yellow]{project.name}[/yellow][/bold]'s modules:")
		for module_name in project_modules:
			rprint(f' [bold][blue]*[/blue][/bold] {module_name}')
	
	def add(self, project_path: AnyPath, module_path: AnyPath):
		( Project(project_path)
			.make_block_ids_trackable()
			.add_module(Project(module_path).make_block_ids_trackable())
			.package_sb3() )

	def remove(self, project_path, module_id):
		( Project(project_path)
			.make_block_ids_trackable()
			.remove_module(module_id)
			.package_sb3() )


if __name__ == '__main__':
	Interface()
