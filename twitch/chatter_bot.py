import logging
from twitchio.ext import commands
from config.config import Config
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import asyncio
from peft import PeftModel

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class TwitchBot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=Config.TWITCH_ACCESS_TOKEN,
            client_id=Config.TWITCH_CLIENT_ID,
            prefix='!',
            initial_channels=[Config.TWITCH_CHANNEL]
        )
        
        # Load the base model and tokenizer
        logging.info(f"Loading base model: {Config.BASE_MODEL}")
        self.tokenizer = AutoTokenizer.from_pretrained(Config.MODEL_PATH)
        
        # Load the base model first
        self.model = AutoModelForCausalLM.from_pretrained(
            Config.BASE_MODEL,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )
        
        # Then load the adapter on top of the base model
        logging.info(f"Loading adapter from: {Config.MODEL_PATH}")
        self.model = PeftModel.from_pretrained(self.model, Config.MODEL_PATH)
        self.model.to("cuda" if torch.cuda.is_available() else "cpu")
        
        # Set model to evaluation mode
        self.model.eval()

        # Message generation frequency in seconds
        self.message_frequency = Config.MESSAGE_FREQUENCY

    async def event_ready(self):
        logging.info(f'Bot is ready | {self.nick}')
        
        # Start the message generation task
        self.loop.create_task(self.generate_and_send_messages())

    async def generate_and_send_messages(self):
        while True:
            try:
                # Generate a random message using the same format as during training
                # Use a simple system message to simulate a user trigger
                input_text = "<|im_start|>user\nSay something interesting to chat<|im_end|>\n<|im_start|>assistant\n"
                
                inputs = self.tokenizer(input_text, return_tensors="pt").to(self.model.device)
                
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs, 
                        max_new_tokens=80,
                        temperature=0.7,
                        top_p=0.9,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
                
                message = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                # Extract just the assistant's reply
                parts = message.split("<|im_start|>assistant\n")
                if len(parts) > 1:
                    message = parts[1].strip()
                else:
                    # Fallback in case the format is different
                    message = message.replace(input_text, "").strip()

                # Ask the user if they want to send the message
                logging.info("Generated message: " + message)
                response = input("Do you want to send this message? (y/n): ")

                if response.lower() == "y":
                    # Send the generated message to the channel
                    await self.get_channel(Config.TWITCH_CHANNEL).send(message)
                else:
                    logging.info("User chose not to send the message.")
                
                # Wait for the specified frequency before generating the next message
                await asyncio.sleep(self.message_frequency)
            except Exception as e:
                logging.error(f"Error generating and sending message: {e}")
                # Wait for a short time before trying again
                await asyncio.sleep(10)


async def main():
    bot = TwitchBot()
    await bot.start()

if __name__ == "__main__":
    asyncio.run(main())