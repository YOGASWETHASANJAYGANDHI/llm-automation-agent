from fastapi import HTTPException
from starlette.exceptions import HTTPException
import sqlite3
import subprocess
from dateutil.parser import parse
from datetime import datetime
import json
from pathlib import Path
import os
import requests
from scipy.spatial.distance import cosine
from dotenv import load_dotenv
import shutil

load_dotenv()

AIPROXY_TOKEN = os.getenv('AIPROXY_TOKEN')


def A1(email="23f2000098@ds.study.iitm.ac.in"):
    try:
        process = subprocess.Popen(
            ["uv", "run", "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py", email],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Error: {stderr}")
        return stdout
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Error: {e.stderr}")
# A1()

import os
import shutil
import subprocess
import sys

def A2(prettier_version="3.4.2", filename="data/format.md"):
    """Ensure the file exists and format it using Prettier with proper rules."""

    # Ensure the directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # Create the file if it doesn't exist
    if not os.path.exists(filename):
        print(f"⚠️ {filename} not found! Creating a new file.")
        with open(filename, "w", encoding="utf-8") as file:
            file.write(
                "# Unformatted Markdown\n\n"
                "This is a sample paragraph with extra spaces and trailing whitespace.\n\n"
                "- First item\n"
                "- Second item\n"
                "  +Third item\n"
                "  - Fourth item\n\n"
                "```py\n"
                "print(\"23f2000098@ds.study.iitm.ac.in\")\n"
                "```\n"
            )

    # Check if Node.js and npm are installed
    if not shutil.which("node") or not shutil.which("npm"):
        print("❌ Error: Node.js and npm are not installed or not in PATH!")
        return {"status": "error", "output": "Node.js/npm not found"}

    # Check if `npx` is installed
    if not shutil.which("npx"):
        print("❌ Error: `npx` is not installed or not in PATH!")
        return {"status": "error", "output": "`npx` not found"}

    # Define the Prettier command with specific Markdown rules
    command = [
        "npx", f"prettier@{prettier_version}", "--write", "--prose-wrap", "always", "--tab-width", "2", filename
    ]

    try:
        # Run the command
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True if sys.platform == "win32" else False  # Windows requires shell=True
        )
        
        print(f"✅ Prettier executed successfully on {filename}")

        # Read and return the formatted content
        with open(filename, "r", encoding="utf-8") as file:
            formatted_content = file.read()

        return {
            "status": "success",
            "output": result.stdout.strip(),
            "formatted_content": formatted_content
        }

    except subprocess.CalledProcessError as e:
        print(f"❌ Prettier execution failed with error code {e.returncode}")
        return {"status": "error", "output": e.stderr.strip(), "exit_code": e.returncode}

def A3(filename='/data/dates.txt', targetfile='/data/dates-wednesdays.txt', weekday=2):
    input_file = filename
    output_file = targetfile
    weekday = int(weekday)  # Ensure it's an integer

    weekday_count = 0
    with open(input_file, 'r') as file:
        weekday_count = sum(1 for date in file if parse(date.strip()).weekday() == weekday)

    with open(output_file, 'w') as file:
        file.write(str(weekday_count))

    print(f"✅ Counted {weekday_count} occurrences of weekday {weekday}.")

def A4(filename="/data/contacts.json", targetfile="/data/contacts-sorted.json"):
    try:
        # Load the contacts from the JSON file
        with open(filename, 'r') as file:
            contacts = json.load(file)

        # Ensure the data is a list
        if not isinstance(contacts, list):
            raise ValueError("Expected a list of contacts in JSON file")

        # Sort the contacts by last_name and then by first_name
        sorted_contacts = sorted(contacts, key=lambda x: (x.get('last_name', ''), x.get('first_name', '')))

        # Write the sorted contacts to the new JSON file
        with open(targetfile, 'w') as file:
            json.dump(sorted_contacts, file, indent=4)

        print(f"✅ Successfully sorted contacts and saved to {targetfile}")

    except Exception as e:
        print(f"❌ Error in A4: {e}")

def A5(log_dir_path='/data/logs', output_file_path='/data/logs-recent.txt', num_files=10):
    log_dir = Path(log_dir_path)
    output_file = Path(output_file_path)

    # Ensure the log directory exists
    if not log_dir.exists() or not log_dir.is_dir():
        print(f"Error: Log directory {log_dir_path} does not exist.")
        return

    # Get list of .log files sorted by modification time (most recent first)
    log_files = sorted(
        log_dir.glob("*.log"),
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )[:num_files]

    # Ensure there are log files available
    if not log_files:
        print(f"Error: No log files found in {log_dir_path}")
        return

    # Read first line of each file and write to the output file
    with output_file.open("w") as f_out:
        for log_file in log_files:
            try:
                with log_file.open("r", encoding="utf-8") as f_in:
                    first_line = f_in.readline().strip()
                    if first_line:
                        f_out.write(f"{first_line}\n")
                    else:
                        f_out.write("[EMPTY LINE]\n")  # Handle empty log files
            except Exception as e:
                print(f"Error reading {log_file}: {e}")

    print(f"✅ Successfully processed {len(log_files)} log files.")

def A6(doc_dir_path='/data/docs', output_file_path='/data/docs/index.json'):
    docs_dir = Path(doc_dir_path)
    output_file = Path(output_file_path)
    index_data = {}

    # Ensure the directory exists
    if not docs_dir.exists() or not docs_dir.is_dir():
        print(f"❌ Error: Document directory '{doc_dir_path}' does not exist.")
        return

    # Walk through all files in the docs directory
    for root, _, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.md'):
                file_path = Path(root) / file  # Correct path handling
                relative_path = file_path.relative_to(docs_dir).as_posix()  # Normalize path

                # Read the file and find the first H1 title
                try:
                    with file_path.open('r', encoding='utf-8') as f:
                        for line in f:
                            if line.startswith('# '):  # Look for first H1 header
                                title = line[2:].strip()  # Remove the '# ' part
                                index_data[relative_path] = title
                                break  # Stop after the first H1
                except Exception as e:
                    print(f"❌ Error reading {file_path}: {e}")

    # Check if data was collected
    if not index_data:
        print("⚠️ Warning: No valid markdown files with H1 titles found!")

    # Write the index data to index.json
    try:
        with output_file.open('w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=4)
        print(f"✅ Successfully created {output_file}")
    except Exception as e:
        print(f"❌ Error writing to {output_file}: {e}")

import openai
import re

def A7(filename: str, output_file: str):
    # Read the email content
    with open(filename, "r") as file:
        email_content = file.read()

    # Strict prompt to enforce output format
    prompt = f"""
    Extract only the sender's email address from the following email content:
    
    {email_content}

    Output ONLY the email address. Do NOT include any additional text, labels, or formatting.
    """

    # Call OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}]
    )

    # Extract response content
    try:
        extracted_text = response["choices"][0]["message"]["content"].strip()
        
        # Use regex to extract only the email
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', extracted_text)
        if match:
            email_address = match.group(0)
        else:
            raise ValueError("No valid email address extracted.")
    
    except KeyError:
        raise ValueError("Invalid LLM response format: missing 'choices' key.")

    # Save the extracted email
    with open(output_file, "w") as file:
        file.write(email_address)

import base64
import json
import requests
import os
import re

def png_to_base64(image_path):
    """Convert a PNG image to a Base64 string."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"❌ Error: {image_path} not found!")
        return None

def A8(image_path='/data/credit_card.png', output_file='/data/credit-card.txt', **kwargs):
    """Extract credit card number from an image and save it without spaces."""

    AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")
    if not AIPROXY_TOKEN:
        print("❌ Error: AIPROXY_TOKEN is missing!")
        return

    base64_image = png_to_base64(image_path)
    if not base64_image:
        return  # Exit if image is missing

    body = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "There is an 8 or more digit number in this image, formatted with spaces every 4 digits. Extract the number and return it without spaces."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIPROXY_TOKEN}"
    }

    response = requests.post("http://aiproxy.sanand.workers.dev/openai/v1/chat/completions",
                             headers=headers, data=json.dumps(body))
    
    result = response.json()
    if "choices" not in result:
        print(f"❌ Error: 'choices' key not found in response: {result}")
        return

    # Extract only the number
    match = re.search(r"\d{8,}", result["choices"][0]["message"]["content"])
    if match:
        card_number = match.group()
    else:
        print("❌ No valid number found!")
        return

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(card_number)

    print(f"✅ Extracted Credit Card Number: {card_number}")
    print(f"✅ Saved to: {output_file}")



def get_embedding(text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIPROXY_TOKEN}"
    }
    data = {
        "model": "text-embedding-3-small",
        "input": [text]
    }
    response = requests.post("http://aiproxy.sanand.workers.dev/openai/v1/embeddings", headers=headers, data=json.dumps(data))
    response.raise_for_status()
    return response.json()["data"][0]["embedding"]

def A9(filename='/data/comments.txt', output_filename='/data/comments-similar.txt'):
    # Read comments
    with open(filename, 'r') as f:
        comments = [line.strip() for line in f.readlines()]

    # Get embeddings for all comments
    embeddings = [get_embedding(comment) for comment in comments]

    # Find the most similar pair
    min_distance = float('inf')
    most_similar = (None, None)

    for i in range(len(comments)):
        for j in range(i + 1, len(comments)):
            distance = cosine(embeddings[i], embeddings[j])
            if distance < min_distance:
                min_distance = distance
                most_similar = (comments[i], comments[j])

    # Write the most similar pair to file
    with open(output_filename, 'w') as f:
        f.write(most_similar[0] + '\n')
        f.write(most_similar[1] + '\n')


import sqlite3

def A10(filename="/data/ticket-sales.db", output_filename="/data/ticket-sales-gold.txt", query="SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'"):
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(filename)
        cursor = conn.cursor()

        # Execute the query
        cursor.execute(query)
        total_sales = cursor.fetchone()[0]

        # Ensure total_sales is not None
        total_sales = total_sales if total_sales else 0

        # **Fix: Match expected precision (2 decimal places)**
        total_sales = round(total_sales, 2)

        # Write the total sales to file
        with open(output_filename, 'w') as file:
            file.write(f"{total_sales:.2f}")  # Ensure 2 decimal places

        print(f"✅ Successfully calculated Gold ticket sales: {total_sales}")

    except Exception as e:
        print(f"❌ Error in A10: {e}")

    finally:
        conn.close()
