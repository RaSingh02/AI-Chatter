import logging
from unsloth import FastLanguageModel
from unsloth import is_bfloat16_supported
from unsloth.chat_templates import get_chat_template, train_on_responses_only
from transformers import TrainingArguments, DataCollatorForSeq2Seq
from trl import SFTTrainer
import json
from config import Config

logging.basicConfig(level=logging.INFO)


def train_model():
    # Load model and tokenizer
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=Config.BASE_MODEL,
        max_seq_length=Config.MAX_SEQ_LENGTH,
        load_in_4bit=Config.LOAD_IN_4BIT
    )

    # Apply LoRA adapters
    model = FastLanguageModel.get_peft_model(
        model,
        r=Config.LORA_RANK,
        target_modules=["q_proj", "k_proj", "v_proj",
                        "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_alpha=Config.LORA_ALPHA,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing="unsloth"
    )

    # Load and format dataset
    with open('formatted_dataset.json', 'r') as f:
        messages = json.load(f)

    dataset = [{"role": "assistant", "content": msg} for msg in messages]

    # Apply chat template
    tokenizer = get_chat_template(tokenizer, chat_template="llama-3.1")

    # Configure trainer
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="content",
        max_seq_length=Config.MAX_SEQ_LENGTH,
        data_collator=DataCollatorForSeq2Seq(tokenizer=tokenizer),
        args=TrainingArguments(
            per_device_train_batch_size=Config.BATCH_SIZE,
            gradient_accumulation_steps=Config.GRADIENT_ACCUMULATION_STEPS,
            warmup_steps=Config.WARMUP_STEPS,
            max_steps=Config.TRAINING_STEPS,
            learning_rate=Config.LEARNING_RATE,
            fp16=not is_bfloat16_supported(),
            bf16=is_bfloat16_supported(),
            logging_steps=1,
            optim="adamw_8bit",
            weight_decay=Config.WEIGHT_DECAY,
            output_dir=Config.MODEL_PATH
        )
    )

    # Train only on assistant responses
    trainer = train_on_responses_only(
        trainer,
        instruction_part="<|start_header_id|>user<|end_header_id|>\n\n",
        response_part="<|start_header_id|>assistant<|end_header_id|>\n\n"
    )

    # Start training
    trainer.train()

    # Save model
    model.save_pretrained(Config.MODEL_PATH)
    tokenizer.save_pretrained(Config.MODEL_PATH)


if __name__ == '__main__':
    train_model()
