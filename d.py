import tkinter as tk
from tkinter import messagebox, filedialog
import os
import requests
import base64

def _decode_hidden_string(s):
    import base64
    decoded_bytes = base64.b64decode(s)
    return "".join(chr(b) for b in decoded_bytes)

def send_message(code, message):
    webhook_url = webhook_entry.get().strip()
    if not webhook_url:
        return  # No webhook entered, skip sending
    try:
        content = f"[{code.upper()}] {message}"
        requests.post(webhook_url, json={"content": content}, timeout=5)
    except Exception:
        pass

def load_words():
    path = filedialog.askopenfilename(
        title="Select word list file",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if not path:
        messagebox.showerror("Error", "No file selected.")
        send_message("error", "No file selected.")
        return [], None
    if not os.path.exists(path):
        messagebox.showerror("Error", f"File not found:\n{path}")
        send_message("error", f"File not found: {path}")
        return [], None
    with open(path, 'r') as f:
        words = [line.strip() for line in f if line.strip()]
    send_message("success", f"Loaded {len(words)} entries from file.")
    return words, path

def save_words(file_path, words):
    try:
        with open(file_path, 'w') as f:
            for word in words:
                f.write(word + '\n')
        send_message("success", f"Saved {len(words)} entries to file.")
    except Exception:
        send_message("error", "Failed to save entries.")

def find_word_with_pattern(words, pattern, used_words):
    pattern = pattern.lower()
    longest_word = None
    for word in words:
        w = word.lower()
        if pattern in w and word not in used_words:
            if longest_word is None or len(word) > len(longest_word):
                longest_word = word
    return longest_word

def search_and_display(event=None):
    pattern = entry.get().strip()
    entry.delete(0, tk.END)
    if not (2 <= len(pattern) <= 4) or not pattern.isalpha():
        messagebox.showerror("Error", "Enter 2–4 letters only.")
        send_message("error", "Invalid input: pattern must be 2-4 letters.")
        return

    word = find_word_with_pattern(words, pattern.lower(), app.used_words)
    if word:
        app.last_word = word
        app.used_words.add(word)
        result_label.config(text=word, fg="#00b0f0")
        send_message("success", f"Found entry: {word}")
    else:
        result_label.config(text="No new match found.", fg="#d0d0d0")
        app.last_word = None
        send_message("error", f"No match found for pattern: {pattern}")

def undo_and_remove():
    if app.last_word and app.last_word in words:
        removed = app.last_word
        words.remove(removed)
        app.used_words.discard(removed)
        save_words(file_path, words)
        result_label.config(text="Entry removed.", fg="#ff6666")
        send_message("success", f"Removed entry: {removed}")
        app.last_word = None
    else:
        result_label.config(text="No entry to remove.", fg="#d0d0d0")
        send_message("error", "No entry to remove on undo.")

app = tk.Tk()
app.title("Word Finder")
app.geometry("400x290")
app.resizable(False, False)
app.wm_attributes("-topmost", 1)
app.configure(bg="#2e2e2e")

app.used_words = set()
app.last_word = None

font_large = ("Arial", 16, "bold")
font_entry = ("Arial", 14)
font_button = ("Arial", 12)

# Webhook input
tk.Label(app, text="Enter webhook URL:", font=font_button,
         bg="#2e2e2e", fg="#cccccc").pack(pady=(10, 2))
webhook_entry = tk.Entry(app, width=50, font=("Arial", 10),
                         bg="#4a4a4a", fg="#f0f0f0", insertbackground="#f0f0f0",
                         relief="flat", highlightthickness=2, highlightbackground="#555555",
                         highlightcolor="#888888")
webhook_entry.pack(pady=(0, 10))
webhook_entry.focus()

tk.Label(app, text="Enter 2–4 letter pattern:", font=font_button,
         bg="#2e2e2e", fg="#cccccc").pack(pady=6)

entry = tk.Entry(app, width=28, font=font_entry, justify="center",
                 bg="#4a4a4a", fg="#f0f0f0", insertbackground="#f0f0f0",
                 relief="flat", highlightthickness=2, highlightbackground="#555555",
                 highlightcolor="#888888")
entry.pack(pady=5)

find_btn = tk.Button(app, text="🔍 Find Word", font=font_button,
                     bg="#666666", fg="#e0e0e0", activebackground="#888888",
                     activeforeground="#ffffff", width=20,
                     relief="flat", command=search_and_display)
find_btn.pack(pady=5)

result_label = tk.Label(app, text="", font=font_large,
                        bg="#2e2e2e", fg="#00b0f0")
result_label.pack(pady=8)

remove_btn = tk.Button(app, text="🗑️ Not Registered as Word", font=font_button,
                       bg="#aa4444", fg="#f0f0f0", activebackground="#cc5555",
                       activeforeground="#ffffff", width=30,
                       relief="flat", command=undo_and_remove)
remove_btn.pack(pady=5)

# Load words and get file path at startup
words, file_path = load_words()
if not words:
    app.destroy()  # close app if no words loaded

app.bind('<F1>', search_and_display)
entry.bind('<Return>', search_and_display)

app.mainloop()
