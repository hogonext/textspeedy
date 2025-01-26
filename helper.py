import sys
import io
import os
import os
import json
import tempfile
import re
from collections import OrderedDict

import requests

import base64
import xml.etree.ElementTree as ET

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

import webbrowser
from urllib.parse import quote
import html
from html.parser import HTMLParser

from datetime import datetime
from tkinter.font import Font

from database import Database

executable_apps = {}

db = Database()

settings_path = 'data/settings.json'

def get_theme():
    theme = get_json_value(settings_path,'Theme')
    if theme == 'dark':
        return "darkly"
    else:  # light
        return "yeti"


# Function to count words in the Text widget
def count_words(content):

    if content is None:
        return 0
    # Split the text into words and filter out any empty strings
    words = [word for word in content.split() if word]
    word_count = len(words)
    return word_count


def execute(code):
    try:
        # Create a stream to capture stdout
        original_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        # sys.stdout = captured_output = []

        # Execute the provided code
        # exec(code)

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as tmp:
            tmp.write(code)
            tmp_name = tmp.name

        try:
            os.system(f"python {tmp_name}")
        finally:
            os.remove(tmp_name)

        # Restore the original stdout
        sys.stdout = original_stdout

        # Join the captured output into a single string
        output_string = captured_output.getvalue()
        return output_string
    except Exception as e:
        return f"An error occurred: {e}"


def get_local_date_time():
    # Get the current local date and time
    current_datetime = datetime.now()
    # Convert to the specified format
    return current_datetime.strftime('%Y-%m-%d %H:%M:%S')


def listToString(s):
    # Initialize an empty string
    str1 = ""
    # Ensure s is a list or tuple of strings
    if isinstance(s, (list, tuple)):
        # Return string
        return str1.join(s)
    else:
        raise ValueError("The argument must be an iterable of strings")


def highlight_lines_with_hashes(text_widget):
    # Configure a tag for lines starting with '# ' followed by a space
    text_widget.tag_configure("hash_line", foreground="green")

    # Get the content of the Text widget
    content = text_widget.get("1.0", "end").splitlines()

    # Iterate through each line
    for i, line in enumerate(content):
        stripped_line = line.strip()
        if stripped_line.startswith("# ") or stripped_line.startswith("## ") or stripped_line.startswith("### ") or stripped_line.startswith("#### ") or stripped_line.startswith("##### ") or stripped_line.startswith("###### "):
            # Apply the tag to the line
            text_widget.tag_add("hash_line", f"{i+1}.0", f"{i+1}.end")


def highlight_bold(text_widget):
    # Define a tag for blue bold text
    orange_bold_font = Font(
        text_widget, text_widget.cget("font"), weight="bold")
    text_widget.tag_configure(
        "orange_bold", foreground="orange", font=orange_bold_font)

    # Search for the pattern and apply the tag
    start = "1.0"
    while True:
        # Find the start of the pattern
        start_index = text_widget.search(r'\*\*', start, tk.END, regexp=True)
        if not start_index:
            break
        # Find the end of the pattern
        end_index = text_widget.search(
            r'\*\*', start_index + "+2c", tk.END, regexp=True)
        if not end_index:
            break
        # Apply the tag to the text between the patterns
        text_widget.tag_add("orange_bold", start_index + "+2c", end_index)
        # Update the start position
        start = end_index + "+2c"


def highlight_italic(text_widget):
    # Define a tag for orange italic text
    blue_italic_font = Font(
        text_widget, text_widget.cget("font"), slant="italic")
    text_widget.tag_configure(
        "blue_italic", foreground="blue", font=blue_italic_font)

    # Search for the pattern and apply the tag
    start = "1.0"
    while True:
        # Find the start of the pattern
        start_index = text_widget.search(
            r'_(\S+?)_', start, tk.END, regexp=True)
        if not start_index:
            break
        # Find the end of the pattern
        end_index = text_widget.search('_', start_index + "+1c", tk.END)
        if not end_index:
            break
        # Apply the tag to the text between the underscores
        text_widget.tag_add("blue_italic", start_index, end_index + "+1c")
        # Update the start position
        start = end_index + "+2c"


def highlight_markdown(text_widget):
    highlight_lines_with_hashes(text_widget)
    highlight_bold(text_widget)
    highlight_italic(text_widget)


def strip_tags(html):
    # This inner function will be called when data is encountered
    def handle_data(parser, data):
        text.append(data)

    # Initialize a list to store parsed text
    text = []
    # Create a new parser instance
    parser = HTMLParser()
    # Assign the handle_data function to the parser's data handler
    parser.handle_data = lambda data: handle_data(parser, data)
    # Feed the HTML content to the parser
    parser.feed(html)
    # Return the joined parsed text
    return ''.join(text)


def open_email_client(subject, recipient, body):
    """
    Opens the default email client with a new email draft.

    Args:
        subject (str): The subject line of the email.
        recipient (str): The recipient's email address.
        body (str): The email content in HTML format.

    Returns:
        None
    """
    # Convert HTML body content to plain text
    plain_text_body = strip_tags(html.unescape(body))

    # Encode the plain text body to properly format it for the mailto link
    encoded_body = quote(plain_text_body)

    mailto_link = f"mailto:{recipient}?subject={subject}&body={encoded_body}"
    webbrowser.open(mailto_link)


def publish_WP(url, username, password, title, status, category, content):

    url = url + 'posts'

    credentials = username + ':' + password
    cred_token = base64.b64encode(credentials.encode())

    header = {'Authorization': 'Basic ' + cred_token.decode('utf-8')}

    post = {
        'title': title,
        'status': status,
        'content': content,
        'categories': category,

    }

    response = requests.post(url, headers=header, json=post)

    print(response)


def get_website_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def capitalize_each_word(text):
    return '\n'.join(' '.join(word.capitalize() for word in line.split()) for line in text.splitlines())


def remove_duplicate_lines(text):
    lines_seen = set()
    result = []
    for line in text.splitlines():
        if line not in lines_seen:
            result.append(line)
            lines_seen.add(line)
    return '\n'.join(result)


def remove_empty_lines(text):
    return '\n'.join(line for line in text.splitlines() if line.strip())


def remove_line_breaks(text):
    pattern = r"(?<!\n)\n"
    return re.sub(pattern, " ", text)


def extract_emails(text):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return '\n'.join(emails)


def extract_all_phone_numbers(text):
    phone_pattern = r'\+?\d+(?:[- (]+\d+\)?)+'
    phone_numbers = re.findall(phone_pattern, text)
    return '\n'.join(phone_numbers)


def extract_urls(text):
    # Regular expression pattern for matching URLs
    # This pattern is fairly comprehensive but can be customized
    url_pattern = re.compile(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    )

    urls = re.findall(url_pattern, text)

    # Use OrderedDict to maintain insertion order of unique URLs
    unique_urls = OrderedDict.fromkeys(urls)

    result_string = "\n".join(unique_urls)
    return result_string


def extract_links_from_sitemaps(sitemap_urls):
    print(sitemap_urls)
    all_links = []  # Initialize an empty list to store all extracted links
    for sitemap_url in sitemap_urls:
        response = requests.get(sitemap_url)
        print(sitemap_url)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            links = [element.text for element in root.findall(
                './/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
            # Add the links from this sitemap to the overall list
            all_links.extend(links)
        else:
            print(f"Failed to retrieve the sitemap at {
                  sitemap_url}: HTTP {response.status_code}")

    # Join all the links into a single string
    all_links_string = '\n'.join(all_links)
    return all_links_string


def clear_treeview(treeview):
    for item in treeview.get_children():
        treeview.delete(item)


def center_window(win, width, height):
    # Get screen width and height
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()

    # Calculate center coordinates
    x = int((screen_width - width) / 2)
    y = int((screen_height - height) / 2)

    # Set window position
    win.geometry(f"{width}x{height}+{x}+{y}")


def apply_vscode_dark_theme(root):
    # Define the colors for the VSCode dark theme
    dark_bg = '#1E1E1E'  # Dark background color, similar to VSCode's default dark theme
    light_fg = '#D4D4D4'  # Light foreground color, similar to VSCode's default text color
    # Dark foreground color for less emphasis, similar to VSCode's comments color
    dark_fg = '#808080'
    # Background color for selected items, similar to VSCode's selection color
    select_bg = '#264F78'
    select_fg = '#FFFFFF'  # Foreground color for selected items

    # Configure the style for the dark theme
    style = ttk.Style(root)
    # 'clam' theme provides a good base for customization
    style.theme_use('clam')

    # Configure styles for different widgets
    style.configure('TButton', background=dark_bg,
                    foreground=light_fg, borderwidth=1)
    style.map('TButton', background=[
              ('active', select_bg)], foreground=[('active', select_fg)])

    style.configure('TLabel', background=dark_bg, foreground=light_fg)
    style.configure('TMenu', background=dark_bg, foreground=light_fg)
    style.configure('TEntry', background=dark_bg,
                    foreground=light_fg, fieldbackground=dark_fg)
    style.configure('TCombobox', background=dark_bg,
                    foreground=light_fg, fieldbackground=dark_fg)
    style.configure('TCheckbutton', background=dark_bg, foreground=light_fg)
    style.configure('TRadiobutton', background=dark_bg, foreground=light_fg)

    style.configure('Treeview', background=dark_bg,
                    foreground=light_fg, fieldbackground=dark_fg)
    style.map('Treeview', background=[('selected', select_bg)], foreground=[
              ('selected', select_fg)])

    style.configure('Vertical.TScrollbar',
                    background=dark_bg, troughcolor=dark_fg)
    style.configure('Horizontal.TScrollbar',
                    background=dark_bg, troughcolor=dark_fg)

    # Function to apply the theme to Text and ScrolledText widgets
    def apply_text_theme(widget):
        if isinstance(widget, (tk.Text, ScrolledText)):
            widget.config(bg=dark_bg, fg=light_fg, insertbackground=light_fg,
                          selectbackground=select_bg, selectforeground=select_fg)
        for child in widget.winfo_children():
            apply_text_theme(child)

    # Apply the theme to all Text and ScrolledText widgets
    apply_text_theme(root)


def plaintext_to_html(text):
    """Converts plaintext to HTML, preserving newlines and escaping special characters.

    Args:
      text: The plaintext string to convert.

    Returns:
      A string containing the HTML representation of the plaintext.
    """

    html_text = text.replace("&", "&amp;")
    # html_text = html_text.replace("<", "&lt;")
    # html_text = html_text.replace(">", "&gt;")
    html_text = html_text.replace("\n", "<br>\n")
    return f"<p>{html_text}</p>"


def scan_all_executables(output_file="executables.json"):
    """Scans all drives and directories on Windows for executable files
    and saves their names and paths to a JSON file.

    Args:
      output_file: The name of the JSON file to save the results.
    """

    executables = []
    for drive in range(ord('A'), ord('Z') + 1):  # Check drives from A to Z
        drive_letter = chr(drive)
        drive_path = drive_letter + ":\\"
        if os.path.exists(drive_path):
            for root, _, files in os.walk(drive_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file.lower().endswith(('.exe', '.bat', '.cmd', '.com', '.ps1')):
                        executables.append({
                            "name": file,
                            "path": file_path
                        })

    with open(output_file, 'w') as f:
        json.dump(executables, f, indent=2)

    print(f"Executable information saved to {output_file}")


# --- File Operations ---
def read_json_file(filename="settings.json"):
    """Reads data from a JSON file.

    Args:
      filename: The name of the JSON file.

    Returns:
      A Python dictionary containing the data from the JSON file.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return None


def write_json_file(data, filename="settings.json"):
    """Writes data to a JSON file.

    Args:
      data: The data to write, typically a dictionary.
      filename: The name of the JSON file.
    """
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)  # indent for pretty printing


# --- Search Operations ---
def search_in_json_object(data, search_key):
    """Searches for a key in a JSON object (dictionary).

    Args:
      data: The JSON object (dictionary).
      search_key: The key to search for.

    Returns:
      The value associated with the key if found, otherwise None.
    """
    if search_key in data:
        return data[search_key]
    else:
        return None


def search_in_json_array(data, search_key, search_value):
    """Searches for a value associated with a key in a JSON array of objects.

    Args:
      data: The JSON array of objects.
      search_key: The key to search within each object.
      search_value: The value to search for.

    Returns:
      The object where the key-value pair is found, otherwise None.
    """
    for item in data:
        if item.get(search_key) == search_value:
            return item
    return None


def update_json_value(filename, key, new_value):
    """Updates a single setting in a JSON file with the structure {key: value}.

    Args:
      filename: The name of the JSON file.
      key: The key of the setting to update.
      new_value: The new value for the setting.
    """
    try:
        # 1. Read the existing settings
        with open(filename, 'r', encoding='utf-8') as f:
            settings = json.load(f)

        # 2. Update the specific key
        if key in settings:
            settings[key] = new_value
        else:
            print(f"Key '{key}' not found in settings.")

        # 3. Write the updated settings back to the file
        with open(filename, 'w') as f:
            json.dump(settings, f, indent=2)

    except FileNotFoundError:
        print(f"File '{filename}' not found.")


def get_json_value(filename, key):
    """Gets the value of a specific key from a JSON file with the structure {key: value}.

    Args:
      filename: The name of the JSON file.
      key: The key to retrieve the value for.

    Returns:
      The value associated with the key if found, otherwise None.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            file = json.load(f)

        if key in file:
            return file[key]
        else:
            print(f"Key '{key}' not found in settings.")
            return None

    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return None


def search_executables(search_key):
    import fnmatch  # For wildcard matching

    """Searches for executables using 'like' logic (with wildcards)
    and returns an array of [name, path] for matching entries.
    """
    json_file = "executables.json"

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            filtered_executables = []
            for line in f:
                try:
                    exe = json.loads(line)
                    for key, value in exe.items():
                        if fnmatch.fnmatch(str(value).lower(), f"*{search_key.lower()}*"):
                            filtered_executables.append(
                                [exe['name'], exe['path']])
                            break
                except json.JSONDecodeError:
                    pass
        return filtered_executables
    except FileNotFoundError:
        print(f"File '{json_file}' not found.")
        return []


def load_executables():
    json_file = "executables.json"

    """Loads executable data from the JSON file into the static variable."""
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
            # Convert list of dictionaries to dictionary with 'name' as key
            list = {exe['name']: exe['path'] for exe in data}
        return list
        print("Executables loaded successfully.")
    except FileNotFoundError:
        print(f"File '{json_file}' not found.")


def dict_to_array(my_dict):
    """Converts a dictionary to an array of [key, value] pairs.

    Args:
      my_dict: The dictionary to convert.

    Returns:
      An array of [key, value] pairs.
    """
    return [[key, value] for key, value in my_dict.items()]


def get_file_content(file_path):
    """
    Reads and returns the content of a file.

    Args:
      file_path: The path to the file.

    Returns:
      The content of the file as a string, or None if an error occurs.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None


def write_to_file(file_path, content, mode="w"):
    """
    Writes content to a file.

    Args:
      file_path: The path to the file.
      content: The content to write to the file.
      mode: The file opening mode.
            "w" (default): Write mode (overwrites the file if it exists).
            "a": Append mode (adds content to the end of the file).
    """
    try:
        with open(file_path, mode) as file:
            file.write(content)
    except OSError as error:
        print(f"Error writing to file: {error}")


def update_file_content(filename, old_string, new_string):
    """
    Updates the content of a file by replacing all occurrences of an old string with a new string.

    Args:
      filename: The path to the file to update.
      old_string: The string to be replaced.
      new_string: The string to replace the old string with.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            file_content = f.read()

        new_content = file_content.replace(old_string, new_string)

        with open(filename, 'w') as f:
            f.write(new_content)

        print(f"File '{filename}' updated successfully.")

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


def add_or_update_key(filename, key, value):

    with open(filename, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    if key in json_data:
        json_data[key] = value
        print(f"Key '{key}' updated with value '{value}'")
    else:
        json_data[key] = value
        print(f"Key '{key}' added with value '{value}'")

    with open(filename, 'w') as f:
        json.dump(json_data, f, indent=2)

    return json_data


def update_json_key(filename, old_key, new_key):
    """
    Checks if a key exists in a JSON object and updates the key if found.

    Args:
      json_data: The JSON data (either a string or a Python object).
      old_key: The existing key to search for.
      new_key: The new key to replace the old key.

    Returns:
      The updated JSON data.
    """

    with open(filename, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    if old_key in json_data:
        json_data[new_key] = json_data.pop(old_key)
        print(f"Key '{old_key}' updated to '{new_key}'")
    else:
        print(f"Key '{old_key}' not found.")

    with open(filename, 'w') as f:
        json.dump(json_data, f, indent=2)

    return json_data


def get_key_by_value(filename, target_value):

    with open(filename, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    found_key = ''

    for key, value in json_data.items():
        if value == target_value:
            found_key = key

    return found_key


def search_json(filename, search_text):
    """
    Searches a JSON object for any matching text in keys or values and returns a list of matching key-value pairs.

    Args:
      json_data: The JSON data to search (dictionary).
      search_text: The text to search for in keys and values.

    Returns:
      A list of matching key-value pairs as tuples.
    """

    with open(filename, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    search_text = search_text.lower()
    results = []

    for key, value in json_data.items():
        if search_text in key.lower() or search_text in str(value).lower():
            results.append((key, value))

    return results


def json_to_array(json_data):
    """
    Converts a JSON object (list or dictionary) to an array of dictionaries.

    Args:
      json_data: The JSON data to convert.

    Returns:
      An array of dictionaries.
    """

    if isinstance(json_data, list):
        return json_data  # Already an array
    elif isinstance(json_data, dict):
        return [json_data]  # Convert single object to array
    else:
        return []  # Not a valid JSON object


def get_content_by_shortcut(shortcut):
    root_dir = os.getcwd() + '/data/'
    shortcuts_path = root_dir + 'shortcuts.json'

    try:
        value = get_json_value(shortcuts_path, shortcut)
        file_path = root_dir + value
    except Exception as e:
        print(f"An error occurred: {e}")

    return get_file_content(file_path)
