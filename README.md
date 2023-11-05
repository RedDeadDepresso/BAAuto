# BAAuto: Blue Archive Automation Tool

<p align="center">
  <a href="https://github.com/RedDeadDepresso/BAAuto--gh-stats/commits/master/traffic/views">
    <img src="https://img.shields.io/badge/dynamic/json?color=success&label=Github%20views|all&query=count&url=https://github.com/RedDeadDepresso/BAAuto--gh-stats/raw/master/traffic/views/latest-accum.json?raw=True&logo=github" valign="middle" alt="GitHub views|any|total" />
    <img src="https://img.shields.io/badge/dynamic/json?color=success&label=14d&query=count&url=https://github.com/RedDeadDepresso/BAAuto--gh-stats/raw/master/traffic/views/latest.json?raw=True" valign="middle" alt="GitHub views|any|14d" /></a>
• <a href="https://github.com/RedDeadDepresso/BAAuto--gh-stats/commits/master/traffic/views">
    <img src="https://img.shields.io/badge/dynamic/json?color=success&label=Github%20views|unq&query=uniques&url=https://github.com/RedDeadDepresso/BAAuto--gh-stats/raw/master/traffic/views/latest-accum.json?raw=True&logo=github" valign="middle" alt="GitHub views|unique per day|total" />
    <img src="https://img.shields.io/badge/dynamic/json?color=success&label=14d&query=uniques&url=https://github.com/RedDeadDepresso/BAAuto--gh-stats/raw/master/traffic/views/latest.json?raw=True" valign="middle" alt="GitHub views|unique per day|14d" /></a>
</p>

<p align="center">
  <a href="https://github.com/RedDeadDepresso/BAAuto--gh-stats/commits/master/traffic/clones">
    <img src="https://img.shields.io/badge/dynamic/json?color=success&label=Github%20clones|all&query=count&url=https://github.com/RedDeadDepresso/BAAuto--gh-stats/raw/master/traffic/clones/latest-accum.json?raw=True&logo=github" valign="middle" alt="GitHub clones|any|total" />
    <img src="https://img.shields.io/badge/dynamic/json?color=success&label=14d&query=count&url=https://github.com/RedDeadDepresso/BAAuto--gh-stats/raw/master/traffic/clones/latest.json?raw=True" valign="middle" alt="GitHub clones|any|14d" /></a>
• <a href="https://github.com/RedDeadDepresso/BAAuto--gh-stats/commits/master/traffic/clones">
    <img src="https://img.shields.io/badge/dynamic/json?color=success&label=Github%20clones|unq&query=uniques&url=https://github.com/RedDeadDepresso/BAAuto--gh-stats/raw/master/traffic/clones/latest-accum.json?raw=True&logo=github" valign="middle" alt="GitHub clones|unique per day|total" />
    <img src="https://img.shields.io/badge/dynamic/json?color=success&label=14d&query=uniques&url=https://github.com/RedDeadDepresso/BAAuto--gh-stats/raw/master/traffic/clones/latest.json?raw=True" valign="middle" alt="GitHub clones|unique per day|14d" /></a>
</p>

![example](https://github.com/RedDeadDepresso/BAAuto/assets/94017243/8c661360-5667-401a-986d-3fb0f7400462)

BAAuto is a Python-based automation tool designed to streamline various tasks in Blue Archive. It's a modified version of Egoistically's [ALAuto](https://github.com/Egoistically/ALAuto), unfortunately only for the Global server with support for English and Chinese languages. With a user-friendly GUI, BAAuto simplifies tasks such as login, cafe, bounty, scrimmage, tactical challenge, mission, and reward claiming.

UPDATE: Another project, [MaaAssistantArknights/MBA](https://github.com/MaaAssistantArknights/MBA), is currently in development with more planned features. BAAuto will be supported until MBA reaches a significant stage in its development. However, no new features will be added.

## Table of Contents
- [Requirements on Windows](#requirements-on-windows)
- [Supported Emulators](#supported-emulators)
- [Graphics Settings in Blue Archive](#graphics-settings-in-blue-archive)
- [Installation and Usage](#installation-and-usage)
- [Known Bugs](#known-bugs)
- [Acknowledgment](#acknowledgment)

## Requirements on Windows
To use BAAuto effectively, you'll need the following:

- Python 3.7.X installed and added to your system's PATH.
- The latest [ADB](https://developer.android.com/studio/releases/platform-tools) added to your system's PATH.
- An ADB-debugging enabled emulator with a resolution of **1280x720** and running Android 5 or newer.

## Supported Emulators
BAAuto has been tested and confirmed to work with the following emulators:

- Bluestacks
- LDPlayer9
- MuMu Player

While other emulators may work, these have been tested extensively and are recommended for optimal performance.

## Graphics Settings in Blue Archive
For the best experience, configure your Blue Archive settings as follows:

- Minimum: Medium graphics settings at 30fps.
- Recommended: Medium, High, or Very High graphics settings at 60fps.
  
Please note that BAAuto may require adjustments to the source code if you choose lower graphics settings than the ones listed above.

## Installation and Usage
Follow these steps to get BAAuto up and running:

1. Clone or download this repository.
2. Install the required packages using `pip3` with the command `pip3 install -r requirements.txt`.
3. Ensure that ADB debugging is enabled on your emulator.
4. Run `BAAuto.py` and modify the connection address to match your emulator's ADB port and configure other settings to your preference.
5. Changes are automatically saved except for the Mission/Commissions/Event section.
6. For Event, you need to upload a cropped image of the event banner (without a background) in the `assets/EN/goto` or `assets/CN/goto` directory and save it as `event_banner.png`.
7. Avoid setting the number of sweeps higher than 30, as this may cause BAAuto to assume the game is stuck.
8. If you've enabled "Tap Students" in the Cafe, make sure to zoom out and swipe to the bottom-left corner before starting the script. You can make a pull request if you have a solution for zooming out using ADB.
9. If you've selected "Exit Emulator" or "Exit BAAuto and Emulator", provide the emulator path. For BlueStacks instances, create a shortcut for Blue Archive from the instance and choose it as the emulator path to ensure BAAuto only closes that specific instance.
10. If you'd like to create new assets, you can refer to [this guide](https://github.com/Egoistically/ALAuto/wiki/Creating-new-assets-for-bot).

Please feel free to use and modify BAAuto as you see fit. Your feedback and contributions are always welcome.

## Known Bugs
Here are some known issues with BAAuto:

- Ascreencap does not work; use uiautomator2 instead.
- The script relies heavily on "time.sleep()," which can make it slower at times.
- There's no implementation of data validation for the "config.json" file. The GUI and script may crash if the file is corrupted or contains incorrect data.

## Acknowledgment
I'd like to express my gratitude to the following individuals, listed in no particular order:

- [Akascape](https://github.com/Akascape): Provided customtkinter widgets that are both complex and user-friendly.
- [Egoistically](https://github.com/Egoistically): For making ALAuto open-source and providing the foundation for BAAuto.
- [hgjhgj](https://github.com/hgjazhgj): Supplied the BAAuto OCR library and was the first to star the repository, which greatly motivated me.
- [LmeSzinc](https://github.com/LmeSzinc) and [MistEO](https://github.com/MistEO): Creators of Alas and MAA, respectively, who inspired me to develop BAAuto.
- [TomSchimansky](https://github.com/TomSchimansky): Created customtkinter, making it possible for an inexperienced programmer like me to create a modern GUI.
