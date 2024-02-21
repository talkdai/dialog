# Plugins and Addons ‐ Extending Dialog

## Extending the default LLM

This project uses as a base LLM implementation the class ChatOpenAI from Langchain. If you want to extend the default LLM, you can create a new class that inherits from AbstractLLM (located in the file src/llm/abstract_llm.py) and override the methods you want to change and add behavior.

To use your custom LLM, just add the environment variable LLM_CLASS to your .env file/environment variables:

```
LLM_CLASS=plugins.my_llm.MyLLMClass
```

If you don't implement your own LLM model or your model doesn't inherit the class from AbstractLLM, the default LLM will be used by default.

## Adding extra routes to the project

The project is extensible and can support extra endpoints. To add new endpoints, you need to create a package inside the `src/plugins` folder and, inside the new package folder, add the following file:

- `__init__.py`: the default package initializer from Python (this file can be empty), but we recommend you to create the router here.

Inside the `__init__.py` file, you need to create a FastAPI router that will be loaded into the app dynamically:

```python
from fastapi import APIRouter

router = APIRouter()

# add your routes here
```

The variable that instantiates APIRouter must be called **router**.

After creating the plugin, to run it, add the environment variable PLUGINS to your .env file:

```bash
PLUGINS=plugins.your_plugin_name # or PLUGINS=plugins.your_plugin_name.file_name if there is another file to be used as entrypoint
```

### WhatsApp Text to Audio Synthesis

We already made a WhatsApp plugin that converts the LLM processed output from the message an user sent, into an audio file and sends it back to the user.

To use this plugin, you need to clone the [WhatsApp Audio Synth repo](https://github.com/talkdai/whats_audio_synth) inside the plugins folder of this repo and add the following environment variables to your .env file:

```bash
WHATSAPP_API_TOKEN=
WHATSAPP_ACCOUNT_NUMBER=
PLUGINS=plugins.whats_audio_synth.main,
```
