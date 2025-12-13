import argparse
import shlex
import subprocess
import time
from typing import Tuple

from PIL import Image

from data.app_config import AppConfig
from utils.step_doc_creator import get_arg_formatter

import logging


class OpenSplatNet3:
	def __init__(self, command_name, app_config: AppConfig):
		self.logger = logging.getLogger(OpenSplatNet3.__name__)

		self.command_name = command_name
		self.app_config = app_config

		self.parser = argparse.ArgumentParser(prog=self.command_name,
											  description='Opens the SplatNet3 app inside the Nintendo Switch App immediately and waits until a pixel with a specific color is found for a given ratio.',
											  formatter_class=get_arg_formatter(),
											  conflict_handler='resolve')
		self.parser.add_argument('-h', '--help', required=False, help=argparse.SUPPRESS)
		self.parser.add_argument('--max-attempts', required=False, default=3,
								 help='How often the step should attempt to open SplatNet3 before giving up. Default: 3')
		self.parser.add_argument('--max-wait-secs', required=False, default=60,
								 help='How long the step should wait for SplatNet3 to load before it considers the attempt failed. Default: 45 seconds')
		self.parser.add_argument('-d', '--duration', required=False, default=500,
								 help='The frequency of how often this command should check whether SplatNet3 is open. Default: 500 ms')

		self.parser.add_argument('-c', '--color', required=False, default='#292E35',
								 help='The color which should be searched as hex color. Default: "#292E35"')
		self.parser.add_argument('-actual', '--actual', required=False, default='./screenshots/actual-nsa-opened.png',
								 help='The file path where the actual screenshot of the emulator should be stored. Default: "./screenshots/actual-nsa-opened.png"')
		self.parser.add_argument('-lb', '--lower-bound', required=False, default=0.3,
								 help='The lower bound of the ratio of pixels in the area which must have the given color. Default: 0.3')
		self.parser.add_argument('-ub', '--upper-bound', required=False, default=0.7,
								 help='The upper bound of the ratio of pixels in the area which must have the given color. Default: 0.7')
		self.parser.add_argument('-x1', '--x1', required=False, default=0,
								 help='The X coordinate of the upper left corner of the area which should be checked. Default: 0')
		self.parser.add_argument('-y1', '--y1', required=False, default=1000,
								 help='The Y coordinate of the upper left corner of the area which should be checked. Default: 1000')
		self.parser.add_argument('-x2', '--x2', required=False, default=1000,
								 help='The X coordinate of the lower right corner of the area which should be checked. Default: 1000')
		self.parser.add_argument('-y2', '--y2', required=False, default=1500,
								 help='The Y coordinate of the lower right corner of the area which should be checked. Default: 1500')

		self.description = self.parser.format_help()
		self.introduction = 'This command attempts to open the Nintendo Switch App and load SplatNet3 afterwards.'

	def execute(self, args):
		only_args = shlex.split(args)[1:]
		parsed_args = self.parser.parse_args(only_args)

		found = False

		unprefixed_hex = parsed_args.color.replace('#', '')
		expected_r = int(unprefixed_hex[0:2], 16)
		expected_g = int(unprefixed_hex[2:4], 16)
		expected_b = int(unprefixed_hex[4:6], 16)

		bounding_box_pixels = (int(parsed_args.x2) - int(parsed_args.x1)) * (int(parsed_args.y2) - int(parsed_args.y1))
		lower_bound = bounding_box_pixels * float(parsed_args.lower_bound)
		upper_bound = bounding_box_pixels * float(parsed_args.upper_bound)

		for i in range(int(parsed_args.max_attempts)):
			self.logger.info(f'Open SplatNet3 app - attempt {i + 1}/{parsed_args.max_attempts}')

			subprocess.run(f'{self.app_config.emulator_config.adb_path} shell am start https://s.nintendo.com/av5ja-lp1/znca/game/4834290508791808',
						   shell=True,
						   stdout=subprocess.PIPE,
						   stderr=subprocess.PIPE)

			start_time = time.time()

			while not found and time.time() - start_time < int(parsed_args.max_wait_secs):
				time.sleep(int(parsed_args.duration) / 1000.0)

				subprocess.run(f'{self.app_config.emulator_config.adb_path} exec-out screencap -p > {parsed_args.actual}',
							   shell=True,
							   stdout=subprocess.PIPE,
							   stderr=subprocess.PIPE)

				cropped_screenshot = Image.open(parsed_args.actual).crop((int(parsed_args.x1), int(parsed_args.y1), int(parsed_args.x2), int(parsed_args.y2)))

				all_pixels = cropped_screenshot.convert("RGBA").getdata()
				total_found = 0

				pixel: Tuple[int, int, int, int]
				for pixel in all_pixels:
					if pixel[0] == expected_r and pixel[1] == expected_g and pixel[2] == expected_b:
						total_found += 1

				found = lower_bound <= total_found <= upper_bound

				if self.app_config.debug:
					self.logger.info(f'Result of the pixel search: found = {found}')

			if not found:
				self.logger.info(f'Opening SplatNet3 - attempt {i + 1}/{parsed_args.max_attempts} failed.')
			else:
				self.logger.info(f'Opening SplatNet3 - attempt {i + 1}/{parsed_args.max_attempts} success - done after {time.time() - start_time:.1f} seconds.')
				break

		if not found:
			raise Exception(f'Could not open SplatNet3 app in {parsed_args.max_attempts} attempts.')
