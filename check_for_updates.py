import ttkbootstrap as ttk
from ttkbootstrap.constants import *

import webbrowser

def open_link():
  """Opens the specified URL in a web browser."""
  webbrowser.open("https://hogonext.com/textspeedy-download/")

# Create the main window
root = ttk.Window(themename="yeti")
root.title("TextSpeedy - Check for Updates")

# Hide both minimize and maximize buttons
root.attributes('-toolwindow', True)

root.geometry("400x50")
root.update_idletasks()

# Calculate the offset to center the window
x = (root.winfo_screenwidth() - root.winfo_width()) // 2
y = (root.winfo_screenheight() - root.winfo_height()) // 3
root.geometry(f"+{x}+{y}")

# Create a label with the link text
link_label = ttk.Label(root, text="Visit website to download new version", foreground="blue", cursor="hand2")
link_label.pack(padx=10, pady=10)

# Bind the open_link function to the label's click event
link_label.bind("<Button-1>", lambda e: open_link())

root.mainloop()