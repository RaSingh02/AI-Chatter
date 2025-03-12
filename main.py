import argparse
import asyncio
import sys

from utils.dataset_formatter import format_dataset
from fine_tuning.model_fine_tuner import train_model
from twitch.chatter_bot import TwitchBot
from utils.auto_chat_recorder import main as auto_chat_recorder_main


def run_dataset_formatter():
    format_dataset()


def run_model_fine_tuner():
    train_model()


async def run_bot():
    bot = TwitchBot()
    await bot.start()


async def run_auto_chat_recorder():
    await auto_chat_recorder_main()


# Run the script with the following arguments:
# python main.py <script>
# train = model_fine_tuner
# bot = twitch_bot
# auto = auto_chat_recorder


def main():
    parser = argparse.ArgumentParser(
        description="Run various project scripts.")
    parser.add_argument(
        "script",
        choices=["train", "bot", "auto", "format"],
        help="Choose which script to run."
    )

    args = parser.parse_args()

    if args.script == "train":
        run_model_fine_tuner()
    elif args.script == "format":
        run_dataset_formatter()
    elif args.script == "bot":
        asyncio.run(run_bot())
    elif args.script == "auto":
        asyncio.run(run_auto_chat_recorder())
    else:
        print("Invalid script choice.")
        sys.exit(1)


if __name__ == "__main__":
    main()
