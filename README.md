# AI Twitch Chat Bot with Deepseek R1

This project implements an AI-powered Twitch chat bot that uses a fine-tuned Deepseek R1 model to interact in Twitch chat. It includes tools for collecting chat data, formatting datasets, and fine-tuning the model.

## Features

- Real-time Twitch chat monitoring
- Chat message collection and dataset creation
- Model fine-tuning with LoRA adapters
- Live stream detection
- AI-powered chat interactions
- Automated chat recording and dataset generation

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

## Usage

### Automated Chat Recording

The project includes an automated system for recording chat when a streamer goes live and formatting the dataset when they go offline:

```bash
python main.py auto
```

This will:
1. Monitor the specified Twitch channel
2. Automatically start recording chat when the streamer goes live
3. Stop recording when the streamer goes offline
4. Format the chat logs into a dataset for training

### Model Fine-tuning

To fine-tune the model on collected chat data:

```bash
python main.py train
```

### Running the Chat Bot

To run the AI chat bot in a Twitch channel:

```bash
python main.py bot
```

## Project Structure

- `config/` - Configuration files and settings
- `data/` - Directory for chat logs and formatted datasets
- `fine_tuning/` - Model fine-tuning scripts
- `logs/` - Log files from various components
- `model/` - Trained model files
- `twitch/` - Twitch API integration and chat handling
- `utils/` - Utility functions and helper scripts

## GitHub Actions Automation

This project includes a GitHub Actions workflow that can automatically run the auto chat recorder on a schedule, even when your local machine is offline.

### Setting Up GitHub Actions Secrets

To use the GitHub Actions workflow, you need to set up the following secrets in your GitHub repository:

1. Go to your GitHub repository
2. Click on "Settings" > "Secrets and variables" > "Actions"
3. Click on "New repository secret"
4. Add the following secrets:
   - `ACCESS_TOKEN`: Your Twitch access token
   - `REFRESH_TOKEN`: Your Twitch refresh token
   - `CLIENT_ID`: Your Twitch client ID
   - `CHANNEL`: The Twitch channel to monitor
   - `MODEL`: The model to use (e.g., `unsloth/DeepSeek-R1-Distill-Qwen-1.5B-unsloth-bnb-4bit`)

### Workflow Configuration

The workflow is configured to:
- Run every 6 hours by default
- Run for a maximum of 5 hours each time
- Can be manually triggered using the "Actions" tab in GitHub
- Uses CPU-based PyTorch to ensure compatibility with GitHub Actions runners

To modify the schedule, edit the `.github/workflows/auto_chat_recorder.yml` file.

## Logs and Data

- Live stream detection logs: `logs/live_stream_detector/`
- Auto chat recorder logs: `logs/`
- Chat logs: `data/chat_logs/`
- Formatted datasets: `data/formatted_logs/`
