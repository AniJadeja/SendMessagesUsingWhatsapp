import mailbox
import os
import sys

# Automatically use the .mbox file in the same directory as the script
mbox_file = 'inbox.mbox'  # Replace with your mbox file name

# Determine the directory where the executable is located
if getattr(sys, 'frozen', False):
    current_dir = os.path.dirname(sys.executable)  # Executable path
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Script path

mbox_path = os.path.join(current_dir, mbox_file)

print(f"Reading mbox file: {mbox_path}")
print(f"Current directory: {current_dir}")

mbox = mailbox.mbox(mbox_path)

contacts = set()

# Iterate through all the messages in the MBOX file
for message in mbox:
    sender = message['from']
    name = sender.split("<")[0].strip()
    email = sender.split("<")[1].replace(">", "").strip()
    contact = f"{name},{email}"
    contacts.add(contact)
    print(f"Added contact: {contact}")
    break  # Only process the first message

print("Contacts extracted:")
for contact in contacts:
    print(contact)

print("Writing contacts to output.csv")
# Write to output.csv
output_file = os.path.join(current_dir, 'output.csv')
with open(output_file, 'w') as f:
    print("Writing header to output.csv")
    f.write('"Name","Email"\n')
   
    for line in contacts:
        print(" line: ", line, " contacts: ", contacts)
        print(f"Writing: {line}")
        f.write(line + '\n')

print("Output written to output.csv")

# Print output.csv file itself
with open(output_file, 'r') as f:
    print(f.read())
