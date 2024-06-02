# Extending Models through our Class API

In this project, we have a class-based API that allows you to extend the default LLM and add extra methods to your own LLM, enabling better fit for the problem you are trying to solve.

## Extending the default LLM

This project is built on top of [dialog-lib](https://github.com/talkdai/dialog-lib), our library that provides a class-based API to create LLM models based on Langchain.

If you want to extend the default LLM, you can create a new class that inherits from AbstractLLM (as the default one does, available in the file `src/dialog/llm/agents/default.py) and override the methods you want to change and add behavior.

To use your custom LLM, you just need to add the environment variable LLM_CLASS to your `.env` file:

```
LLM_CLASS=plugins.my_llm.MyLLMClass
```

### Is it possible to use LangChain's LCEL as my agent?

You can user the default LangChain LCEL approach! It's totally up to you, but the LCEL must return a LangChain `Runnable` object in order to work and this object must be importable from the path you set in the `LLM_CLASS` environment variable.

We have an example of an LCEL implementation inside the file `src/dialog/llm/agents/lcel.py`. You can use it by setting the `LLM_CLASS` environment variable to `dialog.llm.agents.lcel.runnable`.

### What happens if my class doesn't implement the AbstractLLM from Dialog Lib or doesn't return a Runnable object?

If your class doesn't implement the AbstractLLM or doesn't return a Runnable object, the project will raise an error and load the default agent available in the file `src/dialog/llm/agents/default.py`.

## Adding extra routes to the project

Dialog is pretty extensible, being a FastAPI based project allows you to be very creative.

### Writing a new plugin without a PyPI Package.

To add new endpoints or features, you need to create a package inside the `src/plugins` folder and, inside the new package folder, add the following file:

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

### Available Plugins

 - [WhatsApp messaging with Audio Synthetizing](https://github.com/talkdai/dialog-whatsapp)
 - [Sentry](https://github.com/walison17/dialog-sentry/)
 - [Wati](https://github.com/talkdai/dialog-wati)
