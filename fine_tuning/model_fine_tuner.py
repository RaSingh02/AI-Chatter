import logging
import torch
import json
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import DataCollatorForSeq2Seq
from trl import SFTTrainer
from config.config import Config

logging.basicConfig(level=logging.INFO)


def train_model():
    logging.info("Starting model fine-tuning with PEFT/LoRA")
    
    # Check if GPU is available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logging.info(f"Using device: {device}")
    
    # Determine precision
    use_4bit = Config.LOAD_IN_4BIT
    use_bf16 = torch.cuda.is_available() and torch.cuda.get_device_capability()[0] >= 8
    
    logging.info(f"Loading model: {Config.BASE_MODEL}")
    
    # Load base model and tokenizer
    model = AutoModelForCausalLM.from_pretrained(
        Config.BASE_MODEL,
        device_map="auto",
        load_in_4bit=use_4bit,
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
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    
    # Apply LoRA adapters
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    # Load and format dataset
    logging.info("Loading dataset")
    with open('formatted_dataset.json', 'r') as f:
        messages = json.load(f)
    
    dataset = [{"role": "assistant", "content": msg} for msg in messages]
    
    # Configure tokenizer for chat
    if hasattr(tokenizer, 'apply_chat_template'):
        tokenizer.chat_template = tokenizer.chat_template or "llama-3.1"
    
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
    )
    
    # Configure SFT trainer
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="content",
        max_seq_length=Config.MAX_SEQ_LENGTH,
        data_collator=DataCollatorForSeq2Seq(tokenizer=tokenizer, padding=True),
        args=training_args,
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
