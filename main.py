import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
import cv2
import tkinterdnd2 as tkdnd

# Variables
SUPPORTED_TYPES = {'.jpg', '.jpeg', '.png', '.heic', '.mp4', '.mov', '.avi'}
root = tk.Tk()
source_entry = tk.Entry(root, width=60)
dest_entry = tk.Entry(root, width=60)
types_entry = tk.Entry(root, width=60)
progress = None

def update_supported_types():
    raw = types_entry.get()
    extensions = {ext.strip().lower() for ext in raw.split(',') if ext.strip().startswith('.')}
    if not extensions:
        messagebox.showerror("Invalid Input", "You must enter at least one valid extension (e.g., .jpg,.mp4)")
        return
    SUPPORTED_TYPES.clear()
    SUPPORTED_TYPES.update(extensions)
    messagebox.showinfo("Updated", f"Supported file types are now:\n{', '.join(SUPPORTED_TYPES)}")

def get_datetime_taken(file_path):
    try:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in {'.jpg', '.jpeg', '.png', '.heic'}:
            image = Image.open(file_path)
            exif_data = image._getexif()
            if exif_data:
                for tag, value in exif_data.items():
                    if TAGS.get(tag) == 'DateTimeOriginal':
                        return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
        elif ext in {'.mp4', '.mov', '.avi'}:
            return datetime.fromtimestamp(os.path.getmtime(file_path))
    except:
        pass
    return datetime.fromtimestamp(os.path.getmtime(file_path))

def sanitize_filename(dt):
    return dt.strftime("%m-%d-%Y %H-%M-%S")

def transfer_files(source_folder, destination_folder, move=False):
    total_files = sum(len(files) for _, _, files in os.walk(source_folder))
    progress["maximum"] = total_files
    progress["value"] = 0
    root.update_idletasks()

    file_count = 0
    for root_dir, _, files in os.walk(source_folder):
        for file in files:
            if file.lower().endswith(tuple(SUPPORTED_TYPES)):
                source_path = os.path.join(root_dir, file)

                dt_taken = get_datetime_taken(source_path)
                date_folder = dt_taken.strftime("%Y-%m-%d")
                subfolder = os.path.join(destination_folder, date_folder)
                os.makedirs(subfolder, exist_ok=True)

                filename = sanitize_filename(dt_taken)
                ext = os.path.splitext(file)[1]
                destination_path = os.path.join(subfolder, f"{filename}{ext}")

                counter = 1
                while os.path.exists(destination_path):
                    destination_path = os.path.join(subfolder, f"{filename}_{counter}{ext}")
                    counter += 1

                if move:
                    shutil.move(source_path, destination_path)
                else:
                    shutil.copy2(source_path, destination_path)

                file_count += 1
                progress["value"] += 1
                root.update_idletasks()

    return file_count

def browse_source():
    folder = filedialog.askdirectory(title="Select Source Folder")
    source_entry.delete(0, tk.END)
    source_entry.insert(0, folder)

def browse_destination():
    folder = filedialog.askdirectory(title="Select Destination Folder")
    dest_entry.delete(0, tk.END)
    dest_entry.insert(0, folder)

def on_drop(event, target_entry):
    dropped_path = event.data.strip('{}')
    if os.path.isdir(dropped_path):
        target_entry.delete(0, tk.END)
        target_entry.insert(0, dropped_path)

def start_transfer(move=False):
    src = source_entry.get()
    dst = dest_entry.get()

    if not os.path.isdir(src) or not os.path.isdir(dst):
        messagebox.showerror("Error", "Please select valid source and destination folders.")
        return

    try:
        count = transfer_files(src, dst, move=move)
        messagebox.showinfo("Success", f"{'Moved' if move else 'Copied'} {count} files.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{e}")

def setup_gui():
    root.title("Media Transfer Tool")

    tk.Label(root, text="Source Folder").grid(row=0, column=0, padx=10, pady=5, sticky='e')
    source_entry.grid(row=0, column=1, pady=5)
    tk.Button(root, text="Browse", command=browse_source).grid(row=0, column=2, padx=10)

    tk.Label(root, text="Destination Folder").grid(row=1, column=0, padx=10, pady=5, sticky='e')
    dest_entry.grid(row=1, column=1, pady=5)
    tk.Button(root, text="Browse", command=browse_destination).grid(row=1, column=2, padx=10)

    #global progress
    #progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
    #progress.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

    tk.Label(root, text="Supported Types (comma-separated)").grid(row=3, column=0, padx=10, pady=5, sticky='e')
    types_entry.grid(row=3, column=1, pady=5)
    types_entry.insert(0, ','.join(sorted(SUPPORTED_TYPES)))
    tk.Button(root, text="Update", command=update_supported_types).grid(row=3, column=2, padx=10)

    tk.Button(root, text="Copy Files", command=lambda: start_transfer(move=False), bg="lightblue").grid(row=4, column=1, pady=10, sticky='w')
    tk.Button(root, text="Move Files", command=lambda: start_transfer(move=True), bg="lightgreen").grid(row=4, column=1, pady=10, sticky='e')

    try:
        dnd = tkdnd.TkinterDnD.Tk()
        dnd.withdraw()
        source_entry.drop_target_register(tkdnd.DND_FILES)
        source_entry.dnd_bind('<<Drop>>', lambda e: on_drop(e, source_entry))
        dest_entry.drop_target_register(tkdnd.DND_FILES)
        dest_entry.dnd_bind('<<Drop>>', lambda e: on_drop(e, dest_entry))
    except:
        print("tkinterDnD2 not installed — drag and drop won't work")

    root.mainloop()

if __name__ == "__main__":
    setup_gui()
