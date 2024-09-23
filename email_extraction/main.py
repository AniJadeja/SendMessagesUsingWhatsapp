import mailbox
import os
import sys
import time

def loader(message, duration=5):
    """Displays a simple loading animation."""
    print(message, end='', flush=True)
    for _ in range(duration):
        print('.', end='', flush=True)
        time.sleep(1)
    print()  # New line after loading

# Automatically use the .mbox file in the same directory as the script
mbox_file = 'inbox.mbox'  # Replace with your mbox file name

# Determine the directory where the executable is located
if getattr(sys, 'frozen', False):
    current_dir = os.path.dirname(sys.executable)  # Executable path
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Script path

mbox_path = os.path.join(current_dir, mbox_file)

# Start the loader
loader("Loading MBOX file ", duration=5)
mbox = mailbox.mbox(mbox_path)
contacts = set()

# Set of terms to exclude from the email addresses (refined)
exclude_terms = {
    'noreply', 'no-reply', 'info', 'notifications', 'help', 'newsletter', 'sales', 'marketing',
    'contact', 'support', 'admin', 'service', 'billing', 'orders', 'accounts', 'offers', 'promo',
    'subscriptions', 'customerservice', 'feedback', 'events', 'careers', 'jobs', 'press', 'media',
    'partners', 'webmaster', 'postmaster', 'notify', 'system', 'do-not', 
    
    # added by ani
    'no.reply', 'recruiting','hr', 'jobs', 'talent', 'cv', 'recruiting', 'placements','livehire', 'linkedin', 
    
    'indeed', 'myworkday','breezy-mail', 'hiring', 'hr', 'staffing', 'staples', 'git', 'donotreply', 'team', 'dell', 'DoNotReply', 'lever', 'hire','donotreply', 'immigration', 'invite',
}

# Set of common personal email domains to include
include_terms = {
    '@gmail', '@yahoo', '@outlook', '@hotmail', '@icloud', '@aol',
    '@yandex', '@live', '@fastmail', '@msn', '@qq', '@naver', '@rediffmail', '@tutanota',
}

# Iterate through all the messages in the MBOX file
for message in mbox:
    sender = message['from']
    if not sender:
        continue  # Skip if sender is None

    # Extract name and email
    if '<' in sender:
        name = sender.split("<")[0].strip()
        email = sender.split("<")[1].replace(">", "").strip()
    else:
        name = sender.strip()
        email = sender.strip()

    # Convert email to lowercase for case-insensitive matching
    email_lower = email.lower()

    # Check if the email meets inclusion and exclusion criteria
    if (any(term in email_lower for term in exclude_terms) or 
        not any(term in email_lower for term in include_terms)):
        continue  # Skip this email

    # Combine name and email to create a unique contact
    contact = f"{name},{email}"
    contacts.add(contact)

# Check if contacts are found
if not contacts:
    print("No contacts found after filtering.")
else:
    print(f"Found {len(contacts)} contacts.")

# Writing contacts to output.csv
output_file = os.path.join(current_dir, 'output.csv')
with open(output_file, 'w') as f:
    f.write('"Name","Email"\n')
    for line in contacts:
        f.write(line + '\n')

print("Output written to output.csv")
