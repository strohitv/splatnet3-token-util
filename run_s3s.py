import json
import os
import shutil
import subprocess
import sys

# This script serves as a wrapper for s3s and automatically refreshes the tokens used by it if necessary

DEFAULT_CONFIG = {
	's3s_directory': '',
	's3s_refresh_rc': '42',
	's3s_update': False,
	'stu_update': False,
	'generated_config_filepath': 'config.txt',
	'git_command': 'git',
	'python_command': 'python3',
	'pip_command': 'pip3'
}


def load_and_check_config():
	if not os.path.exists('config_run_s3s.json'):
		write_config_and_exit(DEFAULT_CONFIG)

	with open('config_run_s3s.json', 'r') as f:
		config = json.load(f)

	save_config = False
	for key in DEFAULT_CONFIG:
		if key not in config:
			config[key] = DEFAULT_CONFIG[key]
			save_config = True

	if save_config:
		write_config_and_exit(config)

	if not os.path.exists(config['s3s_directory']):
		print('ERROR: s3s_directory does not exist, exiting.')
		sys.exit(3)

	return config


def write_config_and_exit(config):
	with open('config_run_s3s.json', 'w') as f:
		json.dump(config, f, indent=4)

	print('Saved config file "config_run_s3s.json". Please fill it according to your needs and restart this script afterwards. Exiting now.')
	sys.exit(0)


def main():
	config = load_and_check_config()

	if len(sys.argv[1:]) == 0:
		print('Using "--help" as command line args since you did not provide any.')
		sys.argv += ['--help']
		print()

	s3s_args = ' '.join(['--norefresh', config['s3s_refresh_rc']] + sys.argv[1:])

	while True:
		# 1. prepare s3s run
		print('###########')
		print('running s3s')
		print('###########')
		print()

		print(f'Running s3s with command "{config['python_command']} {os.path.join(config['s3s_directory'], 's3s.py')} {s3s_args}"')
		print()

		if config['s3s_update']:
			print(f'1/2 Running s3s update with command "{config['git_command']} pull"')
			subprocess.run(f'{config['git_command']} pull',
						   cwd=config['s3s_directory'],
						   shell=True)
			print()
			print(f'2/2 Running s3s update with command "{config['pip_command']} install -r requirements.txt"')
			subprocess.run(f'{config['pip_command']} install -r requirements.txt',
						   cwd=config['s3s_directory'],
						   shell=True)
			print()
			config['s3s_update'] = False

		# 2. run s3s and store return code
		s3s_proc = subprocess.run(f'{config['python_command']} {os.path.join(config['s3s_directory'], 's3s.py')} {s3s_args}',
								  cwd=config['s3s_directory'],
								  shell=True)

		print()
		print(f's3s finished. Return code: {s3s_proc.returncode}')

		# stop script if s3s ran successfully
		if s3s_proc.returncode == 0:
			print('s3s finished successful -> exiting script.')
			sys.exit(0)

		print()

		# stop script if s3s failed
		if s3s_proc.returncode != int(config['s3s_refresh_rc']):
			# ERROR: s3s failed
			print('ERROR DURING s3s!!!')
			print('exiting script.')
			sys.exit(1)

		# 3. token refresh required - prepare splatnet3-token-util run
		print('###########################')
		print('running splanet3-token-util')
		print('###########################')
		print()

		if config['stu_update']:
			print(f'1/2 Running splatnet3-token-util update with command "{config['git_command']} pull"')
			subprocess.run(f'{config['git_command']} pull',
						   shell=True)
			print()
			print(f'2/2 Running splatnet3-token-util update with command "{config['pip_command']} install -r requirements.txt"')
			subprocess.run(f'{config['pip_command']} install -r requirements.txt',
						   shell=True)
			print()
			config['stu_update'] = False

		# 4. run splatnet3-token-util and act according to result
		stu_proc = subprocess.run(f'{config['python_command']} main.py',
								  shell=True)

		print()

		if stu_proc.returncode == 0:
			# copy config to s3s directory
			shutil.copyfile(config['generated_config_filepath'], os.path.join(config['s3s_directory'], 'config.txt'))
			print('config.txt written into s3s folder')
			print()
		else:
			# ERROR: splatnet3-token-util stopped after X failed attempts
			print('ERROR DURING TOKEN EXTRACTION!!!')
			print('exiting the script')
			sys.exit(2)


if __name__ == '__main__':
	main()
