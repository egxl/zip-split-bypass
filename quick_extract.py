#!/usr/bin/env python3
"""
quick_extract.py

Prompts user to select a “fake-split” ZIP, then extracts it using Java’s `jar xf`
into a new folder named after the ZIP (without `.zip`) in the same directory.

Requirements:
  - Python 3
  - Java (jar) on PATH
"""

import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

def main():
    root = tk.Tk()
    root.withdraw()

    messagebox.showinfo("ZIP-Split Bypass", "Select your fake-split ZIP to extract.")
    zip_path = filedialog.askopenfilename(
        title="Choose a fake-split ZIP file",
        filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")]
    )
    if not zip_path:
        return

    zip_dir = os.path.dirname(zip_path)
    zip_name = os.path.splitext(os.path.basename(zip_path))[0]
    extract_dir = os.path.join(zip_dir, zip_name)

    os.makedirs(extract_dir, exist_ok=True)

    try:
        subprocess.run(["jar", "xf", zip_path], cwd=extract_dir, check=True)
        messagebox.showinfo("Success", f"Extraction complete in:\n{extract_dir}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to extract:\n{zip_path}\n\n{e}")

if __name__ == "__main__":
    main()