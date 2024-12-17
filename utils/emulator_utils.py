import io
import os
import shutil
import subprocess
import time
from subprocess import Popen


def boot_emulator(config):
	print('Booting emulator...')
	emulator_proc = Popen(f'{config.emulator_path} -avd {config.avd_name}{' -no-window' if not config.show_window else ''}',
						  shell=True,
						  stdout=subprocess.PIPE,
						  stderr=subprocess.PIPE)

	for line in io.TextIOWrapper(emulator_proc.stdout, encoding="utf-8"):
		if config.debug:
			print(line.strip())

		if not line:
			break

		line = line.strip()
		if line.startswith('INFO') and 'Boot completed in' in line:
			break

	time.sleep(20.0)
	print('Emulator booted successfully!')
	print()

	return emulator_proc


def create_snapshot(config):
	print(f'Creating snapshot...')
	# get emulator name
	emulator_devices_proc = Popen(f'{config.adb_path} devices',
								  shell=True,
								  stdout=subprocess.PIPE,
								  stderr=subprocess.PIPE)

	emulator_name = 'emulator-5554'
	for line in io.TextIOWrapper(emulator_devices_proc.stdout, encoding="utf-8"):
		if config.debug:
			print(line.strip())

		if not line:
			break

		line = line.strip()
		if line.startswith('emulator'):
			emulator_name = line.split('\t')[0]
			break

	# do snapshot
	subprocess.run(f'{config.adb_path} -s {emulator_name} emu avd snapshot save {config.snapshot_name}',
				   shell=True,
				   stdout=subprocess.PIPE,
				   stderr=subprocess.PIPE)
	print(f'Snapshot created!')
	print()

def delete_snapshot(config):
	shutil.rmtree(os.path.expanduser(os.path.join(config.snapshot_dir, config.snapshot_name)))

def wait_for_shutdown(emulator_proc):
	print(f'Waiting for emulator to shut down...')

	result = None
	while result is None:
		result = emulator_proc.poll()
		time.sleep(1.0)

	print(f'Emulator shut down!')
	print()
