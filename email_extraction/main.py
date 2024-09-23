import mailbox
import os
import sys
import time
from datetime import datetime
from multiprocessing import Pool, cpu_count, Value
import csv
from itertools import islice

def process_message(message):
    try:
        sender = message["from"]
        if not sender:
            return None

        if "<" in sender:
            name = sender.split("<")[0].strip()
            email = sender.split("<")[1].replace(">", "").strip()
        else:
            name = sender.strip()
            email = sender.strip()

        email_lower = email.lower()

        if any(term in email_lower for term in EXCLUDE_TERMS) or not any(
            term in email_lower for term in INCLUDE_TERMS
        ):
            return ("ignored", f"{name},{email}")

        return ("contact", f"{name},{email}")
    except Exception as e:
        return ("error", str(sender))

def process_chunk(chunk):
    contacts = set()
    ignored = set()
    errors = set()

    for message in chunk:
        result = process_message(message)
        if result:
            category, data = result
            if category == "contact":
                contacts.add(data)
            elif category == "ignored":
                ignored.add(data)
            elif category == "error":
                errors.add(data)

    return contacts, ignored, errors

def chunked_iterable(iterable, size):
    it = iter(iterable)
    while True:
        chunk = tuple(islice(it, size))
        if not chunk:
            break
        yield chunk

def init_worker(counter):
    global processed_chunks
    processed_chunks = counter

def update_progress(result):
    with processed_chunks.get_lock():
        processed_chunks.value += 1
    progress = processed_chunks.value / total_chunks * 100
    print(f"\rProgress: {progress:.2f}%", end="", flush=True)

if __name__ == "__main__":
    EXCLUDE_TERMS = {
        "noreply", "no-reply", "info", "notifications", "help", "vosyn.ai",
        "hello", "team", "alerts", "research", "onlineservices", "invoice",
        "marketing", "notification", "docusign", "dse", "reply", "notion",
        "donotreply", "support", "newsletter", "sales", "contact", "admin",
        "inquiries", "service", "billing", "orders", "accounts", "offers",
        "promo", "deals", "subscriptions", "customerservice", "registrations",
        "feedback", "services", "events", "careers", "jobs", "press", "media",
        "partners", "webmaster", "postmaster", "notify", "do-not", "no.reply",
        "recruiting", "hr", "talent", "cv", "placements", "livehire", "linkedin",
        "indeed", "myworkday", "breezy-mail", "hiring", "staffing", "staples",
        "git", "lever", "hire", "immigration", "invite", "team", "dell", "paypal",
        "coursera", "godaddy", "do-no-reply", "no-reply", "SystemMessage",
        "system", "SystemMessages", "notifications", "recruitment", "recruit",
        "recruiter", "recruiters", "recruitments", "recommendations",
        "recommendation", "recommend"
    }

    INCLUDE_TERMS = {
        "gmail", "yahoo", "outlook", "hotmail", "icloud", "aol", "gmx",
        "protonmail", "zoho", "yandex", "live", "me", "fastmail", "msn",
        "qq", "naver", "rediffmail", "tutanota"
    }

    start_time = datetime.now()
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    if getattr(sys, "frozen", False):
        current_dir = os.path.dirname(sys.executable)
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))

    mbox_file = "inbox.mbox"
    mbox_path = os.path.join(current_dir, mbox_file)

    print("Loading MBOX file...")
    mbox = mailbox.mbox(mbox_path)

    num_processes = cpu_count()
    chunk_size = 100
    total_messages = len(mbox)
    total_chunks = (total_messages + chunk_size - 1) // chunk_size

    print(f"Processing {total_messages} messages using {num_processes} processes...")

    all_contacts = set()
    all_ignored = set()
    all_errors = set()

    processed_chunks = Value('i', 0)

    with Pool(processes=num_processes, initializer=init_worker, initargs=(processed_chunks,)) as pool:
        results = pool.imap_unordered(process_chunk, chunked_iterable(mbox, chunk_size))
        
        for result in results:
            contacts, ignored, errors = result
            all_contacts.update(contacts)
            all_ignored.update(ignored)
            all_errors.update(errors)
            update_progress(result)

    print("\nProcessing complete.")
    print(f"Found {len(all_contacts)} contacts.")

    output_file = os.path.join(current_dir, "output.csv")
    with open(output_file, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Email"])
        for contact in all_contacts:
            writer.writerow(contact.split(','))

    print("Output written to output.csv")

    ignored_file = os.path.join(current_dir, "ignored.csv")
    with open(ignored_file, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Email"])
        for ignored in all_ignored:
            writer.writerow(ignored.split(','))

    print("Ignored contacts written to ignored.csv")

    error_file = os.path.join(current_dir, "error_context.csv")
    with open(error_file, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Sender"])
        for error in all_errors:
            writer.writerow([error])

    print("Error contacts written to error_context.csv")

    end_time = datetime.now()
    print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

    elapsed_time = end_time - start_time
    minutes, seconds = divmod(elapsed_time.total_seconds(), 60)
    print(f"Total time taken: {int(minutes)} minutes and {int(seconds)} seconds.")