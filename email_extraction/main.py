import mailbox
import os
import sys
import time
from datetime import datetime

def loader(message, duration=5):
    """Displays a simple loading animation."""
    print(message, end="", flush=True)
    for _ in range(duration):
        print(".", end="", flush=True)
        time.sleep(1)
    print()  # New line after loading


# Automatically use the .mbox file in the same directory as the script
mbox_file = "inbox.mbox"  # Replace with your mbox file name

# Determine the directory where the executable is located
if getattr(sys, "frozen", False):
    current_dir = os.path.dirname(sys.executable)  # Executable path
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Script path

mbox_path = os.path.join(current_dir, mbox_file)

# Log the start time
start_time = datetime.now()
print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

# Start the loader
loader("Loading MBOX file ", duration=5)
mbox = mailbox.mbox(mbox_path)
contacts = set()

exclude_terms = {
    "noreply",
    "no-reply",
    "info",
    "notifications",
    "help",
    "vosyn.ai",
    "hello",
    "team",
    "alerts",
    "research",
    "onlineservices",
    "invoice",
    "marketing",
    "notification",
    "docusign",
    "dse",
    "reply",
    "notion",
    "donotreply",
    "support",
    "newsletter",
    "sales",
    "contact",
    "admin",
    "inquiries",
    "service",
    "billing",
    "orders",
    "accounts",
    "offers",
    "promo",
    "deals",
    "subscriptions",
    "customerservice",
    "registrations",
    "feedback",
    "services",
    "events",
    "careers",
    "jobs",
    "press",
    "media",
    "partners",
    "webmaster",
    "postmaster",
    "notify",
    "do-not",
    "no.reply",
    "recruiting",
    "hr",
    "talent",
    "cv",
    "placements",
    "livehire",
    "linkedin",
    "indeed",
    "myworkday",
    "breezy-mail",
    "hiring",
    "staffing",
    "staples",
    "git",
    "lever",
    "hire",
    "immigration",
    "invite",
    "team",
    "dell",
    "paypal",
    "coursera",
    "godaddy",
    "do-no-reply",
    "no-reply",
    "SystemMessage",
    "system",
    "SystemMessages",
    "notifications",
    "recruitment",
    "recruit",
    "recruiter",
    "recruiters",
    "recruitments",
    "recommendations",
    "recommendation",
    "recommend",
}

include_terms = {
    "gmail",
    "yahoo",
    "outlook",
    "hotmail",
    "icloud",
    "aol",
    "gmx",
    "protonmail",
    "zoho",
    "yandex",
    "live",
    "me",
    "fastmail",
    "msn",
    "qq",
    "naver",
    "rediffmail",
    "tutanota",
}

error_contacts = set()
ignored_file = os.path.join(current_dir, "ignored.csv")
with open(ignored_file, "a") as f:
    f.write('"Name","Email"\n')

# Iterate through all the messages in the MBOX file
for message in mbox:
    try:
        sender = message["from"]
        if not sender:
            continue  # Skip if sender is None

        # Extract name and email
        if "<" in sender:
            name = sender.split("<")[0].strip()
            email = sender.split("<")[1].replace(">", "").strip()
        else:
            name = sender.strip()
            email = sender.strip()

        # Convert email to lowercase for case-insensitive matching
        email_lower = email.lower()

        # Check if the email meets inclusion and exclusion criteria
        if any(term in email_lower for term in exclude_terms) or not any(
            term in email_lower for term in include_terms
        ):
            with open(ignored_file, "a") as f:
                f.write(f'"{name}","{email}"\n')
            continue  # Skip this email

        # Combine name and email to create a unique contact
        contact = f"{name},{email}"
        contacts.add(contact)
    except Exception as e:
        print(f"Could not process sender: {sender}. Error: {e}")
        error_contacts.add(sender)

# Check if contacts are found
if not contacts:
    print("No contacts found after filtering.")
else:
    print(f"Found {len(contacts)} contacts.")

# Writing contacts to output.csv
output_file = os.path.join(current_dir, "output.csv")
with open(output_file, "w") as f:
    f.write('"Name","Email"\n')
    for line in contacts:
        f.write(line + "\n")

print("Output written to output.csv")

# Writing error contacts to error_context.csv
error_file = os.path.join(current_dir, "error_context.csv")
with open(error_file, "w") as f:
    f.write('"Sender"\n')
    for line in error_contacts:
        f.write(line + "\n")

print("Error contacts written to error_context.csv")

# Log the end time
end_time = datetime.now()
print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

# Calculate the total runtime
elapsed_time = end_time - start_time
minutes, seconds = divmod(elapsed_time.total_seconds(), 60)
print(f"Total time taken: {int(minutes)} minutes and {int(seconds)} seconds.")
