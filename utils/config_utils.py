import io
import json
import os
import platform
import subprocess
from pathlib import Path
from subprocess import Popen

from data.app_config import AppConfig
from data.s3s_config import S3sConfig


def __search_path(find_app_command, app_name):
	find_proc = Popen(f'{find_app_command} {app_name}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	for line in io.TextIOWrapper(find_proc.stdout, encoding="utf-8"):
		if not line:
			break

		return line.strip()

	return ''


def load_config(args):
	regenerated = False

	if args.reinitialize_configs or not os.path.exists(args.config):
		print('Generation of configs was manually triggered.' if args.reinitialize_configs else f'Config file "{args.config}" does not exist.')
		print(f'Attempting to generate config file at "{args.config}"')
		print()

		find_app_command = 'which'

		home = Path.home()
		snapshot_dir = os.path.join(home, '.android', 'avd', 'REPLACEMENT_STRING.avd', 'snapshots').replace('REPLACEMENT_STRING', '{AVD_NAME}')

		os_name = platform.system()
		if os_name == 'Windows':
			print('Found Windows')
			find_app_command = 'where.exe'
			local_app_data_dir = os.getenv('LOCALAPPDATA')
			emulator_path = os.path.join(local_app_data_dir, 'Android\\Sdk\\emulator\\emulator.exe')
			adb_path = os.path.join(local_app_data_dir, 'Android\\Sdk\\platform-tools\\adb.exe')
		elif os_name == 'Darwin':
			print('Found macOS')
			emulator_path = os.path.join(home, 'Library/Android/sdk/emulator/emulator')
			adb_path = os.path.join(home, 'Library/Android/sdk/platform-tools/adb')
		else:
			print('Found Linux or an unknown operating system')
			emulator_path = os.path.join(home, 'Android/Sdk/emulator/emulator')
			adb_path = os.path.join(home, 'Android/Sdk/platform-tools/adb')

		if not os.path.exists(emulator_path):
			print(f'Standard emulator path "{emulator_path}" does not exist, searching $PATH')
			emulator_path_new = __search_path(find_app_command, f'emulator{'.exe' if os_name == 'Windows' else ''}')

			if os.path.exists(emulator_path_new):
				emulator_path = emulator_path_new
				print(f'Found emulator path "{emulator_path}" in $PATH')
			else:
				print(f'Could not find emulator path')

		if not os.path.exists(adb_path):
			print(f'Standard adb path "{adb_path}" does not exist, searching $PATH')
			adb_path_new = __search_path(find_app_command, f'adb{'.exe' if os_name == 'Windows' else ''}')

			if os.path.exists(adb_path_new):
				adb_path = adb_path_new
				print(f'Found adb path "{adb_path}" in $PATH')
			else:
				print(f'Could not find adb path')

		if not os.path.exists(emulator_path) or not os.path.exists(adb_path):
			print(f'emulator path "{emulator_path}" or adb path "{adb_path}" does not exist, searching $ANDROID_HOME')
			android_home = os.getenv('ANDROID_HOME')

			if android_home:
				emulator_path_new = os.path.join(android_home, 'emulator', f'emulator{'.exe' if os_name == 'Windows' else ''}')
				adb_path_new = os.path.join(android_home, 'platform-tools', f'adb{'.exe' if os_name == 'Windows' else ''}')

				if os.path.exists(emulator_path_new) and os.path.exists(adb_path_new):
					emulator_path = emulator_path_new
					adb_path = adb_path_new
					print(f'Found emulator path "{emulator_path}" and adb path "{adb_path}" in $ANDROID_HOME')
				else:
					print(f'Could not find emulator path or adb path even though $ANDROID_HOME was set, giving up.')
					print()
					print('ERROR: please edit config.json and set the locations to the emulator and adb paths manually.')
			else:
				print(f'Could not find emulator path or adb path because $ANDROID_HOME is not set, giving up.')
				print()
				print('ERROR: please edit config.json and set the locations to the emulator and adb paths manually.')

		default_config = AppConfig()

		default_config.emulator_config.emulator_path = emulator_path
		default_config.emulator_config.adb_path = adb_path
		default_config.emulator_config.snapshot_dir = snapshot_dir

		default_config.run_config.boot_script_path = os.path.join('.', 'config', 'boot.txt')
		default_config.run_config.cleanup_script_path = os.path.join('.', 'config', 'cleanup.txt')
		default_config.run_config.template_path = os.path.join('.', 'config', 'template.txt')
		default_config.run_config.target_path = os.path.join('.', 'config.txt')
		default_config.run_config.stats_csv_path = os.path.join('.', 'stats.csv')

		os.makedirs(os.path.dirname(args.config), exist_ok=True)

		with open(args.config, 'w') as f:
			f.write(default_config.to_json())

		print()
		print(f'Generated config file at "{args.config}", please edit it to your needs and run the application again.')
		print()
		regenerated = True

	# read config
	with open(args.config, 'r') as f:
		app_config = AppConfig(**json.loads(f.read())) # AppConfig.from_json(json.loads(f.read()))

	return regenerated, app_config


def create_script_file(all_available_steps, script_path, script_summary, steps_name):
	default_script = \
		('############################\n'
		 '# STEPS FILE DOCUMENTATION #\n'
		 '############################\n'
		 '# \n'
		 '# \n') + script_summary + ('# \n'
									 '# \n'
									 '# Available commands:\n'
									 '# - Use # at the start of a line to create a comment (line will be ignored)\n'
									 '# - WARNING: # after a command will lead to an error, # must be at the start of a line\n')

	for key in all_available_steps:
		default_script += f'# \n# - {key}: {all_available_steps[key].description()}\n'

	default_script += f'\necho Please insert your {steps_name} steps here.'
	os.makedirs(os.path.dirname(script_path), exist_ok=True)

	with open(script_path, 'w') as f:
		f.write(default_script)


def ensure_scripts_exist(args, app_config: AppConfig, all_available_steps):
	regenerated = False

	if args.reinitialize_configs or not os.path.exists(app_config.run_config.boot_script_path):
		print(f'Attempting to generate boot file at "{app_config.run_config.boot_script_path}"')

		boot_summary = ('# This file contains the steps required to open the NSA SplatNet 3 app.\n'
						'# \n'
						'# It starts executing AFTER the emulator has been started.\n'
						'# Once this file has been fully executed, the script will create a snapshot of the emulator.\n'
						'# \n'
						'# Your goal for this script is to bring the freshly booted emulator to a state where the NSA app is opened and has entered SplatNet 3.\n')

		create_script_file(all_available_steps, app_config.run_config.boot_script_path, boot_summary, 'boot')

		print(f'Successfully generated boot file at "{app_config.run_config.boot_script_path}", please fill it with correct steps and run the application again')
		regenerated = True

	if args.reinitialize_configs or not os.path.exists(app_config.run_config.cleanup_script_path):
		print(f'Attempting to generate boot file at "{app_config.run_config.cleanup_script_path}"')

		cleanup_summary = ('# This file contains the steps required to close the NSA SplatNet 3 app and shut down the emulator.\n'
						   '# \n'
						   '# It starts executing AFTER the snapshot of the emulator has been created.\n'
						   '# Once this file has been fully executed, the script will analyse the snapshot RAM dump to find the tokens.\n'
						   '# \n'
						   '# Your goal for this script is to close the SplatNet 3 app and shut down the emulator.\n')

		create_script_file(all_available_steps, app_config.run_config.cleanup_script_path, cleanup_summary, 'cleanup')

		print(f'Successfully generated cleanup file at "{app_config.run_config.cleanup_script_path}", please fill it with correct steps and run the application again')
		regenerated = True

	return regenerated


def ensure_template_exists(args, app_config: AppConfig):
	regenerated = False

	if args.reinitialize_configs or not os.path.exists(app_config.run_config.template_path):
		print(f'Attempting to generate template file at "{app_config.run_config.template_path}"')

		s3s_config = S3sConfig()
		os.makedirs(os.path.dirname(app_config.run_config.template_path), exist_ok=True)

		with open(app_config.run_config.template_path, 'w') as f:
			f.write(s3s_config.to_json())

		print(f'Successfully generated template file at "{app_config.run_config.template_path}", please fill it with correct values and run the application again')
		regenerated = True

	return regenerated
