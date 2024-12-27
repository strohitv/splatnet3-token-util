import argparse
import sys
import time
import datetime

from steps import all_steps
from utils.config_utils import load_config, ensure_scripts_exist, ensure_template_exists
from utils.emulator_utils import boot_emulator, wait_for_shutdown, create_snapshot, delete_snapshot
from utils.script_utils import execute_script
from utils.snapshot_utils import search_for_tokens
from utils.stats_utils import prepare_stats, write_stats
from utils.template_utils import create_target_file

if __name__ == '__main__':
	parser = argparse.ArgumentParser(prog='splatnet3-emu-token-util',
									 description='SplatNet3 Emulator Token Utility application to extract NSO SplatNet3 tokens from a controlled Android Studio emulator process')
	parser.add_argument('-c', '--config', required=False, help='Path to configuration file', default='./config/config.json')
	parser.add_argument('-r', '--reinitialize-configs', required=False,
						help='Generates the config again (and potentially overwrites existing ones)', default=False,
						action='store_true')
	args = parser.parse_args()

	regenerated, app_config = load_config(args)
	all_available_steps = all_steps.get_steps(app_config)

	regenerated |= ensure_scripts_exist(args, app_config, all_available_steps)
	regenerated |= ensure_template_exists(args, app_config)

	if regenerated:
		print('Configs were regenerated, application will exit. Bye!')
		sys.exit(0)

	started_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	start = time.time()
	prepare_stats(app_config.log_stats_csv, app_config.stats_csv_path)

	g_token = None
	bullet_token = None
	session_token = None

	attempt = 0
	for attempt in range(app_config.max_attempts):
		print(f'### Attempt {attempt + 1} / {app_config.max_attempts} ###')
		print()

		# run emulator and create RAM dump
		emulator_proc = boot_emulator(app_config)

		execute_script(all_available_steps, app_config.boot_script_path, 'boot', app_config.debug)
		create_snapshot(app_config)
		execute_script(all_available_steps, app_config.cleanup_script_path, 'cleanup', app_config.debug)

		wait_for_shutdown(emulator_proc)

		# extract tokens from RAM dump
		g_token, bullet_token, session_token = search_for_tokens(app_config)
		delete_snapshot(app_config)

		if g_token is not None and bullet_token is not None and session_token is not None:
			break

	# export tokens to target file
	finished_successful = g_token is not None and bullet_token is not None and session_token is not None
	end = time.time()
	elapsed = end - start

	write_stats(app_config.log_stats_csv, app_config.stats_csv_path, started_at, finished_successful, attempt + 1, elapsed)

	if finished_successful:
		create_target_file(app_config, g_token, bullet_token, session_token)
		print(f'Done after {attempt + 1} attempts. Application will exit now. Bye!')
	else:
		print(f'Could not find all three tokens in {app_config.max_attempts} attempts, application will stop now.\nPlease try again.\nBye!')
		sys.exit(1)
