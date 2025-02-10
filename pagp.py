import openai
import json
import yaml
import os
import argparse
from dotenv import load_dotenv

load_dotenv()

# Get API variables
API_BASE_URL = os.getenv("PAGP_BASE_URL")
API_KEY = os.getenv("PAGP_API_KEY")
MODEL = os.getenv("PAGP_MODEL")


# Initialize OpenAI client
client = openai.OpenAI(
    base_url=API_BASE_URL,
    api_key=API_KEY
)

parser = argparse.ArgumentParser(description="Python Auto Generating Prompt (PAGP) Executor")
parser.add_argument("--config", required=True, help="Path to the config.yaml file")
parser.add_argument("--input", required=True, help="Path to the input data file (JSON)")
parser.add_argument("--output", required=True, help="Path to the output file (JSON)")
args = parser.parse_args()

config_path = os.path.abspath(args.config)
config_dir = os.path.dirname(config_path)

with open(config_path, "r") as f:
    config = yaml.safe_load(f)

def resolve_path(relative_path):
    return os.path.join(config_dir, relative_path)

with open(resolve_path(config["supporting_materials"]["system_prompt"]), "r") as f:
    system_prompt = f.read()

with open(resolve_path(config["supporting_materials"]["prompt_template"]), "r") as f:
    prompt_template = f.read()

input_path = os.path.abspath(args.input)
with open(input_path, "r") as f:
    input_data = json.load(f)

additional_inclusions = {}
for key, relative_path in config["supporting_materials"].get("additional_inclusions", {}).items():
    with open(resolve_path(relative_path), "r") as f:
        additional_inclusions[key] = yaml.safe_load(f) if relative_path.endswith(".yaml") else json.load(f)

def execute_prompt(item):
    """Generates a dynamic prompt response for an item."""
    prompt = prompt_template.replace("{system_prompt}", system_prompt)

    for key, value in additional_inclusions.items():
        prompt = prompt.replace(f"{{{key}}}", json.dumps(value, indent=2))

    for var, field in config["variables"].items():
        prompt = prompt.replace(var, str(item.get(field, "")))  # Default to "" if missing

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}]
        )

        response_content = response.choices[0].message.content
        return json.loads(response_content)

    except Exception as e:
        print(f"❌ Error processing item {item['id']}: {str(e)}")
        return None

output_path = os.path.abspath(args.output)
processed_results = []

for item in input_data:
    print(f"🔄 Processing item {item['id']}...")

    result = execute_prompt(item)
    if result:
        processed_results.append(result)

        # Save incrementally
        with open(output_path, "w") as f:
            json.dump(processed_results, f, indent=2)

print("✅ Processing complete! Results saved.")