import ttkbootstrap as ttk
from ttkbootstrap.constants import *

def on_esc_key(event):
    if event.keysym == 'Escape':
        root.destroy()

def on_focus_out(event):
    if event.widget == entry:
        root.destroy()

# Create the main window
root = ttk.Window(themename="darkly")
root.bind("<KeyPress>", on_esc_key)  # Bind to any key press

# Create a frame for the title bar (though we won't use it for a button)
title_bar = ttk.Frame(root)
title_bar.pack(fill=X)

# Hide the title bar
root.overrideredirect(True)

# Create an input box
entry = ttk.Entry(root)
entry.pack(padx=10, pady=10)

# Set focus on the entry widget
entry.focus_set()

# Bind the focus out event to the entry widget
entry.bind("<FocusOut>", on_focus_out)

root.geometry("300x50")
root.update_idletasks()

# Calculate the offset to center the window
x = (root.winfo_screenwidth() - root.winfo_width()) // 2
y = (root.winfo_screenheight() - root.winfo_height()) // 2
root.geometry(f"+{x}+{y}")

# Adjust the width of the entry widget to be 80% of the form's width
def adjust_entry_width(event=None):
    form_width = root.winfo_width()
    entry_width = int(form_width * 0.8)
    entry.config(width=entry_width)

# Bind the configure event to adjust the entry width when the form is resized
root.bind("<Configure>", adjust_entry_width)

# Initial adjustment of the entry width
adjust_entry_width()

root.mainloop()