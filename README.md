# TitanEngine 🎬

A Python tool that automatically generates complete AI-powered videos from a single topic input.

You give it a topic. It writes a script, generates images, adds voiceover, and produces a finished MP4 video — fully automated.





---

## What it does

1. **Generates a script** — sends your topic to any LLM via OpenRouter API, receives structured scene data as JSON
2. **Generates images** — creates visuals for each scene using any HuggingFace image model (example: I used Flux)
3. **Generates voiceover** — converts narration text to speech using Microsoft Edge TTS ( because it's free and quality of voice really good)
4. **Renders video** — combines image + audio into a video clip per scene using FFmpeg, then merges all clips into one final MP4

---

## How to change the AI models

This tool is designed to be model-agnostic. You can swap any model without touching the main code — just edit `config.py`.

### Change the language model (script generation)

Open `config.py` and change the `model_llm` value:

```python
VIDEO_CONFIG = {
    "model_llm": "mistralai/mistral-7b-instruct",  # change this to any OpenRouter model ( be careful, some of them are expensive, check prices before you do it.)
}
```

Any model available on [openrouter.ai/models](https://openrouter.ai/models) works here. Examples:
- `"openai/gpt-4o" ( be careful, this one very expensive )`
- `"mistralai/mistral-7b-instruct"`
- `"google/gemma-2-9b-it"`
- `"meta-llama/llama-3-8b-instruct"`

### Change the image generation model

```python
VIDEO_CONFIG = {
    "model_flux": "black-forest-labs/FLUX.1-schnell",  # change this to any HuggingFace diffusion model ( be careful, some of them are also expensive)
}
```

Any HuggingFace model compatible with `diffusers` `FluxPipeline` or `StableDiffusionPipeline` works. Examples:
- `"black-forest-labs/FLUX.1-schnell"` — fast, default
- `"black-forest-labs/FLUX.1-dev"` — higher quality, slower
- `"stabilityai/stable-diffusion-xl-base-1.0"` — classic SDXL

> **Note:** If you switch from a Flux model to Stable Diffusion, you also need to change `FluxPipeline` to `StableDiffusionPipeline` in `main.py`.

### Change the voice

```python
VIDEO_CONFIG = {
    "voice": "en-US-GuyNeural",  # change this to any Edge TTS voice
}
```

Full list of available voices: run `edge-tts --list-voices` in your terminal.

---

## Setup

### Requirements

```
Python 3.10+
FFmpeg installed and added to PATH
NVIDIA GPU recommended (CUDA) for image generation
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure API keys

Create a `config.py` file in the root folder:

```python
HF_TOKEN = "your_huggingface_token_here"
OR_KEY = "your_openrouter_api_key_here"

VIDEO_CONFIG = {
    "model_llm": "mistralai/mistral-7b-instruct",
    "model_flux": "black-forest-labs/FLUX.1-schnell",
    "voice": "en-US-GuyNeural",
    "width": 1280,
    "height": 720,
    "font_path": "C:/Windows/Fonts/arial.ttf",
}

BASE_PATH = "output/"
OUT_DIR = "output/temp/"
SCENES_DIR = "output/scenes/"
```

Get your keys here:
- HuggingFace token: [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
- OpenRouter key: [openrouter.ai/keys](https://openrouter.ai/keys)

### Run

```bash
python main.py
```

---

## Project structure

```
titanengine/
│
├── main.py          # TitanEngine class — full pipeline
├── config.py        # Your API keys and model settings ( don't show them to anyone )
├── requirements.txt # Python dependencies
├── .gitignore       # Hides config.py and output files
└── output/          # Generated videos saved here ( you can choose path where you want to save them )
```

---


### Important: Adjusting Paths for Your Operating System

Depending on whether you run this engine on a local machine (Windows/Mac) or a cloud GPU server (like RunPod/Linux), you must verify two paths in `config.py`:

1. **`font_path` (FFmpeg Subtitles)**: FFmpeg needs a physical font file to burn subtitles into the video.
   - **Windows Default**: `"C:/Windows/Fonts/arial.ttf"`
   - **Linux / RunPod Default**: `"/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"` *(Make sure to run `apt-get install -y fonts-dejavu-core` on your Linux instance if it is missing).*
   - **Mac Default**: `"/Library/Fonts/Arial.ttf"`

2. **Folder Outputs**: Ensure the `BASE_PATH`, `OUT_DIR`, and `SCENES_DIR` strings match your system’s folder format (e.g., using forward slashes `/` for Linux/RunPod and ensuring the root directory folders exist before execution, it's an important!).

P.S: I tested program using RunPod. 

### 📝 Note on Sample Video Results

The video clips included in the `samples/` directory represent different development iterations and testing environments ( you will see when you check them). Throughout a long optimization process, I experimented across multiple open-source models, rendering resolutions, and parameters on RunPod. 

While the current `main.py` code provides the baseline architectural framework, the provided clips demonstrate the practical results achieved at various successful stages of this generative pipeline.


## Tech stack

| Tool | Purpose |
|------|---------|
| Python asyncio | Parallel scene processing |
| OpenRouter API | LLM script generation |
| HuggingFace Diffusers | Local AI image generation |
| Microsoft Edge TTS | Text-to-speech voiceover |
| FFmpeg | Video rendering and encoding |
| PyTorch + CUDA | GPU inference for image models |

---
## Motivation

I saw channels like: https://www.youtube.com/@chillfinancialhistorian + https://www.youtube.com/watch?v=WjQyB2Q7PYU&t=452s and similiar to them. I thought that it's 
incredible and great opportunity to create a faceless channel. What was incredible to me was that these videos were 15-30 minutes long and not shorts. I thought it was really cool to make a program with which I could make long videos on topics that I would choose myself and of course the most important that the program should create videos as cheaper as it's possible, for this point you need to choose cheap models not like GPT. 

## Status

Personal project built while learning Python independently.
Not production-ready — built for learning and experimentation only.
