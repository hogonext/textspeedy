import os
import shutil
import sys
import tkinter as tk
import webbrowser
from pystray import MenuItem as item
import pystray
import subprocess
from PIL import Image

from tkinter import Menu, messagebox, simpledialog, END, VERTICAL

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

import settings_dialog
# import url_extractor

import helper
import webview
import markdown

current_version = "1.2"
root_dir = os.getcwd() + '/data/'
shortcuts_path = 'data/shortcuts.json'

selected_node_title = ''
selected_shortcut = ''
selected_note_content = ''

selected_path = ''  # file or folder path


def center_dialog(dialog):
    root.update_idletasks()
    width = dialog.winfo_width()
    height = dialog.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    dialog.geometry(f'+{x}+{y}')


def clear_treeview(treeview):
    for item in treeview.get_children():
        treeview.delete(item)


def treeview_has_items(treeview):
    for item in treeview.get_children():
        return True
    return False


def select_first_item(treeview):
    # Assuming 'tree' is your Treeview widget
    if treeview_has_items(treeview) == False:
        return
    # Get the ID of the first item
    first_item = treeview.get_children()[0]
    # Set the focus to the first item
    treeview.focus(first_item)
    # Change the selection to the first item
    treeview.selection_set(first_item)


def update_editor(editor, new_content):
    # Clear the current content
    editor.delete('1.0', tk.END)
    # Insert the new content
    editor.insert('1.0', new_content)

    helper.highlight_markdown(editor)


def on_text_change(event):
    global selected_path, selected_shortcut, selected_note_content

    try:
        selected_note_content = editor.get("1.0", "end-1c")
        helper.write_to_file(selected_path, selected_note_content)
        helper.highlight_markdown(editor)
        update_status_label('')

    except Exception as e:
        print(f"An error occurred: {e}")


def update_shortcut(event):
    global selected_path, selected_shortcut, selected_node_title, shortcuts_path

    new_shortcut = simpledialog.askstring(
        title="Update shortcut", prompt="Enter new shortcut:\t\t\t", initialvalue=selected_shortcut
    )

    if new_shortcut != None and new_shortcut != "":
        # helper.update_json_key(shortcuts_path, selected_shortcut, new_shortcut)
        print(new_shortcut)
        helper.add_or_update_key(
            shortcuts_path, new_shortcut, selected_path.replace(root_dir, ''))
        selected_shortcut = new_shortcut

        clear_treeview(treeview)
        populate_treeview(treeview, '', root_dir)


def on_right_click_treeview(event):
    # Identify the row clicked
    row_id = treeview.identify_row(event.y)
    if row_id:
        # Set the selection to the row where the right click occurred
        treeview.selection_set(row_id)
    # Display the popup menu
    try:
        popup_menu_treeview.tk_popup(event.x_root, event.y_root, 0)
    finally:
        # Release the grab (for Tk 8.0a1 only)
        popup_menu_treeview.grab_release()


def on_right_click_editor(event):
    try:
        popup_menu_text.tk_popup(event.x_root, event.y_root, 0)
    finally:
        popup_menu_text.grab_release()


def on_left_click_editor(event):
    editor.focus_set()
    update_status_label('mouse')


def update_status_label(event_type):

    content = editor.get("1.0", tk.END)

    word_count = str(helper.count_words(content))

    # Get the index of the last character in the Text widget
    last_char_index = editor.index('end-1c')
    # Extract the line number from the index
    total_lines = last_char_index.split('.')[0]

    if (event_type == 'mouse'):
        cursor_position = editor.index(tk.CURRENT)  # Get the cursor position
    else:  # keyboard
        cursor_position = editor.index(tk.INSERT)  # Get the cursor position
    line, _ = cursor_position.split('.')  # Extract the line number

    info = "File: " + selected_node_title + " | " + "Shortcut: " + selected_shortcut

    info = info + " | " + "Words: " + word_count + \
        " | " + " | " + "Lines: " + total_lines

    info = info + " | " + "Key Cursor at line: " + str(line)

    status_label.config(text=info)


def live_preview(event):
    content = editor.get("1.0", "end-1c")

    html_content = markdown.markdown(content)

    window = webview.create_window(
        'Live Preview', html=html_content, width=1024, height=768, zoomable=True)
    webview.start()


def run_code(event):
    content = editor.get("1.0", "end-1c")
    output = helper.execute(content)
    print(output)


def run_code_live_output(event):
    content = editor.get("1.0", "end-1c")
    output = helper.execute(content)
    output = helper.plaintext_to_html(output)
    print(output)
    window = webview.create_window(
        'Live Preview', html=output, width=1024, height=768, zoomable=True)
    webview.start()


def send_emai(event):
    global selected_node_title, selected_note_content

    helper.open_email_client(selected_node_title, '', selected_note_content)


def publish_WP(event):
    global selected_node_title, selected_note_content

    url = helper.db.get_settings_by_key('WP_URL')[0]
    username = helper.db.get_settings_by_key('WP_Username')[0]
    password = helper.db.get_settings_by_key('WP_Password')[0]

    helper.publish_WP(url, username, password,
                      selected_node_title, 'draft', 1, selected_note_content)

    messagebox.showinfo('Publish Wordpress',
                        'This note is published successfully')


def display_about(event):
    content = 'Version:' + current_version + "\n" + \
        "Website: https://hogonext.com/textspeedy"
    messagebox.showinfo('TextSpeedy', content)


def display_text_utility(event):
    import text_utility
    text_utility.display()


def display_settings_dialog(event):
    settings_dialog.display()


def populate_treeview(tree, parent, path):
    global shortcuts_path
    text_formats = ('.md', '.txt', '.py', '.json', 'html', 'css', 'js')

    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            node = tree.insert(parent, 'end', text=item, open=False)
            populate_treeview(tree, node, item_path)
        elif item_path.endswith(text_formats):
            value = item_path.replace(root_dir, '').replace('\\', '/')
            shortcut = helper.get_key_by_value(shortcuts_path, value)
            tree.insert(parent, 'end', text=item, values=(f"{shortcut}"))


def filter_tree(tree, path, search_text=""):
    global shortcuts_path
    """
    Handles treeview population and filtering for files and directories.

    Args:
        tree: The ttk.Treeview widget.
        path: The path to the directory to display.
        search_text: The text to filter the tree by.
    """

    text_formats = ('.md', '.txt', '.py', '.json', '.html', '.css', '.js')

    def populate_treeview(parent, path):
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                if search_text.lower() in item.lower():
                    node = tree.insert(parent, 'end', text=item, open=False)
                    populate_treeview(node, item_path)
                else:
                    # Check if any children match the search text
                    has_matching_children = False
                    for child in os.listdir(item_path):
                        if search_text.lower() in child.lower():
                            has_matching_children = True
                            break
                    if has_matching_children:
                        node = tree.insert(
                            parent, 'end', text=item, open=False)
                        populate_treeview(node, item_path)
            elif item_path.endswith(text_formats):
                if search_text.lower() in item.lower():
                    value = item_path.replace(root_dir, '').replace('\\', '/')
                    shortcut = helper.get_key_by_value(shortcuts_path, value)
                    tree.insert(parent, 'end', text=item,
                                values=(f"{shortcut}"))

    tree.delete(*tree.get_children())  # Clear the treeview
    populate_treeview('', path)


def create_new_folder_at_root_level(tree, path):
    selected_path = os.path.join(path, root_dir)
    if os.path.isdir(selected_path):
        new_folder_name = simpledialog.askstring(
            "New Folder", "Enter folder name:\t\t\t\t\t", initialvalue='New folder')
        if new_folder_name:
            new_folder_path = os.path.join(selected_path, new_folder_name)
            os.makedirs(new_folder_path, exist_ok=True)
            tree.insert('', 'end', text=new_folder_name)
            tree.item('', open=True)


def create_new_folder(tree, path):
    selected_item = tree.selection()
    if selected_item:
        file_path = generate_path(tree, selected_item[0])
        selected_path = os.path.join(path, file_path)
        if os.path.isdir(selected_path):
            new_folder_name = simpledialog.askstring(
                "New Folder", "Enter folder name:\t\t\t\t\t", initialvalue='New folder')
            if new_folder_name:
                new_folder_path = os.path.join(selected_path, new_folder_name)
                os.makedirs(new_folder_path, exist_ok=True)
                tree.insert(selected_item, 'end', text=new_folder_name)
                tree.item(selected_item, open=True)
        else:
            messagebox.showerror("Error", "Selected item is not a folder")
    else:
        messagebox.showerror("Error", "No folder selected")


def create_new_file_at_root_level(tree, path):

    selected_path = os.path.join(path, root_dir)
    if os.path.isdir(selected_path):
        new_file_name = simpledialog.askstring("New File", "Enter file name:\t\t\t\t\t")
        if new_file_name:
            root, ext = os.path.splitext(new_file_name)
            if not ext:
                new_file_name = new_file_name + '.md'
            new_file_path = os.path.join(selected_path, new_file_name)
            with open(new_file_path, 'w') as file:
                file.write("")  # Create an empty file
            tree.insert('', 'end', text=new_file_name)
            tree.item('', open=True)


def create_new_file(tree, path):

    if tree.focus() and not tree.selection():
        print('a')
        root_items = tree.get_children()
        if root_items:  # Make sure there are root items
            tree.selection_set(root_items[0])
            print('a')
    selected_item = tree.selection()
    if selected_item:
        # parent_folder = tree.item(selected_item, 'text')
        # parent_path = os.path.join(path, parent_folder)
        file_path = generate_path(tree, selected_item[0])
        selected_path = os.path.join(path, file_path)
        if os.path.isdir(selected_path):
            new_file_name = simpledialog.askstring(
                "New File", "Enter file name:\t\t\t\t\t")
            if new_file_name:
                root, ext = os.path.splitext(new_file_name)
                if not ext:
                    new_file_name = new_file_name + '.md'
                new_file_path = os.path.join(selected_path, new_file_name)
                with open(new_file_path, 'w') as file:
                    file.write("")  # Create an empty file
                tree.insert(selected_item, 'end', text=new_file_name)
                tree.item(selected_item, open=True)
        else:
            messagebox.showerror("Error", "Selected item is not a folder")
    else:
        messagebox.showerror("Error", "No folder selected")


def delete_item(tree, path):

    answer = messagebox.askyesno(title='Confirmation',
                                 message='Are you sure that you want to delete this note?')

    if not answer:
        return

    selected_item = tree.selection()
    if selected_item:
        file_path = generate_path(tree, selected_item[0])
        selected_path = os.path.join(path, file_path)
        if os.path.isdir(selected_path):
            shutil.rmtree(selected_path)
        elif os.path.isfile(selected_path):
            os.remove(selected_path)
        tree.delete(selected_item)
    else:
        messagebox.showerror("Error", "No item selected")


def show_file_content(tree, path, text_widget):
    global selected_path, selected_node_title, selected_shortcut
    # clear before select new one
    text_widget.delete(1.0, tk.END)
    selected_node_title = ''
    selected_shortcut = ''
    status_label.config(text='')

    selected_item = tree.selection()
    if selected_item:
        file_path = generate_path(tree, selected_item[0])
        selected_path = os.path.join(path, file_path)
        if os.path.isfile(selected_path):
            with open(selected_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
                text_widget.delete(1.0, tk.END)
                text_widget.insert(tk.END, content)
                selected_node_title = tree.item(selected_item, 'text')
                values = tree.item(selected_item, 'values')
                if values:
                    selected_shortcut = values[0]
                helper.highlight_markdown(editor)
                update_status_label('')


def rename_item(tree, path):
    selected_item = tree.selection()
    if selected_item:
        old_name = tree.item(selected_item, 'text')
        file_path = generate_path(tree, selected_item[0])
        old_path = os.path.join(path, file_path)
        new_name = simpledialog.askstring(
            "Rename", "Enter new name:\t\t\t\t\t", initialvalue=old_name)
        if new_name:
            new_path = old_path.replace(old_name, new_name)

            os.rename(old_path, new_path)
            # replace root_dir to get the rest of the path to save into json
            tree.item(selected_item, text=new_name)
            helper.update_json_value(
                shortcuts_path, selected_shortcut, new_path.replace(root_dir, ''))

            if os.path.isdir(new_path):
                old_folder_path = old_path.replace(root_dir, '') + '/'
                new_folder_path = new_path.replace(root_dir, '') + '/'
                helper.update_file_content(
                    shortcuts_path, old_folder_path, new_folder_path)


def refresh_tree(tree, parent, path):
    clear_treeview(tree)
    populate_treeview(treeview, parent, path)


def generate_path(tree, selected_item):
    """
    Gets the concatenated string from the root node to the selected node 
    of a tkinter Treeview.
    """

    path = []
    current_item = selected_item

    while current_item != '':
        path.append(tree.item(current_item)['text'])
        current_item = tree.parent(current_item)

    return '/'.join(path[::-1])  # Reverse the list to get root first


def on_search_change(event):
    global root_dir

    search_text = searchbox.get()
    clear_treeview(treeview)

    filter_tree(treeview, root_dir, search_text)


def create_app():
    global root, treeview, editor, status_label, searchbox

    new_version = helper.get_website_content(
        "https://hogonext.com/textspeedy-vesion.html")

    if (new_version != current_version):
        subprocess.run(["python", "check_for_updates.py"])

    root = ttk.Window(themename=helper.get_theme())

    root.title("TextSpeedy")
    root.geometry('1360x768')
    root.state('zoomed')  # Set the window to fullscreen

    # Create File menu
    menubar = Menu(root)
    file_menu = Menu(menubar, tearoff=0)
    file_menu.add_command(
        label="New Note", command=lambda event=None: create_new_file(event), accelerator="Ctrl+N")
    file_menu.add_command(label="New Folder",
                          command=lambda event=None: create_new_folder(event))

    file_menu.add_separator()
    file_menu.add_command(
        label="Settings", command=lambda event=None: display_settings_dialog(event), accelerator="F4")

    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=sys.exit)

    plugin_menu = Menu(menubar, tearoff=0)

    plugin_menu.add_command(
        label="Text Utility", command=lambda event=None: display_text_utility(event), accelerator="F7")

    help_menu = Menu(menubar, tearoff=0)
    help_menu.add_command(
        label="Website", command=lambda: webbrowser.open("https://hogonext.com/textspeedy/"))
    help_menu.add_command(
        label="Python Snippets", command=lambda: webbrowser.open("https://hogonext.com/blog/python-code/"))
    help_menu.add_command(
        label="About", command=lambda event=None: display_about(event))

    menubar.add_cascade(label="File", menu=file_menu)
    menubar.add_cascade(label="Plugin", menu=plugin_menu)
    menubar.add_cascade(label="Help", menu=help_menu)

    root.config(menu=menubar)

    # Create layout
    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True)

    # Status frame at the left
    left_frame = tk.Frame(frame)
    left_frame.pack(side="left", fill="y")

    # Status frame at the right
    right_frame = tk.Frame(frame)
    right_frame.pack(side="left", fill="both", expand=True)

    # Status frame at the bottom
    status_frame = tk.Frame(right_frame)
    status_frame.pack(side="bottom", fill="x")

    searchbox = tk.Entry(left_frame)
    searchbox.pack(side="top", fill="x")
    # Bind the key release event to the entry widget
    searchbox.bind("<KeyRelease>", on_search_change)

    # Load the search icon image (replace 'search_icon.png' with your image path)
    search_icon = tk.PhotoImage(file='image/search16px.png')

    # Create a label to display the icon
    icon_label = tk.Label(searchbox, image=search_icon)
    icon_label.pack(side="right")  # Place the icon on the right side

    # List on the left

    treeview = ttk.Treeview(
        left_frame, show='tree headings', columns=("Shortcut"))
    treeview.pack(side="left", fill="y")

    # Define columns
    # Default column for tree structure
    treeview.heading("#0", text="Title", anchor='w')
    treeview.heading("Shortcut", text="Shortcut", anchor='w')

    # Set column widths
    treeview.column("#0", width=250)  # Set width of first column
    treeview.column("Shortcut", width=80)  # Set width of second column

    populate_treeview(treeview, '', root_dir)

    # Create and pack the scrollbars for the Treeview and Text widget
    treeview_scrollbar = tk.Scrollbar(
        left_frame, orient="vertical", command=treeview.yview)
    treeview.config(yscrollcommand=treeview_scrollbar.set)
    treeview_scrollbar.pack(side="left", fill="y")

    # Bind the Treeview selection event to show file content
    treeview.bind('<<TreeviewSelect>>', lambda event: show_file_content(
        treeview, root_dir, editor))

    # Text widget on the right
    editor = tk.Text(right_frame, wrap="word")

    editor.pack(side="left", fill="both", expand=True)
    editor.bind('<KeyRelease>', on_text_change)

    # Create and pack the scrollbars for the Text widget
    text_scrollbar = tk.Scrollbar(
        right_frame, orient="vertical", command=editor.yview)
    editor.config(yscrollcommand=text_scrollbar.set)
    text_scrollbar.pack(side="right", fill="y")

    # Create the status label inside the status frame
    status_label = tk.Label(status_frame, text='Ready',
                            bd=1, relief=tk.SUNKEN, anchor='w')
    status_label.pack(side="bottom", fill="x")

    # UI end block code

    # load_nodes(treeview)
    select_first_item(treeview)

    root.bind('<Control-n>', create_new_file)
    root.bind('<Control-d>', delete_item)
    root.bind('<Control-l>', live_preview)
    root.bind('<Control-e>', send_emai)
    root.bind('<F4>', display_settings_dialog)
    root.bind('<F5>', run_code)
    root.bind('<F7>', display_text_utility)
    root.bind('<F9>', run_code_live_output)
    root.bind('<F10>', publish_WP)

    # Create the popup menu
    global popup_menu_treeview
    popup_menu_treeview = tk.Menu(root, tearoff=0)
    popup_menu_treeview.add_command(
        label="Create New File at Root level", command=lambda event=None: create_new_file_at_root_level(treeview, root_dir))
    popup_menu_treeview.add_command(
        label="Create New Folder at Root level", command=lambda event=None: create_new_folder_at_root_level(treeview, root_dir))
    popup_menu_treeview.add_command(
        label="Create New File", command=lambda event=None: create_new_file(treeview, root_dir), accelerator="Ctrl+N")
    popup_menu_treeview.add_command(
        label="Create New Folder", command=lambda event=None: create_new_folder(treeview, root_dir))
    popup_menu_treeview.add_command(
        label="Update Shortcut", command=lambda event=None: update_shortcut(event))
    popup_menu_treeview.add_command(
        label="Delete Item", command=lambda event=None: delete_item(treeview, root_dir), accelerator="Ctrl+D")
    popup_menu_treeview.add_command(
        label="Rename Item", command=lambda event=None: rename_item(treeview, root_dir))
    popup_menu_treeview.add_command(
        label="Refresh", command=lambda event=None: refresh_tree(treeview, '', root_dir), accelerator="Ctrl+F5")

    # Bind the right click event to the Treeview
    treeview.bind('<Button-3>', on_right_click_treeview)

    # Create the popup menu
    global popup_menu_text
    popup_menu_text = tk.Menu(root, tearoff=0)
    popup_menu_text.add_command(
        label="Live Preview", command=lambda event=None: live_preview(event), accelerator="Ctrl+L")
    popup_menu_text.add_command(
        label="Send Email", command=lambda event=None: send_emai(event), accelerator="Ctrl+E")
    popup_menu_text.add_command(
        label="Run Code", command=lambda event=None: run_code(event), accelerator="F5")
    popup_menu_text.add_command(
        label="Run Code With Live Output", command=lambda event=None: run_code_live_output(event), accelerator="F9")
    popup_menu_text.add_command(
        label="Publish Wordpress", command=lambda event=None: publish_WP(event), accelerator="F10")

    # Bind the click event to the Text widget
    editor.bind('<Button-1>', on_left_click_editor)
    editor.bind('<Button-3>', on_right_click_editor)

    # Define a function for quit the window
    def quit_window(icon, item):
        icon.stop()
        root.destroy()

    # Define a function to show the window again
    def show_window(icon, item):
        icon.stop()

        root.deiconify()
        # Adjust format if needed
        root.geometry('1360x768')
        root.state('zoomed')  # Set the window to fullscreen

    # Hide the window and show on the system taskbar

    image = Image.open("textspeedy.ico")

    def hide_window():

        root.withdraw()

        menu = item('Open',
                    show_window), (item('Exit', quit_window))
        icon = pystray.Icon("name", image, "TextSpeedy", menu)
        icon.run()

    root.protocol('WM_DELETE_WINDOW', hide_window)

    root.iconbitmap("textspeedy.ico")

    helper.center_window(root, 1360, 768)

    # hide_window()

    path = 'G:\\My Drive\\HogoNext\\textspeedy/data/Command'

    if os.path.isdir(path):
        print('yes')

    root.mainloop()


if __name__ == "__main__":
    create_app()
