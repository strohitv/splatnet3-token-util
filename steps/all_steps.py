from steps.block_until_screenshot_region_matches import BlockUntilScreenshotRegionMatches
from steps.echo import Echo
from steps.long_press_power_button import LongPressPowerButton
from steps.swipe import Swipe
from steps.tap import Tap
from steps.wait_ms import WaitMS
from steps.wait_s import WaitS


def get_steps(config):
	steps = {
		'block_until_screenshot_region_matches': BlockUntilScreenshotRegionMatches('block_until_screenshot_region_matches', config),
		'echo': Echo('echo', config),
		'long_press_power_button': LongPressPowerButton('long_press_power_button', config),
		'swipe': Swipe('swipe', config),
		'tap': Tap('tap', config),
		'wait_s': WaitS('wait_s', config),
		'wait_ms': WaitMS('wait_ms', config)
	}

	return steps
