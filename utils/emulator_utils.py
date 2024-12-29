import io
import os
import shutil
import subprocess
import time
from subprocess import Popen
from time import sleep


def boot_emulator(app_config):
	print('Booting emulator...')
	emulator_proc = Popen(f'{app_config.emulator_path} -avd {app_config.avd_name}{' -no-window' if not app_config.show_window else ''}',
						  shell=True,
						  stdout=subprocess.PIPE,
						  stderr=subprocess.PIPE)

	for line in io.TextIOWrapper(emulator_proc.stdout, encoding="utf-8"):
		if app_config.debug:
			print(line.strip())

		if not line:
			break

		line = line.strip()
		if line.startswith('INFO') and 'Boot completed in' in line:
			break
	# don't wait here cause the required time depends on HW. Should be part of boot script
	# time.sleep(20.0)
	print('Emulator booted successfully!')
	print()

	return emulator_proc


def get_emulator_name(app_config):
	emulator_devices_proc = Popen(f'{app_config.adb_path} devices',
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
		if line.startswith('emulator'):
			emulator_name = line.split('\t')[0]
			break

	return emulator_name


def create_snapshot(app_config):
	print(f'Creating snapshot...')
	# get emulator name
	emulator_name = get_emulator_name(app_config)

	# do snapshot
	subprocess.run(f'{app_config.adb_path} -s {emulator_name} emu avd snapshot save {app_config.snapshot_name}',
				   shell=True,
				   stdout=subprocess.PIPE,
				   stderr=subprocess.PIPE)
	print(f'Snapshot created!')
	print()


def delete_snapshot(app_config):
	shutil.rmtree(os.path.expanduser(os.path.join(app_config.snapshot_dir, app_config.snapshot_name)))


def request_emulator_shutdown(app_config):
	print(f'Requesting emulator shutdown...')
	# get emulator name
	emulator_name = get_emulator_name(app_config)

	# do snapshot
	subprocess.run(f'{app_config.adb_path} -s {emulator_name} emu kill',
				   shell=True,
				   stdout=subprocess.PIPE,
				   stderr=subprocess.PIPE)

	print('Requested emulator shutdown! Giving the emulator a grace period of 10 seconds to shut down...')
	sleep(5)
	print('10 seconds passed.')
	print()


def wait_for_shutdown(emulator_proc):
	print(f'Waiting for emulator to shut down...')

	result = None
	while result is None:
		result = emulator_proc.poll()
		time.sleep(1.0)

	print(f'Emulator shut down!')
	print()
