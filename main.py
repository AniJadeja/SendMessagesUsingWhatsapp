import logging
import csv

# User imports
from wp_scripts.whatsapp import send_messages

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', handlers=[
    logging.FileHandler("./logs/messageLogs.txt"),
    logging.StreamHandler()
])
logger = logging.getLogger(__name__)

def load_contacts_from_csv(csv_file_path):
    """Load contacts from a CSV file and return a list of dictionaries."""
    contacts = []
    with open(csv_file_path, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            contact = {
                "Name": row["Name"],
                "Phone_Number": row["Phone_Number"]
            }
            contacts.append(contact)
    return contacts

if __name__ == "__main__":
    import json

    # Load contacts from the CSV file (updated format)
    contacts = load_contacts_from_csv('./store/data.csv')

    # Load message template from external JSON file
    with open('./store/messageTemplate.json', 'r') as f:
        template_data = json.load(f)
        sender_name = template_data["SenderName"]
        message_template = template_data["Message"]

    # Send messages using the template and contact information
    send_messages(contacts, message_template, sender_name, keep_open=False, open_browser=True)
