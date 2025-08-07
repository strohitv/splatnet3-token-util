import base64
import os
import re

import requests
import uncurl

from data.app_config import AppConfig


def read_in_chunks(file_object, chunk_size=10 * 1024 * 1024):
	while True:
		data = file_object.read(chunk_size)
		if not data:
			break
		yield data


def try_base64_decode(base64_string):
	try:
		base64.b64decode(base64_string)
		return True
	except Exception as e:
		return False


def search_for_tokens(app_config: AppConfig):
	snapshot_path = os.path.expanduser(os.path.join(app_config.emulator_config.get_snapshot_dir(), app_config.emulator_config.snapshot_name, 'ram.bin'))

	gtoken = None if app_config.token_config.extract_g_token else 'NO_G_TOKEN_EXTRACTED'
	bullet_token = None if app_config.token_config.extract_bullet_token else 'NO_BULLET_TOKEN_EXTRACTED'
	session_token = None if app_config.token_config.extract_session_token else 'skip'

	# analyse snapshot and find values
	print(f'Searching for tokens...')
	with open(snapshot_path, 'rb') as f:
		for piece in read_in_chunks(f):
			# _gtoken search
			if gtoken is None and b'_gtoken=ey' in piece:
				gtoken = ''
				index = piece.index(b'_gtoken=ey') + len(b'_gtoken=')
				while index < len(piece):
					next_piece = piece[index]
					if chr(next_piece) == '\x00':
						break
					gtoken += chr(next_piece)
					index += 1

				if len(gtoken) < 850 or (app_config.token_config.validate_g_token and not re.match(r'^[0-9a-zA-Z.=\-_]+$', gtoken)):
					gtoken = None

				if gtoken is not None:
					# bullet_token request to SplatNet3
					if app_config.token_config.extract_bullet_token:
						try:
							curl_request = app_config.token_config.bullet_token_curl_request.replace('{GTOKEN}', gtoken)
							ctx = uncurl.parse_context(curl_request)
							response = requests.request(ctx.method.upper(), ctx.url, data=ctx.data, cookies=ctx.cookies, headers=ctx.headers, auth=ctx.auth)
							if 200 <= response.status_code < 300:
								bullet_token = response.json()['bulletToken']
							else:
								print('ERROR: did not receive a 2xx response when loading bullet_token with gtoken')
								if app_config.token_config.validate_g_token:
									gtoken = None
						except Exception as e:
							print('ERROR: exception occurred when loading bullet_token with gtoken')
							print(e)
							bullet_token = None
							if app_config.token_config.validate_g_token:
								gtoken = None

			# session_token search
			if session_token is None and b'eyJhbGciOiJIUzI1NiJ9' in piece:
				session_token = ''
				index = piece.index(b'eyJhbGciOiJIUzI1NiJ9')
				while index < len(piece):
					next_piece = piece[index]
					if chr(next_piece) == '\x00':
						break
					session_token += chr(next_piece)
					index += 1

				if len(session_token) < 260 or (app_config.token_config.validate_session_token and not re.match(r'^[0-9a-zA-Z.=\-_]+$', session_token)):
					session_token = None

			if app_config.debug:
				print('next chunk done')

	print('Result:')
	print('- SKIPPED\tgToken' if gtoken == 'NO_G_TOKEN_EXTRACTED' else '- SUCCESS\tgToken' if gtoken is not None else '- FAIL\t\tgToken')
	print('- SKIPPED\tbulletToken' if bullet_token == 'NO_BULLET_TOKEN_EXTRACTED' else '- SUCCESS\tbulletToken' if bullet_token is not None else '- FAIL\t\tbulletToken')
	print('- SKIPPED\tsessionToken' if session_token == 'skip' else '- SUCCESS\tsessionToken' if session_token is not None else '- FAIL\t\tsessionToken')
	print()

	if gtoken is not None:
		gtoken = re.sub(r'[^0-9a-zA-Z.=\-_]+', '*', gtoken)

	if bullet_token is not None:
		bullet_token = re.sub(r'[^0-9a-zA-Z.=\-_]+', '*', bullet_token)

	if session_token is not None:
		session_token = re.sub(r'[^0-9a-zA-Z.=\-_]+', '*', session_token)

	return gtoken, bullet_token, session_token
