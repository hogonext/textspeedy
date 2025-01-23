import ttkbootstrap as ttk
from ttkbootstrap.constants import *

import helper
import pyperclip
import time

from pynput import keyboard
from pynput.keyboard import Key, Controller

keys = []

kb = Controller()

quick_type = False

def on_esc_key(event):
    if event.keysym == 'Escape':
        root.destroy()

def on_focus_out(event):
    if event.widget == searchbox:
        root.destroy()

def show_window():
    root.deiconify()

def on_press(key):
    global quick_type 

    if hasattr(key, 'char'):
        try:
            # Alphanumeric key (handling the case of '/' is inside the try-except block)
            if key.char == '/':
                keys.clear()
            elif key.char.isalnum() or key.char == '.':
                keys.append(key.char)

        except AttributeError:
            # Handle the case where `key` doesn't have a `char` attribute
            print("Error: Key does not have a 'char' attribute.")

        except Exception as e:  # Catch any other unexpected exceptions
            print(f"An unexpected error occurred: {e}")
    else:
        # Special key
        if key == keyboard.Key.space:
            shortcut = listToString(keys)
            is_runcommand = False

            if shortcut.startswith('.'):
                is_runcommand = True
                shortcut = shortcut[1:]  # remove first char

            data = helper.db.search_by_shortcut(shortcut)

            if (data != None and shortcut != ''):
                if shortcut.lower() == data[6].lower():  # paste snippet
                    content = data[3]

                    if is_runcommand == True:  # run command
                        old_shortcut = '.' + shortcut
                        delText(old_shortcut)
                        output = helper.execute(content)
                        print(output)
                        copy_paste(output)
                    else:  # paste content of shortcut
                        delText(shortcut)

                        copy_paste(content)

            keys.clear()

        elif key == keyboard.Key.enter:
            keys.clear()

def copy_paste(content):
    pyperclip.copy(content)
    # Retrieve the text from the clipboard
    pasted_text = pyperclip.paste()
    # Press and release Ctrl+V
    with kb.pressed(Key.ctrl):
        kb.press('v')
        kb.release('v')
    time.sleep(1)
    pyperclip.copy('')

    # Add other special keys as needed


def listToString(s):
    # Initialize an empty string
    str1 = ""
    # Ensure s is a list or tuple of strings
    if isinstance(s, (list, tuple)):
        # Return string
        return str1.join(s)
    else:
        raise ValueError("The argument must be an iterable of strings")

def delText(s):
    for i in range(len(s)+2):
        kb.press(Key.backspace)
        kb.release(Key.backspace)

def show_popup(event=None):
    global popup

    if popup:
        popup.destroy()

    word = searchbox.get()
    print(word)    
    if word:
        data = helper.db.search_note_item_by_title_for_treeview(searchbox.get())


        car_brands = ["Toyota", "Honda", "Ford", "Chevrolet", "BMW", "Mercedes-Benz",
                    "Audi", "Nissan", "Hyundai", "Kia", "Volkswagen", "Volvo", "Mazda"]
        converted_array = [f"{item[2]} {item[1]}" for item in data]
        print(converted_array)

        suggestions = [brand for brand in converted_array if word.lower() in brand.lower()]
        #suggestions = [brand for brand in car_brands if word.lower() in brand.lower()]
        print(suggestions)

    if not suggestions:
        return

    popup = ttk.Toplevel(root)
    popup.overrideredirect(True)
    popup.geometry(f"+{x}+{y+50}")
    popup.geometry("400x200")

    # Tạo Treeview
    treeview = ttk.Treeview(popup, columns=("Shortcut", "Title"), show="headings")
    treeview.heading("Shortcut", text="Shortcut", anchor='w')
    treeview.heading("Title", text="Title", anchor='w')

    treeview.column("Shortcut", width=60, anchor='w')
    treeview.column("Title", width=250, anchor='w')

    treeview.pack(expand=True, fill=ttk.BOTH)

    # Chèn dữ liệu vào Treeview
    for suggestion in suggestions:
        parts = suggestion.split(' ', 1)  # Tách chuỗi thành hai phần
        treeview.insert("", "end", values=(parts[0], parts[1]))

    treeview.pack(padx=5, pady=5)

popup = None  # Initialize popup variable


# Set up the listener in a non-blocking fashion
listener = keyboard.Listener(on_press=on_press)
listener.start()

# Create the main window
root = ttk.Window(themename="darkly")
root.bind("<KeyPress>", on_esc_key)  # Bind to any key press


# Create a frame for the title bar (though we won't use it for a button)
title_bar = ttk.Frame(root)
title_bar.pack(fill=X)

# Hide the title bar
root.overrideredirect(True)

# Create an input box
searchbox = ttk.Entry(root)
searchbox.pack(padx=10, pady=10, fill="x")
# Initially set a larger font size
searchbox.configure(font=('TkDefaultFont', 12))
# Load the search icon image (replace 'search_icon.png' with your image path)
search_icon = ttk.PhotoImage(file='image/search24px.png')

# Create a label to display the icon
icon_label = ttk.Label(searchbox, image=search_icon)
icon_label.pack(side="right")  # Place the icon on the right side

# Set focus on the entry widget
searchbox.focus_set()

# Bind the focus out event to the entry widget
searchbox.bind("<FocusOut>", on_focus_out)
searchbox.bind("<KeyRelease>", show_popup)

root.geometry("400x50")
root.update_idletasks()

# Calculate the offset to center the window
x = (root.winfo_screenwidth() - root.winfo_width()) // 2
y = (root.winfo_screenheight() - root.winfo_height()) // 3
root.geometry(f"+{x}+{y}")

root.mainloop()