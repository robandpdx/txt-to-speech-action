# txt-to-speech-action

Composite GitHub Action that turns batches of plain-text podcast scripts into Azure AI Speech audio. The action installs the Azure Speech SDK, loads the project-specific `speech_library`, and generates host and guest tracks for every `.txt` file beneath each speaker directory.

> The repository already vendors a minimal `speech_library` package so the action can import it without extra setup. Replace the stub implementation in [speech_library/library.py](speech_library/library.py) with your actual synthesis code and ensure your scripts live under [scripts/](scripts).

## How It Works
- Sets up Python 3.11 inside the workflow runner.
- Installs `azure-cognitiveservices-speech` (>= 1.36.0).
- Imports `speech_library` and walks `SCRIPTS_ROOT / "host"` and `SCRIPTS_ROOT / "guest"`.
- Calls `synthesize_text_file()` for every discovered text script and prints the resulting audio path.

Your repository must provide the `speech_library` package plus a `scripts/host` and `scripts/guest` tree (or whatever `SCRIPTS_ROOT` resolves to) containing `.txt` files that match the voices you want synthesized.

## Inputs

| Name | Required | Default | Description |
| ---- | -------- | ------- | ----------- |
| `speech_key` | ✅ | — | Azure Speech resource key used for authentication. |
| `endpoint_url` | ✅ | — | Full Azure Speech endpoint URL, e.g. `https://<region>.tts.speech.microsoft.com/cognitiveservices/v1`. |
| `host_voice` | ❌ | `en-US-Ava:DragonHDLatestNeural` | Neural voice for scripts under `host/`. |
| `guest_voice` | ❌ | `en-US-Andrew:DragonHDLatestNeural` | Neural voice for scripts under `guest/`. |

> **Note**: Voice names must exist in the Azure Speech region tied to your endpoint.

## Usage Examples

### Basic workflow

```yaml
name: Build Speech Library

on:
	workflow_dispatch:

jobs:
	synthesize:
		runs-on: ubuntu-latest
		steps:
			- name: Check out scripts and library
				uses: actions/checkout@v4

			- name: Generate podcast voices
				uses: robandpdx/txt-to-speech-action@main
				with:
					speech_key: ${{ secrets.AZURE_SPEECH_KEY }}
					endpoint_url: ${{ secrets.AZURE_SPEECH_ENDPOINT }}
					host_voice: en-US-AvaMultilingualNeural
					guest_voice: en-US-GuyNeural
```

### Combining with artifact upload

```yaml
jobs:
	synthesize:
		runs-on: ubuntu-latest
		steps:
			- uses: actions/checkout@v4

			- name: Generate audio
				id: generate
				uses: robandpdx/txt-to-speech-action@main
				with:
					speech_key: ${{ secrets.AZURE_SPEECH_KEY }}
					endpoint_url: ${{ secrets.AZURE_SPEECH_ENDPOINT }}

			- name: Upload WAV files
				uses: actions/upload-artifact@v4
				with:
					name: speech-audio
					path: output/**/*.wav
```

## Troubleshooting
- **Missing module `speech_library`**: ensure your repository contains the package and that Python can import it (e.g., root-level `speech_library/__init__.py`).
- **`FileNotFoundError` for `host` or `guest` scripts**: verify that the `SCRIPTS_ROOT` directories exist and include `.txt` files before running the action.
- **Authentication errors**: confirm `speech_key` and `endpoint_url` belong to the same Azure Speech resource and were provided as workflow secrets.

## Related Files
- Action implementation: [action.yml](action.yml)