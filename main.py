import argparse
import base64
import io
import json
import os
import shutil
import subprocess
import sys
import time
from subprocess import Popen

from data.config import Config
from data.s3s_config import S3sConfig
from steps import all_steps


def read_in_chunks(file_object, chunk_size=10 * 1024 * 1024):
	while True:
		data = file_object.read(chunk_size)
		if not data:
			break
		yield data


if __name__ == '__main__':
	parser = argparse.ArgumentParser(prog='splatnet3-emu-token-util',
									 description='SplatNet3 Emulator Token Utility application to extract NSO SplatNet3 tokens from a controlled Android Studio emulator process')
	parser.add_argument('-c', '--config', required=False, help='Path to configuration file', default='./config/config.json')
	parser.add_argument('-r', '--reinitialize-configs', required=False,
						help='Generates the config again (and potentially overwrites existing ones)', default=False,
						action='store_true')
	args = parser.parse_args()

	regenerated = False

	if args.reinitialize_configs or not os.path.exists(args.config):
		print(f'Attempting to generate config file at "{args.config}"')
		default_config = Config()
		os.makedirs(os.path.dirname(args.config), exist_ok=True)

		with open(args.config, 'w') as f:
			f.write(default_config.to_json())

		print(
			f'Successfully generated config file at "{args.config}", please fill it with correct values and run the application again')
		regenerated = True

	# read config
	with open(args.config, 'r') as f:
		config = Config.from_json(json.loads(f.read()))

	all_available_steps = all_steps.get_steps(config)

	if args.reinitialize_configs or not os.path.exists(config.boot_script_path):
		print(f'Attempting to generate boot file at "{config.boot_script_path}"')

		default_boot_config_script = \
			('############################\n'
			 '# STEPS FILE DOCUMENTATION #\n'
			 '############################\n'
			 '# \n'
			 '# This file contains the steps required to open the NSO SplatNet 3 app.\n'
			 '# It starts executing AFTER the emulator has been started.\n'
			 '# Once this file has been fully executed, the script will create a snapshot of the emulator.\n'
			 '# Your goal for this script is to bring the freshly booted emulator to a state where the NSO app is opened and has entered SplatNet 3.\n'
			 '# \n'
			 '# Available commands:\n'
			 '# - Use # at the start of a line to create a comment (line will be ignored)\n'
			 '# - WARNING: # after a command will lead to an error, # must be at the start of a line\n')

		for key in all_available_steps:
			default_boot_config_script += f'# \n# - {key}: {all_available_steps[key].description()}\n'

		default_boot_config_script += f'\necho Please insert your boot steps here.'
		os.makedirs(os.path.dirname(config.boot_script_path), exist_ok=True)

		with open(config.boot_script_path, 'w') as f:
			f.write(default_boot_config_script)

		print(
			f'Successfully generated boot file at "{config.boot_script_path}", please fill it with correct steps and run the application again')
		regenerated = True

	if args.reinitialize_configs or not os.path.exists(config.cleanup_script_path):
		print(f'Attempting to generate boot file at "{config.cleanup_script_path}"')

		default_cleanup_config_script = \
			('############################\n'
			 '# STEPS FILE DOCUMENTATION #\n'
			 '############################\n'
			 '# \n'
			 '# This file contains the steps required to close the NSO SplatNet 3 app and shut down the emulator.\n'
			 '# It starts executing AFTER the snapshot of the emulator has been created.\n'
			 '# Once this file has been fully executed, the script will analyse the snapshot RAM dump to find the tokens.\n'
			 '# Your goal for this script is to close the SplatNet 3 app and shut down the emulator.\n'
			 '# \n'
			 '# Available commands:\n'
			 '# - Use # at the start of a line to create a comment (line will be ignored)\n'
			 '# - WARNING: # after a command will lead to an error, # must be at the start of a line\n')

		for key in all_available_steps:
			default_cleanup_config_script += f'# \n# - {key}: {all_available_steps[key].description()}\n'

		default_cleanup_config_script += f'\necho Please insert your cleanup steps here.'
		os.makedirs(os.path.dirname(config.cleanup_script_path), exist_ok=True)

		with open(config.cleanup_script_path, 'w') as f:
			f.write(default_cleanup_config_script)

		print(
			f'Successfully generated cleanup file at "{config.cleanup_script_path}", please fill it with correct steps and run the application again')
		regenerated = True

	if args.reinitialize_configs or not os.path.exists(config.template_path):
		print(f'Attempting to generate template file at "{config.template_path}"')

		s3s_config = S3sConfig()
		os.makedirs(os.path.dirname(config.template_path), exist_ok=True)

		with open(config.template_path, 'w') as f:
			f.write(s3s_config.to_json())

		print(
			f'Successfully generated template file at "{config.template_path}", please fill it with correct values and run the application again')
		regenerated = True

	if regenerated:
		print('Configs were regenerated, application will exit. Bye!')
		sys.exit(0)

	# run the actual script
	gtoken = None
	bullet_token = None
	session_token = None

	attempt = 0
	for attempt in range(config.max_attempts):
		# run emulator
		print(f'### Attempt {attempt + 1} / {config.max_attempts} ###')
		print()
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

		print('Executing boot script...')
		with open(config.boot_script_path, 'r') as boot_script:
			while True:
				line = boot_script.readline()

				if not line:
					break

				line = line.strip()

				if config.debug:
					print(line)

				if line.startswith('#') or line == '':
					continue

				command = line.split(' ')[0]
				if command in all_available_steps:
					step = all_available_steps[command]
					step.execute(line)

		print()
		print(f'Creating snapshot...')
		# get emulator name
		emulator_devies_proc = Popen(f'{config.adb_path} devices',
									 shell=True,
									 stdout=subprocess.PIPE,
									 stderr=subprocess.PIPE)

		emulator_name = 'emulator-5554'
		for line in io.TextIOWrapper(emulator_devies_proc.stdout, encoding="utf-8"):
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

		print(f'Executing cleanup script...')
		with open(config.cleanup_script_path, 'r') as cleanup_script:
			while True:
				line = cleanup_script.readline()
				if not line:
					break

				line = line.strip()
				if line.startswith('#') or line == '':
					continue

				command = line.split(' ')[0]
				if command in all_available_steps:
					step = all_available_steps[command]
					step.execute(line)

		# wait for emulator process to exit
		print()
		print(f'Waiting for emulator to shut down...')

		result = None
		while result is None:
			result = emulator_proc.poll()
			time.sleep(1.0)

		print(f'Emulator shut down!')
		snapshot_path = os.path.expanduser(os.path.join(config.snapshot_dir, config.snapshot_name, 'ram.bin'))

		# analyse snapshot and find values
		print()
		print(f'Searching for tokens...')
		with open(snapshot_path, 'rb') as f:
			for piece in read_in_chunks(f):
				# _gtoken search
				if gtoken is None and b'_gtoken=ey' in piece:
					gtoken = ''
					index = piece.index(b'_gtoken=ey') + len(b'_gtoken=')
					while index < len(piece):
						next_piece = piece[index]
						if chr(next_piece) == '\x00':
							break
						gtoken += chr(next_piece)
						index += 1

					if len(gtoken) < 850:
						# TODO jwt validation
						gtoken = None

				# bullet_token search
				if bullet_token is None and b'"bulletToken":"' in piece:
					bullet_token = ''
					index = piece.index(b'"bulletToken":"') + len(b'"bulletToken":"')
					while index < len(piece):
						next_piece = piece[index]
						if chr(next_piece) == '\x00':
							bullet_token = None
							break
						if chr(next_piece) == '"':
							break
						bullet_token += chr(next_piece)
						index += 1

					if len(bullet_token) > 100:
						try:
							base64.b64decode(bullet_token)
						except Exception as e:
							bullet_token = None
					else:
						bullet_token = None

				# session_token search
				if session_token is None and b'eyJhbGciOiJIUzI1NiJ9' in piece:
					session_token = ''
					index = piece.index(b'eyJhbGciOiJIUzI1NiJ9')
					while index < len(piece):
						next_piece = piece[index]
						if chr(next_piece) == '\x00':
							break
						session_token += chr(next_piece)
						index += 1

					if len(session_token) < 260:
						# TODO jwt validation
						session_token = None

				if config.debug:
					print('next chunk done')

		print('- SUCCESS\tgToken' if gtoken is not None else '- FAIL\t\tgToken')
		print('- SUCCESS\tbulletToken' if bullet_token is not None else '- FAIL\t\tbulletToken')
		print('- SUCCESS\tsessionToken' if session_token is not None else '- FAIL\t\tsessionToken')

		# delete snapshot file
		shutil.rmtree(os.path.expanduser(os.path.join(config.snapshot_dir, config.snapshot_name)))

		if gtoken is None or bullet_token is None or session_token is None:
			print(f'Could not find all three tokens.')
			print()
		else:
			break

	# export tokens to target file
	if gtoken is not None and bullet_token is not None and session_token is not None:
		print()
		print(f'Reading the template file...')
		with open(config.template_path, 'r') as template:
			print(f'Creating target file content from template...')
			final_file = template.read()
			final_file = final_file.replace('{GTOKEN}', gtoken)
			final_file = final_file.replace('{BULLETTOKEN}', bullet_token)
			final_file = final_file.replace('{SESSIONTOKEN}', session_token)

			print(f'Creating the target file...')
			with open(config.target_path, 'w') as target_file:
				print(f'Writing content...')
				target_file.write(final_file)
				print(f'Done after {attempt + 1} attempts. Application will exit now. Bye!')
	else:
		print(f'Could not find all three tokens in {config.max_attempts} attempts, application will stop now.\nPlease try again.\nBye!')
