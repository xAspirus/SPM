import json
import os

from rich import print as rprint

AnyPath = str
OMEGA = 'Ω'


class Zip:
	""" Header for zip/unzip commands """
	def unzip(in_path: str, out_path: str):
		os.system(f"unzip -o '{in_path}' -d '{out_path}'")
	
	def zip(in_path: str, out_path: str):
		os.system(f"zip -rj '{out_path}' '{in_path}'")


class Project:
	def __init__(self, sb3_path: AnyPath):
		self.name = sb3_path.split('/')[-1].replace('.sb3','')
		self.id = self.name + OMEGA
		self.sb3_path = sb3_path
		self.json = {}

		if not os.path.isfile(self.sb3_path):
			raise FileNotFoundError(f'Project file "{self.sb3_path}" does not exist')
		Zip.unzip(self.sb3_path, f'./__{self.name}__')
		with open(f'./__{self.name}__/project.json', 'r') as fp:
			self.json = json.loads(fp.read())
	
	def __del__(self):
		os.system(f"rm -rf './__{self.name}__'")

	def package_sb3(self, output_file: AnyPath = None):
		if output_file is None: output_file = self.sb3_path
		with open(f'./__{self.name}__/project.json', 'w') as fp:
			fp.write(json.dumps(self.json))
		Zip.zip(f'./__{self.name}__', output_file)
	
	def get_sprite(self, sprite_name: str):
		for sprite in self.json['targets']:
			if sprite['name'] == sprite_name:
				return sprite
		raise KeyError(f'Sprite "{sprite_name}" does not exist')

	def make_block_ids_trackable(self):
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
			if block['opcode'] == 'procedures_prototype':
				block['mutation']['argumentids'] = str([
					self.id+x if x.count(OMEGA) == 0 else x
					for x in eval(block['mutation']['argumentids'])
				]).replace("'", '"') # FIXME?
				block['inputs'] = {
					(self.id+key) if key.count(OMEGA) == 0 else key: value
					for key, value in block['inputs'].items()
				}
				for input in block['inputs'].values():
					if input[1].count(OMEGA) == 0:
						input[1] = self.id+input[1]

	def get_module_blocks(self):
		return {
			key: value
			for key, value in self.get_sprite('Main')['blocks'].items()
			if key.startswith(self.id)
		}

	def get_blocks_except_module(self, module_id):
		return {
			key: value
			for key, value in self.get_sprite('Main')['blocks'].items()
			if not key.startswith(module_id)
		}

	def add_module(self, module: 'Project'):
		sprite = self.get_sprite('Main')
		module_sprite = module.get_sprite('Main')
		sprite['variables'] = {**sprite['variables'], **module_sprite['variables']}
		sprite['blocks'] = {**self.get_blocks_except_module(module.id), **module.get_module_blocks()}
	
	def remove_module(self, module_id):
		sprite = self.get_sprite('Main')
		sprite['blocks'] = self.get_blocks_except_module(module_id)
