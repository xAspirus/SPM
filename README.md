# Scratch Package Manager
Develop scratch projects by dividing code into modules.


## Installation
Just add a link to spm to a folder in your path.

```sh
link -sf /path/to/repo/spm.py ~/.bin/spm
# In your shell configs
# zsh:  ~/.zshrc
PATH+=(~/.bin)
# bash: ~/.bash_login
PATH=$PATH:~/.bin
```

# Warning: Using SPM with Turbowarp
Turbowarp has a feature which optimizes the IDs of blocks, which makes it
impossible for spm to track blocks. To fix this add this javascript code to
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
If using Turbowarp Desktop, see (Advanced customizations)[https://github.com/TurboWarp/desktop#advanced-customizations]
 

## Documentation

### Project requirements

1. Project must have a sprite named `Main`
2. All custom blocks which contain the `_` character will be not visible.
   (This causes a bug in DevTools which prompts to delete variables, even
   if they are used by these blocks. See #issue_pending )
3. All custom blocks which contain the `!` character will be not included
   when the project is added as a module.

### Basic Usage

#### Adding a module to a project
`spm /path/to/Main_Project.sb3 add /path/to/Module_Project.sb3`
All blocks, variables, lists and costumes from Module_Project.sb3 will be
added to Main_Project.sb3.

#### Removing a module from a project
`spm /path/to/Main_Project.sb3 remove Module_Project`
When removing a module, only specify the name of the module project.

#### Updating a module in a project
To update a module, just run the add command again. Any changes will be
reflected in the main project.

#### Dealing with Dependencies
spm will not resolve dependencies on its own. Just add every dependency to the
Main project. Only blocks which are not part of a module are included.
spm will prompt a list of dependent modules.

#### Workflow
Ideally, you should be using Turbowarp Desktop or the Scratch Desktop app and
work in a folder which holds all the modules and main project files.
After running any command, Ctrl+R will reload the editor.

### Advanced Usage

spm can be imported as a module in a python script to create a automated
build system.

## Thanks to

@scratch/garbomuffin
@scratch/geotale
