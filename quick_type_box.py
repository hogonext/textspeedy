import ttkbootstrap as ttk
from ttkbootstrap.constants import *

import helper

quick_type = False


def on_esc_key(event):
    if event.keysym == 'Escape':
        root.destroy()


def on_focus_out(event):
    if event.widget == searchbox:
        root.destroy()


def show_window():
    root.deiconify()


def run_command(event):
    global quick_type

    shortcut = searchbox.get()

    print(shortcut)
    data = helper.db.search_by_shortcut(shortcut)

    if shortcut.lower() == data[6].lower():  # paste snippet
        content = data[3]

        if (data != None):
            output = helper.execute(content)


def show_popup(event=None):
    global popup

    if popup:
        popup.destroy()

    word = searchbox.get()
    if word:

        data = helper.json_to_array(helper.search_json('shortcuts.json', word))

        converted_array = [f"{item[0]} {item[1]}" for item in data]

        suggestions = [
            brand for brand in converted_array if word.lower() in brand.lower()]

    if not suggestions:
        return

    popup = ttk.Toplevel(root)
    popup.overrideredirect(True)
    popup.geometry(f"+{x}+{y+50}")
    popup.geometry("400x200")

    # Tạo Treeview
    treeview = ttk.Treeview(popup, columns=(
        "Shortcut", "File Path"), show="headings")
    treeview.heading("Shortcut", text="Shortcut", anchor='w')
    treeview.heading("File Path", text="File Path", anchor='w')

    treeview.column("Shortcut", width=60, anchor='w')
    treeview.column("File Path", width=250, anchor='w')

    # Tạo Scrollbar
    scrollbar = ttk.Scrollbar(popup, orient="vertical", command=treeview.yview)
    treeview.configure(yscrollcommand=scrollbar.set)

    treeview.bind("<KeyPress>", on_esc_key)  # Bind to escape key

    # Đặt Treeview và Scrollbar vào Frame
    treeview.pack(side=ttk.LEFT, expand=True, fill=ttk.BOTH)
    scrollbar.pack(side=ttk.RIGHT, fill=ttk.Y)

    # Chèn dữ liệu vào Treeview
    for suggestion in suggestions:
        parts = suggestion.split(' ', 1)  # Tách chuỗi thành hai phần
        treeview.insert("", "end", values=(parts[0], parts[1]))

    treeview.pack(padx=5, pady=5)


popup = None  # Initialize popup variable

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
searchbox.configure(font=('TkDefaultFont', 11))
# Load the search icon image (replace 'search_icon.png' with your image path)
search_icon = ttk.PhotoImage(file='image/search32px.png')

# Create a label to display the icon
icon_label = ttk.Label(searchbox, image=search_icon)
icon_label.pack(side="right")  # Place the icon on the right side

# Set focus on the entry widget
searchbox.focus_set()

# Bind the focus out event to the entry widget
#searchbox.bind("<FocusOut>", on_focus_out)
searchbox.bind("<KeyRelease>", show_popup)
searchbox.bind('<KeyRelease-Return>', run_command)

root.geometry("400x60")
root.update_idletasks()

# Calculate the offset to center the window
x = (root.winfo_screenwidth() - root.winfo_width()) // 2
y = (root.winfo_screenheight() - root.winfo_height()) // 3
root.geometry(f"+{x}+{y}")

root.mainloop()
