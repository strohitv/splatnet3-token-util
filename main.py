import argparse
import atexit
import json

import multiprocess
import os
import signal
import sys
import time
import datetime

from data.app_config import AppConfig
from steps import all_steps
from utils.config_utils import load_config, ensure_scripts_exist, ensure_template_exists, save_config
from utils.emulator_utils import boot_emulator, run_adb, wait_for_shutdown, create_snapshot, delete_snapshot, request_emulator_shutdown
from utils.script_utils import execute_script
from utils.snapshot_utils import search_for_tokens
from utils.splatnet3_utils import is_homepage_reachable
from utils.stats_utils import prepare_stats, write_stats
from utils.step_doc_creator import create_step_doc
from utils.template_utils import create_target_file

import logging

from utils.update_utils import check_for_update, update, print_update_notification

logging.basicConfig(format='%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

SUCCESS = 0
INPUT_VALIDATION_FAILED = 1
NOT_ALL_TOKENS_FOUND = 2
INVALID_TOKENS_FOUND = 3
UPDATE_FAILED = 4


def run_token_extraction(app_config: AppConfig, all_available_steps, print_to_console, start, started_at, attempt, emulator_pid):
	# run emulator and create RAM dump
	emulator_proc = boot_emulator(app_config)
	emulator_pid.value = emulator_proc.pid

	execute_script(all_available_steps, app_config.run_config.boot_script_path, 'boot', app_config.debug)
	create_snapshot(app_config)
	execute_script(all_available_steps, app_config.run_config.cleanup_script_path, 'cleanup', app_config.debug)
	wait_for_shutdown(emulator_proc)
	emulator_pid.value = 0

	# extract tokens from RAM dump
	g_token, bullet_token, session_token, user_agent, web_view_version, na_country, na_language, app_language = search_for_tokens(app_config)
	delete_snapshot(app_config)

	if g_token is not None and bullet_token is not None and session_token is not None and na_country is not None:
		# do a webrequest to see whether they work
		if (app_config.token_config.validate_splat3_homepage
			and app_config.token_config.extract_g_token and app_config.token_config.validate_g_token
			and app_config.token_config.extract_bullet_token and app_config.token_config.validate_bullet_token):

			if not is_homepage_reachable(g_token, bullet_token, user_agent, web_view_version, na_country, na_language, app_language):
				logger.info('tokens were found but are invalid, attempt did not work')
				logger.info('')
				sys.exit(INVALID_TOKENS_FOUND)

		# export tokens to target file
		end = time.time()
		elapsed = end - start

		create_target_file(app_config, g_token, bullet_token, session_token, user_agent, web_view_version, na_country, na_language, app_language)
		write_stats(app_config.run_config.log_stats_csv, app_config.run_config.stats_csv_path, started_at, True, attempt, elapsed)
		logger.info(f'Done after {attempt} attempts and {elapsed:0.1f} seconds total. Application will exit now. Bye!')

		if print_to_console:
			print(json.dumps({
				'g_token': g_token,
				'bullet_token': bullet_token,
				'session_token': session_token,
				'user_agent': user_agent,
				'web_view_version': web_view_version,
				'na_country': na_country,
				'na_language': na_language,
				'app_language': app_language
			}))

		sys.exit(SUCCESS)
	else:
		logger.info('not all tokens could be found, attempt did not work')
		logger.info('')
		sys.exit(NOT_ALL_TOKENS_FOUND)


def main():
	parser = argparse.ArgumentParser(prog='main.py',
									 description='SplatNet3 Emulator Token Utility application to extract NSA SplatNet3 tokens from a controlled Android Studio emulator process')
	parser.add_argument('-c', '--config', required=False, help='Path to configuration file', default='./config/config.json')
	parser.add_argument('-cout', '--console-out', required=False,
						help='Prints the tokens to stdout. It will still save the tokens to the file. Format: `{"g_token": "{GTOKEN}", "bullet_token": "{BULLETTOKEN}", "session_token": "{SESSIONTOKEN}", "user_agent": "{USERAGENT}", "web_view_version": "{WEBVIEWVERSION}", "na_country": "{NACOUNTRY}", "na_language": "{NALANGUAGE}", "app_language": "{APPLANGUAGE}"}`',
						default=False, action='store_true')
	parser.add_argument('-r', '--reinitialize-configs', required=False,
						help='Regenerates the configuration file (and overwrites existing ones)', default=False, action='store_true')
	parser.add_argument('-b', '-emu', '--boot-emulator', '--emu', required=False, help='Boots the emulator', default=False, action='store_true')
	parser.add_argument('-a', '-adb', '--run-adb', '--adb', dest='ADB_COMMAND', required=False, help='Executes a command via android debug bridge (adb)')
	parser.add_argument('--disable-update-check', required=False, help='Disables update check for this single call', default=False, action='store_true')
	parser.add_argument('-u', '-update', '--update', required=False, help='Updates the application', default=False, action='store_true')
	args = parser.parse_args()

	regenerated, app_config = load_config(args)
	save_config(args.config, app_config)

	all_available_steps = all_steps.get_steps(app_config)

	if args.update:
		error_command = update(app_config)

		if error_command is not None:
			logger.info('')
			logger.error(f'ERROR while executing command `{error_command}` during update. See logs above for details.')
			sys.exit(UPDATE_FAILED)

		logger.info('')
		logger.info(f'Update successful. Please call `python main.py` again to use the application.')
		sys.exit(SUCCESS)

	if app_config.update_config.check_for_update and not args.disable_update_check:
		if check_for_update(app_config):
			print_update_notification(app_config)
			atexit.register(lambda: print_update_notification(app_config, prefix='\n'))

	export_step_doc_env = os.environ.get('STU_EXPORT_STEP_DOC_ENV')
	if export_step_doc_env is not None and export_step_doc_env.lower().strip() == 'true':
		logger.info('$STU_EXPORT_STEP_DOC_ENV environment variable is set to "true", (re-)creating steps_documentation.md')
		create_step_doc(all_available_steps)

	regenerated |= ensure_scripts_exist(args, app_config)
	regenerated |= ensure_template_exists(args, app_config)

	if regenerated:
		logger.info('Configs were regenerated, application will exit. Bye!')
		logger.info('')
		sys.exit(SUCCESS)

	if args.boot_emulator:
		emulator_proc = boot_emulator(app_config)
		wait_for_shutdown(emulator_proc)
		logger.info('Emulator was shut down, application will exit. Bye!')
		sys.exit(SUCCESS)

	if args.ADB_COMMAND is not None:
		run_adb(app_config, args.ADB_COMMAND)
		logger.info('Command execution finished, application will exit. Bye!')
		sys.exit(SUCCESS)

	if not os.path.exists(app_config.emulator_config.emulator_path):
		logger.info('ERROR: emulator_path in config does not exist. Please edit the config file and insert a valid emulator_path. Exiting now.')
		sys.exit(INPUT_VALIDATION_FAILED)

	if not os.path.exists(app_config.emulator_config.adb_path):
		logger.info('ERROR: adb_path in config does not exist. Please edit the config file and insert a valid adb_path. Exiting now.')
		sys.exit(INPUT_VALIDATION_FAILED)

	if not os.path.exists(os.path.dirname(app_config.emulator_config.get_snapshot_dir())):
		logger.info('ERROR: parent directory of snapshot_dir in config does not exist. Please edit the config file and insert a valid snapshot_dir. Exiting now.')
		sys.exit(INPUT_VALIDATION_FAILED)

	if not os.path.exists(app_config.run_config.boot_script_path):
		logger.info('ERROR: boot_script_path in config does not exist. Please edit the config file and insert a valid boot_script_path. Exiting now.')
		sys.exit(INPUT_VALIDATION_FAILED)

	if not os.path.exists(app_config.run_config.cleanup_script_path):
		logger.info('ERROR: cleanup_script_path in config does not exist. Please edit the config file and insert a valid cleanup_script_path. Exiting now.')
		sys.exit(INPUT_VALIDATION_FAILED)

	if not os.path.exists(app_config.run_config.template_path):
		logger.info('ERROR: template_path in config does not exist. Please edit the config file and insert a valid template_path. Exiting now.')
		sys.exit(INPUT_VALIDATION_FAILED)

	start_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	logger.info(f'### Script started at {start_datetime} ###')

	start_time = time.time()
	prepare_stats(app_config.run_config.log_stats_csv, app_config.run_config.stats_csv_path)

	last_allowed_attempt_start_time = start_time + max(5, app_config.run_config.max_run_duration_minutes) * 60
	attempt = 0
	while time.time() < last_allowed_attempt_start_time:
		attempt += 1

		logger.info(f'### Attempt {attempt} ###')
		logger.info('')
		logger.info(f'Expecting this attempt to take {max(60, app_config.run_config.max_attempt_duration_seconds)} seconds at worst.')
		logger.info('')

		extraction_process = None
		emulator_pid = multiprocess.Value('i', 0)
		try:
			extraction_process = multiprocess.Process(target=run_token_extraction,
													  args=(app_config, all_available_steps, args.console_out, start_time, start_datetime, attempt, emulator_pid))
			extraction_process.start()

			targeted_end_time = time.time() + max(60, app_config.run_config.max_attempt_duration_seconds)
			while time.time() < targeted_end_time and extraction_process.is_alive():
				time.sleep(1)

			if extraction_process.is_alive():
				raise Exception(f'Extraction did not finish in time ({max(60, app_config.run_config.max_attempt_duration_seconds)} seconds), forcing restart...')
			elif extraction_process.exitcode is not None and extraction_process.exitcode == 0:
				sys.exit(SUCCESS)

		except Exception as e:
			logger.info(f'### Exception ###')
			logger.info(e)
			logger.info('')

			if extraction_process is not None and extraction_process.is_alive():
				logger.info(f'Terminating extraction process...')
				extraction_process.terminate()
				time.sleep(10)
				extraction_process.kill()
				logger.info('Process terminated.')
				logger.info('')

			# ensure a potentially created snapshot has been deleted.
			delete_snapshot(app_config)
			request_emulator_shutdown(app_config)

			if emulator_pid.value is not None and emulator_pid.value > 0:
				try:
					logger.info('Emulator process might still be alive, sending KILL signal...')
					logger.info('')
					os.kill(emulator_pid.value, signal.SIGKILL)
				except Exception as e2:
					logger.info(e2)

	ended = time.time()
	elapsed = ended - start_time

	write_stats(app_config.run_config.log_stats_csv, app_config.run_config.stats_csv_path, start_datetime, False, attempt, elapsed)
	logger.info(f'Could not find all requested tokens in {attempt} attempts, application will stop now.\nPlease fix potential errors and try again.\nBye!')
	logger.info('')
	sys.exit(NOT_ALL_TOKENS_FOUND)


if __name__ == '__main__':
	main()
