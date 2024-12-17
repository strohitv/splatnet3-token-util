import argparse
import os.path
import shlex
import subprocess
import time

from PIL import Image
import imagehash

from data.config import Config


class BlockUntilScreenshotRegionMatches:
	def __init__(self, command_name, config: Config):
		self.command_name = command_name
		self.config = config

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
		parsed_args = parser.parse_args(only_args)

		os.makedirs(os.path.dirname(parsed_args.filename), exist_ok=True)
		os.makedirs(os.path.dirname(parsed_args.actual_screenshot_path), exist_ok=True)

		found = False

		while not found:
			time.sleep(int(parsed_args.duration) / 1000.0)

			print(f'Comparing screenshot "{parsed_args.actual_screenshot_path}" to base screenshot "{parsed_args.filename}".')
			subprocess.run(f'{self.config.adb_path} exec-out screencap -p > {parsed_args.actual_screenshot_path}', shell=True)

			found = self.compare(parsed_args.filename, parsed_args.actual_screenshot_path, parsed_args.x1, parsed_args.y1, parsed_args.x2, parsed_args.y2, self.config.debug)

		time.sleep(int(parsed_args.duration) / 1000.0)
		print('Found.')

	def description(self):
		return ('waits a region in a screenshot to match the template provided. If the region does not match, it will wait for [DURATION] milliseconds.'
				f'\n#    - Use: "{self.command_name} [TEMPLATE_SCREENSHOT] [REGION_X1] [REGION_Y1] [REGION_X2] [REGION_Y2] [DURATION_MS] [ACTUAL_SCREENSHOT_PATH]" to do the comparison.'
				f'\n#        - [TEMPLATE_SCREENSHOT]: a file path to a screenshot which will be used as the base for comparison.'
				f'\n#        - [REGION_X1]: X coordinate of the top left corner of the region to be compared.'
				f'\n#        - [REGION_Y1]: Y coordinate of the top left corner of the region to be compared.'
				f'\n#        - [REGION_X2]: X coordinate of the bottom right corner of the region to be compared.'
				f'\n#        - [REGION_Y2]: Y coordinate of the bottom right corner of the region to be compared.'
				f'\n#        - [DURATION_MS]: Optional duration in ms to wait before attempting again. It will wait for 1000 ms if no value is provided.'
				f'\n#        - [ACTUAL_SCREENSHOT_PATH]: Optional path in which the screenshot will be saved. It will save to \'./screenshot.png\' if no value is provided.'
				f'\n#    - Example 1: "{self.command_name} -f ./base.png -x1 100 -y1 200 -x2 300 -y2 400 -d 2000 -asp ./compare.png" to compare the rectangle from (100, 200) to (300, 400) of base.png and compare.png. If not found, wait for 2 seconds.'
				f'\n#    - Example 2: "{self.command_name} --filename ./base.png --x1 100 --y1 200 --x2 300 --y2 400 --duration 2000 --actual_screenshot_path ./compare.png" to compare the rectangle from (100, 200) to (300, 400) of base.png and compare.png. If not found, wait for 2 seconds.')

	def compare(self, filename, actual_screenshot_path, x1, y1, x2, y2, debug):
		base_image = Image.open(filename)
		compare_image = Image.open(actual_screenshot_path)

		base_cropped = base_image.crop((int(x1), int(y1), int(x2), int(y2)))
		compare_image_cropped = compare_image.crop((int(x1), int(y1), int(x2), int(y2)))

		hash0 = imagehash.average_hash(base_cropped)
		hash1 = imagehash.average_hash(compare_image_cropped)

		if debug:
			print(f'hash #1: {hash0}, hash #2: {hash1}, difference: {hash1 - hash0}')

		cutoff = 5

		hash_diff = hash0 - hash1
		return hash_diff < cutoff


