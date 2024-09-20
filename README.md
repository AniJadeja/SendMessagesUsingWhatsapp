# WhatsApp Automation Script

This repository contains a WhatsApp automation script that uses Selenium to automate sending messages to contacts via WhatsApp Web. The script is written in Python and has been tested on **Fedora 40**.

## Prerequisites

Before setting up the project, ensure you have the following tools installed on your **Linux** machine:

1. **Python 3.x** - Make sure Python 3.x is installed.
2. **pip** - Python's package manager.
3. **Google Chrome** - Required for Selenium WebDriver.
4. **ChromeDriver** - Driver required by Selenium to interact with Google Chrome.

Tested on **Fedora 40**, but it should work on other Linux distributions with minor changes.

## Installation

Follow these steps to set up the project:

1. **Clone the Repository**

   Open your terminal and clone this repository to your local machine.

   ```
   git clone https://github.com/your-username/whatsapp-automation.git
   cd whatsapp-automation
   ```
2. **Install python dependencies & Google Chrome & Chrome Driver**
   ```
   pip install selenium
   sudo dnf install chrome driver
   pip install webdriver-manager
   pip install selenium webdriver-manager
   ```
   ```
   sudo dnf install fedora-workstation-repositories
   sudo dnf config-manager --set-enabled google-chrome
   sudo dnf install google-chrome-stable
   ```
3. **Project Structure**
   ```
   ├── main.py                    # Entry point to run the script
   ├── wp_scripts/
   │   │   ├── utils.py               # Utility functions like delay, search, etc.
   │   └── whatsapp.py            # Main automation script for WhatsApp
   ├── store/
   │   └── messageStore.json      # Contacts and messages configuration
   └── logs/
       └── messageLogs.txt        # Log file for tracking sent messages
   ```
4. **Running The Script**
   ```
   python main.py
   ```

5. **Known Issues**
   
  - `WhatsApp Web Login`: If you haven't logged into WhatsApp Web previously, you'll need to log in manually when the script runs for the first time.
  - `Timeout Handling`: If the chat for a contact does not open within the timeout period (3 seconds by default), the script will skip that contact and log an appropriate message in the messageLogs.txt.
  - `Session Expiration`: If your WhatsApp Web session expires or you're logged out, the script won't work until you manually log in again.

6. **Note**

  - This script is developed and tested on Fedora 40 and assumes that user is familiar with linux.
  - As of now, it has some paths hard coded tailored to linux env only.
