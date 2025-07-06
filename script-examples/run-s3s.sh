#!/usr/bin/env bash

# This script demonstrates how to execute the refresh and run s3s afterwards with valid tokens

# VARIABLES - change them according to your system
MAIN_DIRECTORY="$HOME/code/python/splatnet3-token-util" # insert path to project directory

S3S_DIRECTORY="$HOME/code/python/s3s" # insert path to s3s directory
S3S_REFRESH_RC=42 # you don't really need to change this value, just don't change it to 0 or 1 or it won't work
S3S_ARGS="$@" # insert your command arguments for the s3s command

UPDATE_S3S=0 # 1 to run git pull and python -m pip install, 0 to disable automatic updates
UPDATE_STU=0 # 1 to run git pull and python -m pip install, 0 to disable automatic updates

USE_CONDA=0 # 1 if you want to use (mini)conda, 0 otherwise
CONDA_SOURCE="$HOME/miniconda3/etc/profile.d/conda.sh" # insert path to conda main script
CONDA_ENVIRONMENT="splatnet3-token-util" # insert name of your conda environment here

# actual script

if [[ -z "${S3S_ARGS// }" ]];
then
	echo "using '--help' as command line args since you did not provide any."
	S3S_ARGS="--help"
fi

# 0. activate conda environment (installation of libs has to be prepared beforehand)
if [ $USE_CONDA -gt 0 ];
then
	echo "using conda environment '$CONDA_ENVIRONMENT'"
	source "$CONDA_SOURCE"
	conda init
	conda activate "$CONDA_ENVIRONMENT"
fi

CURRENT_TIME=$(date +%s)
NEXT_RUN_TIME=$((CURRENT_TIME + 0 * 60))

while :
do
	# 1. prepare s3s run
	echo "###########"
	echo "running s3s"
	echo "###########"
	echo ""

	echo "Running s3s with command 'python s3s.py --norefresh $S3S_REFRESH_RC $S3S_ARGS'"
	echo ""

	cd $S3S_DIRECTORY

	if [ $UPDATE_S3S -ne 0 ];
	then
		git pull
		python -m pip install -r requirements.txt
		UPDATE_S3S=0
		echo ""
	fi

	# 2. run s3s and store return code
	(python s3s.py --norefresh $S3S_REFRESH_RC $S3S_ARGS)
	S3S_RC=$?

	echo ""
	echo "s3s finished. Return code: $S3S_RC"

	if [[ $S3S_RC -eq 0 ]];
	then
		echo "s3s finished successful -> exiting script."
		exit 0
	fi

	echo ""

	# stop script if s3s failed
	if [ "$S3S_RC" -ne "$S3S_REFRESH_RC" ];
	then
		# ERROR: s3s failed
		echo "ERROR DURING s3s!!!"
		echo "exiting script."
		exit 2
	fi

	# 3. s3s finished - wait up to 115 minutes before refreshing tokens again if monitoring mode
	CURRENT_TIME=$(date +%s)
	if [ $NEXT_RUN_TIME -gt $CURRENT_TIME ];
	then
		SLEEP_TIME=$((NEXT_RUN_TIME - CURRENT_TIME))
		WAKEUP_TIME=$(date -d "$SLEEP_TIME secs" '+%H:%M')
		echo "Less than 115 minutes have passed since the last execution. Sleeping for $((SLEEP_TIME / 60)) minutes (until $WAKEUP_TIME)"
		sleep $SLEEP_TIME
	fi

	# 4. token refresh required - prepare splatnet3-token-util run
	cd "$MAIN_DIRECTORY"

	echo "###########################"
	echo "running splanet3-token-util"
	echo "###########################"
	echo ""

	if [ $UPDATE_STU -gt 0 ];
	then
		git pull
		python -m pip install -r requirements.txt
		UPDATE_STU=0
	fi

	# 5. run splatnet3-token-util and check result
	if python3 main.py;
	then
		CURRENT_TIME=$(date +%s)
		NEXT_RUN_TIME=$((CURRENT_TIME + 115 * 60))

		# copy config to s3s directory
		cp -f "$MAIN_DIRECTORY/config.txt" "$S3S_DIRECTORY/config.txt"
		echo "config.txt written into s3s folder"
		echo ""
	else
		# ERROR: splatnet3-token-util stopped after X failed attempts
		echo "ERROR DURING TOKEN EXTRACTION!!!"

		echo "exiting the script"
		exit 1
	fi
done
