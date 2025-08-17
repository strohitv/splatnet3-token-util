# Notes for developers

This document aims to provide information for developers who intend to use splatnet3-token-util to receive SplatNet3 tokens. It won't go too deep though because there are many different types of applications which could want to use this project.

Integrating splatnet3-token-util with your application should be rather simple. You can run `python main.py` and get the tokens in one of three ways:
1. calling `python main.py -cout` from your application and reading the tokens from stdout after the script has exited with return code 0. This method is probably the easiest one.
2. calling `python main.py` without the `-cout` argument and reading the created result file from the disk. This method has the advantage that the format of the result file can be chosen freely.
3. using a wrapper script which runs your application and waits for some indicator that the tokens need to be refreshed. It then switches to splatnet3-token-util, waits for a positive response and feeds the tokens back to the other application. This is the most complex solution.

1 and 2 mean that you extend your application, which becomes the "host" of splatnet3-token-util. Point 3 requires you to write an additional wrapper script and potentially do a smaller change to your main application if it can't communicate yet that the tokens need to be refreshed.

## 1. Using the stdout to get the token
The easiest way is to run `python main.py -cout`. When this arg is passed, splatnet3-token-util will send the extracted tokens to the stdout in a json format in addition to creating the text file.

Make sure to check for return code 0 before trying to read from stdout. All logs are on stderr so if the return code is not rc 0, nothing will be printed to stdout and your application will block indefinitely, should it not have a timeout.
```json
{"g_token": "{GTOKEN}", "bullet_token": "{BULLETTOKEN}", "session_token": "{SESSIONTOKEN}"}
```
Not that it will send the json without line breaks, so reading one line from stdout should be enough to receive the entire json.

## 2. Reading from the created file
If you omit the `-cout` argument and only run `python main.py`, you'll have to read from the created config file. You can freely choose the format of that file, whether it be JSON, XML, YAML, CSV, an INI format or whatever. Just use the following placeholders:
- `{GTOKEN}` will be replaced with the gToken
- `{BULLETTOKEN}` will be replaced with the bulletToken
- `{SESSIONTOKEN}` will be replaced with the sessionToken

As always, wait for the application to exit with return code 0 and read the file from the location set in config.json.

## 3. Using a wrapper script
Last but not least, you could create a wrapper script. Unlike the other two options, this makes your application and splatnet3-token-util "independent partners on the same level" both controlled by the wrapper script. On the other hand, writing a wrapper script requires more work and could potentially require you to still change your main application should it not be able to communicate with the wrapper script. The wrapper script would then use one of the previous 2 methods so it's basically "on top" of the other 2 methods.

An example for a wrapper script is included in this project, it is used to combine s3s and splatnet3-token-util. See [run_s3s.py](./run_s3s.py) for an example on how one could look like. It waits for s3s to exit with a special "tokens are not valid" return code and run splatnet3-token-util in that case. Afterward, it simply boots s3s again. Changes in s3s were required, too, they can be found [here](https://github.com/frozenpandaman/s3s/pull/213/files). Two additional PRs were added for bugs, too ([1](https://github.com/frozenpandaman/s3s/pull/214/files) and [2](https://github.com/frozenpandaman/s3s/pull/215/files)). 
