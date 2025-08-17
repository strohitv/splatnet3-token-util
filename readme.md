# SplatNet3-Token-Util
This project contains an application which can be used to extract the gToken and bullet_token from the Nintendo SplatNet3 app in the Nintendo Switch App. It does that by booting and controlling an Android emulator on which the App is installed. After opening SplatNet3, it saves an emulator snapshot which contains a dump of the RAM, and searches for the gToken inside that dump file. If it finds one, it'll attempt to get the bullet_token via request to Nintendo's servers, similar to how opening SplatNet3 does it.

The tokens get stored into a file which can be freely configured, however this project was created specifically to be compatible with [s3s](https://github.com/frozenpandaman/s3s) by frozenpandaman. For this reason, the example template file included here is compatible with the s3s config.txt file.

## QUICK START GUIDE FOR USERS: running s3s with the provided example files

An easy way to set up the script to work with s3s is described in [quickstart_s3s_guide.md](quickstart_s3s_guide.md). Please head there if you want to use this project in combination with s3s.

## For developers: Integration into other applications
If you are a developer and want to integrate splatnet3-token-util into your app, please refer to the [developer notes](./developer_notes.md) for a first introduction in how to do it. If you have any questions, feel free to open an issue, I'll get to it as soon as possible.

## Installation

This chapter contains a short summary of what you need to do to download and install this project locally.

### Prerequisites

Please install this software to use this script on your computer:
- an Android Emulator (I use Android Studio)
- git
- python in version 3.11 or higher
- pip - this usually is a part of python
- cURL

### Download & Create dependencies

These 3 commands will set up the script and prepare it for use:
```shell
# clone project
git clone git@github.com:strohitv/splatnet3-token-util.git

# install python requirements
pip install -r requirements.txt

# this will generate the configuration files in the ./config directory if they don't exist yet.
python main.py
```
After running them, you're good to go and can use the script.

## Token extraction workflow
Once everything is set up, running `main.py` will start the token extraction. Here's a short summary on what is going to happen step by step:
1. Boot an emulator with the requested AVD (Android Virtual Device = the emulated phone)
2. Once the boot is complete, run the  `./config/boot.txt`. This file contains step-by-step instructions on how to control the emulator until SplatNet3 is opened
3. As soon as SplatNet3 is open, a snapshot will be created. This snapshot contains a dump of the entire emulator RAM which should also contain tokens.
4. Next is to shut down the emulator again. This is done similar to step 2, but the steps required to close all apps and initiate the shutdown are in `./config/cleanup.txt`.
5. After the emulator has been shut down, the script will locate and open the RAM dump and search for the gToken and bullettoken. It can also search for the session token but this is disabled by default because it's not as stable as the other two.
6. If it finds all tokens, it will open `./config/template.txt` and replace these placeholders with the found values:
   - `{GTOKEN}` will be replaced with the gToken
   - `{BULLETTOKEN}` will be replaced with the bulletToken
   - `{SESSIONTOKEN}` will be replaced with the sessionToken
7. The final file will be written to `./config.txt` and can be used by other applications.

Most of these settings can be changed in `./config/config.json` which gets generated the first time the script is started.

## Important parts of the project
Here is a list of some important files and directories of the project structure

### Main files, documentation files and configuration files
- `main.py`: this is the main script which will be used to start the token extraction. Use `python main.py --help` to get the available arguments
- `run_s3s.py`: this script manages the integration with s3s. Unlike main.py, this script does not have its own help command because it redirects all arguments directly to s3s. Please use refer to [quickstart_s3s_guide.md](quickstart_s3s_guide.md) for additional documentation.
- `quickstart_s3s_tutortial.md`: this markdown file contains a documentation on how to connect splatnet3-token-util and s3s to add a local automatic token refresh to s3s.
- `config` directory: this directory contains configuration files for `main.py`
  - `config/config.json`: this configuration file gets created on first use and contains the configuration for `main.py`
  - `config/boot.txt`: this file contains the steps required to open SplatNet3 in the freshly opened emulator.
  - `config/cleanup.txt`: this file contains the steps required to close SplatNet3 and shut the emulator down once the tokens have been extracted.
  - `config/template.txt`: this file contains the the template file with placeholders. These placeholders will be replaced with the tokens and be written to `config.txt`.
- `config.txt`: the final generated file with all tokens added
- `steps_documentation.md`: this markdown file contains an automatically generated documentation of all steps you can use to control the emulator in `boot.txt` and `cleanup.txt`
- `script-examples` directory: this directory contains useful example files to help with setting up the project
  - `script-examples/config` contains sample configuration files. The `template.txt` file works with s3s and the `pixel_4_api_30_play_store` directory contains sample `boot.txt` and `cleanup.txt` files which work with a Pixel 4 API 30 AVD. These files are used in the [quickstart_s3s_guide.md](quickstart_s3s_guide.md).
  - `script-examples/systemd` contains sample systemd configuration files. These files can be used on a Linux computer to make the token extraction run based on a timer.
- `screenshots` directory: the emulator gets controlled mostly by matching a screenshot of the current emulator screen with template screenshots. If they match, something will be done and if they don't, something else will be done. The `screenshots` directory contains the template screenshots used for the comparison.

### Code files
- `main.py`: this is the main script which will be used to start the token extraction. Use `python main.py --help` to get the available arguments
- `run_s3s.py`: this script manages the integration with s3s. Unlike main.py, this script does not have its own help command because it redirects all arguments directly to s3s. Please use refer to [quickstart_s3s_guide.md](quickstart_s3s_guide.md) for additional documentation.
- `data` directory: this directory contains code to load and parse the `config/config.json` file to get the settings for `main.py`
- `steps` directory: this directory contains the implementation for the steps available in `config/boot.txt` and `config/cleanup.txt`. For usage documentation, please refer to `steps_documentation.md`.
- `utils` directory: this directory contains util files which are used throughout the project
  - `utils/config_utils.py`: methods which are used to load and generate the configuration files in the `config` directory
  - `utils/emulator_utils.py`: methods which control the emulator by calling `emulator` and `adb` applications (these apps are installed when installing the Android emulator)
  - `utils/script_utils.py`: this file contains all methods required for parsing and executing `boot.txt` and `cleanup.txt`
  - `utils/snapshot_utils.py`: this file is responsible for extracting the tokens from the RAM dump file
  - `utils/splatnet3_utils.py`: this file is used to check whether the tokens are valid by calling the SplatNet3 homepage
  - `utils/stats_utils.py`: this file is responsible for generating a statistics file which tracks duration and success of executions of the `main.py` script. This feature is not active by default and needs to be enabled in the `config/config.json` file first.
  - `utils/step_doc_creator.py`: this file generates the `steps_documentation.md` documentation file
  - `utils/template_utils.py`: this file fills the `config/template.txt` file with found tokens and stores it to `config.txt`

## main.py basic commands
Currently, `main.py` offers three main commands you can execute: 
```shell
# run token extraction
python main.py

# boot emulator (blocks until emulator shuts down)
python main.py --emu

# run adb command to control emulator
python main.py --adb="COMMAND ARGUMENTS"
# example: python main.py -adb="shell input tap X Y" to tap on position (X, Y) on the screen
```

### further command examples
PLEASE NOTE: this script does not work when several emulators are booted at the same time. If you do that and want to use the ADB commands, add `-s EMULATOR-NAME` to the adb command, for example `python main.py --adb="-s emulator-5554 shell input tap X Y"`

- start emulator: `python main.py --emu`
- do a tap on the emulator: `python main.py --adb="shell input tap X Y"`
- do a swipe on the emulator: `python main.py --adb="shell input swipe X1 Y1 X2 Y2 duration(ms)"`
- list all devices + ports: `python main.py --adb="devices"`
- save a screenshot: `python main.py --adb="exec-out screencap -p > FILENAME.png"` - this needs to be done using CMD because Powershell messes up the filename. FILENAME can freely be chosen
- save a snapshot: `python main.py --adb="emu avd snapshot save SNAPSHOT_NAME"` where SNAPSHOT_NAME can be freely chosen. Snapshots will be saved to `$HOME/.android/avd/{AVD_NAME}.avd/snapshots`, a dump of the RAM is in the `ram.bin` file
- force shutdown the emulator: `python main.py --adb="emu kill"`

**IMPORTANT**: to ensure the emulator is always reloading the NSA app from scratch, it needs to be closed before the emulator gets shut down!

## ram.bin file
- use a hex editor (recommendation: Linux: gHex, Windows: HxD) to search through the RAM
- not all Snapshots contain all Tokens sadly
- gtoken: search for `_gtoken=ey`
- bullettoken: search for `"bulletToken":"`, if not found, search for `Bearer ` and afterwards a weird String with roughly 124 characters
- sessionToken: search for `SessionToken">ey`, better string: `eyJhbGciOiJIUzI1NiJ9` (which usually is the first part of the session token)

# Contribution
If you want to add a feature or fix a bug, please fork the project and send a pull request once your code is ready to be merged. Please use "Conventional Commits" to create the commit message if possible. Additionally, please set your IDE up to respect the settings from the `.editorconfig` file. I appreciate all help! 

Should you need help with using the application or stumble across an error, please open an issue.

# License
This software is released under the Creative Commons BY-NC-SA 4.0 license. In short, this means:
- you may edit and redistribute the application, however you need to properly attribute the changed version so that your users can find the original project and can understand what changes were made and why.
- you are **not** permitted to use this application or a changed version in a commercial way, **no exceptions**!
- if you redistribute a changed version, you are required to put it under the same Creative Commons BY-NC-SA 4.0 or a compatible license. A "compatible" license is one which also has these three properties listed here.

Details can be found either in the [LICENSE file](./LICENSE) or at the [official Creative Commons website](https://creativecommons.org/licenses/by-nc-sa/4.0/).
