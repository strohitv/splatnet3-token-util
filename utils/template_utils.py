import json
import sys


def create_target_file(app_config, g_token, bullet_token, session_token):
	print(f'Reading the template file "{app_config.template_path}".')
	with open(app_config.template_path, 'r') as template:
		print(f'Creating target file content from template.')
		template_file = template.read()

		if app_config.validate_target_file_as_json:
			try:
				json.loads(template_file)
			except json.decoder.JSONDecodeError as e:
				print(f'\n### Failed to load template file content, it is not a valid JSON file. Please check the template file, it seems to not contain a valid JSON structure. ###')
				# issue caused by user, app is not able to resolve it -> stop here
				sys.exit(2)

		final_file = template_file.replace('{GTOKEN}', g_token).replace('{BULLETTOKEN}', bullet_token).replace('{SESSIONTOKEN}', session_token)

		if app_config.validate_target_file_as_json:
			try:
				json.loads(final_file)
			except json.decoder.JSONDecodeError as e:
				print(f'\n### Failed to store target file content, it is not a valid JSON file. ###\n')
				# no sys.exit here as we were obviously able to read the template file, thus the issue has to be with the tokens. Try again or stop cause max attempts.
				raise e

		print(f'Creating the target file "{app_config.target_path}".')
		with open(app_config.target_path, 'w') as target_file:
			print(f'Writing content.')
			target_file.write(final_file)
			print('Content written successfully.')
			print()
