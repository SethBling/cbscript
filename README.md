# Introduction

CBScript is a transpiled language, designed by SethBling. This compiler will compile CBScript files into Minecraft datapack zip files. It has many higher level language features that don't exist at the Minecraft command level. Awareness of implementation details will help you avoid performance overhead and bugs. The files in the datapack are generally organized by source file line numbers to make it easier to find the particular compiled mcfunction files you're looking for.

# Installation and Requirements

The CBScript compiler requires python 2.7. In order to run it via the run.cmd file, you'll need the Python "py launcher", which comes with newer installations of Python, and can be used to launch a specific version. You'll need to install the Python dependencies with

```pip install -r requirements.txt```

There are instructions in run.cmd for setting up your Window registry to be able to double click .cbscript files in order to run the compiler.

You can use cbscript-npp-highlighting.xml with Notepad++ to add syntax highlighting.

# Running the Compiler

When you use run.cmd with your .cbscript file as an argument, a command window will pop up. This command window will monitor your .cbscript file for changes, and recompile any time it observes the file has been changed. Each cbscript file has a world file at the beginning that specifies where to place the compiled datapack. The compiled datapack will be placed in that world's /datapacks folder, with the same base name as the .cbscript file, overwriting it as necessary. You can use /reload in game to reload the datapack when it's been recompiled.

# Features

CBScript includes many high level features that simplify the syntax and construction of datapacks, as well as make them easier to maintain. Look at the scripts in the "/scripts" folder for examples. There are also archived script subfolders that contain datapacks for older versions of the game.

* Include files
* Arithmetic expressions
* For/while loops
* If/else if/else blocks
* Execute syntax
* Tellraw with simplified syntax
* Title/subtitle/actionbar with simplified syntax.
* Macro function support
* Entity selector definitions, including data paths
* Advancement/loot table/block tag/predicate definitions.
* Function/method calls with parameters.
* Switch, supporting both numbers and block types
* Compile-time variables
* Compile-time loop unrolling
* Compile-time macros
* Template functions
* Coordinate vectors
