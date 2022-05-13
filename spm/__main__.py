import rich_click as click
from rich import print as rprint

from package import Package
from scratch import Project


@click.group()
def main():
	...


def get_main_sprite_name(project: Project) -> str:
	if project.name in project.sprites and project.name != 'Stage':
		return project.name
	else:
		return next(filter(lambda x: x != 'Stage', project.sprites))


@main.command('merge')
@click.argument('main_path')
@click.option('--main_sprite_name', type=str, default=None)
@click.argument('pkg_path')
@click.option('--pkg_sprite_name', type=str, default=None)
def merge(main_path: str, pkg_path: str, main_sprite_name: str, pkg_sprite_name: str):
	main = Project(main_path)
	pkg  = Project(pkg_path)
	if main_sprite_name is None:
		main_sprite_name = get_main_sprite_name(main)
	if pkg_sprite_name is None:
		pkg_sprite_name = get_main_sprite_name(pkg)
	Package.convert_sprite(main.sprites[main_sprite_name])
	Package.convert_sprite(pkg.sprites[pkg_sprite_name])
	main.sprites[main_sprite_name].add(pkg.sprites[pkg_sprite_name])
	main.export_sb3(main_path)


def remove(main_path: str, main_sprite_name: str, pkg_name: str):
	main = Project(main_path)
	if main_sprite_name is None:
		main_sprite_name = get_main_sprite_name(main)
	Package.convert(main.sprites[main_sprite_name])
	main.sprites[main_sprite_name].remove(pkg_name)
	main.export_sb3(main_path)


main()
