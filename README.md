# BAAuto
![example](https://github.com/RedDeadDepresso/BAAuto/assets/94017243/8c661360-5667-401a-986d-3fb0f7400462)
A modified version of [Egoistically's ALAuto](https://github.com/Egoistically/ALAuto) adapted for Blue Archive with GUI to automate simple tasks. Currently, only for the Global server with support for English and Chinese language, but it should be easy to implement new servers by changing the templates.

Tasks supported: Login, Cafe, Bounty, Scrimmage, Tactical Challenge, Mission/Commissions/Event and Claim Rewards

UPDATE: Someone is making one with more features planned than mine https://github.com/MaaAssistantArknights/MBA. I will try to maintain BAAuto until MBA is at a decent point in development. However, I don't plan to add any new features.

## Requirements on Windows
* Python 3.7.X installed and added to PATH.
* Latest [ADB](https://developer.android.com/studio/releases/platform-tools) added to PATH.
* ADB debugging enabled emulator with **1280x720 resolution** and **Android 5 or newer**.
  
## Graphics Settings in Blue Archive
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
7. DO NOT set the number of sweeps higher than 30. This will make BAAuto think that the game is stuck.
8. If you enabled Tap Students in Cafe, zoom out and swipe to bottom-left so that the bottom-left corner is visible before starting the script. Please make a pull request if you know how to zoom out using Adb.
9. Check the [Alauto's Wiki](https://github.com/Egoistically/ALAuto/wiki/Config.ini-and-Modules-explanation), some information are still relevant.

## Relevant information
* If you'd like to create new assets you can check [this guide](https://github.com/Egoistically/ALAuto/wiki/Creating-new-assets-for-bot).
* The GUI was inspired by [MaaAssistantArknights](https://github.com/MaaAssistantArknights/MaaAssistantArknights) and [Alas](https://github.com/LmeSzinc/AzurLaneAutoScript). It is just an interface to modify config.json and display script.py output.
* I am sorry if it does not follow best practices sometimes since this is my first project I tried to minimise modification to the original script. 
* Feel free to do whatever you want with BAAuto, I do not mind.

## Changes Made
* Changed resolution from 1920x1080 to 1280x720. 
* Changed config file to json.
* Implemented uiautomator2 to detect crashes. Threshold are same consecutive 60 clicks or 35 swipes.

## Bugs
* Ascreencap does not work. Use uiautomator2 instead.
* The GUI is a mess, in particularly the Mission/Commissions/Event section.
* The script depends highly on time.sleep() making it sometimes slow.
* No implementation of data validation for the config.json. GUI and Script will most likely crash if the file is corrupted or have incorrect data.

## Acknowledgement
The project was not possible thanks to these people, with no specific order of importance:
  - [Akascape](https://github.com/Akascape), who provided complex yet easy to use customtkinter widgets.
  - [Egoistically](https://github.com/Egoistically), for making ALAuto open-source and providing the foundations to build BAAuto.
  - [hgjhgj](https://github.com/hgjazhgj), not only for supplying the BAAuto OCR library but also for being first to star the repo, which greatly motivated me.
  - [LmeSzinc](https://github.com/LmeSzinc) and [MistEO](https://github.com/MistEO), the creators of Alas and MAA, respectively, who served as an inspiration for me to develop my own bot.
  - [TomSchimansky](https://github.com/TomSchimansky), whose created customtkinter allowing an inexperienced programmer like me to create a modern GUI.
