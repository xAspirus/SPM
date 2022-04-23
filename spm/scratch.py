import tempfile
import json
from zipfile import ZipFile


class Project:
	def __init__(self, sb3_path: str):
		self.sprites: dict[str, Sprite]
		self.unpacked = tempfile.TemporaryDirectory()
		self.load_sb3(sb3_path)
	
	def load_sb3(self, sb3_path: str):
		with ZipFile(sb3_path, 'r') as sb3:
			self.json = json.loads(sb3.read('project.json'))
		self.load_attributes()
		return self
	
	def load_attributes(self):
		self.sprites = {
			sprite['name']: Sprite(sprite, self)
			for sprite in self.json['targets']
		}
		return self


class Variable:
	def __init__(self, id, name, value):
		self.id: str = id
		self.name: str = name
		self.value = value


class List:
	def __init__(self, id, name, value):
		self.id: str = id
		self.name: str = name
		self.value: list = value


class Comment:
	def __init__(self, id, block_id, x, y, width, height, minimized, text):
		self.id: str = id
		self.block_id: str = block_id
		self.x: float = x
		self.y: float = y
		self.width: float = width
		self.height: float = height
		self.minimized: bool = minimized
		self.text: str = text


class Costume:
	def __init__(self, assetId, name, md5ext, dataFormat, rotationCenterX, rotationCenterY, bitmapResolution=None):
		self.asset_id: str = assetId
		self.name: str = name
		self.bitmap_resolution: float = bitmapResolution
		self.md5ext: str = md5ext
		self.data_format: str = dataFormat
		self.rotation_center_x: float = rotationCenterX
		self.rotation_center_y: float = rotationCenterY


class Sound:
	def __init__(self, assetId, name, dataFormat, format, rate, sampleCount, md5ext):
		self.asset_id: str = assetId
		self.name: str = name
		self.data_format: str = dataFormat
		self.format: str = format
		self.rate: int = rate
		self.sample_count: int = sampleCount,
		self.md5ext: str = md5ext


class Sprite:
	def __init__(self, json: dict, project: Project):
		self.is_stage: bool
		self.name: str
		self.variables: dict[str, Variable]
		self.lists: dict[str, List]
		self.broadcasts: dict[str, str]
		self.comments: dict[Comment]
		self.costumes: dict[Costume]
		self.sounds: dict[Sound]
		self.blocks: dict[dict]

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
			var.id: [var.name, var.value]
			for var in self.lists.values()
		}
		self.json['comments'] = {
			com.id: [com.block_id, com.x, com.y, com.width, com.height, com.minimized, com.text]
			for com in self.comments.values()
		}
		self.json['costumes'] = [
			{
				'assetId': val.asset_id,
				'name': val.name,
				'bitmapResolution': val.bitmap_resolution,
				'md5ext': val.md5ext,
				'dataFormat': val.data_format,
				'rotationCenterX': val.rotation_center_x,
				'rotationCenterY': val.rotation_center_y
			}
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
		return self.json
	
	def load_attributes(self):
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
			id: Comment(id, *val)
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
