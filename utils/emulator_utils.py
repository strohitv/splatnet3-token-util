import io
import os
import shutil
import subprocess
import sys
import time
from subprocess import Popen
from time import sleep

from data.app_config import AppConfig

import logging

logger = logging.getLogger(__name__)


def boot_emulator(app_config: AppConfig):
	logger.info('Booting emulator...')
	emulator_proc = Popen(
		f'{app_config.emulator_config.emulator_path} {app_config.emulator_config.get_emulator_boot_args()}',
		shell=True,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE)

	for line in io.TextIOWrapper(emulator_proc.stdout, encoding="utf-8"):
		if not line:
			break

		if app_config.debug:
			logger.info(line.strip())

		line = line.strip()
		# todo compatibility with other emus
		if line.startswith('INFO') and 'Boot completed in' in line:
			break

	# don't wait here cause the required time depends on HW. Should be part of boot script
	# time.sleep(20.0)

	logger.info('Emulator booted successfully!')
	logger.info('')

	return emulator_proc


def get_emulator_name(app_config: AppConfig):
	emulator_devices_proc = Popen(f'{app_config.emulator_config.adb_path} devices',
								  shell=True,
								  stdout=subprocess.PIPE,
								  stderr=subprocess.PIPE)
	emulator_name = 'emulator-5554'
	for line in io.TextIOWrapper(emulator_devices_proc.stdout, encoding="utf-8"):
		if not line:
			break

		if app_config.debug:
			logger.info(line.strip())

		line = line.strip()

		# todo compatibility with other emus
		if line.startswith('emulator'):
			emulator_name = line.split('\t')[0]
			break

	return emulator_name


def run_adb(app_config: AppConfig, command: str):
	logger.info(f'Running adb command "{command}"...\n')
	# get emulator name
	emulator_name = get_emulator_name(app_config)

	# run command
	subprocess.run(f'{app_config.emulator_config.adb_path} -s {emulator_name} {command}',
				   shell=True,
				   stderr=sys.stderr,
				   stdout=sys.stderr)
	logger.info(f'Command execution finished')
	logger.info('')


def create_snapshot(app_config: AppConfig):
	logger.info(f'')
	logger.info(f'')
	logger.info('#################')
	logger.info('SNAPSHOT CREATION')
	logger.info('#################')
	logger.info(f'')
	logger.info(f'Creating snapshot of emulator state...')

	snapshot_path = os.path.expanduser(os.path.join(app_config.emulator_config.get_snapshot_dir(), app_config.emulator_config.snapshot_name, 'ram.bin'))

	while not os.path.exists(snapshot_path):
		# get emulator name
		emulator_name = get_emulator_name(app_config)

		# do snapshot
		subprocess.run(f'{app_config.emulator_config.adb_path} -s {emulator_name} emu avd snapshot save {app_config.emulator_config.snapshot_name}',
					   shell=True,
					   stdout=sys.stderr,
					   stderr=sys.stderr)

		if not os.path.exists(snapshot_path):
			sleep(1)

	logger.info(f'Snapshot created!')
	logger.info('')


def delete_snapshot(app_config: AppConfig):
	full_path = os.path.join(app_config.emulator_config.get_snapshot_dir(), app_config.emulator_config.snapshot_name)
	if os.path.exists(full_path):
		shutil.rmtree(full_path)


def request_emulator_shutdown(app_config: AppConfig):
	logger.info(f'Requesting emulator shutdown...')
	# get emulator name
	emulator_name = get_emulator_name(app_config)

	# do snapshot
	subprocess.run(f'{app_config.emulator_config.adb_path} -s {emulator_name} emu kill',
				   shell=True,
				   stdout=sys.stderr,
				   stderr=sys.stderr)

	sleep_time = 5
	logger.info(f'Requested emulator shutdown! Giving the emulator a grace period of {sleep_time} seconds to shut down...')
	sleep(sleep_time)
	logger.info(f'{sleep_time} seconds passed.')
	logger.info('')


def wait_for_shutdown(emulator_proc):
	logger.info(f'Waiting for emulator to shut down...')

	result = None
	while result is None:
		result = emulator_proc.poll()
		time.sleep(1.0)

	logger.info(f'Emulator shut down!')
	logger.info('')
