# BAAuto
A modified version of [Egoistically's ALAuto](https://github.com/Egoistically/ALAuto) adapted for Blue Archive with GUI to automate simple tasks. Currently, only for the EN server but it should be easy to implement new servers by changing the templates.
If you are on the CN server you can check [MapleWithered/Sensei007](https://github.com/MapleWithered/Sensei007) (I was not aware of its existence before starting this project).

## Requirements on Windows
* Python 3.7.X installed and added to PATH.
* Latest [ADB](https://developer.android.com/studio/releases/platform-tools) added to PATH.
* ADB debugging enabled emulator with **1280x720 resolution** and **Android 5 or newer**.
## Graphics Settings
* Minimum: Medium at 30fps
* Recommended: Medium, High or Very High at 60 fps. 
* Lower settings may be possible with some changes to the script.
* Tested on Windows 11 with BlueStacks.

## Installation and Usage
1. Clone or download this repository.
2. Install the required packages via `pip3` with the command `pip3 install -r requirements.txt`.
3. Enable adb debugging on your emulator.
4. Run `BAAuto.py` and change connection address to your emulator's adb port, then change the rest to your likings. 
5. Changes are automatically saved except for Mission/Commissions/Event in the Farming section
6. For Event you have to upload a crop of the event banner from homescreen or campaign screen without any background in assets/EN/goto and save it as event_banner.png.
7. Check the [Alauto's Wiki](https://github.com/Egoistically/ALAuto/wiki/Config.ini-and-Modules-explanation), some information are still relevant.

## Relevant information
* It started as a learning experience and a challenge for myself. However, I have been very busy lately so I am unsure to continue it. 
Feel free to do whatever you want with it, I do not mind.
* I am sorry if it does not follow best practices sometimes since this is my first project I tried to minimise modification to the original script. 
* If you'd like to create new assets you can check [this guide](https://github.com/Egoistically/ALAuto/wiki/Creating-new-assets-for-bot).
* The GUI was inspired by [MaaAssistantArknights](https://github.com/MaaAssistantArknights/MaaAssistantArknights) and [Alas](https://github.com/LmeSzinc/AzurLaneAutoScript). It is just an interface to modify config.json and display script.py output.

## Changes Made
* Changed resolution from 1920x1080 to 1280x720. 
* Changed config file to json.
* Implemented uiautomator2 to detect crashes. Threshold are same consecutive 60 clicks or 35 swipes.

## Bugs
* Ascreencap does not work. Use uiautomator2 instead.
* The GUI is a mess, in particularly the Mission/Commissions/Event section.
* The script depends highly on time.sleep() making it sometimes slow.
* No implementation of data validation for the config.json. Script will most likely crash if the file is corrupted.
