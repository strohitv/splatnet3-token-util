import configparser
import json
import os

from data.config import Config
from data.s3s_config import S3sConfig


def load_config(args):
	regenerated = False

	if args.reinitialize_configs or not os.path.exists(args.config):
		print(f'Attempting to generate config file at "{args.config}"')
		default_config = Config()
		os.makedirs(os.path.dirname(args.config), exist_ok=True)

		with open(args.config, 'w') as f:
			f.write(default_config.to_json())

		print(f'Successfully generated config file at "{args.config}", please fill it with correct values and run the application again')
		regenerated = True

	# read config
	with open(args.config, 'r') as f:
		config = Config.from_json(json.loads(f.read()))

	return regenerated, config


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


def ensure_scripts_exist(args, config, all_available_steps):
	regenerated = False

	if args.reinitialize_configs or not os.path.exists(config.boot_script_path):
		print(f'Attempting to generate boot file at "{config.boot_script_path}"')

		boot_summary = ('# This file contains the steps required to open the NSO SplatNet 3 app.\n'
						'# \n'
						'# It starts executing AFTER the emulator has been started.\n'
						'# Once this file has been fully executed, the script will create a snapshot of the emulator.\n'
						'# \n'
						'# Your goal for this script is to bring the freshly booted emulator to a state where the NSO app is opened and has entered SplatNet 3.\n')

		create_script_file(all_available_steps, config.boot_script_path, boot_summary, 'boot')

		print(f'Successfully generated boot file at "{config.boot_script_path}", please fill it with correct steps and run the application again')
		regenerated = True

	if args.reinitialize_configs or not os.path.exists(config.cleanup_script_path):
		print(f'Attempting to generate boot file at "{config.cleanup_script_path}"')

		cleanup_summary = ('# This file contains the steps required to close the NSO SplatNet 3 app and shut down the emulator.\n'
						   '# \n'
						   '# It starts executing AFTER the snapshot of the emulator has been created.\n'
						   '# Once this file has been fully executed, the script will analyse the snapshot RAM dump to find the tokens.\n'
						   '# \n'
						   '# Your goal for this script is to close the SplatNet 3 app and shut down the emulator.\n')

		create_script_file(all_available_steps, config.cleanup_script_path, cleanup_summary, 'cleanup')

		print(f'Successfully generated cleanup file at "{config.cleanup_script_path}", please fill it with correct steps and run the application again')
		regenerated = True

	return regenerated


def ensure_template_exists(args, config):
	regenerated = False

	if args.reinitialize_configs or not os.path.exists(config.template_path):
		print(f'Attempting to generate template file at "{config.template_path}"')

		s3s_config = S3sConfig()
		os.makedirs(os.path.dirname(config.template_path), exist_ok=True)

		with open(config.template_path, 'w') as f:
			f.write(s3s_config.to_json())

		print(f'Successfully generated template file at "{config.template_path}", please fill it with correct values and run the application again')
		regenerated = True

	return regenerated
