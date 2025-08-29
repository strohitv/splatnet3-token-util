import base64
import os
import re
from urllib.parse import urlparse, parse_qs

import requests
import uncurl

from data.app_config import AppConfig

import logging

from utils.splatnet3_utils import download_splatnet3_main_js

logger = logging.getLogger(__name__)


def read_in_chunks(file_object, chunk_size=50 * 1024):
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


def search_for_web_view_version_in_js(content):
	if b'"revision_info_not_set"' in content:
		index = content.index(b'"revision_info_not_set"')
		i = index
		quotes_indices = []
		while i > index - 100 and len(quotes_indices) < 2:
			i -= 1
			if chr(content[i]) == '"':
				quotes_indices.append(i)

		i = index
		backtick_indices = []
		while i < index + 100 and len(backtick_indices) < 3:
			i += 1
			if chr(content[i]) == '`':
				backtick_indices.append(i)

		if len(quotes_indices) == 2 and len(backtick_indices) == 3:
			version = ''
			revision = ''
			for i in range(backtick_indices[1] + 1, backtick_indices[2]):
				character = chr(content[i])
				if character == '-':
					break
				version += character

			for i in range(quotes_indices[1] + 1, quotes_indices[0]):
				revision += chr(content[i])

			web_view_version = f'{version}-{revision[:8]}'

			result = re.search("^[1-9]?[0-9]\\.[0-9]\\.[0-9]-[a-z0-9]{8}$", web_view_version)
			if result is None:
				web_view_version = None

			return web_view_version

	return None


def search_for_tokens(app_config: AppConfig):
	snapshot_path = os.path.expanduser(os.path.join(app_config.emulator_config.get_snapshot_dir(), app_config.emulator_config.snapshot_name, 'ram.bin'))

	g_token = None if app_config.token_config.extract_g_token else 'NO_G_TOKEN_EXTRACTED'
	bullet_token = None if app_config.token_config.extract_bullet_token else 'NO_BULLET_TOKEN_EXTRACTED'
	session_token = None if app_config.token_config.extract_session_token else 'skip'

	web_view_version = None
	na_country = None
	na_language = None
	app_language = None
	user_agent = None

	logger.info(f'')
	logger.info(f'')
	logger.info('################')
	logger.info('TOKEN EXTRACTION')
	logger.info('################')
	logger.info(f'')
	logger.info(f'Searching for metadata...')
	with open(snapshot_path, 'rb') as f:
		for piece in read_in_chunks(f):
			if web_view_version is None and b'x-web-view-ver' in piece:
				web_view_version = ''
				index = piece.index(b'x-web-view-ver') + len(b'x-web-view-ver')
				while index < len(piece) and piece[index] < 48:
					index += 1

				while index < len(piece):
					next_piece = piece[index]
					if chr(next_piece) == '\x00':
						break
					web_view_version += chr(next_piece)
					index += 1

				result = re.search("^[1-9]?[0-9]\\.[0-9]\\.[0-9]-[a-z0-9]{8}$", web_view_version)
				if result is None:
					web_view_version = None

			if web_view_version is None:
				web_view_version = search_for_web_view_version_in_js(piece)

			if user_agent is None and b'Mozilla/5.0' in piece:
				user_agent = ''
				index = piece.index(b'Mozilla/5.0')
				while index < len(piece):
					next_piece = piece[index]
					if chr(next_piece) == '\x00':
						break
					user_agent += chr(next_piece)
					index += 1

				result = re.search("^Mozilla/5.0 \\([^)]+\\) [a-zA-Z]+/[0-9]+(\\.[0-9]+)* \\([^)]+\\)( [a-zA-Z ]+/[0-9]+(\\.[0-9]+)*)*$", user_agent)
				if result is None:
					user_agent = None

			if na_language is None and b'&na_lang=' in piece:
				na_language = ''
				index = piece.index(b'&na_lang=') + len(b'&na_lang=')
				while index < len(piece):
					next_piece = piece[index]
					if chr(next_piece).upper() not in '-ABCDEFGHIJKLMNOPQRSTUVWXYZ':
						break
					na_language += chr(next_piece)
					index += 1

				na_language_valid = re.search("^[a-z]{2}(-[A-Z]{2})?$", na_language)

				if not na_language_valid:
					na_language = None

			if na_country is None and b'&na_country=' in piece:
				na_country = ''
				index = piece.index(b'&na_country=') + len(b'&na_country=')
				while index < len(piece):
					next_piece = piece[index]
					if chr(next_piece).upper() not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
						break
					na_country += chr(next_piece)
					index += 1

				na_country_valid = re.search("^[A-Z]{2}$", na_country)

				if not na_country_valid:
					na_country = None

			if (na_country is None or na_language is None or app_language is None) and b'api.lp1.av5ja.srv.nintendo.net/?lang=' in piece:
				found_url = ''
				index = piece.index(b'api.lp1.av5ja.srv.nintendo.net/?lang=')
				while index < len(piece):
					next_piece = piece[index]
					if chr(next_piece) == '\x00':
						break
					found_url += chr(next_piece)
					index += 1

				try:
					parsed_url = urlparse(found_url)
					query_args = parse_qs(parsed_url.query)
					if 'lang' in query_args:
						app_language_found = query_args['lang'][0]
						app_language_valid = re.search("^[a-z]{2}(-[A-Z]{2})?$", app_language_found)

						if app_language is None:
							if app_language_valid:
								app_language = app_language_found
							else:
								app_language = None

					if 'na_country' in query_args:
						na_country_found = query_args['na_country'][0]
						na_country_valid = re.search("^[A-Z]{2}$", na_country_found)

						if na_country is None:
							if na_country_valid:
								na_country = na_country_found
							else:
								na_country = None

					if 'na_lang' in query_args:
						na_language_found = query_args['na_lang'][0]
						na_language_valid = re.search("^[a-z]{2}(-[A-Z]{2})?$", na_language_found)

						if na_language is None:
							if na_language_valid:
								na_language = na_language_found
							else:
								na_language = None

				except Exception as e:
					pass

	if not web_view_version:
		logger.info(f'web_view_version not found, searching in main.js as fallback...')
		main_js = download_splatnet3_main_js('https://api.lp1.av5ja.srv.nintendo.net')
		web_view_version = search_for_web_view_version_in_js(main_js)

	if na_country is None and na_language is not None:
		na_country = na_language.split('-')[1]

	logger.info(f'Searching for tokens...')
	with open(snapshot_path, 'rb') as f:
		for piece in read_in_chunks(f):
			# _gtoken search
			if g_token is None and b'_gtoken=ey' in piece:
				g_token = ''
				index = piece.index(b'_gtoken=ey') + len(b'_gtoken=')
				while index < len(piece):
					next_piece = piece[index]
					if chr(next_piece) == '\x00':
						break
					g_token += chr(next_piece)
					index += 1

				if len(g_token) < 850 or (app_config.token_config.validate_g_token and not re.match(r'^[0-9a-zA-Z.=\-_]+$', g_token)):
					g_token = None

				if g_token is not None:
					# bullet_token request to SplatNet3
					if app_config.token_config.extract_bullet_token:
						try:
							curl_request = f"curl 'https://api.lp1.av5ja.srv.nintendo.net/api/bullet_tokens' --compressed -X POST -H 'User-Agent: {user_agent}' -H 'Accept: */*' -H 'Accept-Language: {app_language}' -H 'Accept-Encoding: gzip, deflate, br, zstd' -H 'Referer: https://api.lp1.av5ja.srv.nintendo.net?lang={app_language}&na_country={na_country}&na_lang={na_language}' -H 'content-type: application/json' -H 'x-web-view-ver: {web_view_version}' -H 'Origin: https://api.lp1.av5ja.srv.nintendo.net'  -H 'X-Requested-With: com.nintendo.znca' -H 'x-nacountry: {na_country}' -H 'Cookie: _gtoken={g_token}'"
							ctx = uncurl.parse_context(curl_request)
							response = requests.request(ctx.method.upper(), ctx.url, data=ctx.data, cookies=ctx.cookies, headers=ctx.headers, auth=ctx.auth)
							if 200 <= response.status_code < 300:
								bullet_token = response.json()['bulletToken']
							else:
								logger.info('ERROR: did not receive a 2xx response when loading bullet_token with gtoken')
								if app_config.token_config.validate_g_token:
									g_token = None
						except Exception as e:
							logger.info('ERROR: exception occurred when loading bullet_token with gtoken')
							logger.info(e)
							bullet_token = None
							if app_config.token_config.validate_g_token:
								g_token = None

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
				logger.info('next chunk done')

	logger.info('')
	logger.info('Tokens:')
	logger.info('- SKIPPED\tgToken' if g_token == 'NO_G_TOKEN_EXTRACTED' else '- SUCCESS\tgToken' if g_token is not None else '- FAIL\t\tgToken')
	logger.info(
		'- SKIPPED\tbulletToken' if bullet_token == 'NO_BULLET_TOKEN_EXTRACTED' else '- SUCCESS\tbulletToken' if bullet_token is not None else '- FAIL\t\tbulletToken')
	logger.info('- SKIPPED\tsessionToken' if session_token == 'skip' else '- SUCCESS\tsessionToken' if session_token is not None else '- FAIL\t\tsessionToken')
	logger.info('')
	logger.info('Metadata:')
	logger.info('- SUCCESS\tuserAgent' if user_agent is not None else '- FAIL\t\tuserAgent')
	logger.info('- SUCCESS\twebViewVer' if web_view_version is not None else '- FAIL\t\twebViewVer')
	logger.info('- SUCCESS\tnaCountry' if na_country is not None else '- FAIL\t\tnaCountry')
	logger.info('- SUCCESS\tnaLang' if na_language is not None else '- FAIL\t\tnaLang')
	logger.info('- SUCCESS\tappLang' if app_language is not None else '- FAIL\t\tappLang')
	logger.info('')

	if g_token is not None:
		g_token = re.sub(r'[^0-9a-zA-Z.=\-_]+', '*', g_token)

	if bullet_token is not None:
		bullet_token = re.sub(r'[^0-9a-zA-Z.=\-_]+', '*', bullet_token)

	if session_token is not None:
		session_token = re.sub(r'[^0-9a-zA-Z.=\-_]+', '*', session_token)

	return g_token, bullet_token, session_token, user_agent, web_view_version, na_country, na_language, app_language
