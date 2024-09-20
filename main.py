import logging

#user imports
from wp_scripts.whatsapp import send_messages

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', handlers=[
    logging.FileHandler("./logs/messageLogs.txt"),
    logging.StreamHandler()
])
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    import json

    # Load messages from external JSON file
    # user imports
    with open('./store/messageStore.json', 'r') as f:
        messages = json.load(f)

    # Send messages
    send_messages(messages, keep_open=False, open_browser=False)
