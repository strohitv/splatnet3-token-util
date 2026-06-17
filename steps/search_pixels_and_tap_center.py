import argparse
import os.path
import shlex
import subprocess
import time

from PIL import Image
import imagehash

from data.app_config import AppConfig
from steps.execute_while import ExecuteWhile
from utils import script_utils
from utils.step_doc_creator import get_arg_formatter

import logging


class SearchPixelsAndTapCenter:
	def __init__(self, command_name, app_config: AppConfig, all_steps):
		self.logger = logging.getLogger(SearchPixelsAndTapCenter.__name__)

		self.command_name = command_name
		self.app_config = app_config
		self.all_steps = all_steps

		self.execute_command_step = None
		for step_key in self.all_steps:
			if isinstance(self.all_steps[step_key], ExecuteWhile):
				self.execute_command_step = self.all_steps[step_key]
				break

		if self.execute_command_step is None:
			raise Exception('Could not find execute_command_step!')

		self.parsed_args = None

		self.parser = argparse.ArgumentParser(prog=self.command_name,
											  description='Searches a given region on the emulator screen for pixels with a given color and taps the center.',
											  formatter_class=get_arg_formatter(),
											  conflict_handler='resolve')
		self.parser.add_argument('-h', '--help', required=False, help=argparse.SUPPRESS)
		self.parser.add_argument('-actual', '--actual', required=False, default='./screenshots/screenshot.png',
								 help='The file path where the actual screenshot of the emulator should be stored. Default: "./screenshots/screenshot.png"')
		self.parser.add_argument('-x1', '--x1', required=True, help='The X coordinate of the top left corner of the region to search through')
		self.parser.add_argument('-y1', '--y1', required=True, help='The Y coordinate of the top left corner of the region to search through')
		self.parser.add_argument('-x2', '--x2', required=True, help='The X coordinate of the bottom right corner of the region to search through')
		self.parser.add_argument('-y2', '--y2', required=True, help='The Y coordinate of the bottom right corner of the region to search through')
		self.parser.add_argument('-cmd', '--command', required=False, default='wait_ms 1 -silent',
								 help='The command which should be executed if the requested search can not be found. Several commands can be provided by splitting them with a semicolon `;`. Default: "wait_ms 1 -silent"')
		self.parser.add_argument('-d', '--duration', required=False, default=500,
								 help='The frequency of how often this command should check whether the regions match. Default: 500 ms')
		self.parser.add_argument('-ca', '--continue_after', required=False, default=10,
								 help='Optional arg which lets the script continue if the execution is still active after X seconds. Default: 10')
		self.parser.add_argument('-r', '--red', required=True,
								 help='The red value of the pixel.')
		self.parser.add_argument('-g', '--green', required=True,
								 help='The green value of the pixel.')
		self.parser.add_argument('-b', '--blue', required=True,
								 help='The blue value of the pixel.')

		self.parser.add_argument('-ei', '--execute_immediately', required=False,
								 help='Usually, this command checks whether the given template comparison image can be found already BEFORE executing the -cmd arg. If the -ei arg is provided, the order will switch and the -cmd will be executed immediately instead of doing one image comparison first',
								 default=False,
								 action='store_true')

		self.description = self.parser.format_help()
		self.introduction = 'This command scans a given region on the emulator screen and looks if that region contains a given smaller image taken from the template screenshot. If it finds it, it will tap the center of it until something happens. If it cannot find it, it will execute the provided command and restart.\n\nExample: the prime example where this step is being used is searching for the SplatNet3 app icon inside the Nintendo Switch App. It will search for it through all app icons and if it finds it, will open SplatNet3. Otherwise, SplatNet 3 is probably further back in the list, so it will scroll a bit and search again until it finds it.'

	def execute(self, args):
		only_args = shlex.split(args)[1:]
		parsed_args = self.parser.parse_args(only_args)
		self.parsed_args = parsed_args

		execute_immediately = False if parsed_args.execute_immediately is None else parsed_args.execute_immediately

		os.makedirs(os.path.dirname(parsed_args.actual), exist_ok=True)

		start = time.time()

		try:
			offset = None

			while offset is None and (time.time() - start) < int(parsed_args.continue_after):
				if not execute_immediately:
					self.logger.info(
						f'Searching for pixels with color r: {parsed_args.red}, g: {parsed_args.green}, b: {parsed_args.blue} in screenshot "{parsed_args.actual}".')

					subprocess.run(f'"{self.app_config.emulator_config.adb_path}" exec-out screencap -p > {parsed_args.actual}',
								   shell=True,
								   stdout=subprocess.PIPE,
								   stderr=subprocess.PIPE)

					compare_image = Image.open(parsed_args.actual)

					offset = self.compare(
						compare_image,
						int(parsed_args.x1),
						int(parsed_args.y1),
						int(parsed_args.x2),
						int(parsed_args.y2),
						int(parsed_args.red),
						int(parsed_args.green),
						int(parsed_args.blue),
						self.app_config.debug)

					if offset is not None:
						break

				execute_immediately = False

				script_utils.execute(parsed_args.command, self.all_steps)

				time.sleep(int(parsed_args.duration) / 1000.0)

			if offset is None:
				return

			x1, y1, x2, y2 = offset

			tap_x = int((x1 + x2) / 2)
			tap_y = int((y1 + y2) / 2)

			self.logger.info(f'Found at: ({x1}, {y2}), tapping position ({tap_x}, {tap_y}) until something happens')

			script_utils.execute(
				f'{self.execute_command_step.command_name} -mode found -template {parsed_args.actual} -actual {parsed_args.actual}_tapped.png -x1 {x1} -y1 {y1} -x2 {x2} -y2 {y2} -d 2000 -cmd "tap -x {tap_x} -y {tap_y}"',
				self.all_steps)

			end = time.time()
			self.logger.info(f'Finished {self.command_name} after {(end - start):0.1f} seconds.')
		except Exception as e:
			self.logger.info(f'ERROR occurred, stopping.')
			self.logger.info(e)

		self.logger.info('')

	def compare(self, base_image, x1, y1, x2, y2, red, green, blue, debug):
		base_cropped = base_image.crop((int(x1), int(y1), int(x2), int(y2))).convert('RGB')
		pixels = base_cropped.load()

		result_x1, result_y1, result_x2, result_y2 = None, None, None, None

		# step 1: get lowest x
		for x in range(x2 - x1):
			for y in range(y2 - y1):
				if pixels[x, y] == (red, green, blue):
					result_x1 = x
					break

			if result_x1 is not None:
				break

		if result_x1 is None:
			return None

		# step 2: get lowest y
		for y in range(y2 - y1):
			for x in range(x2 - x1):
				if pixels[x, y] == (red, green, blue):
					result_y1 = y
					break

			if result_y1 is not None:
				break

		# step 3: get highest x
		for temp_x in range(x2 - x1):
			x = x2 - x1 - temp_x - 1
			for y in range(y2 - y1):
				if pixels[x, y] == (red, green, blue):
					result_x2 = x
					break

			if result_x2 is not None:
				break

		# step 4: get highest x
		for temp_y in range(y2 - y1):
			y = y2 - y1 - temp_y - 1
			for x in range(x2 - x1):
				if pixels[x, y] == (red, green, blue):
					result_y2 = y
					break

			if result_y2 is not None:
				break

		return x1 + result_x1, y1 + result_y1, x1 + result_x2, y1 + result_y2
