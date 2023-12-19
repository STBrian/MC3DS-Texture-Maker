# mc3ds-texture-maker
MC3DS Texture Maker is a python script that helps with the creation of new textures packs for the Minecraft:  New 3DS Edition.

# How to use
The README file refers to the latest version v1.0.0-beta.

When first opened, if running from the binary it will ask you to enter the name of the output folder you wish to be the folder where output files will be stored
```
Running from executable file
Enter the output folder:
```
Otherwise, if running from source, the default folder will be used `MC3DS`.

## Menu
In the menu there is a list of available options
```
Choose an option:
    1: Change an item texture
    2: Change a block texture
    0: Exit
Enter an option:
```
The options are self explanatory.

## Change an item/block texture
When selected option `1` or `2`, a submenu will show on screen
```
Choose an option:
    1: Search unmodified item by text
    2: Search modified item by text
    3: Show unmodified items
    4: Show modified items
    0: Back
Enter an option:
```
Again, the options are self explanatory.

### Search by text
If options `1` or `2` selected, then the program will ask for a search text
```
Enter the search text:
```
When you finish of writing the text simply press Enter, and the program will look for coincidences

### Show
When options `3` or `4` selected, the program will look for coincidences based on the option. For unmodified items or previously modified items by you, if you wish.

## Select an ID
Let's take an example. If you select `items`, the option `1` and type `carrot`, then the result list of items will look like this:
```
Enter the search text: carrot
1: carrot
2: arrow
3: golden_carrot
4: minecart
5: charcoal
6: cauldron
7: carrot_on_a_stick
8: quartz
9: camera
0: back
Enter the ID: 
```
In this part you need to enter the ID of the item which corresponds to the texture you want to change. 

If you want to change the `golden_carrot` texture, then need to type `3` and press Enter.

## Open the texture
This is the last part before you get the custom atlas.

In this part, a explorer window will show up asking to open an image file.

Search for the image you want to be replaced for

Once you selected it, just press the Open button.

The program will load you selected image and will automatically start the process.

## Output files
When finished, the program will store the custom atlas in the folder which name will be the one you previously selected. Inside the folder there will be an atlas folder where the atlas are stored.

To use them in game you need to know a bit about Luma and the layeredFS function it has.

But if you already know about that, prefect, you need to put your atlas in the directory `luma/titles/{your game ID}/romfs/atlas/` in your sdcard.

If you don't know your game ID, here's a list with the game IDs for each region version of the game:
|Region|Game ID|
|:-|:-|
|USA|00040000001B8700|
|EU|000400000017CA00|
|JP|000400000017FD00|

(You must use the one that corresponds to your game's region)

# Building
#### Windows
Open the `build.bat` file 

or 

Type the following command in a console in the root folder of the project:
```bash
pyinstaller mc3ds-tm.spec
```