# Python Auto Generating Prompt (PAGP)

## Overview

PAGP (Python Auto Generating Prompt) is a **generalized LLM-driven execution framework** designed to process **structured tasks** such as:

- **Metadata Extraction** (e.g., extracting key concepts, sentiment analysis)
- **Summarization** (e.g., generating executive summaries)
- **Classification** (e.g., assigning categories based on ontology)

The system is designed to be **fully modular**, allowing different use cases by simply switching **configuration files**.

---

## 📂 Folder Structure

```
pagp/
  pagp.py  # Main script
  .env  # Environment variables file
  test_input_data.json  # Sample input file
  examples/
    metadata/
      config.yaml
      system_prompt.txt
      prompt_template.txt
    summarize/
      config.yaml
      system_prompt.txt
      prompt_template.txt
    classify/
      config.yaml
      system_prompt.txt
      prompt_template.txt
      ontology.yaml
      expansion_rules.json
```

---

## 🚀 How to Use

### 1️⃣ Install Dependencies

```bash
pip install openai pyyaml python-dotenv
```

### 2️⃣ Set Environment Variables

Create a `.env` file in the root directory and define:

```env
PAGP_BASE_URL="http://127.0.0.1:1234/v1"
PAGP_API_KEY="lm-studio"
PAGP_MODEL="hermes-3-llama-3.2-3b"
```

Alternatively, you can export them manually:

```bash
export PAGP_BASE_URL="http://127.0.0.1:1234/v1"
export PAGP_API_KEY="lm-studio"
export PAGP_MODEL="hermes-3-llama-3.2-3b"
```

### 3️⃣ Run PAGP for Different Tasks

#### **Metadata Extraction**

```bash
python pagp.py --config examples/metadata/config.yaml --input test_input_data.json --output test_metadata.json
```

#### **Summarization**

```bash
python pagp.py --config examples/summarize/config.yaml --input test_input_data.json --output test_summaries.json
```

#### **Classification**

```bash
python pagp.py --config examples/classify/config.yaml --input test_input_data.json --output test_classifications.json
```

---

## 🛠 Configuration (`config.yaml`)

Each use case has its own `config.yaml` file that defines:

```yaml
execution:
  batch_processing: true
  incremental_saving: true
  max_retries: 3

supporting_materials:
  system_prompt: "system_prompt.txt"
  prompt_template: "prompt_template.txt"

input:
  source_type: "json"
  file_path: "../test_input_data.json"

output:
  format: "json"
  destination: "../test_output.json"

variables:
  "{title}": "title"
  "{description}": "description"
```

---

## 🔧 Customization

- Modify `system_prompt.txt` for different LLM instructions.
- Modify `prompt_template.txt` for **dynamic input formatting**.
- Add new folders for **new use cases** with corresponding `config.yaml`.

---

## 📜 License

This project is open-source. Feel free to modify and extend it!

---

## 🏆 Contributors

- [Your Name]
- [Your Organization]

---

🚀 **Now you can package and share PAGP easily!** Let me know if you need further modifications!
