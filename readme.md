# Installation
First, install Android Studio + emulator. Then do the [initial steps](## Initial steps) listed further down to prepare the emulator for the token extraction.

You need to install miniconda first. Afterwards, install the required libs using this command:
```shell
conda env create --name splatnet3-token-util --file conda-environment.yml
```
(you can give the environment another name, splatnet3-token-util is just recommended because it's the name of this project)

# Usage
The application will create default configs in the `./config/` folder at first launch.

Once that is done, edit the `./config/boot.txt` and `./config/cleanup.txt` files to mimic user behaviour when accessing the NSO SplatNet3 app via the emulator.

Examples of boot and cleanup scripts are located in the `./script-examples` folder while basic screenshots for comparison are provided in the `./screenshots` folder.

# Command line parameters
```shell
# deletes and creates the config files anew. This option is used to FORCE the deletion and recreation, config files will automatically be generated without this flag should one missing.
python main.py -r 

# file path of the config file. Since all other settings are stored in the config file, this parameter can be used to create different runs (for example if different emulators for different switch accounts should be started).
python main.py -c [CONFIG]
```


# Steps required to set up token extraction
There's initial steps required to do once. Once the emu is set up, it needs to be brought to a state where you can extract the tokens from RAM, then a snapshot needs to be done. Finally, the RAM dump needs to be analysed.

Note: The name of the example Emulator used in this tutorial is `NSO_SplatNet3_Pixel_8_API_34`, so everywhere this name appears it's the name of the emulated device.

## Initial steps
1. Install Android Studio (only possible with an x64 architecture)
2. Create an Emulator, choose a newer Android version with Google Play installed
3. After creation, use the `list emulators` and `start emulators` commands to start the emulator as Android Studio uses the default snapshot different. Changes done to the android system while hosting the emulator in Android Studio won't always reflect to the status of the emulator this script will use.
4. [optional but recommended] Open Settings -> Accessibility -> System Controls -> Change System Navigation to 3 buttons and also System -> Gestures -> Press & hold power button -> Set to Power menu so that the power button will bring up the power menu
5. Start the Emulator, open Google Play Store and do the login with your Google Account. Select "No" for "Back up device data"
6. Install NSO app via Google Play
7. Open NSO app, don't allow sending usage data and do the Login using your Nintendo account. If Chrome asks whether you want to use your gmail account, disallow ("Use without an account")
8. Once you're logged in, go to the main menu by pressing the main button
9. Press the main button a second time to get to the default screen
10. Open the app launcher menu which contains all apps
11. Tap and Hold the NSO app until the menu opens. Then drag it to the main screen on a good position
12. Head to Settings App
13. Go to your Android build number (usually in the About menu down at the end) and tap the build number ~7 times, until a message appears telling you you're a developer now
14. Go to Settings -> System -> Developer Mode and activate USB debugging as well as Show Taps and Show Pointer Location to get detailed information about where your tap is located. This allows for an easier tap position evaluation later for automation
15. Disable Developer Mode again
16. Go to Play Store -> Profile -> Manage apps & device -> Manage tab -> Tap on NSO app -> Tap on the three dots on the top right corner -> check "Enable Auto Update"
16. Close Play Store 
17. Close the emulator
18. Head to the config.ini file of the emulator (for example: `C:\Users\<USER>\.android\avd\NSO_SplatNet3_Pixel_8_API_34.avd\config.ini`) and edit it
19. Set these options as follows: `fastboot.forceChosenSnapshotBoot=no` and `fastboot.forceColdBoot=yes` and `fastboot.forceFastBoot=no` and `hw.gpu.enabled=no` and `hw.gpu.mode=off`. Both `hw.gpu` settings are required to allow the emulator to run in headless (no-window) mode, which is better for automation.
20. Save the file and close it again
21. Start the emulator again: Slowly simulate the Clicks required to open the NSO app + SplatNet 3 main menu by slowly doing taps and write down the screen positions (X and Y) at the top screen everytime you do a tap (write down start and end positions for swipes). Also pay attention to how long each screen loads (should I just wait for a default time instead of doing some kind of screen capture) - that wait time should be doubled or more. Ideally, it should only be three taps if the NSO app is located on the default main screen.
22. You can also use ADB (see commands below) to store screenshots of every step to take an image comparison to be more certain on where you are right now.
23. At the end, close all apps and shut down the emulator again.

This should be everything required. Next up is the automation

## Automation - Commands
- list emulators: `C:\Users\<USER>\AppData\Local\Android\Sdk\emulator\emulator.exe -list-avds`
- start emulator: `C:\Users\<USER>\AppData\Local\Android\Sdk\emulator\emulator.exe -avd NSO_SplatNet3_Pixel_8_API_34 -no-window` without opening a window of the emulator - wait for the `INFO    | Boot completed in 27392 ms` message and then wait some more seconds (maybe 5) because that message comes a bit early.
- do a tap on the emulator: `C:\Users\<USER>\AppData\Local\Android\Sdk\platform-tools\adb.exe shell input tap X Y`
- do a swipe on the emulator: `C:\Users\<USER>\AppData\Local\Android\Sdk\platform-tools\adb.exe shell input swipe X1 Y1 X2 Y2 [duration(ms)]`
- list all devices + ports: `C:\Users\<USER>\AppData\Local\Android\Sdk\platform-tools\adb.exe devices`
- save a screenshot: `cmd /C "C:\Users\<USER>\AppData\Local\Android\Sdk\platform-tools\adb.exe exec-out screencap -p > FILENAME.png"` - this needs to be done using CMD cause Powereshell messes up the filename. FILENAME can freely be chosen
- save a snapshot: `C:\Users\marco.lenovo-laptop\AppData\Local\Android\Sdk\platform-tools\adb.exe -s EMULATOR_NAME emu avd snapshot save SNAPSHOT_NAME` where EMULATOR_NAME comes from the list all devices + ports command and SNAPSHOT_NAME can be chosen as the user pleases. Snapshots will be saved to `C:\Users\<USER>\.android\avd\NSO_SplatNet3_Pixel_8_API_34.avd\snapshots`, RAM dump is in the `ram.bin` file
- shutdown the emulator: `C:\Users\<USER>\AppData\Local\Android\Sdk\platform-tools\adb.exe -s emulator-5554 emu kill`
- **IMPORTANT**: not all tokens are always in the RAM, I have the best success when doing the snapshot very shortly after the homepage has been loaded. Especially Bullettoken and sometimes SessionToken get garbage collected very quickly, so don't wait too long! For BulletToken, it's a time window of maybe 3 seconds before the garbage collection starts deleting the RAM fragments which allow finding the SAFE bulletToken (`Bearer ` strings are available much longer so a fallback is possible).
- **IMPORTANT 2**: to ensure it's always reloading the app from scratch, it needs to be closed before the emulator gets shut down!

## ram.bin file
- use a hex editor (Windows: HxD) to search through the RAM
- not all Snapshots contain all Tokens sadly
- gtoken: search for `_gtoken=ey`
- bullettoken: search for `"bulletToken":"`, if not found, search for `Bearer ` and afterwards a weird String with roughly 124 characters
- sessionToken: search for `SessionToken">ey`, better string: `eyJhbGciOiJIUzI1NiJ9` (which usually is the first part of the session token)
