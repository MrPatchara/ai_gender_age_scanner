import cv2
import numpy as np
import webbrowser
import tkinter as tk
from tkinter import Label, Button, Frame, Toplevel, StringVar, messagebox
from PIL import Image, ImageTk
import time
import json
import subprocess
from tkinter import TclError

# Load pre-trained models for GenderNet
gender_net = cv2.dnn.readNetFromCaffe('deploy_gender.prototxt', 'gender_net.caffemodel')

# Load pre-trained Haar cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Define gender list
GENDER_LIST = ['Male', 'Female']

# Initialize ad URLs dictionary
ad_urls = {gender: "" for gender in GENDER_LIST}
# Initialize delay
delay_seconds = 10

# Load ad URLs and delay from file
def load_settings():
    global ad_urls, delay_seconds
    try:
        with open('settings.json', 'r') as file:
            settings = json.load(file)
            ad_urls = settings.get('ad_urls', ad_urls)
            delay_seconds = settings.get('delay_seconds', delay_seconds)
    except FileNotFoundError:
        ad_urls = {gender: "" for gender in GENDER_LIST}
        delay_seconds = 10
    except json.JSONDecodeError:
        ad_urls = {gender: "" for gender in GENDER_LIST}
        delay_seconds = 10

# Save ad URLs and delay to file
def save_settings():
    global ad_urls, delay_seconds
    settings = {
        'ad_urls': ad_urls,
        'delay_seconds': delay_seconds
    }
    with open('settings.json', 'w') as file:
        json.dump(settings, file, indent=4)
    messagebox.showinfo("Save Settings", "Settings have been saved successfully.")

# Initialize the settings
load_settings()

# Set up video capture from the webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 60)

# Initialize a flag to track if an ad has been opened
ad_opened = False

def close_all_browsers():
    subprocess.call(["taskkill", "/F", "/IM", "chrome.exe"])
    subprocess.call(["taskkill", "/F", "/IM", "firefox.exe"])
    subprocess.call(["taskkill", "/F", "/IM", "msedge.exe"])

# Countdown function
def countdown_popup(root, seconds):
    countdown_window = Toplevel(root)
    countdown_window.title("Preparing Camera")
    countdown_window.geometry("150x150")
    countdown_window.configure(bg='#2E2E2E')

    countdown_label = Label(countdown_window, text="", font=("Arial", 24), bg='#2E2E2E', fg='#FFFFFF')
    countdown_label.pack(expand=True)

    for i in range(seconds, 0, -1):
        try:
            countdown_label.config(text=f"{i}")
            countdown_window.update()
        except TclError:
            break
        time.sleep(1)

    try:
        countdown_window.destroy()
    except TclError:
        pass

def countdown_and_display_gender(root, gender):
    countdown_window = Toplevel(root)
    countdown_window.title("Gender Detected")
    countdown_window.geometry("300x200")
    countdown_window.configure(bg='#2E2E2E')

    Label(countdown_window, text=f"Detected Gender: {gender}", font=("Arial", 14), bg='#2E2E2E', fg='#FFFFFF').grid(row=0, column=0, padx=20, pady=20)

    countdown_label = Label(countdown_window, text="", font=("Arial", 16), bg='#2E2E2E', fg='#FFFFFF')
    countdown_label.grid(row=1, column=0, padx=20, pady=20)

    for i in range(3, 0, -1):
        countdown_label.config(text=f"Opening ad in {i} seconds...")
        countdown_window.update()
        time.sleep(1)

    countdown_window.destroy()

    close_all_browsers()

    ad_url = ad_urls.get(gender)
    if ad_url:
        webbrowser.open(ad_url, new=2, autoraise=True)
    else:
        messagebox.showerror("No Ad Found!", "No ad available for this gender")

def detect_gender(frame):
    blob = cv2.dnn.blobFromImage(frame, 1.0, (227, 227), (78.4263377603, 87.7689143744, 114.895847746), swapRB=False)
    gender_net.setInput(blob)
    gender_preds = gender_net.forward()
    gender = GENDER_LIST[gender_preds[0].argmax()]
    return gender

def start_detection():
    global is_first_scan
    if is_first_scan:
        countdown_popup(root, 10)  # Countdown 10 seconds before opening the camera
        is_first_scan = False
    
    global ad_opened
    last_ad_time = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        gender = detect_gender(frame)

        label = f'{gender}'
        cv2.putText(frame, label, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        # Convert frame to PhotoImage and update the label
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame_rgb)
        frame_tk = ImageTk.PhotoImage(frame_pil)
        video_label.config(image=frame_tk)
        video_label.image = frame_tk

        current_time = time.time()

        if not ad_opened or (current_time - last_ad_time > delay_seconds):
            countdown_and_display_gender(root, gender)
            ad_opened = True
            last_ad_time = current_time

        root.update_idletasks()
        root.update()

    cap.release()

def close_program():
    cap.release()
    root.destroy()

def open_settings():
    settings_window = Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("500x300")
    settings_window.configure(bg='#2E2E2E')

    Label(settings_window, text="Set Ad URLs and Delay", font=("Arial", 16), bg='#2E2E2E', fg='#FFFFFF').grid(row=0, column=0, columnspan=2, pady=10)

    # Add gender selection
    gender_var = StringVar(value='Male')
    Label(settings_window, text="Select Gender:", font=("Arial", 12), bg='#2E2E2E', fg='#FFFFFF').grid(row=1, column=0, padx=10, pady=5, sticky='e')
    
    male_button = Button(settings_window, text="Male", command=lambda: open_gender_settings(settings_window, 'Male'), font=("Arial", 12), bg='#FF5722', fg='#FFFFFF', padx=20, pady=10)
    male_button.grid(row=1, column=1, padx=10, pady=5)
    
    female_button = Button(settings_window, text="Female", command=lambda: open_gender_settings(settings_window, 'Female'), font=("Arial", 12), bg='#FF69B4', fg='#FFFFFF', padx=20, pady=10)
    female_button.grid(row=1, column=2, padx=10, pady=5)
    
    # Add delay setting
    row = 2
    delay_var = StringVar()
    delay_var.set(str(delay_seconds))
    Label(settings_window, text="Ad Delay (seconds): ", font=("Arial", 12), bg='#2E2E2E', fg='#FFFFFF').grid(row=row, column=0, padx=10, pady=5, sticky='e')
    delay_entry = tk.Entry(settings_window, textvariable=delay_var, width=10)
    delay_entry.grid(row=row, column=1, padx=10, pady=5, sticky='w')
    
    def save_settings_main():
        global delay_seconds
        try:
            delay_seconds = int(delay_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer for the delay.")
            return
        save_settings()
        settings_window.destroy()
    
    save_button = Button(settings_window, text="Save", command=save_settings_main, font=("Arial", 12), bg='#008CBA', fg='#FFFFFF', padx=20, pady=10)
    save_button.grid(row=row+1, column=1, padx=10, pady=20, sticky='e')
    
    exit_button = Button(settings_window, text="Exit", command=settings_window.destroy, font=("Arial", 12), bg='#FF0000', fg='#FFFFFF', padx=20, pady=10)
    exit_button.grid(row=row+1, column=0, padx=10, pady=20, sticky='w')

def open_gender_settings(parent, gender):
    gender_settings_window = Toplevel(parent)
    gender_settings_window.title(f"Settings for {gender}")
    gender_settings_window.geometry("500x500")
    gender_settings_window.configure(bg='#2E2E2E')

    Label(gender_settings_window, text=f"Ad URL for {gender}", font=("Arial", 14), bg='#2E2E2E', fg='#FFFFFF').grid(row=0, column=0, columnspan=2, pady=10)

    entry_var = StringVar()
    entry_var.set(ad_urls[gender])
    entry = tk.Entry(gender_settings_window, textvariable=entry_var, width=60)
    entry.grid(row=1, column=0, padx=10, pady=5, columnspan=2)

    def save_entry():
        global ad_urls
        ad_urls[gender] = entry_var.get()
        save_settings()
        gender_settings_window.destroy()
    
    save_button = Button(gender_settings_window, text="Save", command=save_entry, font=("Arial", 12), bg='#008CBA', fg='#FFFFFF', padx=20, pady=10)
    save_button.grid(row=2, column=1, padx=10, pady=20, sticky='e')

    exit_button = Button(gender_settings_window, text="Exit", command=gender_settings_window.destroy, font=("Arial", 12), bg='#FF0000', fg='#FFFFFF', padx=20, pady=10)
    exit_button.grid(row=2, column=0, padx=10, pady=20, sticky='w')

def open_contact_developer():
    contact_window = Toplevel(root)
    contact_window.title("Contact Developer")
    contact_window.geometry("250x380")
    contact_window.configure(bg='#2E2E2E')
    contact_window.iconphoto(False, tk.PhotoImage(file='pic.png'))

    developer_photo = Image.open("pic.png")
    developer_photo = developer_photo.resize((100, 100), Image.Resampling.LANCZOS)
    developer_photo = ImageTk.PhotoImage(developer_photo)
    photo_label = Label(contact_window, image=developer_photo, bg='#2E2E2E')
    photo_label.image = developer_photo
    photo_label.pack(pady=10)

    Label(contact_window, text="Patchara Al-umaree", font=("Arial", 10), bg='#2E2E2E', fg='#FFFFFF').pack(pady=10)
    Label(contact_window, text="Email: Patcharaalumaree@gmail.com", font=("Arial", 10), bg='#2E2E2E', fg='#FFFFFF').pack(pady=10)
    Label(contact_window, text="Student ID: 6651630177", font=("Arial", 10), bg='#2E2E2E', fg='#FFFFFF').pack(pady=10)

    def open_github():
        webbrowser.open("https://github.com/MrPatchara")
    github_button = Button(contact_window, text="GitHub", command=open_github, font=("Arial", 12), bg='#008CBA', fg='#FFFFFF').pack(pady=10)

    Button(contact_window, text="Close", command=contact_window.destroy, font=("Arial", 12), bg='#FF0000', fg='#FFFFFF').pack(pady=20)

def create_gui():
    global root, is_first_scan, video_label
    is_first_scan = True

    root = tk.Tk()
    root.title("SMART AD SELECTOR")
    
    #set resolution fullscreen
    root.attributes('-fullscreen', True)
    root.configure(bg='#2E2E2E')
    root.iconphoto(False, tk.PhotoImage(file='icon.png'))

    Label(root, text="SMART AD SELECTOR ( ป้ายโฆษณาอัจฉริยะ )", font=("Arial", 25), bg='#2E2E2E', fg='#FFFFFF').pack(pady=20)
    
    # Frame for the video feed
    video_frame = Frame(root, bg='#2E2E2E')
    video_frame.pack(padx=20, pady=20)

    # Label to display video
    video_label = Label(video_frame, bg='#2E2E2E')
    video_label.pack()

    # Label for banner image
    banner = Image.open("banner.png")
    banner = banner.resize((760, 180), Image.Resampling.LANCZOS)
    banner = ImageTk.PhotoImage(banner)
    banner_label = Label(root, image=banner, bg='#2E2E2E')
    banner_label.image = banner
    banner_label.pack(pady=10)
    
    Label(root, text="ป้ายโฆษณาอัจฉริยะจําแนกตาม เพศ", font=("Arial", 15), bg='#2E2E2E', fg='#FFFFFF').pack(pady=20)

    button_frame = Frame(root, bg='#2E2E2E')
    button_frame.pack(pady=20)

    start_icon = Image.open("start_icon.png")
    start_icon = start_icon.resize((40, 40), Image.Resampling.LANCZOS)
    start_icon = ImageTk.PhotoImage(start_icon)

    exit_icon = Image.open("exit_icon.png")
    exit_icon = exit_icon.resize((40, 40), Image.Resampling.LANCZOS)
    exit_icon = ImageTk.PhotoImage(exit_icon)

    settings_icon = Image.open("settings_icon.png")
    settings_icon = settings_icon.resize((40, 40), Image.Resampling.LANCZOS)
    settings_icon = ImageTk.PhotoImage(settings_icon)

    contact_icon = Image.open("contact_icon.png")
    contact_icon = contact_icon.resize((40, 40), Image.Resampling.LANCZOS)
    contact_icon = ImageTk.PhotoImage(contact_icon)

    start_button = Button(button_frame, text="Start", image=start_icon, compound="left", command=start_detection, font=("Arial", 12), bg='#008CBA', fg='#FFFFFF', padx=20, pady=10)
    start_button.grid(row=0, column=0, padx=10)

    exit_button = Button(button_frame, text="Exit", image=exit_icon, compound="left", command=close_program, font=("Arial", 12), bg='#FF0000', fg='#FFFFFF', padx=20, pady=10)
    exit_button.grid(row=0, column=1, padx=10)

    settings_button = Button(button_frame, text="Settings", image=settings_icon, compound="left", command=open_settings, font=("Arial", 12), bg='#4CAF50', fg='#FFFFFF', padx=20, pady=10)
    settings_button.grid(row=0, column=2, padx=10)

    contact_button = Button(button_frame, text="Developer", image=contact_icon, compound="left", command=open_contact_developer, font=("Arial", 12), bg='#FF5722', fg='#FFFFFF', padx=20, pady=10)
    contact_button.grid(row=0, column=3, padx=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
