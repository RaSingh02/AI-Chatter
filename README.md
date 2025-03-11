# AI Twitch Chat Bot with Deepseek R1

This project implements an AI-powered Twitch chat bot that uses a fine-tuned Deepseek R1 model to interact in Twitch chat. It includes tools for collecting chat data, formatting datasets, and fine-tuning the model.

## Features

- Real-time Twitch chat monitoring
- Chat message collection and dataset creation
- Model fine-tuning with LoRA adapters
- Live stream detection
- AI-powered chat interactions

## Requirements

- Python 3.7+
- PyTorch
- CUDA-compatible GPU (recommended for model fine-tuning)

## Installation

1. Clone the repository
2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your Twitch credentials:

```
ACCESS_TOKEN=your_access_token
REFRESH_TOKEN=your_refresh_token
CLIENT_ID=your_client_id
CHANNEL=streamer_channel
MODEL=your_model (default: deepseek-r1)
```
