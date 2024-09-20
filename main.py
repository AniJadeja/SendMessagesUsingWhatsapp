import logging

# User imports
from wp_scripts.whatsapp import send_messages

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', handlers=[
    logging.FileHandler("./logs/messageLogs.txt"),
    logging.StreamHandler()
])
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    import json

    # Load contacts from the external JSON file (updated format)
    with open('./store/messageStore.json', 'r') as f:
        contacts = json.load(f)

    # Load message template from external JSON file
    with open('./store/messageTemplate.json', 'r') as f:
        template_data = json.load(f)
        sender_name = template_data["SenderName"]
        message_template = template_data["Message"]

    # Send messages using the template and contact information
    send_messages(contacts, message_template, sender_name, keep_open=False, open_browser=True)
