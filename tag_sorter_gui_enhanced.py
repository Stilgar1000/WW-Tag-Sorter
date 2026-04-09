import tkinter as tk
from tkinter import filedialog, messagebox
import os
from sort_io_tags_FIXED import sort_tags  # Assuming this exists and is correctly implemented

def select_input_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    input_file_entry.delete(0, tk.END)  # Clear the entry
    input_file_entry.insert(0, file_path)  # Insert the selected file path

def select_output_directory():
    output_dir = filedialog.askdirectory()
    output_directory_entry.delete(0, tk.END)  # Clear the entry
    output_directory_entry.insert(0, output_dir)  # Insert the selected directory

def run_sorting():
    input_file = input_file_entry.get()
    output_directory = output_directory_entry.get()

    if not input_file or not output_directory:
        messagebox.showerror("Error", "Please select both input file and output directory.")
        return

    try:
        output_file_name = os.path.join(output_directory, "sorted_tags.csv")
        sort_tags(input_file, output_file_name)  # Call the sorting function
        messagebox.showinfo("Success", f"Sorting complete! Output saved to: {output_file_name}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Create main application window
app = tk.Tk()
app.title("Tag Sorter")

# Input file section
tk.Label(app, text="Input CSV File:").pack()
input_file_entry = tk.Entry(app, width=40)
input_file_entry.pack()
tk.Button(app, text="Browse", command=select_input_file).pack()

# Output directory section
tk.Label(app, text="Output Directory:").pack()
output_directory_entry = tk.Entry(app, width=40)
output_directory_entry.pack()
tk.Button(app, text="Browse", command=select_output_directory).pack()

# Run sorting button
tk.Button(app, text="Sort Tags", command=run_sorting).pack()

# Default output directory creation
default_output_dir = os.path.join(os.getcwd(), "sorted_output")
os.makedirs(default_output_dir, exist_ok=True)
output_directory_entry.insert(0, default_output_dir)

app.mainloop()