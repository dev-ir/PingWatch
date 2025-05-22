import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk
from ping3 import ping
import threading
import time
import datetime
import urllib.request
import io
import webbrowser
from collections import deque

# وضعیت کلی
running = False
timeout_count = 0
recent_pings = deque(maxlen=5)

def start_pinging():
    global running, timeout_count
    if running:
        return
    running = True
    dns_entry.config(state="disabled")
    timeout_count = 0
    recent_pings.clear()

    def ping_loop():
        global timeout_count
        while running:
            address = dns_entry.get()
            latency = ping(address, timeout=1)
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")

            if latency is None:
                msg = f"[{timestamp}] Timeout"
                color = "red"
                timeout_count += 1
            else:
                ms = int(latency * 1000)
                recent_pings.append(ms)
                timeout_count = 0
                msg = f"[{timestamp}] Ping: {ms} ms"
                if ms < 50:
                    color = "green"
                elif ms < 150:
                    color = "blue"
                else:
                    color = "red"

            # نمایش در لاگ
            log_box.insert(tk.END, msg + "\n", color)
            log_box.see(tk.END)
            status_label.config(text=msg, fg=color)

            # وضعیت اینترنت دقیق
            if timeout_count >= 3:
                internet_status.config(
                    text="❌ اینترنت قطع است - بیش از ۳ بار عدم پاسخ",
                    fg="red"
                )
            elif len(recent_pings) >= 3:
                avg_ping = sum(recent_pings) / len(recent_pings)
                jitter = max(recent_pings) - min(recent_pings)

                if avg_ping < 80 and jitter < 50:
                    internet_status.config(
                        text="✅ اینترنت متصل است - پینگ عالی",
                        fg="green"
                    )
                elif avg_ping < 150:
                    internet_status.config(
                        text="✅ اینترنت متصل است - پینگ متوسط",
                        fg="blue"
                    )
                else:
                    internet_status.config(
                        text="⚠️ اینترنت متصل است - نوسان یا پینگ بالا",
                        fg="orange"
                    )

            # ذخیره لاگ
            if save_log_var.get():
                with open("ping_log.txt", "a", encoding="utf-8") as f:
                    f.write(msg + "\n")

            time.sleep(1)

    threading.Thread(target=ping_loop, daemon=True).start()

def stop_pinging():
    global running
    running = False
    dns_entry.config(state="normal")

def exit_program():
    stop_pinging()
    root.destroy()

def open_about():
    webbrowser.open("https://www.youtube.com/@dvhost_cloud")

# رابط کاربری
root = tk.Tk()
root.title("Ping Monitor")
root.geometry("440x570")
root.configure(bg="white")
root.resizable(False, False)

# لوگو از URL
logo_url = "https://dvhost.ir/dl/logo--Photoroom.png"
with urllib.request.urlopen(logo_url) as u:
    raw_data = u.read()
image = Image.open(io.BytesIO(raw_data)).resize((100, 100), Image.LANCZOS)
photo = ImageTk.PhotoImage(image)
tk.Label(root, image=photo, bg="white").pack(pady=(15, 5))

# عنوان
tk.Label(root, text="Ping Monitor", font=("Segoe UI", 14, "bold"), bg="white").pack()

# ورودی DNS
dns_frame = tk.Frame(root, bg="white")
dns_frame.pack(pady=(15, 0))
tk.Label(dns_frame, text="DNS Server:", bg="white", font=("Segoe UI", 10)).pack(side="left")
dns_entry = tk.Entry(dns_frame, font=("Segoe UI", 10), justify="center", width=20)
dns_entry.insert(0, "8.8.8.8")
dns_entry.pack(side="left", padx=5)

# لاگ پینگ‌ها
log_box = scrolledtext.ScrolledText(root, width=54, height=10, font=("Consolas", 9))
log_box.pack(pady=15)
log_box.tag_config("green", foreground="green")
log_box.tag_config("blue", foreground="blue")
log_box.tag_config("red", foreground="red")

# چک‌باکس ذخیره
save_log_var = tk.BooleanVar()
tk.Checkbutton(root, text="ذخیره لاگ", variable=save_log_var, bg="white", font=("Segoe UI", 9)).pack()

# باکس وضعیت اتصال
status_frame = tk.LabelFrame(root, text="وضعیت اتصال", font=("Segoe UI", 10), padx=10, pady=5, bg="white")
status_frame.pack(pady=10)
internet_status = tk.Label(status_frame, text="بررسی نشده", font=("Segoe UI", 10, "bold"), bg="white")
internet_status.pack()

# آخرین پینگ
status_label = tk.Label(root, text="", font=("Segoe UI", 9), bg="white")
status_label.pack(pady=(5, 5))

# دکمه‌ها
button_frame = tk.Frame(root, bg="white")
button_frame.pack(pady=10)

tk.Button(button_frame, text="شروع", width=10, bg="#4CAF50", fg="white", font=("Segoe UI", 10, "bold"), command=start_pinging).grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="توقف", width=10, bg="#333333", fg="white", font=("Segoe UI", 10, "bold"), command=stop_pinging).grid(row=0, column=1, padx=5)
tk.Button(button_frame, text="خروج", width=10, bg="#D32F2F", fg="white", font=("Segoe UI", 10, "bold"), command=exit_program).grid(row=0, column=2, padx=5)

# درباره ما
tk.Label(root, text="درباره ما", fg="blue", cursor="hand2", bg="white", font=("Segoe UI", 9, "underline")).pack(pady=5)
root.bind("<Button-1>", lambda e: open_about() if e.widget.cget("text") == "درباره ما" else None)

# اجرا
root.mainloop()
