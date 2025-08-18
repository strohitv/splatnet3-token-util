import io
import logging
import subprocess
from subprocess import Popen

from data.app_config import AppConfig

logger = logging.getLogger(__name__)


def check_for_update(app_config: AppConfig):
	git_fetch_proc = Popen(
		f'{app_config.update_config.git_command} fetch',
		shell=True,
		stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT)

	for line in io.TextIOWrapper(git_fetch_proc.stdout, encoding="utf-8"):
		if not line:
			break

		# git fetch never prints something, thus any line should be considered an issue
		logger.error(line.strip())

	git_status_proc = Popen(
		f'{app_config.update_config.git_command} status -sb',
		shell=True,
		stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT)

	update_is_available = False
	for line in io.TextIOWrapper(git_status_proc.stdout, encoding="utf-8"):
		if not line:
			break

		if app_config.debug:
			logger.info(line.strip())

		line = line.strip()
		if 'behind' in line:
			update_is_available = True

	return update_is_available


def print_update_notification(app_config: AppConfig, prefix=''):
	logger.info(prefix)
	logger.info('######')
	logger.info('!! UPDATE AVAILABLE !!')
	logger.info('vvvvvv')
	logger.info('')
	logger.info('An update is available. Please consider updating using one of the following two approaches:')
	logger.info('')
	logger.info('Automatic update:')
	logger.info('- run `python main.py --update`')
	logger.info('')
	logger.info('Manual update:')
	logger.info(f'- first, run `{app_config.update_config.git_command} pull`')
	logger.info(f'- second, run `{app_config.update_config.pip_command} install -r requirements.txt`')
	logger.info('')
	logger.info('ʌʌʌʌʌʌ')
	logger.info('!! UPDATE AVAILABLE !!')
	logger.info('######')


def update(app_config: AppConfig):
	logger.info(f'Update in progress...')

	update_error_command = None
	current_command = f'{app_config.update_config.git_command} pull'

	logger.info(f'')
	logger.info(f'running command: `{current_command}`')

	git_pull_proc = Popen(
		current_command,
		shell=True,
		stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT)

	for line in io.TextIOWrapper(git_pull_proc.stdout, encoding="utf-8"):
		if not line:
			break

		logger.info(line.strip())

		if 'error' in line.lower() or 'conflict' in line.lower():
			update_error_command = current_command
			logger.error(line.strip())

	if update_error_command is None:
		current_command = f'{app_config.update_config.pip_command} install -r requirements.txt'

		logger.info(f'')
		logger.info(f'running command: `{current_command}`')

		pip_install_proc = Popen(
			current_command,
			shell=True,
			stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT)

		for line in io.TextIOWrapper(pip_install_proc.stdout, encoding="utf-8"):
			if not line:
				break

			logger.info(line.strip())

			if 'error' in line.lower():
				update_error_command = current_command
				logger.error(line.strip())

	return update_error_command
