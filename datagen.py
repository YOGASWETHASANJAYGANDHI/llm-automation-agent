import os
import json
import random
import sqlite3
import hashlib
import datetime
import time
from PIL import Image, ImageDraw, ImageFont
from faker import Faker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
config = {
    "email": os.getenv("EMAIL", "default@example.com"),
    "root": os.getenv("ROOT_DIR", "/data")
}

# Ensure the root directory exists
os.makedirs(config["root"], exist_ok=True)


def num(string):
    """Generate a deterministic number from a string using SHA-256."""
    return int(hashlib.sha256(string.encode()).hexdigest(), 16) % (2**32)


def write_file(path, content):
    """Write content to a file inside the root directory."""
    with open(os.path.join(config["root"], path), "w", encoding="utf-8") as f:
        f.write(content)


def get_markdown(email):
    """Generate poorly formatted Markdown content."""
    return f"""# Unformatted Markdown

This is a sample paragraph with extra  spaces and trailing whitespace.

- First item  
- Second item  
    + Third item  
    *    Fourth item  

```py
print("{email}")
```
"""


def a2_format_markdown():
    """Generate a poorly formatted markdown file."""
    write_file("format.md", get_markdown(config["email"]))


def get_dates(email):
    """Generate random dates in different formats."""
    random.seed(f"{email}:a3", version=2)
    start_date = datetime.datetime(2000, 1, 1)
    end_date = datetime.datetime(2024, 12, 31)
    formats = ["%Y-%m-%d", "%d-%b-%Y", "%b %d, %Y", "%Y/%m/%d %H:%M:%S"]
    timestamps = random.sample(range(int(start_date.timestamp()), int(end_date.timestamp())), 1000)
    return [datetime.datetime.fromtimestamp(ts).strftime(random.choice(formats)) for ts in timestamps]


def a3_dates():
    """Save 1,000 random dates in various formats."""
    dates = get_dates(config["email"])
    write_file("dates.txt", "\n".join(dates))


def get_contacts(email):
    """Generate 100 random contacts."""
    fake = Faker()
    fake.seed_instance(num(f"{email}:a4"))
    return [{"first_name": fake.first_name(), "last_name": fake.last_name(), "email": fake.email()} for _ in range(100)]


def a4_contacts():
    """Save random contacts in JSON format."""
    contacts = get_contacts(config["email"])
    write_file("contacts.json", json.dumps(contacts, indent=2))


def get_logs(email):
    """Generate 50 log files with random text."""
    fake = Faker()
    fake.seed_instance(num(f"{email}:a5"))
    return [(random.randint(1, 24 * 60 * 60 * 365), "\n".join(fake.text() for _ in range(10))) for _ in range(50)]


def a5_logs():
    """Create 50 log files in the logs directory."""
    os.makedirs(os.path.join(config["root"], "logs"), exist_ok=True)
    now = time.time()
    for i, (age, text) in enumerate(get_logs(config["email"])):
        write_file(f"logs/log-{i}.log", text)
        os.utime(os.path.join(config["root"], f"logs/log-{i}.log"), (now - age, now - age))


def a6_docs():
    """Generate random Markdown files in random subdirectories."""
    fake = Faker()
    fake.seed_instance(num(f"{config['email']}:a6"))
    os.makedirs(os.path.join(config["root"], "docs"), exist_ok=True)
    
    for _ in range(10):
        dir_name = fake.word()
        os.makedirs(os.path.join(config["root"], "docs", dir_name), exist_ok=True)
        for _ in range(10):
            file_name = fake.word()
            content = f"# {fake.sentence()}\n\n{fake.paragraph()}"
            write_file(f"docs/{dir_name}/{file_name}.md", content)


def a7_email():
    """Generate a fake email and save it as email.txt."""
    fake = Faker()
    fake.seed_instance(num(f"{config['email']}:a7"))
    email_data = {
        "recipient": fake.email(),
        "from_name": fake.name(),
        "from_email": fake.email(),
        "subject": fake.sentence(),
        "body": fake.text(),
    }
    write_file("email.txt", json.dumps(email_data, indent=2))


def a8_credit_card_image():
    """Generate a fake credit card image."""
    fake = Faker()
    fake.seed_instance(num(f"{config['email']}:a8"))
    
    card_data = {
        "number": fake.credit_card_number(),
        "expiry": fake.credit_card_expire(),
        "name": fake.name().upper(),
    }

    WIDTH, HEIGHT = 1012, 638
    image = Image.new("RGB", (WIDTH, HEIGHT), (25, 68, 141))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    draw.text((50, 250), card_data["number"], fill="white", font=font)
    draw.text((50, 400), "VALID THRU", fill="white", font=font)
    draw.text((50, 480), card_data["expiry"], fill="white", font=font)
    draw.text((50, 550), card_data["name"], fill="white", font=font)

    image.save(os.path.join(config["root"], "credit_card.png"))


def a9_comments():
    """Generate a comments.txt file with 100 random comments."""
    fake = Faker()
    fake.seed_instance(num(f"{config['email']}:a9"))
    comments = [fake.paragraph() for _ in range(100)]
    write_file("comments.txt", "\n".join(comments))


def a10_ticket_sales():
    """Generate a SQLite database for ticket sales."""
    db_path = os.path.join(config["root"], "ticket-sales.db")
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE tickets (
            type TEXT NOT NULL,
            units INTEGER NOT NULL,
            price DECIMAL(10,2) NOT NULL
        )
    """)

    tickets = [(random.choice(["Gold", "Silver", "Bronze"]), random.randint(1, 10), round(random.uniform(50, 150), 2)) for _ in range(1000)]
    cursor.executemany("INSERT INTO tickets VALUES (?, ?, ?)", tickets)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    print("Generating files in", config["root"])
    
    a2_format_markdown()
    a3_dates()
    a4_contacts()
    a5_logs()
    a6_docs()
    a7_email()
    a8_credit_card_image()
    a9_comments()
    a10_ticket_sales()

    print("Data generation complete.")
