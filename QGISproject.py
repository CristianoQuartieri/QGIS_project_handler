import os
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

'''
A couple of infos:
- The folder containing the copies of the layer files and the project file is created in the same directory (folder)
  where the project file we specified is located.
  Extra: The user could be asked where to create this folder; this can be added in the future.
- It does not support zip files (.qgz), but this feature can be added if necessary, automating file extraction.

by Cristiano Quartieri (https://github.com/CristianoQuartieri) with love <3

Small info for me: 
- To make the executable use the cmd, enter the directory where the .py is and write:
  python -m PyInstaller --onefile --noconsole qgis_project_packager_gui.py
'''

def pack_qgis_project(project_path):
    project_path = Path(project_path).resolve()

    if project_path.suffix.lower() != ".qgs":
        messagebox.showerror("Error", "The file MUST be a QGIS project (.qgs)")
        return

    if not project_path.exists():
        messagebox.showerror("Error", "The project file does NOT exist")
        return

    project_name = project_path.stem
    output_folder = project_path.parent / f"{project_name}_package"
    output_folder.mkdir(exist_ok=True)

    # Parsing XML
    tree = ET.parse(project_path)
    root = tree.getroot()

    datasources = [elem.text for elem in root.iter("datasource") if elem.text]

    copied_layers = []
    skipped_layers = []

    for ds in datasources:
        ds_path = Path(ds)
        if ds_path.exists() and ds_path.is_file():
            base_name = ds_path.with_suffix("").name
            for f in ds_path.parent.glob(base_name + ".*"):
                try:
                    shutil.copy(f, output_folder)
                except Exception as e:
                    print(f"Error in the copy of {f}: {e}")
            copied_layers.append(ds_path.name)
        else:
            skipped_layers.append(ds)

    # Copy project file
    shutil.copy(project_path, output_folder)

    msg = f"✅ The copy is completed!\n\n📂 Folder created:\n{output_folder}\n\n"
    msg += f"📄 Project file copied: {project_path.name}\n"
    msg += f"🗺️ Layers copied: {len(copied_layers)}\n"
    if skipped_layers:
        msg += f"\n⚠️ Layers NOT found ({len(skipped_layers)}):\n" + "\n".join(skipped_layers[:5])
        if len(skipped_layers) > 5:
            msg += "\n..."

    messagebox.showinfo("Operation compleated", msg)


def choose_project_file():
    path = filedialog.askopenfilename(
        title="Select the project file QGIS",
        filetypes=[("QGIS Project", "*.qgs")]
    )
    if path:
        entry_path.delete(0, tk.END)
        entry_path.insert(0, path)


def start_packaging():
    path = entry_path.get().strip()
    if not path:
        messagebox.showwarning("Warning", "Insert or select a project file")
        return
    pack_qgis_project(path)


# --- GRAPHIC INTERFACE ---

root = tk.Tk()
root.title("QGIS Project Packager")
root.geometry("520x240")
root.resizable(False, False)

# To enanche the graphic
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)  # better sharpness
except Exception:
    pass

# default font
default_font = ("Segoe UI", 11)
root.option_add("*Font", default_font)

frame = tk.Frame(root, padx=20, pady=20)
frame.pack(fill="both", expand=True)

label = tk.Label(frame, text="Select the project file QGIS (.qgs):", font=("Segoe UI Semibold", 12))
label.pack(anchor="w")

entry_path = tk.Entry(frame, width=50, font=("Segoe UI", 11))
entry_path.pack(side="left", fill="x", expand=True, pady=10)

browse_btn = tk.Button(frame, text="Browse", command=choose_project_file, font=("Segoe UI", 11))
browse_btn.pack(side="right", padx=5, pady=10)

start_btn = tk.Button(
    root,
    text="Create a project folder",
    command=start_packaging,
    bg="#2E8B57",
    fg="white",
    activebackground="#3CB371",
    font=("Segoe UI Semibold", 12),
    padx=10,
    pady=6
)
start_btn.pack(pady=10)

# Signature footer (lol)
footer = tk.Label(root, text="by https://github.com/CristianoQuartieri    <3", font=("Segoe UI Italic", 10), fg="gray")
footer.pack(side="bottom", pady=5)


root.mainloop()