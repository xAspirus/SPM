from rich import print as rprint

from scratch import *

Self = None # Wait for Python 3.11
OMEGA = 'Ω'


class Package(Sprite):
	@classmethod
	def convert_sprite(cls, sprite: Sprite):
		sprite.__class__ = cls
		sprite.package_json: dict = {
			'costumes': {}
		}
		sprite.track()
		if 'package_json' not in sprite.blocks:
			raise Exception('16')
	
	def get_json(self):
		self.blocks['package_json']['parent'] = json.dumps(self.package_json)
		return super().get_json()
	
	def track(self):
		if 'package_json' in self.blocks:
			self.package_json = json.loads(self.blocks['package_json']['parent'])
		else:
			self.blocks['package_json'] = {
				'opcode': '',
				'next': None,
				'parent': '',
				'inputs': {},
				'fields': {},
				'shadow': True,
				'topLevel': False
			}
		for costume in self.costumes.values():
			if costume.name not in self.package_json['costumes']:
				self.package_json['costumes'][costume.name] = self.name
		package_json['costumes'] = {
			a:b
			for a,b in self.package_json['costumes'].items()
			if a in self.costumes
		}
		return self.track_block_ids()
	
	def get_blocks_except_pkg(self, pkg_name: str) -> dict[str, dict]:
		return {
			id:block for id,block in self.blocks.items()
			if not id.startswith(pkg_name)
		}
	
	def get_self_pkg_blocks(self, pkg_name: str) -> dict[str, dict]:
		return {
			id:block for id,block in self.blocks.items()
			if id.startswith(self.name)
			# Remove blocks with '#' in name:
			and not (
				block['opcode'] == 'procedures_definition'
				and '#' in self.blocks[block['inputs']['custom_block'][1]]['mutation']['proccode']
			)
		}
	
	def add(self, pkg_sprite: Self):
		self.variables = {**self.variables, **pkg_sprite.variables}
		self.lists = {**self.lists, **pkg_sprite.lists}
		self.costumes = {
			name:costume
			for name,costume in self.costumes.items()
			if name not in self.package_json[pkg_sprite.name]['costumes']
		}
		for costume in pkg_sprite.costumes.values():
			self.add_costume(costume, f'{pkg_sprite.project.unpacked.name}/{costume.md5ext}')
			self.package_json['costumes'][costume.name] = pkg_sprite.name
		self.blocks = {
			**self.get_blocks_except_pkg(pkg_sprite.name),
			**pkg_sprite.get_self_pkg_blocks(pkg_sprite.name)
		}
		return self
	
	def remove(self, pkg_name: str):
		self.blocks = self.get_blocks_except_pkg(pkg_name)
		for costume_name in self.package_json[pkg_name]['costumes']:
			self.remove_costume(costume_name)
		self.package_json['costumes'] = {
			a:b
			for a,b in self.package_json['costumes']
			if a != pkg_name
		}
		return self
	
	def track_block_ids(self):
		OMEGA = 'Ω'
		tag = self.name + OMEGA
		self.var = {
			var.name: var
			for name, var in self.variables.items()
		}
		for var in self.variables.values():
			var.id = var.name
		self.lists = {
			lst.name: lst
			for name, lst in self.lists.items()
		}
		for lst in self.lists.values():
			lst.id = lst.name
		self.blocks = {
			(tag+key) if (key.count(OMEGA) == 0 and key != 'package_json')
			else key: value
			for key, value in self.blocks.items()
		}
		for bid, block in self.blocks.items():
			if bid == 'package_json': continue
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
				block['mutation']['argumentids'] = json.dumps([
					tag+x if x.count(OMEGA) == 0 else x
					for x in json.loads(block['mutation']['argumentids'])
				], ensure_ascii=False) # aaaaaaaaaaaaaaaaa
				block['inputs'] = {
					(tag+key) if key.count(OMEGA) == 0 else key: value
					for key, value in block['inputs'].items()
				}
				if block['opcode'] == 'procedures_prototype':
					for input in block['inputs'].values():
						if input[1].count(OMEGA) == 0:
							input[1] = tag+input[1]
		return self
