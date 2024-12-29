#!/bin/bash

# This script demonstrates how to run the script and upload the config.txt file to another server using ssh with pubkey auth afterwards

cd /home/stroh/code/python/splatnet3-token-util

# 1. activate conda environment (installation of libs has to be prepared beforehand)
source /home/stroh/miniconda3/etc/profile.d/conda.sh # ~/miniconda3/etc/profile.d/conda.sh # Or path to where your conda is
conda init
conda activate splatnet3-token-util

# 2. run splatnet3-token-util and check result
if python3 main.py; then
	# on success: upload to server
	echo "Main application executed successfully!"
	scp -i /home/stroh/.ssh/server/id_rsa /home/stroh/code/python/splatnet3-token-util/config.txt USER@SOME-SERVER.EXAMPLE:/home/user/source/python/s3s_main/config.txt
	echo "Transferred s3s config successfully!"
else
	# splatnet3-token-util stopped after X failed attempts
	echo "ERROR DURING TOKEN EXTRACTION!!!"
fi
