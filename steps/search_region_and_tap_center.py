import argparse
import os.path
import shlex
import subprocess
import time

from PIL import Image
import imagehash

from data.app_config import AppConfig
from steps.execute_command_as_long_as_region_matches import ExecuteCommandAsLongAsRegionMatches
from utils import script_utils


class SearchRegionAndTapCenter:
	def __init__(self, command_name, app_config: AppConfig, all_steps):
		self.command_name = command_name
		self.app_config = app_config
		self.all_steps = all_steps

		self.execute_command_step = None
		for step_key in self.all_steps:
			if isinstance(self.all_steps[step_key], ExecuteCommandAsLongAsRegionMatches):
				self.execute_command_step = self.all_steps[step_key]
				break

		if self.execute_command_step is None:
			raise Exception('Could not find execute_command_step!')

		self.parsed_args = None

	def execute(self, args):
		only_args = shlex.split(args)[1:]

		parser = argparse.ArgumentParser()
		parser.add_argument('-f', '--filename', required=True)
		parser.add_argument('-region_x1', '--region_x1', required=True)
		parser.add_argument('-region_y1', '--region_y1', required=True)
		parser.add_argument('-region_x2', '--region_x2', required=True)
		parser.add_argument('-region_y2', '--region_y2', required=True)
		parser.add_argument('-comparison_x1', '--comparison_x1', required=True)
		parser.add_argument('-comparison_y1', '--comparison_y1', required=True)
		parser.add_argument('-comparison_x2', '--comparison_x2', required=True)
		parser.add_argument('-comparison_y2', '--comparison_y2', required=True)
		parser.add_argument('-c', '--command', required=True)
		parser.add_argument('-d', '--duration', required=False, default=500)
		parser.add_argument('-asp', '--actual_screenshot_path', required=False, default='./screenshots/screenshot.png')
		parser.add_argument('-co', '--cutoff', required=False, default=5)
		parser.add_argument('-s', '--step', required=False, default=1)

		parsed_args = parser.parse_args(only_args)
		self.parsed_args = parsed_args

		os.makedirs(os.path.dirname(parsed_args.filename), exist_ok=True)
		os.makedirs(os.path.dirname(parsed_args.actual_screenshot_path), exist_ok=True)

		start = time.time()

		try:
			base_image = Image.open(parsed_args.filename)
			base_cropped = base_image.crop((int(parsed_args.comparison_x1), int(parsed_args.comparison_y1), int(parsed_args.comparison_x2), int(parsed_args.comparison_y2)))

			while True:
				print(f'Searching for image from base screenshot "{parsed_args.filename}" in screenshot "{parsed_args.actual_screenshot_path}" with cutoff {parsed_args.cutoff}.')
				subprocess.run(f'{self.app_config.emulator_config.adb_path} exec-out screencap -p > {parsed_args.actual_screenshot_path}',
							shell=True,
							stdout=subprocess.PIPE,
							stderr=subprocess.PIPE)

				compare_image = Image.open(parsed_args.actual_screenshot_path)

				result = self.compare(
					base_cropped,
					compare_image,
					int(parsed_args.comparison_x1),
					int(parsed_args.comparison_y1),
					int(parsed_args.comparison_x2),
					int(parsed_args.comparison_y2),
					int(parsed_args.region_x1),
					int(parsed_args.region_y1),
					int(parsed_args.region_x2),
					int(parsed_args.region_y2),
					int(parsed_args.cutoff),
					int(parsed_args.step),
					self.app_config.debug)

				if result is not None:
					break

				script_utils.execute(parsed_args.command, self.all_steps)

				time.sleep(int(parsed_args.duration) / 1000.0)

			x1, y1, x2, y2 = result

			tap_x = int((x1 + x2) / 2)
			tap_y = int((y1 + y2) / 2)

			print(f'Found at: ({x1}, {y2}), tapping position ({tap_x, tap_y}) until something happens')

			script_utils.execute(f'{self.execute_command_step.command_name} -f {parsed_args.filename} -x1 {x1} -y1 {y1} -x2 {x2} -y2 {y2} -d 500 -asp {parsed_args.actual_screenshot_path}_tapped.png -c "tap -x {tap_x} -y {tap_y}"', self.all_steps)

			end = time.time()
			print(f'Finished search_region_and_tap_center after {(end - start):0.1f} seconds.')
		except Exception as e:
			print(f'ERROR occured, stopping.')
			print(e)

	def description(self):
		return ('searches whether a given region contains an image. If found, it will tap the center of the found image until the image is not found anymore. It will wait for [DURATION] milliseconds every time the region does not contain the image.'
				f'\n#    - Use: "{self.command_name} [TEMPLATE_SCREENSHOT] [REGION_X1] [REGION_Y1] [REGION_X2] [REGION_Y2] [COMPARISON_X1] [COMPARISON_Y1] [COMPARISON_X2] [COMPARISON_Y2] [COMMAND] [DURATION_MS] [ACTUAL_SCREENSHOT_PATH] [CUTOFF] [STEP]" to do the comparison.'
				f'\n#        - [TEMPLATE_SCREENSHOT]: a file path to a screenshot which will be used as the base for comparison.'
				f'\n#        - [REGION_X1]: X coordinate of the top left corner of the region to search in.'
				f'\n#        - [REGION_Y1]: Y coordinate of the top left corner of the region to search in.'
				f'\n#        - [REGION_X2]: X coordinate of the bottom right corner of the region to search in.'
				f'\n#        - [REGION_Y2]: Y coordinate of the bottom right corner of the region to search in.'
				f'\n#        - [COMPARISON_X1]: X coordinate of the top left corner of the comparison image inside the template screenshot.'
				f'\n#        - [COMPARISON_Y1]: Y coordinate of the top left corner of the comparison image inside the template screenshot.'
				f'\n#        - [COMPARISON_X2]: X coordinate of the bottom right corner of the comparison image inside the template screenshot.'
				f'\n#        - [COMPARISON_Y2]: Y coordinate of the bottom right corner of the comparison image inside the template screenshot.'
				f'\n#        - [COMMAND]: The command which should be executed if the region does not contain the image.'
				f'\n#        - [DURATION_MS]: Optional duration in ms to wait before attempting again. It will wait for 1000 ms if no value is provided.'
				f'\n#        - [ACTUAL_SCREENSHOT_PATH]: Optional path in which the screenshot will be saved. It will save to \'./screenshot.png\' if no value is provided.'
				f'\n#        - [CUTOFF]: Optional cutoff for the screenshot comparison. It will be 5 is none is provided. A lower number means stricter comparison.'
				f'\n#        - [STEP]: Optional step size for the screenshot comparison. It will be 1 is none is provided. It sets how many pixels are between the regions from the actual screenshot to compare to the comparison region.'
				f'\n#    - Example 1: "{self.command_name} -f ./base.png -region_x1 1000 -region_y1 2000 -region_x2 3000 -region_y2 4000 -comparison_x1 100 -comparison_y1 100 -comparison_x2 200 -comparison_y2 200 "wait_s 5" -d 2000 -asp ./compare.png" -co 2 -s 2 to execute a wait command of 5 seconds and search for the base rectangle from (100, 100) to (200, 200) of base.png in the region (1000, 2000) to (3000, 4000) inside compare.png with cutoff 2 and skipping every other pixel. If not found, wait for 2 seconds and try again.'
				f'\n#    - Example 2: "{self.command_name} --filename ./base.png --region_x1 1000 --region_y1 2000 --region_x2 3000 --region_y2 4000 --comparison_x1 100 --comparison_y1 100 --comparison_x2 200 --comparison_y2 200 --command "wait_s 5" --duration 2000 --actual_screenshot_path ./compare.png" --cutoff 2 --step 2 to execute a wait command of 5 seconds and search for the base rectangle from (100, 100) to (200, 200) of base.png in the region (1000, 2000) to (3000, 4000) inside compare.png with cutoff 2 and skipping every other pixel. If not found, wait for 2 seconds and try again.')

	def compare(self, base_cropped, compare_image, comparison_x1, comparison_y1, comparison_x2, comparison_y2, region_x1, region_y1, region_x2, region_y2, cutoff, step, debug):
		width = comparison_x2 - comparison_x1
		height = comparison_y2 - comparison_y1

		for x_diff in range(0, max(1, region_x2 - region_x1 - width), step):
			start_x = region_x1 + x_diff

			for y_diff in range(0, max(1, region_y2 - region_y1 - height), step):
				start_y = region_y1 + y_diff
				result = self.compare_region(base_cropped, compare_image, start_x, start_y, width, height, cutoff)

				if result:
					return start_x, start_y, start_x + width, start_y + height

		return None
	
	def compare_region(self, base_cropped, compare_image, x, y, width, height, cutoff):
		try:
			compare_image_cropped = compare_image.crop((int(x), int(y), int(x + width), int(y + height)))

			hash0 = imagehash.average_hash(base_cropped)
			hash1 = imagehash.average_hash(compare_image_cropped)

			hash_diff = hash0 - hash1

			if self.app_config.debug and hash_diff < cutoff:
				print(f'hash #1: {hash0}, hash #2: {hash1}, difference: {hash1 - hash0}')
				base_cropped.save(f'{self.parsed_args.filename}-base-cropped.png')
				compare_image_cropped.save(f'{self.parsed_args.actual_screenshot_path}-image-cropped.png')

		except:
			hash_diff = 1000

		return hash_diff < cutoff
