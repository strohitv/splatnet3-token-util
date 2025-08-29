(Note: this file gets generated from `./utils/step_doc_creator.py`, do not manually change it)

# Steps Documentation
This document lists and describes all possible steps you can use in the `boot.txt` and `cleanup.txt` files. These files use some kind of "custom bash script format" which is very simple and contains all the steps required to control the emulator one step after another. There are no variables, no loops, no ifs and other structures bash usually provides, only a few allowed commands.

Here is the documentation of all commands ("steps") you can use to control the emulator.

## block_while
This command blocks the execution of the script until a specific region of the emulator screen looks similar to the same region in a given template file. Its biggest use case is to optimize load times, for example waiting for an app to become visible on the screen after having tapped the app icon.

### Usage:
```
usage: block_while -mode {found,not-found} -template TEMPLATE [-actual ACTUAL] -x1 X1 -y1 Y1 -x2 X2 -y2 Y2
                   [-d DURATION] [-ca CONTINUE_AFTER] [-co CUTOFF]

Blocks the execution of the script until a specific region on the screen (between points (X1, Y1) to (X2, Y2))
looks similar to the same region on a given template

options:
  -mode, --mode {found,not-found}       Decides whether this step should block as long as the region can be
                                        found or not, `found` = block as long as found, `not-found` = block
                                        until found
  -template, --template TEMPLATE        The file path of the template screenshot which will be used for the
                                        comparison
  -actual, --actual ACTUAL              The file path where the actual screenshot of the emulator should be
                                        stored. Default: "./screenshots/screenshot.png"
  -x1, --x1 X1                          The X coordinate of the top left corner of the region to compare
  -y1, --y1 Y1                          The Y coordinate of the top left corner of the region to compare
  -x2, --x2 X2                          The X coordinate of the bottom right corner of the region to compare
  -y2, --y2 Y2                          The Y coordinate of the bottom right corner of the region to compare
  -d, --duration DURATION               The frequency of how often this command should check whether the
                                        regions match. Default: 1000 ms
  -ca, --continue-after CONTINUE_AFTER  Optional arg which lets the script continue if the block cannot be
                                        resolved after X seconds. Default: 45
  -co, --cutoff CUTOFF                  The cutoff for the comparison. This value decides how similar the
                                        regions must be to be considered equal. Lower values mean stricter
                                        comparison, higher values will match less similar screenshots.
                                        Default: 5

```

## close_nsa
This command forces the Nintendo Switch App to be closed..

### Usage:
```
usage: close_nsa

Closes the Nintendo Switch App

```

## create_screenshot
This command creates a screenshot of the Emulator and saves it to the given location.

### Usage:
```
usage: create_screenshot [-p PATH]

Creates a screenshot of the Emulator

options:
  -p, -path, --path PATH  The file path where the screenshot of the emulator should be stored. Default:
                          "./screenshots/screenshot.png"

```

## echo
This command prints a given text to the console.

### Usage:
```
usage: echo TEXT

Prints a given text to the console

positional arguments:
  TEXT  The text to be printed to console

```

## execute_while
This command repeatedly executes a given command as long as a specific region of the emulator screen looks similar to the same region in a given template file. Its biggest use case is to ensure consistent behaviour of the emulator by ensuring a command really came through. Example: tapping an app icon until it cannot be found anymore (=> the app is now visible).

### Usage:
```
usage: execute_while -mode {found,not-found} -template TEMPLATE [-actual ACTUAL] -x1 X1 -y1 Y1 -x2 X2 -y2 Y2
                     -cmd COMMAND [-d DURATION] [-ca CONTINUE_AFTER] [-co CUTOFF]

Repeatedly executes a given command as long as a specific region on the screen (between points (X1, Y1) to
(X2, Y2)) looks similar to the same region on a given template

options:
  -mode, --mode {found,not-found}       Decides whether this step should execute the command as long as the
                                        region can be found or not, `found` = execute as long as found, `not-
                                        found` = execute until found
  -template, --template TEMPLATE        The file path of the template screenshot which will be used for the
                                        comparison
  -actual, --actual ACTUAL              The file path where the actual screenshot of the emulator should be
                                        stored. Default: "./screenshots/screenshot.png"
  -x1, --x1 X1                          The X coordinate of the top left corner of the region to compare
  -y1, --y1 Y1                          The Y coordinate of the top left corner of the region to compare
  -x2, --x2 X2                          The X coordinate of the bottom right corner of the region to compare
  -y2, --y2 Y2                          The Y coordinate of the bottom right corner of the region to compare
  -cmd, --command COMMAND               The command which should be executed. Several commands can be provided
                                        by splitting them with a semicolon `;`
  -d, --duration DURATION               The frequency of how often this command should check whether the
                                        regions match. Default: 500 ms
  -ca, --continue-after CONTINUE_AFTER  Optional arg which lets the script continue if the block cannot be
                                        resolved after X seconds. Default: 45
  -co, --cutoff CUTOFF                  The cutoff for the comparison. This value decides how similar the
                                        regions must be to be considered equal. Lower values mean stricter
                                        comparison, higher values will match less similar screenshots.
                                        Default: 5

```

## open_splatnet3
This command causes the Nintendo Switch App to open and loads SplatNet3 afterwards.

### Usage:
```
usage: open_splatnet3 [--max-attempts MAX_ATTEMPTS] [--max-wait-secs MAX_WAIT_SECS] [-d DURATION]

Opens the SplatNet3 app inside the Nintendo Switch App immediately.

options:
  --max-attempts MAX_ATTEMPTS    How often the step should attempt to open SplatNet3 before giving up.
                                 Default: 3
  --max-wait-secs MAX_WAIT_SECS  How long the step should wait for SplatNet3 to load before it considers the
                                 attempt failed. Default: 15 seconds
  -d, --duration DURATION        The frequency of how often this command should check whether SplatNet3 is
                                 open. Default: 500 ms

```

## press_power_button_long
This command presses the power button for a long time, which usually opens the power menu.

### Usage:
```
usage: press_power_button_long

Presses the power button for a long time

```

## search_and_tap_center
This command scans a given region on the emulator screen and looks if that region contains a given smaller image taken from the template screenshot. If it finds it, it will tap the center of it until something happens. If it cannot find it, it will execute the provided command and restart.

Example: the prime example where this step is being used is searching for the SplatNet3 app icon inside the Nintendo Switch App. It will search for it through all app icons and if it finds it, will open SplatNet3. Otherwise, SplatNet 3 is probably further back in the list, so it will scroll a bit and search again until it finds it.

### Usage:
```
usage: search_and_tap_center -template TEMPLATE [-actual ACTUAL] -region_x1 REGION_X1 -region_y1 REGION_Y1
                             -region_x2 REGION_X2 -region_y2 REGION_Y2 -comparison_x1 COMPARISON_X1
                             -comparison_y1 COMPARISON_Y1 -comparison_x2 COMPARISON_X2
                             -comparison_y2 COMPARISON_Y2 -cmd COMMAND [-d DURATION] [-co CUTOFF] [-step STEP]
                             [-h_step H_STEP] [-v_step V_STEP] [-ei]

Searches a given region on the emulator screen to contain a (smaller) region from the template screenshot
provided. If it finds it, it will tap the center of it. Otherwise it will execute the provided command and
search again

options:
  -template, --template TEMPLATE                 The file path of the template screenshot which will be used
                                                 for the comparison
  -actual, --actual ACTUAL                       The file path where the actual screenshot of the emulator
                                                 should be stored. Default: "./screenshots/screenshot.png"
  -region_x1, --region_x1 REGION_X1              The X coordinate of the top left corner of the region to
                                                 search through
  -region_y1, --region_y1 REGION_Y1              The Y coordinate of the top left corner of the region to
                                                 search through
  -region_x2, --region_x2 REGION_X2              The X coordinate of the bottom right corner of the region to
                                                 search through
  -region_y2, --region_y2 REGION_Y2              The Y coordinate of the bottom right corner of the region to
                                                 search through
  -comparison_x1, --comparison_x1 COMPARISON_X1  The X coordinate of the top left corner of the region from
                                                 the template screenshot which should be searched for
  -comparison_y1, --comparison_y1 COMPARISON_Y1  The Y coordinate of the top left corner of the region from
                                                 the template screenshot which should be searched for
  -comparison_x2, --comparison_x2 COMPARISON_X2  The X coordinate of the bottom right corner of the region
                                                 from the template screenshot which should be searched for
  -comparison_y2, --comparison_y2 COMPARISON_Y2  The Y coordinate of the bottom right corner of the region
                                                 from the template screenshot which should be searched for
  -cmd, --command COMMAND                        The command which should be executed if the requested search
                                                 can not be found. Several commands can be provided by
                                                 splitting them with a semicolon `;`
  -d, --duration DURATION                        The frequency of how often this command should check whether
                                                 the regions match. Default: 500 ms
  -co, --cutoff CUTOFF                           The cutoff for the comparison. This value decides how similar
                                                 the regions must be to be considered equal. Lower values mean
                                                 stricter comparison, higher values will match less similar
                                                 screenshots. Default: 5
  -step, --step STEP                             Decides how many pixels the region should be moved. Higher
                                                 values are faster but a smaller part of the region is being
                                                 screened and the target region could be missed for that
                                                 reason. Default: 1 => search every possible position in the
                                                 provided screen region
  -h_step, --h_step H_STEP                       Decides how many pixels the region should be moved ONLY
                                                 HORIZONTALLY. This value overrides the -step parameter for
                                                 horizontal steps. Higher values are faster but a smaller part
                                                 of the region is being screened and the target region could
                                                 be missed for that reason. Default: 1 => search every
                                                 possible position in the provided screen region
  -v_step, --v_step V_STEP                       Decides how many pixels the region should be moved ONLY
                                                 VERTICALLY. This value overrides the -step parameter for
                                                 vertical steps. Higher values are faster but a smaller part
                                                 of the region is being screened and the target region could
                                                 be missed for that reason. Default: 1 => search every
                                                 possible position in the provided screen region
  -ei, --execute_immediately                     Usually, this command checks whether the given template
                                                 comparison image can be found already BEFORE executing the
                                                 -cmd arg. If the -ei arg is provided, the order will switch
                                                 and the -cmd will be executed immediately instead of doing
                                                 one image comparison first

```

## shutdown_emu
This command causes the Emulator to shut down.

### Usage:
```
usage: shutdown_emu

Triggers an emulator shutdown..

```

## swipe
This command will swipe from one position to another over the span of a given duration.

### Usage:
```
usage: swipe -x1 X1 -y1 Y1 -x2 X2 -y2 Y2 [-d DURATION]

Swipes from a given starting point (X1, Y1) to a given target point (X2, Y2) on the screen over the span of a
given duration

options:
  -x1, --x1 X1             The X coordinate of the starting position of the swipe
  -y1, --y1 Y1             The Y coordinate of the starting position of the swipe
  -x2, --x2 X2             The X coordinate of the target position of the swipe
  -y2, --y2 Y2             The Y coordinate of the target position of the swipe
  -d, --duration DURATION  The duration how long the swipe should take. Default: 500 ms

```

## tap
This command will tap a given position on the screen.

### Usage:
```
usage: tap -x X -y Y

Taps a given position (X, Y) on the screen once

options:
  -x, --x X  The X coordinate of the position which should be tapped
  -y, --y Y  The Y coordinate of the position which should be tapped

```

## type
This command will type a given text on the android keyboard.

### Usage:
```
usage: type -t TEXT

Types a given text on the android keyboard

options:
  -t, --text TEXT  The text to type

```

## wait_s
This command will block the execution of the script for the given amount of seconds.

### Usage:
```
usage: wait_s seconds

Waits for the given amount of seconds

positional arguments:
  seconds  The amount of seconds to wait

```

## wait_ms
This command will block the execution of the script for the given amount of milliseconds.

### Usage:
```
usage: wait_ms milliseconds

Waits for the given amount of milliseconds

positional arguments:
  milliseconds  The amount of milliseconds to wait

```