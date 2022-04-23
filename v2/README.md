# Scratch Package Manager
Develop scratch projects by dividing code into modules.


## Installation
Requirements:
 * python3
 * python modules:
    * rich
 * zip
 * unzip

Add a symlink to spm.py in /usr/bin/spm and use `git pull` to update.


## Warning: Using SPM with Turbowarp
Turbowarp has a feature which optimizes the IDs of blocks, which makes it
impossible for SPM to track blocks. To fix this add this javascript code to
a userscript.
Warning: SPM will not work with Turbowarp without this fix!
```js
var originalToJson = vm.toJSON;
vm.toJSON = function() {
	return originalToJson.call(
		this,
		{
			allowOptimization: false
		}
	)
}
```
If using Turbowarp Desktop, see [Advanced customizations](https://github.com/TurboWarp/desktop#advanced-customizations)
 

## Documentation

### Project requirements

1. Package modules must have a sprite named `Main`
2. All custom blocks which contain the `_` character will be not visible.
   (This causes a bug in DevTools which prompts to delete variables, even
   if they are used by these blocks. See #issue_pending )
3. All custom blocks which contain the `!` character will be not included
   when the project is added as a module.

### Basic Usage

#### Initializing a project for use with SPM
`spm /path/to/project.sb3 init`

After init, add a name and description in the config comment in the backdrop.
Do not remove the config comment.

#### Adding a package to a project's sprite
`spm /path/to/project.sb3 SpriteName add /path/to/package.sb3`

All blocks, variables, lists and costumes from package.sb3 will be
added to project.sb3 .

#### Removing a package from a project's sprite
`spm /path/to/project.sb3 SpriteName remove PackageName`

When removing a package, only specify the name of the package.

#### Updating a package in a project
To update a package, just run the add command again. Any changes will be
reflected in the project.

#### Dealing with Dependencies
SPM will not resolve dependencies on its own. Just add every dependency to the
Main project. Only blocks which are not part of a package are included.

#### Workflow
In the add command, if package is not a path to a .sb3 file, SPM will look inside the spm-modules directory.
After running any command, Do Ctrl+R to reload the editor.

### Advanced Usage

SPM can be imported as a module in a python script to create a automated
build system.

## Thanks to

* @scratch/garbomuffin
* @scratch/geotale
