import argparse
import asyncio
import sys

import torch
from utils.dataset_formatter import format_dataset
from utils.live_stream_detector import main as live_stream_detector_main
from twitch.chat_reader import main as chat_reader_main
from fine_tuning.model_fine_tuner import train_model


def run_dataset_formatter():
    format_dataset()


async def run_live_stream_detector():
    await live_stream_detector_main()


async def run_chat_reader():
    await chat_reader_main()


def run_model_fine_tuner():
    train_model()


def get_device():
    if torch.backends.mps.is_available():
        return "mps"
    elif torch.cuda.is_available():
        print(torch.cuda.is_available())
    else:
        return "cpu"

# Run the script with the following arguments:
# python main.py <script>
# d = dataset_formatter
# l = live_stream_detector
# c = chat_reader
# m = model_fine_tuner
# cuda = get_device

def main():
    parser = argparse.ArgumentParser(
        description="Run various project scripts.")
    parser.add_argument(
        "script",
        choices=["d", "l", "c", "m", "cuda"],
        help="The script to run"
    )

    args = parser.parse_args()

    if args.script == "d":
        run_dataset_formatter()
    elif args.script == "l":
        asyncio.run(run_live_stream_detector())
    elif args.script == "c":
        asyncio.run(run_chat_reader())
    elif args.script == "m":
        run_model_fine_tuner()
    elif args.script == "cuda":
        print(get_device())
    else:
        print("Invalid script choice.")
        sys.exit(1)


if __name__ == "__main__":
    main()
