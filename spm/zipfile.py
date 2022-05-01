import os


class Zip:
	@staticmethod
	def unzip(in_path: str, out_path: str):
		os.system(f"unzip -o '{in_path}' -d '{out_path}'")
	
	@staticmethod
	def zip(in_path: str, out_path: str):
		os.system(f"zip -rj '{out_path}' '{in_path}'")
