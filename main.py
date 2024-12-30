import argparse
import multiprocessing
import os
import signal
import sys
import time
import datetime

from steps import all_steps
from utils.config_utils import load_config, ensure_scripts_exist, ensure_template_exists
from utils.emulator_utils import boot_emulator, wait_for_shutdown, create_snapshot, delete_snapshot, request_emulator_shutdown
from utils.script_utils import execute_script
from utils.snapshot_utils import search_for_tokens
from utils.stats_utils import prepare_stats, write_stats
from utils.template_utils import create_target_file


def run_token_extraction(app_config, all_available_steps, start, started_at, attempt, emulator_pid):
	# run emulator and create RAM dump
	emulator_proc = boot_emulator(app_config)
	emulator_pid.value = emulator_proc.pid

	execute_script(all_available_steps, app_config.boot_script_path, 'boot', app_config.debug)
	create_snapshot(app_config)
	execute_script(all_available_steps, app_config.cleanup_script_path, 'cleanup', app_config.debug)
	wait_for_shutdown(emulator_proc)
	emulator_pid.value = 0

	# extract tokens from RAM dump
	g_token, bullet_token, session_token = search_for_tokens(app_config)
	delete_snapshot(app_config)

	if g_token is not None and bullet_token is not None and session_token is not None:
		# export tokens to target file
		end = time.time()
		elapsed = end - start

		create_target_file(app_config, g_token, bullet_token, session_token)
		write_stats(app_config.log_stats_csv, app_config.stats_csv_path, started_at, True, attempt + 1, elapsed)
		print(f'Done after {attempt + 1} attempts and {elapsed:0.1f} seconds total. Application will exit now. Bye!')

		sys.exit(0)


def main():
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

	start_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	start_time = time.time()
	prepare_stats(app_config.log_stats_csv, app_config.stats_csv_path)

	attempt = 0
	for attempt in range(app_config.max_attempts):
		print(f'### Attempt {attempt + 1} / {app_config.max_attempts} ###')
		print()
		print(f'Expecting this attempt to end after {app_config.max_duration_seconds_per_attempt} seconds at worst.')
		print()

		extraction_process = None
		emulator_pid = multiprocessing.Value('i', 0)
		try:
			extraction_process = multiprocessing.Process(target=run_token_extraction,
														 args=(app_config, all_available_steps, start_time, start_datetime, attempt, emulator_pid))
			extraction_process.start()

			targeted_end_time = time.time() + app_config.max_duration_seconds_per_attempt
			while time.time() < targeted_end_time and extraction_process.is_alive():
				time.sleep(1)

			if extraction_process.is_alive():
				raise Exception(f'Extraction did not finish in time ({app_config.max_duration_seconds_per_attempt} seconds), forcing restart...')
			elif extraction_process.exitcode is not None and extraction_process.exitcode == 0:
				sys.exit(0)

		except Exception as e:
			print(f'### Exception ###')
			print(e)
			print()

			if extraction_process is not None and extraction_process.is_alive():
				print(f'Terminating extraction process...')
				extraction_process.terminate()
				time.sleep(10)
				extraction_process.kill()
				print('Process terminated.')
				print()

			# ensure a potentially created snapshot has been deleted.
			delete_snapshot(app_config)
			request_emulator_shutdown(app_config)

			if emulator_pid.value is not None and emulator_pid.value > 0:
				try:
					print('Emulator process might still be alive, sending KILL signal...')
					print()
					os.kill(emulator_pid.value, signal.SIGKILL)
				except Exception as e2:
					print(e2)

	ended = time.time()
	elapsed = ended - start_time

	write_stats(app_config.log_stats_csv, app_config.stats_csv_path, start_datetime, False, attempt + 1, elapsed)
	print(f'Could not find all three tokens in {app_config.max_attempts} attempts, application will stop now.\nPlease try again.\nBye!')
	sys.exit(1)


if __name__ == '__main__':
	main()
