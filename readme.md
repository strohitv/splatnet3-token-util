# SplatNet3-Token-Util
This project contains an application which can be used to extract the gToken and bullet_token from the Nintendo SplatNet3 app in the Nintendo Switch App. It does that by booting and controlling an Android emulator on which the App is installed. After opening SplatNet3, it saves an emulator snapshot which contains a dump of the RAM, and searches for the gToken inside that dump file. If it finds one, it'll attempt to get the bullet_token via request to Nintendo's servers, similar to how opening SplatNet3 does it.

The tokens get stored into a file which can be freely configured, however this project was created specifically to be compatible with [s3s](https://github.com/frozenpandaman/s3s) by frozenpandaman. For this reason, the example template file included here is compatible with the s3s config.txt file.

## QUICK START: running s3s with the provided example files

Here are instructions for the most common use case: extracting the tokens and using them to run [s3s](https://github.com/frozenpandaman/s3s) by frozenpandaman. While splatnet3-token-util is designed to be highly configurable, example files for an easy setup and chaining to s3s are provided for user comfort. This quick start guide will show you how to set up everything quickly using the example files.

The first step is to install several required dependencies (pip dependencies, Android Studio, s3s) and setting up the emulator to be in a state that the app can use.

### OPTIONAL: install Miniconda
You should to install miniconda first. Miniconda allows you to split your python installation into several environments, each with their own dependencies installed. If you use multiple python applications each with their own dependencies, you can create an environment for each of them and you will never have conflicts because two apps require different versions of the same dependency.

After miniconda has been installed, create a new environment and set it to be the active one with these commands:
```shell
conda env create --name splatnet3-token-util anaconda::pip
conda activate splatnet3-token-util
```
(you can give the environment another name, splatnet3-token-util is just recommended because it's the name of this project)

### Install dependencies with pip

To install or update the dependencies, use this command:
```shell
pip install -r requirements.txt
```

On some operating systems, pip might not be a known command. In this case, usually something like this works:
```shell
pip3 install -r requirements.txt
python -m pip install -r requirements.txt
python3 -m pip install -r requirements.txt
```

If none of these work either, please resort to a search on the internet to find out how to use pip on python on your operating system.

### Create the config files
The app gets controlled by config files stored in the `./config` directory. To create them, run this command:
```shell
python main.py -r
```

Afterwards, copy `boot.txt`, `cleanup.txt` and `template.txt` from `./script-examples/config` into the freshly created `./config` directory.

In `template.txt`, replace `INSERT_YOUR_STAT_INK_API_KEY_HERE` with your stat.ink api key found on the [profile page](https://stat.ink/profile). Change the language setting if necessary.  
**DO NOT** put a real URL into the `f_gen` setting. This application is thought to be an alternative to the f generation apis. Please do not flood them with weird requests should errors occur.

We don't need to edit `config.json` yet. 

Now that this step is completed, you can use the following commands later in section [Install Android Studio](### Install Android Studio) to run emulator and adb commands:
```shell
# boot emulator (blocks until emulator shuts down)
python main.py --emu

# run adb command to control emulator
python main.py --adb="COMMAND ARGUMENTS"
# example: python main.py -adb="shell input tap X Y" to tap on position (X, Y) on the screen
```

### Install s3s
Please install [s3s](https://github.com/frozenpandaman/s3s) by frozenpandaman. For installation instructions, read the readme.md of the s3s project.

### Install Android Studio
This application was written to be compatible with the Android emulator included in Android Studio. Please install Android Studio on your operating system, usually there are good guides if you search for them on the internet. Afterwards, follow the [initial steps](### Initial Steps) to create and set up the emulator.

Continue here once the initial steps are done.

### Edit config.json
Open `./config/config.json` and check that all settings are correct:
- First,ensure that `adb_path`, `emulator_path` and `snapshot_dir` exist. If they don't, search them on your drive or look up the default path for your operating system on the internet.
- `show_window` should probably remain `true` - on all my computers setting it to `false` crashes the script
- keep `extract_session_token` on `false` - we won't let s3s refresh the tokens by itself so a session token is not necessary.
- keep `debug` on `false` unless you know what you're doing and if you really need to get debug logs.
- if you want an "Excel" file containing a small summary of all runs, set `log_stats_csv` to `true`
- `max_attempt_duration_seconds` sets how many seconds the script is allowed to use to boot the emulator, open SplatNet3, create the snapshot and shut the emulator down again. If it takes longer, a HARD reset will be done, forcing it to start all over again. This is to prevent the script from getting stuck (for example because it accidentially did something which it wasn't supposed to be doing and now it's in the wrong menu)
- `max_run_duration_minutes` sets how many minutes may pass until the script does not retry again and gives up instead. If it takes that long to find the token, something is probably broken and needs to be fixed.

### Copy and edit the application script
Copy `./script-examples/run-s3s.sh` to `./run-s3s.sh`.

Afterwards, open `./run-s3s.sh` and edit the variables at the start of the file in the `# VARIABLES` section so that they work with your installation.

**IMPORTANT:** I recommend to not edit `./script-examples/run-s3s.sh` directly. Copy the file somewhere else and edit the newly created one instead. Updating the splatnet3-token-util might not be possible anymore if you edit `./script-examples/run-s3s.sh` directly because of conflicts in the file.

### Run splatnet3-token-util and s3s
To run s3s in combination with splatnet3-token-util, simply execute the edited shell script from a terminal window instead of using s3s directly.

`sh run-s3s.sh` simply forwards the command line arguments to s3s which means you can use it the same way you would normally use s3s:
```shell
# these uses of s3s...
python s3s.py -M -r
python3 s3s.py -M -r
# ... both translate to this use of run-s3s.sh with added automatic token refresh:
sh run-s3s.sh -M -r

# run either of these commands to get a list of s3s commands (which are all supported by run-s3s.sh)
sh run-s3s.sh 
sh run-s3s.sh -h
sh run-s3s.sh --help
```

`run-s3s.sh` will try to execute s3s with the given parameters. If s3s exits with return code 0 or an error code (usually RC 1), run-s3s.sh will exit with the same result.

It behaves different if s3s finishes with the "outdated tokens" `--norefresh` return code (default: 42): once the tokens are outdated, splatnet3-token-util will be called to refresh the tokens. The newly created `config.txt` file with valid tokens will be copied into the s3s directory and afterwards the run-s3s.sh will automatically restart to call s3s again.

If s3s gets called with monitoring mode (`-M`), the script will switch between s3s monitoring mode and token refresh indefinitely until it gets manually stopped by using `CTRL` + `V`.

**IMPORTANT**: the script ensures that a token refresh will only happen if s3s does not find valid tokens. The bullet_token is valid for 2 hours so there is no need to refresh the tokens earlier. **DO NOT** change to code to act differently and **DO NOT** flood Nintendo with token refreshes!

## Usage
The application will create default configs in the `./config/` folder at first launch.

Once that is done, edit the `./config/boot.txt` and `./config/cleanup.txt` files to mimic user behaviour when accessing the NSA SplatNet3 app via the emulator.

Examples of boot and cleanup scripts are located in the `./script-examples` folder while basic screenshots for comparison are provided in the `./screenshots` folder.

## Command line parameters
```shell
# deletes and creates the config files anew. This option is used to FORCE the deletion and recreation, config files will automatically be generated without this flag should one missing.
python main.py -r 

# file path of the config file. Since all other settings are stored in the config file, this parameter can be used to create different runs (for example if different emulators for different switch accounts should be started).
python main.py -c [CONFIG]

# boot emulator (blocks until emulator shuts down)
python main.py --emu

# run adb command to control emulator
python main.py --adb="COMMAND ARGUMENTS"
# example: python main.py -adb="shell input tap X Y" to tap on position (X, Y) on the screen
```


## Steps required to set up token extraction
There's initial steps required to do once. Once the emu is set up, it needs to be brought to a state where you can extract the tokens from RAM, then a snapshot needs to be done. Finally, the RAM dump needs to be analysed.

Note: The name of the example Emulator used in this tutorial is `SN3`, so everywhere this name appears it's the name of the emulated device.

### Initial steps
1. Install Android Studio (only possible with an x64 architecture)
2. Create an Emulator, choose a newer Android version with Google Play installed. **QUICK START**: use Pixel 8 with Android API level 30 (Android 11). Set `SN3` as name and set it to cold boot.
3. After creation, close Android Studio and don't use it anymore. Changes done to the android system while hosting the emulator in Android Studio won't always reflect to the status of the emulator this script will use. To avoid this, boot the emulator via command line with the command `python main.py --emu`. **DO NOT USE ANDROID STUDIO FROM HERE ON, USE THE COMMAND LINE COMMANDS ONLY**
4. [optional / required for **QUICK START**] Once the emulator is started, open Settings -> Accessibility -> System Controls -> Change `System Navigation` to `3 buttons` and also System -> Gestures -> Press & hold power button -> Set to `Power menu` so that holding the the power button will bring up the power menu
5. Open Google Play Store and do the login with your Google Account. Select "No" for "Back up device data"
6. Install the Nintendo Switch App (NSA) via Google Play
7. Open NSA, don't allow sending usage data and do the Login using your Nintendo account. If Chrome asks whether you want to use your gmail account, disallow ("Use without an account")
8. Once you're logged in on NSA, open SplatNet3 once to ensure it's working fine. It's ok if it displays an error message, the token extraction will still work as long as you can get to the greyish SplatNet3 design.
9. Close all apps via task manager
10. Tap and Hold the NSA app until the menu opens. Then drag it to the main screen on the left side directly below the clock, as it can be seen on the [main menu snapshot image](./screenshots/template-emulator-main-menu.png).
11. Go to Play Store -> Profile -> Manage apps & device -> Manage tab -> Tap on NSA app -> Tap on the three dots on the top right corner -> check "Enable Auto Update"
12. Close all apps via task manager
13. Shut down the emulator by using the control panel window to simulate a long power button press and then select 'Power Off'. If you're following the **QUICK START** instructions, skip steps 14-16 and head back to the guide above.
14. **OPTIONAL from here on** If you're creating your own boot.txt and cleanup.txt scripts: Slowly simulate the clicks required to open the NSA app + SplatNet 3 main menu by slowly doing taps and write down the screen positions (X and Y) at the top screen everytime you do a tap (write down start and end positions for swipes). Also pay attention to how long each screen loads - that wait time should be at least double. Ideally, opening SplatNet3 should only be three taps if the NSA app is located on the default main screen.
15. You can also use ADB (see commands below) via `python main.py -adb="COMMAND"` to store screenshots of every step to take an image comparison to be more certain on where you are right now.
16. At the end, close all apps via task manager and shut down the emulator again.

This should be everything required. Next up is the automation

### Automation - Commands
PLEASE NOTE: this script does not work when several emulators are booted at the same time. If you do that and want to use the ADB commands, add `-s EMULATOR-NAME` to the adb command, for example `python main.py --adb="-s emulator-5554 shell input tap X Y"`

- start emulator: `python main.py --emu`
- do a tap on the emulator: `python main.py --adb="shell input tap X Y"`
- do a swipe on the emulator: `python main.py --adb="shell input swipe X1 Y1 X2 Y2 duration(ms)"`
- list all devices + ports: `python main.py --adb="devices"`
- save a screenshot: `python main.py --adb="exec-out screencap -p > FILENAME.png"` - this needs to be done using CMD cause Powereshell messes up the filename. FILENAME can freely be chosen
- save a snapshot: `python main.py --adb="emu avd snapshot save SNAPSHOT_NAME"` where SNAPSHOT_NAME can be chosen as the user pleases. Snapshots will be saved to `$HOME/.android/avd/SN3.avd\snapshots`, RAM dump is in the `ram.bin` file
- force shutdown the emulator: `python main.py --adb="emu kill"`
- **IMPORTANT**: to ensure it's always reloading the app from scratch, it needs to be closed before the emulator gets shut down!

### ram.bin file
- use a hex editor (recommendation: Linux: gHex, Windows: HxD) to search through the RAM
- not all Snapshots contain all Tokens sadly
- gtoken: search for `_gtoken=ey`
- bullettoken: search for `"bulletToken":"`, if not found, search for `Bearer ` and afterwards a weird String with roughly 124 characters
- sessionToken: search for `SessionToken">ey`, better string: `eyJhbGciOiJIUzI1NiJ9` (which usually is the first part of the session token)

# Contribution
If you want to add a feature or fix a bug, please fork the project and send a pull request once you're done. I appreciate all help!

Should you need help with using the application or stumble across an error, please open an issue.

# License
This software is released under the Creative Commons BY-NC-SA 4.0 license. In short, this means:
- you may edit and redistribute the application, however you need to properly attribute the changed version so that your users can find the original project and can understand what changes were made and why.
- you are **not** permitted to use this application or a changed version in a commercial way, **no exceptions**!
- if you redistribute a changed version, you are required to put it under the same Creative Commons BY-NC-SA 4.0 or a compatible license. A "compatible" license is one which also has these three properties listed here.

Details can be found either in the [LICENSE file](./LICENSE) or at the [official Creative Commons website](https://creativecommons.org/licenses/by-nc-sa/4.0/).