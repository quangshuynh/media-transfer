import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

# Variables
root = tk.Tk()
source_entry = tk.Entry(root, width=60)
dest_entry = tk.Entry(root, width=60)

# File types to transfer
FILE_TYPES = ('.jpg', '.jpeg', '.png', '.heic', '.mp4', '.mov', '.avi')

def transfer_files(source_folder, destination_folder, move=False):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    file_count = 0
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file.lower().endswith(FILE_TYPES):
                source_path = os.path.join(root, file)
                destination_path = os.path.join(destination_folder, file)

                # Prevent overwrite
                base, ext = os.path.splitext(destination_path)
                counter = 1
                while os.path.exists(destination_path):
                    destination_path = f"{base}_{counter}{ext}"
                    counter += 1

                if move:
                    shutil.move(source_path, destination_path)
                else:
                    shutil.copy2(source_path, destination_path)

                file_count += 1

    return file_count

def browse_source():
    folder = filedialog.askdirectory(title="Select iPhone Base Folder")
    source_entry.delete(0, tk.END)
    source_entry.insert(0, folder)

def browse_destination():
    folder = filedialog.askdirectory(title="Select Destination Folder")
    dest_entry.delete(0, tk.END)
    dest_entry.insert(0, folder)

def start_transfer(move=False):
    src = source_entry.get()
    dst = dest_entry.get()

    if not src or not dst:
        messagebox.showerror("Error", "Both source and destination must be selected.")
        return

    try:
        count = transfer_files(src, dst, move=move)
        messagebox.showinfo("Success", f"{'Moved' if move else 'Copied'} {count} files.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{e}")

def main():
    # GUI setup
    root.title("Media Transfer Tool")

    tk.Label(root, text="Source Folder").grid(row=0, column=0, padx=10, pady=5, sticky='e')
    source_entry.grid(row=0, column=1, pady=5)
    tk.Button(root, text="Browse", command=browse_source).grid(row=0, column=2, padx=10)

    tk.Label(root, text="Destination Folder").grid(row=1, column=0, padx=10, pady=5, sticky='e')
    dest_entry.grid(row=1, column=1, pady=5)
    tk.Button(root, text="Browse", command=browse_destination).grid(row=1, column=2, padx=10)

    tk.Button(root, text="Copy Files", command=lambda: start_transfer(move=False), bg="lightblue").grid(row=2, column=1, pady=10, sticky='w')
    tk.Button(root, text="Move Files", command=lambda: start_transfer(move=True), bg="lightgreen").grid(row=2, column=1, pady=10, sticky='e')

    root.mainloop()

if __name__ == "__main__":
    main()
