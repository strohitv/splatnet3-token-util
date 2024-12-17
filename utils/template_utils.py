def create_target_file(config, g_token, bullet_token, session_token):
	print(f'Reading the template file "{config.template_path}".')
	with open(config.template_path, 'r') as template:
		print(f'Creating target file content from template.')
		final_file = template.read()
		final_file = final_file.replace('{GTOKEN}', g_token)
		final_file = final_file.replace('{BULLETTOKEN}', bullet_token)
		final_file = final_file.replace('{SESSIONTOKEN}', session_token)

		print(f'Creating the target file "{config.target_path}".')
		with open(config.target_path, 'w') as target_file:
			print(f'Writing content.')
			target_file.write(final_file)
			print('Content written successfully.')
			print()
