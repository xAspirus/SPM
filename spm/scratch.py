import json
import os
import tempfile
from zipfile import Zip


class Project:
	def __init__(self, sb3_path: str):
		self.name = sb3_path.split('/')[-1].replace('.sb3','')
		self.sprites: dict[str, Sprite]
		self.unpacked = tempfile.TemporaryDirectory()
		self.load_sb3(sb3_path)
	
	def load_sb3(self, sb3_path: str):
		Zip.unzip(sb3_path, self.unpacked.name)
		with open(f'{self.unpacked.name}/project.json', 'r') as fp:
			self.json = json.loads(fp.read())
		self.load_attributes()
		return self

	def export_sb3(self, sb3_path: str):
		with open(f'{self.unpacked.name}/project.json', 'w') as fp:
			fp.write(json.dumps(self.get_json(), ensure_ascii=False))
		Zip.zip(self.unpacked.name, sb3_path)
		return self

	def load_attributes(self):
		self.sprites = {
			sprite['name']: Sprite(sprite, self)
			for sprite in self.json['targets']
		}
		return self
	
	def get_json(self):
		self.json['targets'] = [
			sprite.get_json()
			for sprite in self.sprites.values()
		]
		return self.json


class Variable:
	def __init__(self, id, name, value, is_cloud=False):
		self.id: str = id
		self.name: str = name
		self.value = value
		self.is_cloud = is_cloud


class List:
	def __init__(self, id, name, value):
		self.id: str = id
		self.name: str = name
		self.value: list = value


class Comment:
	def __init__(self, id, blockId, x, y, width, height, minimized, text):
		self.id: str = id
		self.block_id: str = blockId
		self.x: float = x
		self.y: float = y
		self.width: float = width
		self.height: float = height
		self.minimized: bool = minimized
		self.text: str = text


class Costume:
	def __init__(self, assetId, name, md5ext, dataFormat, rotationCenterX,
	             rotationCenterY, bitmapResolution=None
				):
		self.asset_id: str = assetId
		self.name: str = name
		self.bitmap_resolution: float = bitmapResolution
		self.md5ext: str = md5ext
		self.data_format: str = dataFormat
		self.rotation_center_x: float = rotationCenterX
		self.rotation_center_y: float = rotationCenterY
	
	def get_json(self) -> dict:
		json = {
			'assetId': self.asset_id,
			'name': self.name,
			'bitmapResolution': self.bitmap_resolution,
			'md5ext': self.md5ext,
			'dataFormat': self.data_format,
			'rotationCenterX': self.rotation_center_x,
			'rotationCenterY': self.rotation_center_y
		}
		if self.bitmap_resolution is None:
			json.pop('bitmapResolution')
		return json


class Sound:
	def __init__(self, assetId, name, dataFormat, format, rate, sampleCount,
	             md5ext):
		self.asset_id: str = assetId
		self.name: str = name
		self.data_format: str = dataFormat
		self.format: str = format
		self.rate: int = rate
		self.sample_count: int = sampleCount
		self.md5ext: str = md5ext


class Sprite:
	def __init__(self, json: dict, project: Project):
		self.is_stage: bool
		self.name: str
		self.variables: dict[str, Variable]
		self.lists: dict[str, List]
		self.broadcasts: dict[str, str]
		self.comments: dict[str, Comment]
		self.costumes: dict[str, Costume]
		self.sounds: dict[str, Sound]
		self.blocks: dict[str, dict]

		self.project: Project = project
		self.json: dict = json
		self.load_attributes()
	
	def get_json(self):
		self.json['isStage'] = self.is_stage
		self.json['variables'] = {
			var.id: [var.name, var.value]
			for var in self.variables.values()
		}
		self.json['lists'] = {
			lst.id: [lst.name, lst.value]
			for lst in self.lists.values()
		}
		self.json['comments'] = {
			com.id: {
				'blockId': com.block_id,
				'x': com.x,
				'y': com.y,
				'width': com.width,
				'height': com.height,
				'minimized': com.minimized,
				'text': com.text
			}
			for com in self.comments.values()
		}
		self.json['costumes'] = [
			val.get_json()
			for val in self.costumes.values()
		]
		self.json['sounds'] = [
			{
				'assetId': val.asset_id,
				'name': val.name,
				'dataFormat': val.data_format,
				'format': val.format,
				'rate': val.rate,
				'sampleCount': val.sample_count,
				'md5ext': val.md5ext
			}
			for val in self.sounds.values()
		]
		self.json['blocks'] = self.blocks
		return self.json
	
	def load_attributes(self):
		self.name = self.json['name']
		self.is_stage = self.json['isStage']
		self.variables = {
			val[0]: Variable(id, *val)
			for id, val in self.json['variables'].items()
		}
		self.lists = {
			val[0]: List(id, *val)
			for id, val in self.json['lists'].items()
		}
		self.broadcasts = self.json['broadcasts']
		self.comments = {
			id: Comment(id, **val)
			for id, val in self.json['comments'].items()
		}
		self.costumes = {
			val['name']: Costume(**val)
			for val in self.json['costumes']
		}
		self.sounds = {
			val['name']: Sound(**val)
			for val in self.json['sounds']
		}
		self.blocks = self.json['blocks']
		return self
	
	def add_new_costume(self, costume_name: str, costume_path: str):
		raise NotImplemented
		return self
	
	def add_costume(self, costume: Costume, costume_path):
		self.costumes[costume.name] = costume
		os.system(f"cp '{costume_path}' '{self.project.unpacked.name}'")
		return self
	
	def remove_costume(self, costume_name: str):
		os.system(f"rm '{self.project.unpacked.name}/{self.costumes[costume_name].md5ext}'")
		self.costumes.pop(costume_name)
		return self
	
	def add_new_sound(self, sound_name: str, sound_path: str):
		raise NotImplemented
		return self
	
	def add_sound(self, sound: Sound, sound_path: str):
		raise NotImplemented
		return self
