import argparse
import shlex
import time

from data.config import Config


class WaitS:
	def __init__(self, command_name, config: Config):
		self.command_name = command_name
		self.config = config

	def execute(self, args):
		only_args = shlex.split(args)[1:]

		parser = argparse.ArgumentParser()
		parser.add_argument('seconds', default=5)
		parsed_args = parser.parse_args(only_args)

		print(f'Waiting for {parsed_args.seconds} seconds.')
		time.sleep(float(parsed_args.seconds))

	def description(self):
		return ('waits for a given amount of seconds.'
				f'\n#    - Use: "{self.command_name} [NUMBER]" to wait for [NUMBER] seconds. If no number is given, it will wait for 5 seconds.'
				f'\n#    - Example: "{self.command_name} 10" to wait 10 seconds')
