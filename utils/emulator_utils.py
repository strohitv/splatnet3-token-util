import io
import os
import shutil
import subprocess
import sys
import time
from subprocess import Popen
from time import sleep

from data.app_config import AppConfig


def boot_emulator(app_config: AppConfig):
	print('Booting emulator...')
	emulator_proc = Popen(
		f'{app_config.emulator_config.emulator_path} {app_config.emulator_config.get_emulator_boot_args()}',
		shell=True,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE)

	for line in io.TextIOWrapper(emulator_proc.stdout, encoding="utf-8"):
		if app_config.debug:
			print(line.strip())

		if not line:
			break

		line = line.strip()
		# todo compatibility with other emus
		if line.startswith('INFO') and 'Boot completed in' in line:
			break

	# don't wait here cause the required time depends on HW. Should be part of boot script
	# time.sleep(20.0)

	print('Emulator booted successfully!')
	print()

	return emulator_proc


def get_emulator_name(app_config: AppConfig):
	emulator_devices_proc = Popen(f'{app_config.emulator_config.adb_path} devices',
								  shell=True,
								  stdout=subprocess.PIPE,
								  stderr=subprocess.PIPE)
	emulator_name = 'emulator-5554'
	for line in io.TextIOWrapper(emulator_devices_proc.stdout, encoding="utf-8"):
		if app_config.debug:
			print(line.strip())

		if not line:
			break

		line = line.strip()

		# todo compatibility with other emus
		if line.startswith('emulator'):
			emulator_name = line.split('\t')[0]
			break

	return emulator_name


def run_adb(app_config: AppConfig, command: str):
	print(f'Running adb command "{command}"...\n')
	# get emulator name
	emulator_name = get_emulator_name(app_config)

	# run command
	subprocess.run(f'{app_config.emulator_config.adb_path} -s {emulator_name} {command}',
				   shell=True,
				   stderr=sys.stderr,
				   stdout=sys.stdout)
	print(f'Command execution finished')
	print()


def create_snapshot(app_config: AppConfig):
	print(f'Creating snapshot...')
	# get emulator name
	emulator_name = get_emulator_name(app_config)

	# do snapshot
	subprocess.run(f'{app_config.emulator_config.adb_path} -s {emulator_name} emu avd snapshot save {app_config.emulator_config.snapshot_name}',
				   shell=True,
				   stdout=subprocess.PIPE,
				   stderr=subprocess.PIPE)
	print(f'Snapshot created!')
	print()


def delete_snapshot(app_config: AppConfig):
	full_path = os.path.join(app_config.emulator_config.get_snapshot_dir(), app_config.emulator_config.snapshot_name)
	if os.path.exists(full_path):
		shutil.rmtree(full_path)


def request_emulator_shutdown(app_config: AppConfig):
	print(f'Requesting emulator shutdown...')
	# get emulator name
	emulator_name = get_emulator_name(app_config)

	# do snapshot
	subprocess.run(f'{app_config.emulator_config.adb_path} -s {emulator_name} emu kill',
				   shell=True,
				   stdout=subprocess.PIPE,
				   stderr=subprocess.PIPE)

	sleep_time = 5
	print(f'Requested emulator shutdown! Giving the emulator a grace period of {sleep_time} seconds to shut down...')
	sleep(sleep_time)
	print(f'{sleep_time} seconds passed.')
	print()


def wait_for_shutdown(emulator_proc):
	print(f'Waiting for emulator to shut down...')

	result = None
	while result is None:
		result = emulator_proc.poll()
		time.sleep(1.0)

	print(f'Emulator shut down!')
	print()
