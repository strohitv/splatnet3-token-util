import csv
import os


def prepare_stats(should_write_config, csv_path):
	if should_write_config and not os.path.exists(csv_path):
		with open(csv_path, 'w') as csvfile:
			print(f'No stats file found, writing to "{csv_path}"')
			writer = csv.writer(csvfile, delimiter=';')
			writer.writerow(['Started at', 'Result', 'Attempts', 'Elapsed time'])

def write_stats(should_write_config, csv_path, started_at, success, attempt_number, elapsed_time):
	if should_write_config and os.path.exists(csv_path):
		with open(csv_path, 'a') as csvfile:
			print(f'Stats file found, appending to "{csv_path}"')
			writer = csv.writer(csvfile, delimiter=';')
			writer.writerow([started_at, 'success' if success else 'failed', attempt_number, f'{elapsed_time:0.1f}'])
