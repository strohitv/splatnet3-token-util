import json
import sys

from data.app_config import AppConfig

import logging

logger = logging.getLogger(__name__)


def create_target_file(app_config: AppConfig, g_token, bullet_token, session_token, user_agent, web_view_version, na_country, na_language, app_language):
	logger.info(f'Reading the template file "{app_config.run_config.template_path}".')
	with open(app_config.run_config.template_path, 'r') as template:
		logger.info(f'Creating target file content from template.')
		template_file = template.read()

		if app_config.token_config.validate_target_file_as_json:
			try:
				json.loads(template_file)
			except json.decoder.JSONDecodeError as e:
				logger.info(
					f'\n### Failed to load template file content, it is not a valid JSON file. Please check the template file, it seems to not contain a valid JSON structure. ###')
				# issue caused by user, app is not able to resolve it -> stop here
				sys.exit(2)

		final_file = template_file.replace('{GTOKEN}', g_token)
		final_file = final_file.replace('{BULLETTOKEN}', bullet_token)
		final_file = final_file.replace('{SESSIONTOKEN}', session_token)
		final_file = final_file.replace('{USERAGENT}', user_agent)
		final_file = final_file.replace('{WEBVIEWVERSION}', web_view_version)
		final_file = final_file.replace('{NACOUNTRY}', na_country)
		final_file = final_file.replace('{NALANGUAGE}', na_language)
		final_file = final_file.replace('{APPLANGUAGE}', app_language)

		if app_config.token_config.validate_target_file_as_json:
			try:
				json.loads(final_file)
			except json.decoder.JSONDecodeError as e:
				logger.info(f'\n### Failed to store target file content, it is not a valid JSON file. ###\n')
				# no sys.exit here as we were obviously able to read the template file, thus the issue has to be with the tokens. Try again or stop cause max attempts.
				raise e

		logger.info(f'Creating the target file "{app_config.run_config.target_path}".')
		with open(app_config.run_config.target_path, 'w') as target_file:
			logger.info(f'Writing content.')
			target_file.write(final_file)
			target_file.flush()
			logger.info('Content written successfully.')
			logger.info('')
