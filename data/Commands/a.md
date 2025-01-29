import tkinter as tk
from tkinter import filedialog
from rembg import remove
from PIL import Image
import os

def remove_background():
    """
    Removes the background from an image using the selected file.
    """
    try:
        input_path = input_entry.get()
        if not input_path:
            error_label.config(text="Please select an image file.")
            return

        input_img = Image.open(input_path)
        output_img = remove(input_img)

        # Extract filename and directory from input path
        directory, filename = os.path.split(input_path)
        output_filename = os.path.splitext(filename) + "_nobg.png"
        output_path = os.path.join(directory, output_filename)

        output_img.save(output_path)
        error_label.config(text=f"Background removed successfully. Saved to {output_path}", fg="green")
    except Exception as e:
        error_label.config(text=f"Error: {e}", fg="red")

def browse_file():
    """
    Opens a file dialog to select an image file.
    """
    filepath = filedialog.askopenfilename(
        initialdir="/",
        title="Select an Image",
        filetypes=(("Image files", "*.jpg *.jpeg *.png *.bmp"), ("all files", "*.*"))
    )
    if filepath:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, filepath)
        error_label.config(text="")

# Create the main window
window = tk.Tk()
window.title("Background Remover")

# Input file path
input_label = tk.Label(window, text="Input Image:")
input_label.pack(pady=5)

input_entry = tk.Entry(window, width=50)
input_entry.pack(pady=5)

browse_button = tk.Button(window, text="Browse", command=browse_file)
browse_button.pack(pady=5)

# Remove background button
remove_button = tk.Button(window, text="Remove Background", command=remove_background)
remove_button.pack(pady=5)

# Error label
error_label = tk.Label(window, text="", fg="red")
error_label.pack()

window.mainloop()
import tkinter as tk
from tkinter import filedialog
from rembg import remove
from PIL import Image
import os

def remove_background():
    """
    Removes the background from an image using the selected file.
    """
    try:
        input_path = input_entry.get()
        if not input_path:
            error_label.config(text="Please select an image file.")
            return

        input_img = Image.open(input_path)
        output_img = remove(input_img)

        # Extract filename and directory from input path
        directory, filename = os.path.split(input_path)
        output_filename = os.path.splitext(filename) + "_nobg.png"
        output_path = os.path.join(directory, output_filename)

        output_img.save(output_path)
        error_label.config(text=f"Background removed successfully. Saved to {output_path}", fg="green")
    except Exception as e:
        error_label.config(text=f"Error: {e}", fg="red")

def browse_file():
    """
    Opens a file dialog to select an image file.
    """
    filepath = filedialog.askopenfilename(
        initialdir="/",
        title="Select an Image",
        filetypes=(("Image files", "*.jpg *.jpeg *.png *.bmp"), ("all files", "*.*"))
    )
    if filepath:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, filepath)
        error_label.config(text="")

# Create the main window
window = tk.Tk()
window.title("Background Remover")

# Input file path
input_label = tk.Label(window, text="Input Image:")
input_label.pack(pady=5)

input_entry = tk.Entry(window, width=50)
input_entry.pack(pady=5)

browse_button = tk.Button(window, text="Browse", command=browse_file)
browse_button.pack(pady=5)

# Remove background button
remove_button = tk.Button(window, text="Remove Background", command=remove_background)
remove_button.pack(pady=5)

# Error label
error_label = tk.Label(window, text="", fg="red")
error_label.pack()

window.mainloop()
import tkinter as tk
from tkinter import filedialog
from rembg import remove
from PIL import Image
import os

def remove_background():
    """
    Removes the background from an image using the selected file.
    """
    try:
        input_path = input_entry.get()
        if not input_path:
            error_label.config(text="Please select an image file.")
            return

        input_img = Image.open(input_path)
        output_img = remove(input_img)

        # Extract filename and directory from input path
        directory, filename = os.path.split(input_path)
        output_filename = os.path.splitext(filename) + "_nobg.png"
        output_path = os.path.join(directory, output_filename)

        output_img.save(output_path)
        error_label.config(text=f"Background removed successfully. Saved to {output_path}", fg="green")
    except Exception as e:
        error_label.config(text=f"Error: {e}", fg="red")

def browse_file():
    """
    Opens a file dialog to select an image file.
    """
    filepath = filedialog.askopenfilename(
        initialdir="/",
        title="Select an Image",
        filetypes=(("Image files", "*.jpg *.jpeg *.png *.bmp"), ("all files", "*.*"))
    )
    if filepath:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, filepath)
        error_label.config(text="")

# Create the main window
window = tk.Tk()
window.title("Background Remover")

# Input file path
input_label = tk.Label(window, text="Input Image:")
input_label.pack(pady=5)

input_entry = tk.Entry(window, width=50)
input_entry.pack(pady=5)

browse_button = tk.Button(window, text="Browse", command=browse_file)
browse_button.pack(pady=5)

# Remove background button
remove_button = tk.Button(window, text="Remove Background", command=remove_background)
remove_button.pack(pady=5)

# Error label
error_label = tk.Label(window, text="", fg="red")
error_label.pack()

window.mainloop()


