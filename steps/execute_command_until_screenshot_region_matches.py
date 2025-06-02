import argparse
import os.path
import shlex
import subprocess
import time

from PIL import Image
import imagehash

from data.app_config import AppConfig
from utils.script_utils import execute


class ExecuteCommandUntilScreenshotRegionMatches:
	def __init__(self, command_name, app_config: AppConfig, all_steps):
		self.command_name = command_name
		self.app_config = app_config
		self.all_steps = all_steps

	def execute(self, args):
		only_args = shlex.split(args)[1:]

		parser = argparse.ArgumentParser()
		parser.add_argument('-f', '--filename', required=True)
		parser.add_argument('-x1', '--x1', required=True)
		parser.add_argument('-y1', '--y1', required=True)
		parser.add_argument('-x2', '--x2', required=True)
		parser.add_argument('-y2', '--y2', required=True)
		parser.add_argument('-c', '--command', required=True)
		parser.add_argument('-d', '--duration', required=False, default=500)
		parser.add_argument('-asp', '--actual_screenshot_path', required=False, default='./screenshots/screenshot.png')
		parsed_args = parser.parse_args(only_args)

		os.makedirs(os.path.dirname(parsed_args.filename), exist_ok=True)
		os.makedirs(os.path.dirname(parsed_args.actual_screenshot_path), exist_ok=True)

		start = time.time()

		while True:
			print(f'Comparing screenshot "{parsed_args.actual_screenshot_path}" to base screenshot "{parsed_args.filename}".')
			subprocess.run(f'{self.app_config.adb_path} exec-out screencap -p > {parsed_args.actual_screenshot_path}',
						   shell=True,
						   stdout=subprocess.PIPE,
						   stderr=subprocess.PIPE)

			found = self.compare(parsed_args.filename, parsed_args.actual_screenshot_path, parsed_args.x1, parsed_args.y1, parsed_args.x2, parsed_args.y2,
								 self.app_config.debug)

			if found:
				break

			execute(parsed_args.command, self.all_steps)

			time.sleep(int(parsed_args.duration) / 1000.0)


		end = time.time()
		print(f'Found after {(end - start):0.1f} seconds.')

	def description(self):
		return ('executes a given command until a region in a screenshot matches the template provided. It will wait for [DURATION] milliseconds every time the region does not match.'
				f'\n#    - Use: "{self.command_name} [TEMPLATE_SCREENSHOT] [REGION_X1] [REGION_Y1] [REGION_X2] [REGION_Y2] [COMMAND] [DURATION_MS] [ACTUAL_SCREENSHOT_PATH]" to do the comparison.'
				f'\n#        - [TEMPLATE_SCREENSHOT]: a file path to a screenshot which will be used as the base for comparison.'
				f'\n#        - [REGION_X1]: X coordinate of the top left corner of the region to be compared.'
				f'\n#        - [REGION_Y1]: Y coordinate of the top left corner of the region to be compared.'
				f'\n#        - [REGION_X2]: X coordinate of the bottom right corner of the region to be compared.'
				f'\n#        - [REGION_Y2]: Y coordinate of the bottom right corner of the region to be compared.'
				f'\n#        - [COMMAND]: The command which should be executed.'
				f'\n#        - [DURATION_MS]: Optional duration in ms to wait before attempting again. It will wait for 1000 ms if no value is provided.'
				f'\n#        - [ACTUAL_SCREENSHOT_PATH]: Optional path in which the screenshot will be saved. It will save to \'./screenshot.png\' if no value is provided.'
				f'\n#    - Example 1: "{self.command_name} -f ./base.png -x1 100 -y1 200 -x2 300 -y2 400 -c "wait_s 5" -d 2000 -asp ./compare.png" to execute a wait command of 5 seconds and compare the rectangle from (100, 200) to (300, 400) of base.png and compare.png. If not found, wait for 2 seconds and try again.'
				f'\n#    - Example 2: "{self.command_name} --filename ./base.png --x1 100 --y1 200 --x2 300 --y2 400 --command "wait_s 5" --duration 2000 --actual_screenshot_path ./compare.png" to execute a wait command of 5 seconds and compare the rectangle from (100, 200) to (300, 400) of base.png and compare.png. If not found, wait for 2 seconds and try again.')

	def compare(self, filename, actual_screenshot_path, x1, y1, x2, y2, debug):
		cutoff = 5

		try:
			base_image = Image.open(filename)
			compare_image = Image.open(actual_screenshot_path)

			base_cropped = base_image.crop((int(x1), int(y1), int(x2), int(y2)))
			compare_image_cropped = compare_image.crop((int(x1), int(y1), int(x2), int(y2)))

			hash0 = imagehash.average_hash(base_cropped)
			hash1 = imagehash.average_hash(compare_image_cropped)

			if self.app_config.debug:
				print(f'hash #1: {hash0}, hash #2: {hash1}, difference: {hash1 - hash0}')
				base_cropped.save(f'{filename}-cropped.png')
				compare_image_cropped.save(f'{actual_screenshot_path}-cropped.png')

			hash_diff = hash0 - hash1
		except:
			hash_diff = 1000
		
		return hash_diff < cutoff
