from dotenv import load_dotenv
from bs4 import BeautifulSoup
import os
import imaplib
import email
import requests

load_dotenv()

username = os.getenv("EMAIL")
password = os.getenv("PASSWORD")

def connect_to_gmail():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(username, password)
    mail.select("inbox")
    return mail


def click_link(link):
    try:
        response = requests.get(link)
        if response.status_code == 200:
            print(f"Clicked visited: {link}")
        else:
            print(f"Failed to visit: {link}, error code: {response.status_code}")
    except Exception as e:
        print(f"Failed to click: {link}, error: {e}")


def extract_links_from_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    unsubscribe_links =[link["href"] for link in soup.find_all("a", href=True) if "unsubscribe" in link["href"].lower()]
    return unsubscribe_links

def search_for_emails():
    mail = connect_to_gmail()
    _, search_data = mail.search(None, '(BODY "unsubscribe")')
    data = search_data[0].split()

    links = []

    for num in data:
        _, data = mail.fetch(num, "(RFC822)")
        msg = email.message_from_bytes(data[0][1])

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    html_content = part.get_payload(decode=True).decode()
                    links.extend(extract_links_from_html(html_content))
        else:
            content_type = msg.get_content_type()
            content = msg.get_payload(decode=True).decode()

            if content_type == "text/html":
                links.extend(extract_links_from_html(content))

    mail.logout()
    return links

def save_links(links):
    with open("links.txt","w") as file:
        file.write("\n".join(links))

email_links = search_for_emails()
for link in email_links:
    click_link(link)

save_links(email_links)