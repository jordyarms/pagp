import openai
import os
import yaml
import frontmatter
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Parse arguments
parser = argparse.ArgumentParser(description="PAGP: Process Markdown files with YAML frontmatter")
parser.add_argument("--config", required=True, help="Path to the config.yaml file")
parser.add_argument("--folder", help="Folder containing Markdown files")
args = parser.parse_args()

# Load configuration
config_path = os.path.abspath(args.config)
config_dir = os.path.dirname(config_path)

with open(config_path, "r") as f:
    config = yaml.safe_load(f)

# Get API credentials from environment variables
API_BASE_URL = os.getenv("PAGP_BASE_URL")
API_KEY = os.getenv("PAGP_API_KEY")
MODEL = os.getenv("PAGP_MODEL")

# Initialize OpenAI client
client = openai.OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

# Load supporting materials
system_prompt_path = os.path.join(config_dir, config["supporting_materials"]["system_prompt"])
prompt_template_path = os.path.join(config_dir, config["supporting_materials"]["prompt_template"])

with open(system_prompt_path, "r") as f:
    system_prompt = f.read()

with open(prompt_template_path, "r") as f:
    prompt_template = f.read()

# Define Markdown folder
markdown_folder = args.folder if args.folder else config["input"]["folder_path"]
markdown_folder = os.path.abspath(markdown_folder)

# Function to process a single markdown file
def process_markdown(file_path):
    """Reads a Markdown file, runs the LLM prompt, and updates the frontmatter."""
    # Load markdown file
    with open(file_path, "r", encoding="utf-8") as f:
        md = frontmatter.load(f)

    markdown_content = md.content
    yaml_frontmatter = yaml.dump(md.metadata)

    # Replace variables in the prompt
    prompt = prompt_template.replace("{system_prompt}", system_prompt)
    prompt = prompt.replace("{content}", markdown_content)
    prompt = prompt.replace("{frontmatter}", yaml_frontmatter)

    # Call LLM
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}]
        )

        response_content = response.choices[0].message.content
        new_metadata = yaml.safe_load(response_content)  # Extract new frontmatter data

        # Merge new metadata with existing frontmatter
        md.metadata.update(new_metadata)

        # Write back to the original file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(md))

        print(f"✅ Processed: {file_path}")

    except Exception as e:
        print(f"❌ Error processing {file_path}: {str(e)}")

# Iterate over markdown files
for filename in os.listdir(markdown_folder):
    if filename.endswith(".md"):
        process_markdown(os.path.join(markdown_folder, filename))
