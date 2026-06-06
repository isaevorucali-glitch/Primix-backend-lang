import sys
import subprocess
import os
import tkinter as tk
from tkinter import filedialog, messagebox

def run_primix(filepath):
    primix_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'primix.py')
    subprocess.Popen(['python', primix_path, filepath],
                     creationflags=subprocess.CREATE_NEW_CONSOLE)

if len(sys.argv) > 1:
    filepath = sys.argv[1]
    if filepath.endswith('.pmx'):
        run_primix(filepath)
    else:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Primix", "Only .pmx files supported!")
else:
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    filepath = filedialog.askopenfilename(
        title="Choose Primix file",
        filetypes=[("Primix files", "*.pmx"), ("All files", "*.*")]
    )

    if filepath:
        run_primix(filepath)
    else:
        messagebox.showinfo("Primix", "No file selected")