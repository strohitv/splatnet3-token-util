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


class SearchAndTapCenter:
	def __init__(self, command_name, app_config: AppConfig, all_steps):
		self.logger = logging.getLogger(SearchAndTapCenter.__name__)

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
											  description='Searches a given region on the emulator screen to contain a (smaller) region from the template screenshot provided. If it finds it, it will tap the center of it. Otherwise it will execute the provided command and search again',
											  formatter_class=get_arg_formatter(),
											  conflict_handler='resolve')
		self.parser.add_argument('-h', '--help', required=False, help=argparse.SUPPRESS)
		self.parser.add_argument('-template', '--template', required=True, help='The file path of the template screenshot which will be used for the comparison')
		self.parser.add_argument('-actual', '--actual', required=False, default='./screenshots/screenshot.png',
								 help='The file path where the actual screenshot of the emulator should be stored. Default: "./screenshots/screenshot.png"')
		self.parser.add_argument('-region_x1', '--region_x1', required=True, help='The X coordinate of the top left corner of the region to search through')
		self.parser.add_argument('-region_y1', '--region_y1', required=True, help='The Y coordinate of the top left corner of the region to search through')
		self.parser.add_argument('-region_x2', '--region_x2', required=True, help='The X coordinate of the bottom right corner of the region to search through')
		self.parser.add_argument('-region_y2', '--region_y2', required=True, help='The Y coordinate of the bottom right corner of the region to search through')
		self.parser.add_argument('-comparison_x1', '--comparison_x1', required=True,
								 help='The X coordinate of the top left corner of the region from the template screenshot which should be searched for')
		self.parser.add_argument('-comparison_y1', '--comparison_y1', required=True,
								 help='The Y coordinate of the top left corner of the region from the template screenshot which should be searched for')
		self.parser.add_argument('-comparison_x2', '--comparison_x2', required=True,
								 help='The X coordinate of the bottom right corner of the region from the template screenshot which should be searched for')
		self.parser.add_argument('-comparison_y2', '--comparison_y2', required=True,
								 help='The Y coordinate of the bottom right corner of the region from the template screenshot which should be searched for')
		self.parser.add_argument('-cmd', '--command', required=True,
								 help='The command which should be executed if the requested search can not be found. Several commands can be provided by splitting them with a semicolon `;`')
		self.parser.add_argument('-d', '--duration', required=False, default=500,
								 help='The frequency of how often this command should check whether the regions match. Default: 500 ms')
		self.parser.add_argument('-co', '--cutoff', required=False, default=5,
								 help='The cutoff for the comparison. This value decides how similar the regions must be to be considered equal. Lower values mean stricter comparison, higher values will match less similar screenshots. Default: 5')
		self.parser.add_argument('-step', '--step', required=False, default=1,
								 help='Decides how many pixels the region should be moved. Higher values are faster but a smaller part of the region is being screened and the target region could be missed for that reason. Default: 1 => search every possible position in the provided screen region')
		self.parser.add_argument('-h_step', '--h_step', required=False,
								 help='Decides how many pixels the region should be moved ONLY HORIZONTALLY. This value overrides the -step parameter for horizontal steps. Higher values are faster but a smaller part of the region is being screened and the target region could be missed for that reason. Default: 1 => search every possible position in the provided screen region')
		self.parser.add_argument('-v_step', '--v_step', required=False,
								 help='Decides how many pixels the region should be moved ONLY VERTICALLY. This value overrides the -step parameter for vertical steps. Higher values are faster but a smaller part of the region is being screened and the target region could be missed for that reason. Default: 1 => search every possible position in the provided screen region')

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

		os.makedirs(os.path.dirname(parsed_args.template), exist_ok=True)
		os.makedirs(os.path.dirname(parsed_args.actual), exist_ok=True)

		h_step = v_step = parsed_args.step

		if parsed_args.h_step is not None:
			h_step = parsed_args.h_step

		if parsed_args.v_step is not None:
			v_step = parsed_args.v_step

		start = time.time()

		try:
			base_image = Image.open(parsed_args.template)
			base_cropped = base_image.crop(
				(int(parsed_args.comparison_x1), int(parsed_args.comparison_y1), int(parsed_args.comparison_x2), int(parsed_args.comparison_y2)))

			while True:
				if not execute_immediately:
					self.logger.info(
						f'Searching for image from base screenshot "{parsed_args.template}" in screenshot "{parsed_args.actual}" with cutoff {parsed_args.cutoff}.')
					subprocess.run(f'{self.app_config.emulator_config.adb_path} exec-out screencap -p > {parsed_args.actual}',
								   shell=True,
								   stdout=subprocess.PIPE,
								   stderr=subprocess.PIPE)

					compare_image = Image.open(parsed_args.actual)

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
						int(h_step),
						int(v_step),
						self.app_config.debug)

					if result is not None:
						break

				execute_immediately = False

				script_utils.execute(parsed_args.command, self.all_steps)

				time.sleep(int(parsed_args.duration) / 1000.0)

			x1, y1, x2, y2 = result

			tap_x = int((x1 + x2) / 2)
			tap_y = int((y1 + y2) / 2)

			self.logger.info(f'Found at: ({x1}, {y2}), tapping position ({tap_x}, {tap_y}) until something happens')

			script_utils.execute(
				f'{self.execute_command_step.command_name} -mode found -template {parsed_args.template} -actual {parsed_args.actual}_tapped.png -x1 {x1} -y1 {y1} -x2 {x2} -y2 {y2} -d 500 -cmd "tap -x {tap_x} -y {tap_y}"',
				self.all_steps)

			end = time.time()
			self.logger.info(f'Finished {self.command_name} after {(end - start):0.1f} seconds.')
		except Exception as e:
			self.logger.info(f'ERROR occured, stopping.')
			self.logger.info(e)

	def compare(self, base_cropped, compare_image, comparison_x1, comparison_y1, comparison_x2, comparison_y2, region_x1, region_y1, region_x2, region_y2, cutoff, h_step,
				v_step,
				debug):
		width = comparison_x2 - comparison_x1
		height = comparison_y2 - comparison_y1

		for x_diff in range(0, max(1, region_x2 - region_x1 - width), max(1, h_step)):
			start_x = region_x1 + x_diff

			for y_diff in range(0, max(1, region_y2 - region_y1 - height), max(1, v_step)):
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
				self.logger.info(f'hash #1: {hash0}, hash #2: {hash1}, difference: {hash1 - hash0}')
				base_cropped.save(f'{self.parsed_args.template}-base-cropped.png')
				compare_image_cropped.save(f'{self.parsed_args.actual}-image-cropped.png')

		except:
			hash_diff = 1000

		return hash_diff < cutoff
