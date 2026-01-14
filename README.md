# What is MC3DS-Texture-Maker?
MC3DS-Texture-Maker it's a tool with the main purpose of helping texture creators for Minecraft: New Nintendo 3DS Edition, to make their work easier.

Luma's LayeredFS feature is currently used to load custom textures into the game. But in order to create your own textures it is necessary to directly modify the atlas that contains all the blocks or items in the game. And considering that it is necessary to use external tools to convert these atlases from the original format to an editable image in which with your photo editor you need to manually place each texture that you want to change, and later convert that edited image back to the original format, it is a heavy task.

Additionally, the atlas containing the game blocks has several bitmap versions within the file that are not easily modified. For these complicated tasks I have developed this tool.
# Requirements
The executable does not require nothing since all it's packaged inside, but for running from source you need to install some things
- Python 3.11 (at least)
- python3-tkinter
- Install other dependencies with ```pip install -r requirements.txt```
# How to use
The README file refers to the latest beta version v2.0-beta2 since version v1.0-release is outdated and I don't suggest using it

Please use the following video as support:

[![Watch the video](https://img.youtube.com/vi/aXB5lkiK7o4/hqdefault.jpg)](https://www.youtube.com/embed/aXB5lkiK7o4)

## Output files
When finished, the program will store the custom atlas in the folder you previously selected (or default MC3DS). Inside the folder there will be an atlas folder where the atlas are stored.

To use them in game you need to know a bit about Luma and the layeredFS function it has.

But if you already know about that, prefect, you need to put your atlas in the directory `luma/titles/{your game ID}/romfs/atlas/` in your sdcard.

If you don't know your game ID, here's a list with the game IDs for each region version of the game:
|Region|Game ID
|:-|:-|
|USA|00040000001B8700|
|EU|000400000017CA00|
|JP|000400000017FD00|

(You must use the one that corresponds to your game's region)
# Building
### Windows
Execute the `build.bat` file after installed the dependencies

### Linux
#### Install dependencies
```bash
sudo apt-get update
```
Install Python at least 3.11. Replace 3.11 with your version
```bash
sudo apt-get install python3.11 python3-tk python3-pip python3.11-dev
```
Install other dependencies. Replace 3.11 with your version
```bash
python3.11 -m pip install -r requirements.txt
```
#### Build script
```bash
bash ./build.sh --release
```
Execute the `build.sh` file after installed the dependencies
