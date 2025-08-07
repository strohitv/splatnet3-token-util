import argparse
import os.path
import shlex
import subprocess
import time

from PIL import Image
import imagehash

from data.app_config import AppConfig


class BlockAsLongAsRegionMatches:
	def __init__(self, command_name, app_config: AppConfig):
		self.command_name = command_name
		self.app_config = app_config

	def execute(self, args):
		only_args = shlex.split(args)[1:]

		parser = argparse.ArgumentParser()
		parser.add_argument('-f', '--filename', required=True)
		parser.add_argument('-x1', '--x1', required=True)
		parser.add_argument('-y1', '--y1', required=True)
		parser.add_argument('-x2', '--x2', required=True)
		parser.add_argument('-y2', '--y2', required=True)
		parser.add_argument('-d', '--duration', required=False, default=1000)
		parser.add_argument('-asp', '--actual_screenshot_path', required=False, default='./screenshots/screenshot.png')
		parser.add_argument('-co', '--cutoff', required=False, default=5)
		parsed_args = parser.parse_args(only_args)

		os.makedirs(os.path.dirname(parsed_args.filename), exist_ok=True)
		os.makedirs(os.path.dirname(parsed_args.actual_screenshot_path), exist_ok=True)

		start = time.time()

		found = True

		while found:
			time.sleep(int(parsed_args.duration) / 1000.0)

			print(f'Comparing screenshot "{parsed_args.actual_screenshot_path}" to base screenshot "{parsed_args.filename}" with cutoff {parsed_args.cutoff}.')
			subprocess.run(f'{self.app_config.emulator_config.adb_path} exec-out screencap -p > {parsed_args.actual_screenshot_path}',
						   shell=True,
						   stdout=subprocess.PIPE,
						   stderr=subprocess.PIPE)

			found = self.compare(parsed_args.filename, parsed_args.actual_screenshot_path, parsed_args.x1, parsed_args.y1, parsed_args.x2, parsed_args.y2,
						parsed_args.cutoff, self.app_config.debug)

		end = time.time()
		print(f'Not found anymore after {(end - start):0.1f} seconds.')

	def description(self):
		return ('waits for a region in a screenshot to not match the template provided anymore. If the region does still match, it will wait for [DURATION] milliseconds.'
				f'\n#    - Use: "{self.command_name} [TEMPLATE_SCREENSHOT] [REGION_X1] [REGION_Y1] [REGION_X2] [REGION_Y2] [DURATION_MS] [ACTUAL_SCREENSHOT_PATH] [CUTOFF]" to do the comparison.'
				f'\n#        - [TEMPLATE_SCREENSHOT]: a file path to a screenshot which will be used as the base for comparison.'
				f'\n#        - [REGION_X1]: X coordinate of the top left corner of the region to be compared.'
				f'\n#        - [REGION_Y1]: Y coordinate of the top left corner of the region to be compared.'
				f'\n#        - [REGION_X2]: X coordinate of the bottom right corner of the region to be compared.'
				f'\n#        - [REGION_Y2]: Y coordinate of the bottom right corner of the region to be compared.'
				f'\n#        - [DURATION_MS]: Optional duration in ms to wait before attempting again. It will wait for 1000 ms if no value is provided.'
				f'\n#        - [ACTUAL_SCREENSHOT_PATH]: Optional path in which the screenshot will be saved. It will save to \'./screenshot.png\' if no value is provided.'
				f'\n#        - [CUTOFF]: Optional cutoff for the screenshot comparison. It will be 5 is none is provided. A lower number means stricter comparison.'
				f'\n#    - Example 1: "{self.command_name} -f ./base.png -x1 100 -y1 200 -x2 300 -y2 400 -d 2000 -asp ./compare.png" -co 2 to compare the rectangle from (100, 200) to (300, 400) of base.png and compare.png with cutoff 2. If still found, wait for 2 seconds.'
				f'\n#    - Example 2: "{self.command_name} --filename ./base.png --x1 100 --y1 200 --x2 300 --y2 400 --duration 2000 --actual_screenshot_path ./compare.png" --cutoff 2 to compare the rectangle from (100, 200) to (300, 400) of base.png and compare.png with cutoff 2. If still found, wait for 2 seconds.')

	def compare(self, filename, actual_screenshot_path, x1, y1, x2, y2, cutoff, debug):
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
		
		return hash_diff < int(cutoff)
