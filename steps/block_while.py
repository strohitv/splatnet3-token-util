import argparse
import os.path
import shlex
import subprocess
import time

from PIL import Image
import imagehash

from data.app_config import AppConfig
from utils.step_doc_creator import get_arg_formatter

import logging


class BlockWhile:
	def __init__(self, command_name, app_config: AppConfig):
		self.logger = logging.getLogger(BlockWhile.__name__)

		self.command_name = command_name
		self.app_config = app_config

		self.parser = argparse.ArgumentParser(prog=self.command_name,
											  description='Blocks the execution of the script until a specific region on the screen (between points (X1, Y1) to (X2, Y2)) looks similar to the same region on a given template',
											  formatter_class=get_arg_formatter(),
											  conflict_handler='resolve')
		self.parser.add_argument('-h', '--help', required=False, help=argparse.SUPPRESS)
		self.parser.add_argument('-mode', '--mode', required=True, choices=['found', 'not-found'],
								 help='Decides whether this step should block as long as the region can be found or not, `found` = block as long as found, `not-found` = block until found')
		self.parser.add_argument('-template', '--template', required=True, help='The file path of the template screenshot which will be used for the comparison')
		self.parser.add_argument('-actual', '--actual', required=False, default='./screenshots/screenshot.png',
								 help='The file path where the actual screenshot of the emulator should be stored. Default: "./screenshots/screenshot.png"')
		self.parser.add_argument('-x1', '--x1', required=True, help='The X coordinate of the top left corner of the region to compare')
		self.parser.add_argument('-y1', '--y1', required=True, help='The Y coordinate of the top left corner of the region to compare')
		self.parser.add_argument('-x2', '--x2', required=True, help='The X coordinate of the bottom right corner of the region to compare')
		self.parser.add_argument('-y2', '--y2', required=True, help='The Y coordinate of the bottom right corner of the region to compare')
		self.parser.add_argument('-d', '--duration', required=False, default=1000,
								 help='The frequency of how often this command should check whether the regions match. Default: 1000 ms')
		self.parser.add_argument('-co', '--cutoff', required=False, default=5,
								 help='The cutoff for the comparison. This value decides how similar the regions must be to be considered equal. Lower values mean stricter comparison, higher values will match less similar screenshots. Default: 5')

		self.description = self.parser.format_help()
		self.introduction = 'This command blocks the execution of the script until a specific region of the emulator screen looks similar to the same region in a given template file. Its biggest use case is to optimize load times, for example waiting for an app to become visible on the screen after having tapped the app icon.'

	def execute(self, args):
		only_args = shlex.split(args)[1:]
		parsed_args = self.parser.parse_args(only_args)

		os.makedirs(os.path.dirname(parsed_args.template), exist_ok=True)
		os.makedirs(os.path.dirname(parsed_args.actual), exist_ok=True)

		start = time.time()

		expect_found = parsed_args.mode == 'found'
		self.logger.info(f'Blocking as long as region can {"" if expect_found else "not "}be found')

		fulfilled = False

		while not fulfilled:
			time.sleep(int(parsed_args.duration) / 1000.0)

			self.logger.info(f'Comparing screenshot "{parsed_args.actual}" to base screenshot "{parsed_args.template}" with cutoff {parsed_args.cutoff}.')
			subprocess.run(f'{self.app_config.emulator_config.adb_path} exec-out screencap -p > {parsed_args.actual}',
						   shell=True,
						   stdout=subprocess.PIPE,
						   stderr=subprocess.PIPE)

			fulfilled = self.compare(parsed_args.template, parsed_args.actual, parsed_args.x1, parsed_args.y1, parsed_args.x2, parsed_args.y2,
									 parsed_args.cutoff, expect_found, self.app_config.debug)

		end = time.time()
		if expect_found:
			self.logger.info(f'Not found anymore after {(end - start):0.1f} seconds.')
		else:
			self.logger.info(f'Found after {(end - start):0.1f} seconds.')

	def compare(self, template, actual, x1, y1, x2, y2, cutoff, expect_found, debug):
		try:
			base_image = Image.open(template)
			compare_image = Image.open(actual)

			base_cropped = base_image.crop((int(x1), int(y1), int(x2), int(y2)))
			compare_image_cropped = compare_image.crop((int(x1), int(y1), int(x2), int(y2)))

			hash0 = imagehash.average_hash(base_cropped)
			hash1 = imagehash.average_hash(compare_image_cropped)

			if self.app_config.debug:
				self.logger.info(f'hash #1: {hash0}, hash #2: {hash1}, difference: {hash1 - hash0}')
				base_cropped.save(f'{template}-cropped.png')
				compare_image_cropped.save(f'{actual}-cropped.png')

			hash_diff = hash0 - hash1
		except:
			hash_diff = 1000

		if expect_found:
			return hash_diff > int(cutoff)
		else:
			return hash_diff < int(cutoff)
