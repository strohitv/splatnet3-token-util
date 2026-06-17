import argparse
import io
import pathlib
import shlex
import subprocess
import time
from time import sleep
from typing import Tuple

from PIL import Image

from data.app_config import AppConfig
from steps.search_and_tap_center import SearchAndTapCenter
from steps.search_pixels_and_tap_center import SearchPixelsAndTapCenter
from utils import script_utils
from utils.step_doc_creator import get_arg_formatter

import logging


class OpenSplatNet3:
	def __init__(self, command_name, app_config: AppConfig, all_steps):
		self.logger = logging.getLogger(OpenSplatNet3.__name__)

		self.command_name = command_name
		self.app_config = app_config
		self.all_steps = all_steps

		self.search_pixels_and_tap_center_step = None
		for step_key in self.all_steps:
			if isinstance(self.all_steps[step_key], SearchPixelsAndTapCenter):
				self.search_pixels_and_tap_center_step = self.all_steps[step_key]
				break

		if self.search_pixels_and_tap_center_step is None:
			raise Exception('Could not find search_pixels_and_tap_center_step!')

		self.parser = argparse.ArgumentParser(prog=self.command_name,
											  description='Opens the SplatNet3 app inside the Nintendo Switch App immediately and waits until a pixel with a specific color is found for a given ratio.',
											  formatter_class=get_arg_formatter(),
											  conflict_handler='resolve')
		self.parser.add_argument('-h', '--help', required=False, help=argparse.SUPPRESS)
		self.parser.add_argument('--max-attempts', required=False, default=3,
								 help='How often the step should attempt to open SplatNet3 before giving up. Default: 3')
		self.parser.add_argument('--max-wait-secs', required=False, default=6000,
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
		self.introduction = 'This command attempts to open the Nintendo Switch App and load SplatNet3 afterwards. It is also able to update the NSA app if required as well as handling the "About Sending Usage Data" popup in the app.'

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

			subprocess.run(f'"{self.app_config.emulator_config.adb_path}" shell am start https://s.nintendo.com/av5ja-lp1/znca/game/4834290508791808',
						   shell=True,
						   stdout=subprocess.PIPE,
						   stderr=subprocess.PIPE)

			start_time = time.time()

			while not found and time.time() - start_time < int(parsed_args.max_wait_secs):
				time.sleep(int(parsed_args.duration) / 1000.0)

				# "About Sending Usage Data" popup
				script_utils.execute(
					f'{self.search_pixels_and_tap_center_step.command_name} -x1 30 -y1 1930 -x2 580 -y2 2130 -r 2 -g 102 -b 216 -actual "./screenshots/actual_data_usage_popup.png" -ca 2',
					self.all_steps)

				subprocess.run(f'"{self.app_config.emulator_config.adb_path}" exec-out screencap -p > "{parsed_args.actual}"',
							   shell=True,
							   stdout=subprocess.PIPE,
							   stderr=subprocess.PIPE)

				full_screenshot = Image.open(parsed_args.actual)
				self.run_update_loop_if_necessary(full_screenshot)
				cropped_screenshot = full_screenshot.crop((int(parsed_args.x1), int(parsed_args.y1), int(parsed_args.x2), int(parsed_args.y2)))

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

	def run_update_loop_if_necessary(self, full_screenshot):
		all_pixels = full_screenshot.convert("RGBA").getdata()

		total_pixels = len(all_pixels)
		found_darkred_pixels = 0

		pixel: Tuple[int, int, int, int]

		for pixel in all_pixels:
			if pixel[0] == 92 and pixel[1] == 0 and pixel[2] == 7:
				found_darkred_pixels += 1

			if found_darkred_pixels > total_pixels / 2:
				break

		if found_darkred_pixels > total_pixels / 2:
			update_start_time = time.time()
			self.logger.info(f'NSA UPDATE DETECTED')
			self.logger.info(f'')
			self.logger.info(f'Update NSA')
			self.logger.info(f'##########')
			self.logger.info(f'')

			subprocess.run(f'"{self.app_config.emulator_config.adb_path}" shell am start market://details?id=com.nintendo.znca',
						   shell=True,
						   stdout=subprocess.PIPE,
						   stderr=subprocess.PIPE)

			previous_version = self.extract_version()
			self.logger.info(f'previous version: {previous_version}')

			new_version = previous_version

			script_utils.execute(
				f'{self.search_pixels_and_tap_center_step.command_name} -x1 500 -y1 550 -x2 1050 -y2 750 -r 11 -g 87 -b 208 -actual "./screenshots/actual_play_store_nsa.png"',
				self.all_steps)

			while new_version == previous_version:
				sleep(3)
				new_version = self.extract_version()

			self.logger.info(f'updated NSA in {time.time() - update_start_time:.1f} seconds')
			self.logger.info(f'updated version: {new_version}')
			self.logger.info(f'waiting for 3 seconds for the changes to take effect...')

			sleep(3)

			self.logger.info(f'closing Play Store...')
			subprocess.run(f'"{self.app_config.emulator_config.adb_path}" shell am force-stop com.android.vending',
						   shell=True,
						   stdout=subprocess.PIPE,
						   stderr=subprocess.PIPE)

			self.logger.info(f'closing NSA...')
			script_utils.execute(f'close_nsa', self.all_steps)

			self.logger.info(f'reopening NSA...')
			subprocess.run(f'"{self.app_config.emulator_config.adb_path}" shell am start https://s.nintendo.com/av5ja-lp1/znca/game/4834290508791808',
						   shell=True,
						   stdout=subprocess.PIPE,
						   stderr=subprocess.PIPE)
			self.logger.info(f'SUCCESS! NSA version update finished!')

	def extract_version(self):
		version = '0.0.0'

		proc = subprocess.Popen(f'"{self.app_config.emulator_config.adb_path}" shell dumpsys package com.nintendo.znca',
								shell=True,
								stdout=subprocess.PIPE,
								stderr=subprocess.STDOUT)

		for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
			if not line:
				break

			if 'versionName' in line:
				version = line.split('=')[1].strip()
				break

		return version
