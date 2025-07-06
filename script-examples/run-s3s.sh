#!/usr/bin/env bash

# This script demonstrates how to execute the refresh and run s3s afterwards with valid tokens

# VARIABLES - change them according to your system
MAIN_DIRECTORY="$HOME/code/python/splatnet3-token-util" # insert path to project directory

S3S_DIRECTORY="$HOME/code/python/s3s" # insert path to s3s directory
S3S_ARGS="$@" # insert your command arguments for the s3s command

if [[ -z "${S3S_ARGS// }" ]];
then
	echo "using '--help' as command line args since you did not provide any."
	S3S_ARGS="--help"
fi

USE_CONDA=1 # 1 if you want to use (mini)conda, 0 otherwise
CONDA_SOURCE="$HOME/miniconda3/etc/profile.d/conda.sh" # insert path to conda main script
CONDA_ENVIRONMENT="splatnet3-token-util" # insert name of your conda environment here

# actual script
while :
do
	cd "$MAIN_DIRECTORY"

	echo "###########################"
	echo "running splanet3-token-util"
	echo "###########################"
	echo ""

	# 0. activate conda environment (installation of libs has to be prepared beforehand)
	if [ $USE_CONDA -gt 0 ];
	then
		echo "using conda environment '$CONDA_ENVIRONMENT'"
		source "$CONDA_SOURCE"
		conda init
		conda activate "$CONDA_ENVIRONMENT"
	fi

	git pull
	pip install -r ./requirements.txt

	# 1. run splatnet3-token-util and check result
	if [[ $S3S_ARGS == *"-h"* ]] || python3 main.py;
	then
		CURRENT_TIME=$(date +%s)
		NEXT_RUN_TIME=$((CURRENT_TIME + 115 * 60))

		# 2. on success: run s3s
		echo "Main application executed successfully!"
		echo ""

		echo "###########"
		echo "running s3s"
		echo "###########"
		echo ""

		cp -f "$MAIN_DIRECTORY/config.txt" "$S3S_DIRECTORY/config.txt"
		echo "config.txt written into s3s folder"

		echo "Running s3s with command 'python s3s.py --norefresh $S3S_ARGS'"
		echo ""

		cd $S3S_DIRECTORY
		git pull
		pip install -r requirements.txt
		echo ""

		(python s3s.py --norefresh $S3S_ARGS)
		S3S_RC=$?

		echo ""
		echo "s3s finished. Return code: $S3S_RC"
		echo ""

		if [[ $S3S_ARGS != *"-M"* ]] || [[ $S3S_ARGS == *"-h"* ]];
		then
			echo "s3s params did not request monitoring mode (-M) or requested help (-h / --help); only one run required -> exiting script."
			exit 0
		fi

		# stop script if s3s fails
		if [ $S3S_RC -gt 0 ];
		then
			# ERROR: s3s failed
			echo "ERROR DURING s3s!!!"

			echo "exiting the script"
			exit 2
		fi

		# 3. s3s finished - wait up to 115 minutes before refreshing tokens again
		CURRENT_TIME=$(date +%s)
		if [ $NEXT_RUN_TIME -gt $CURRENT_TIME ];
		then
			SLEEP_TIME=$((NEXT_RUN_TIME - CURRENT_TIME))
			WAKEUP_TIME=$(date -d "$SLEEP_TIME secs" '+%H:%M')
			echo "Less than 115 minutes have passed since the last execution. Sleeping for $((SLEEP_TIME / 60)) minutes (until $WAKEUP_TIME)"
			sleep $SLEEP_TIME
		fi
	else
		# ERROR: splatnet3-token-util stopped after X failed attempts
		echo "ERROR DURING TOKEN EXTRACTION!!!"

		echo "exiting the script"
		exit 1
	fi
done
