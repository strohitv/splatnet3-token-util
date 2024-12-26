import argparse
import shlex
import time

from data.app_config import AppConfig


class WaitMS:
	def __init__(self, command_name, app_config: AppConfig):
		self.command_name = command_name
		self.app_config = app_config

	def execute(self, args):
		only_args = shlex.split(args)[1:]

		parser = argparse.ArgumentParser()
		parser.add_argument('milliseconds', default=5000)
		parsed_args = parser.parse_args(only_args)

		print(f'Waiting for {parsed_args.milliseconds} milliseconds.')
		time.sleep(int(parsed_args.milliseconds) / 1000.0)

	def description(self):
		return ('waits for a given amount of milliseconds.'
				f'\n#    - Use: "{self.command_name} [NUMBER]" to wait for [NUMBER] ms. If no number is given, it will wait for 5000 ms (= 5 seconds).'
				f'\n#    - Example: "{self.command_name} 500" to wait 500 ms (0.5 seconds)')
