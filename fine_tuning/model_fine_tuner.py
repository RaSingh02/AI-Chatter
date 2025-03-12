import logging
import torch
import json
import os
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import DataCollatorForSeq2Seq
from trl import SFTTrainer
from config.config import Config
from datasets import Dataset

logging.basicConfig(level=logging.INFO)


def train_model():
    # Disable wandb
    os.environ["WANDB_DISABLED"] = "true"

    logging.info("Starting model fine-tuning with PEFT/LoRA")

    # Check if GPU is available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logging.info(f"Using device: {device}")

    # Determine precision
    use_4bit = Config.LOAD_IN_4BIT
    use_bf16 = torch.cuda.is_available(
    ) and torch.cuda.get_device_capability()[0] >= 8

    logging.info(f"Loading model: {Config.BASE_MODEL}")

    # Configure quantization
    if use_4bit:
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16 if use_bf16 else torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )
    else:
        quantization_config = None

    # Load base model and tokenizer
    model = AutoModelForCausalLM.from_pretrained(
        Config.BASE_MODEL,
        device_map="auto",
        quantization_config=quantization_config,
        torch_dtype=torch.bfloat16 if use_bf16 else torch.float16,
    )

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        Config.BASE_MODEL,
        use_fast=True,
    )

    # Set padding token if not set
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id

    # Prepare model for k-bit training if using 4-bit quantization
    if use_4bit:
        model = prepare_model_for_kbit_training(model)

    # Configure LoRA
    logging.info("Applying LoRA adapters")
    lora_config = LoraConfig(
        r=Config.LORA_RANK,
        lora_alpha=Config.LORA_ALPHA,
        target_modules=["q_proj", "k_proj", "v_proj",
                        "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    # Apply LoRA adapters
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # Load and format dataset
    logging.info("Loading dataset")
    with open('data/formatted_logs/dataset.json', 'r') as f:
        messages = json.load(f)

    dataset = Dataset.from_list([{"text": msg} for msg in messages])

    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            padding=True,
            truncation=True,
            max_length=Config.MAX_SEQ_LENGTH,
            return_tensors="pt"
        )

    # Tokenize the dataset
    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=dataset.column_names
    )

    # Set up training arguments
    logging.info("Configuring trainer")
    training_args = TrainingArguments(
        per_device_train_batch_size=Config.BATCH_SIZE,
        gradient_accumulation_steps=Config.GRADIENT_ACCUMULATION_STEPS,
        warmup_steps=Config.WARMUP_STEPS,
        max_steps=Config.TRAINING_STEPS,
        learning_rate=Config.LEARNING_RATE,
        fp16=not use_bf16,
        bf16=use_bf16,
        logging_steps=1,
        optim="adamw_torch",  # Using standard optimizer for Windows compatibility
        weight_decay=Config.WEIGHT_DECAY,
        output_dir=Config.MODEL_PATH,
        save_strategy="steps",
        save_steps=50,
        save_total_limit=3,
        report_to=[],  # Disable all reporting
        run_name=None,  # Prevent wandb name collision warning
        gradient_checkpointing=True,  # Add this line
    )

    # Configure SFT trainer
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        data_collator=DataCollatorForSeq2Seq(tokenizer, model=model),
        train_dataset=tokenized_dataset,
        peft_config=lora_config,
        formatting_func=lambda x: x['content'],
    )

    # Train model
    logging.info("Starting training")
    trainer.train()

    # Save model
    logging.info(f"Saving model to {Config.MODEL_PATH}")
    model.save_pretrained(Config.MODEL_PATH)
    tokenizer.save_pretrained(Config.MODEL_PATH)
    logging.info("Fine-tuning complete!")


if __name__ == '__main__':
    train_model()
