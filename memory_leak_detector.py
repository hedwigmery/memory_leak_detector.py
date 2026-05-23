import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import threading
import time
import random
import os

root = tk.Tk()
root.title("Memory Leak Detector")
root.geometry("1200x700")
root.configure(bg="black")

# ---------------- TITLE ----------------

title = tk.Label(
    root,
    text="MEMORY LEAK DETECTOR",
    fg="lime",
    bg="black",
    font=("Consolas", 24, "bold")
)
title.pack(pady=10)

# ---------------- TABLE ----------------

columns = (
    "Process",
    "PID",
    "RAM MB",
    "CPU %",
    "Threads",
    "Status",
    "Risk"
)

tree = ttk.Treeview(root, columns=columns, show="headings", height=20)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150)

tree.pack(pady=10)

# ---------------- TERMINAL ----------------

terminal = tk.Text(
    root,
    height=10,
    bg="black",
    fg="lime",
    font=("Consolas", 10)
)

terminal.pack(fill="x", padx=10, pady=10)

# ---------------- STATUS ----------------

status_label = tk.Label(
    root,
    text="SYSTEM STABLE",
    fg="cyan",
    bg="black",
    font=("Consolas", 14, "bold")
)

status_label.pack(pady=5)

# ---------------- PROCESS MEMORY CACHE ----------------

memory_history = {}

# ---------------- LOG FUNCTION ----------------

def log(message):
    terminal.insert(tk.END, message + "\n")
    terminal.see(tk.END)

# ---------------- PROCESS ANALYSIS ----------------

def analyze_processes():

    while True:

        for item in tree.get_children():
            tree.delete(item)

        try:

            for process in psutil.process_iter([

                "pid",
                "name",
                "memory_info",
                "cpu_percent",
                "num_threads",
                "status"

            ]):

                try:

                    pid = process.info["pid"]
                    name = process.info["name"]

                    ram = round(
                        process.info["memory_info"].rss / 1024 / 1024,
                        2
                    )

                    cpu = process.info["cpu_percent"]

                    threads = process.info["num_threads"]

                    status = process.info["status"]

                    # ---------------- RISK DETECTION ----------------

                    risk = "LOW"

                    if ram > 500:
                        risk = "MEDIUM"

                    if ram > 1000:
                        risk = "HIGH"

                    # ---------------- MEMORY LEAK CONTROL ----------------

                    if pid in memory_history:

                        old_ram = memory_history[pid]

                        if ram - old_ram > 200:
                            risk = "LEAK?"

                            log(
                                f"[ALERT] Possible memory leak detected -> {name}"
                            )

                            status_label.config(
                                text="MEMORY ALERT",
                                fg="red"
                            )

                    memory_history[pid] = ram

                    tree.insert(
                        "",
                        tk.END,
                        values=(
                            name,
                            pid,
                            ram,
                            cpu,
                            threads,
                            status,
                            risk
                        )
                    )

                except:
                    pass

            log("[SYSTEM] Process scan completed.")

        except Exception as e:
            log(f"[ERROR] {e}")

        time.sleep(3)

# ---------------- KILL PROCESS ----------------

def kill_process():

    selected = tree.selection()

    if not selected:
        messagebox.showwarning(
            "Warning",
            "Select a process first."
        )
        return

    item = tree.item(selected)

    pid = item["values"][1]

    try:

        os.kill(pid, 9)

        messagebox.showinfo(
            "Success",
            f"Process {pid} terminated."
        )

        log(f"[SYSTEM] Process {pid} killed.")

    except Exception as e:

        messagebox.showerror(
            "Error",
            str(e)
        )

# ---------------- BUTTONS ----------------

button_frame = tk.Frame(root, bg="black")
button_frame.pack(pady=10)

kill_button = tk.Button(
    button_frame,
    text="KILL PROCESS",
    bg="red",
    fg="white",
    font=("Consolas", 12, "bold"),
    command=kill_process
)

kill_button.grid(row=0, column=0, padx=10)

# ---------------- START THREAD ----------------

thread = threading.Thread(
    target=analyze_processes,
    daemon=True
)

thread.start()

# ---------------- MAINLOOP ----------------

root.mainloop()