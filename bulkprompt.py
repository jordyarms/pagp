import openai
import os
import yaml
import json
import frontmatter
import argparse
from dotenv import load_dotenv

# Parse arguments
parser = argparse.ArgumentParser(description="PAGP: Process files with YAML frontmatter or JSON data")
parser.add_argument("--config", required=True, help="Path to the config.yaml file")
parser.add_argument("--mode", required=True, choices=["markdown", "json"], help="Mode of operation: 'markdown' or 'json'")
parser.add_argument("--input", required=True, help="Path to the input file or folder")
parser.add_argument("--output", help="Path to the output file (optional, if not specified, input file will be overwritten)")
args = parser.parse_args()

# Load environment variables and establish OpenAI LLM API connection
load_dotenv()

API_BASE_URL = os.getenv("PAGP_BASE_URL")
API_KEY = os.getenv("PAGP_API_KEY")
MODEL = os.getenv("PAGP_MODEL")

client = openai.OpenAI(base_url=API_BASE_URL, api_key=API_KEY)  # Initialize OpenAI client

# Load configuration, supporting materials
config_path = os.path.abspath(args.config)
config_dir = os.path.dirname(config_path)

with open(config_path, "r") as f:
  config = yaml.safe_load(f)

system_prompt_path = os.path.join(config_dir, config["supporting_materials"]["system_prompt"])
prompt_template_path = os.path.join(config_dir, config["supporting_materials"]["prompt_template"])

additional_inclusions = config.get("additional_inclusions", {})  # Additional inclusions
variables = {var: item.get(field, "") for var, field in config["variables"].items()}  # Variables

with open(system_prompt_path, "r") as f:
  system_prompt = f.read()

with open(prompt_template_path, "r") as f:
  prompt_template = f.read()

# Function to process a single markdown file
def process_markdown(file_path, output_path=None):
  """Reads a Markdown file, runs the LLM prompt, and updates the frontmatter."""
  with open(file_path, "r", encoding="utf-8") as f:
    md = frontmatter.load(f)

  markdown_content = md.content
  yaml_frontmatter = yaml.dump(md.metadata)

  prompt = construct_prompt(prompt_template, markdown_content, yaml_frontmatter)

  response_content = get_chat_completion(prompt)
  if response_content:
    new_metadata = yaml.safe_load(response_content)  # Review this line
    md.metadata.update(new_metadata)

    output_file_path = output_path or file_path
    with open(output_file_path, "w", encoding="utf-8") as f:
      f.write(frontmatter.dumps(md))  # Review this line

    print(f"✅ Processed: {output_file_path}")
  else:
    print(f"❌ Error processing {file_path}")

# Function to process JSON data
def process_json(input_path, output_path=None):
  with open(input_path, "r") as f:
    input_data = json.load(f)

  processed_results = []
  for item in input_data:
    print(f"🔄 Processing item {item['id']}...")
    prompt = construct_prompt(prompt_template, "", "", additional_inclusions, variables)
    result = get_chat_completion(prompt)
    if result:
      processed_results.append(result)

  output_path = output_path or input_path
  with open(output_path, "w") as f:
    json.dump(processed_results, f, indent=2)

  print("✅ Processing complete! Results saved.")

# Function to construct the prompt
def construct_prompt(template, content, frontmatter, additional_inclusions=None, variables=None):
  prompt = template.replace("{content}", content).replace("{frontmatter}", frontmatter)
  if additional_inclusions:
    for key, value in additional_inclusions.items():
      prompt = prompt.replace(f"{{{key}}}", json.dumps(value, indent=2))
  if variables:
    for var, field in variables.items():
      prompt = prompt.replace(var, str(field))
  return prompt

# Function to get chat completion from OpenAI
def get_chat_completion(prompt):
  try:
    response = client.chat.completions.create(
      model=MODEL,
      messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
      ]
    )
    return response.choices[0].message.content
  except Exception as e:
    print(f"❌ Error getting chat completion: {str(e)}")
    return None

# Determine the mode of operation
if args.mode == "markdown":
  input_path = os.path.abspath(args.input)
  if not os.path.isdir(input_path):
    print("❌ Error: --input must be a folder when mode is 'markdown'.")
    parser.print_help()
  else:
    for filename in os.listdir(input_path):
      if filename.endswith(".md"):
        process_markdown(os.path.join(input_path, filename))
elif args.mode == "json":
  process_json(os.path.abspath(args.input), os.path.abspath(args.output) if args.output else None)
else:
  print("❌ Error: Invalid mode specified.")
  parser.print_help()
