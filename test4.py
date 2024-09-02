import cv2
import numpy as np
import webbrowser
import tkinter as tk
from tkinter import Label, Button, Frame, Toplevel, Entry, StringVar, messagebox
from PIL import Image, ImageTk
import time
import json

# Load pre-trained models for AgeNet and GenderNet
age_net = cv2.dnn.readNetFromCaffe('deploy_age.prototxt', 'age_net.caffemodel')
gender_net = cv2.dnn.readNetFromCaffe('deploy_gender.prototxt', 'gender_net.caffemodel')

# Define age and gender lists
AGE_LIST = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
GENDER_LIST = ['Male', 'Female']

# Initialize ad URLs dictionary
ad_urls = {gender: {age: "" for age in AGE_LIST} for gender in GENDER_LIST}
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
        ad_urls = {gender: {age: "" for age in AGE_LIST} for gender in GENDER_LIST}
        delay_seconds = 10
    except json.JSONDecodeError:
        ad_urls = {gender: {age: "" for age in AGE_LIST} for gender in GENDER_LIST}
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

# Initialize a flag to track if an ad has been opened
ad_opened = False

def countdown_and_display_age(root, age, gender):
    countdown_window = Toplevel(root)
    countdown_window.title("Age Detected")
    countdown_window.geometry("300x200")
    countdown_window.configure(bg='#2E2E2E')

    Label(countdown_window, text=f"คุณอายุ {age} ปี", font=("Arial", 14), bg='#2E2E2E', fg='#FFFFFF').grid(row=0, column=0, padx=20, pady=20)

    countdown_label = Label(countdown_window, text="", font=("Arial", 16), bg='#2E2E2E', fg='#FFFFFF')
    countdown_label.grid(row=1, column=0, padx=20, pady=20)

    for i in range(3, 0, -1):
        countdown_label.config(text=f"เปิดโฆษณาใน {i} วินาที...")
        countdown_window.update()
        time.sleep(1)

    countdown_window.destroy()

    # Open ad based on age and gender
    ad_url = ad_urls[gender].get(age)
    if ad_url:
        webbrowser.open(ad_url)

def detect_age_gender(frame):
    blob = cv2.dnn.blobFromImage(frame, 1.0, (227, 227), (78.4263377603, 87.7689143744, 114.895847746), swapRB=False)

    gender_net.setInput(blob)
    gender_preds = gender_net.forward()
    gender = GENDER_LIST[gender_preds[0].argmax()]

    age_net.setInput(blob)
    age_preds = age_net.forward()
    age = AGE_LIST[age_preds[0].argmax()]

    return gender, age

def start_detection():
    global ad_opened
    last_ad_time = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gender, age = detect_age_gender(frame)

        label = f'{gender}, {age}'
        cv2.putText(frame, label, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.imshow("Age and Gender Detection", frame)

        current_time = time.time()

        if not ad_opened or (current_time - last_ad_time > delay_seconds):
            countdown_and_display_age(root, age, gender)
            ad_opened = True
            last_ad_time = current_time

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def close_program():
    cap.release()
    cv2.destroyAllWindows()
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
    
    male_button = Button(settings_window, text="Male", command=lambda: open_gender_settings(settings_window, 'Male'), font=("Arial", 12), bg='#008CBA', fg='#FFFFFF', padx=20, pady=10)
    male_button.grid(row=1, column=1, padx=10, pady=5)
    
    female_button = Button(settings_window, text="Female", command=lambda: open_gender_settings(settings_window, 'Female'), font=("Arial", 12), bg='#FF69B4', fg='#FFFFFF', padx=20, pady=10)
    female_button.grid(row=1, column=2, padx=10, pady=5)
    
    # Add delay setting
    row = 2
    delay_var = StringVar()
    delay_var.set(str(delay_seconds))
    Label(settings_window, text="Ad Delay (seconds): ", font=("Arial", 12), bg='#2E2E2E', fg='#FFFFFF').grid(row=row, column=0, padx=10, pady=5, sticky='e')
    delay_entry = Entry(settings_window, textvariable=delay_var, width=10)
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

    Label(gender_settings_window, text=f"Ad URLs for {gender}", font=("Arial", 14), bg='#2E2E2E', fg='#FFFFFF').grid(row=0, column=0, columnspan=2, pady=10)

    row = 1
    entries = {}
    for age in AGE_LIST:
        Label(gender_settings_window, text=f"{age}: ", font=("Arial", 12), bg='#2E2E2E', fg='#FFFFFF').grid(row=row, column=0, padx=10, pady=5, sticky='e')

        entry_var = StringVar()
        entry_var.set(ad_urls[gender][age])
        entry = Entry(gender_settings_window, textvariable=entry_var, width=60)
        entry.grid(row=row, column=1, padx=10, pady=5, sticky='w')

        entries[age] = entry_var
        row += 1

    def save_entries():
        global ad_urls
        for age, var in entries.items():
            ad_urls[gender][age] = var.get()
        save_settings()
        gender_settings_window.destroy()
    
    save_button = Button(gender_settings_window, text="Save", command=save_entries, font=("Arial", 12), bg='#008CBA', fg='#FFFFFF', padx=20, pady=10)
    save_button.grid(row=row, column=1, padx=10, pady=20, sticky='e')

    exit_button = Button(gender_settings_window, text="Exit", command=gender_settings_window.destroy, font=("Arial", 12), bg='#FF0000', fg='#FFFFFF', padx=20, pady=10)
    exit_button.grid(row=row, column=0, padx=10, pady=20, sticky='w')

def open_contact_developer():
    contact_window = Toplevel(root)
    contact_window.title("Contact Developer")
    contact_window.geometry("400x300")
    contact_window.configure(bg='#2E2E2E')

    Label(contact_window, text="Contact Developer", font=("Arial", 16), bg='#2E2E2E', fg='#FFFFFF').pack(pady=10)

    Label(contact_window, text="Email: developer@example.com", font=("Arial", 12), bg='#2E2E2E', fg='#FFFFFF').pack(pady=10)

    Label(contact_window, text="Phone: +1234567890", font=("Arial", 12), bg='#2E2E2E', fg='#FFFFFF').pack(pady=10)

    Button(contact_window, text="Close", command=contact_window.destroy, font=("Arial", 12), bg='#FF0000', fg='#FFFFFF').pack(pady=20)

def create_gui():
    global root

    root = tk.Tk()
    root.title("AI Age and Gender Scanner")
    root.geometry("600x500")
    root.configure(bg='#2E2E2E')

    Label(root, text="AI Age and Gender Scanner", font=("Arial", 24), bg='#2E2E2E', fg='#FFFFFF').pack(pady=20)

    button_frame = Frame(root, bg='#2E2E2E')
    button_frame.pack(pady=20)

    start_icon = Image.open("start_icon.png")
    start_icon = start_icon.resize((40, 40), Image.Resampling.LANCZOS)
    start_icon = ImageTk.PhotoImage(start_icon)

    exit_icon = Image.open("exit_icon.png")
    exit_icon = exit_icon.resize((40, 40), Image.Resampling.LANCZOS)
    exit_icon = ImageTk.PhotoImage(exit_icon)

    start_button = Button(button_frame, text="Start", image=start_icon, compound="left", command=start_detection, font=("Arial", 12), bg='#008CBA', fg='#FFFFFF', padx=20, pady=10)
    start_button.grid(row=0, column=0, padx=10)

    exit_button = Button(button_frame, text="Exit", image=exit_icon, compound="left", command=close_program, font=("Arial", 12), bg='#FF0000', fg='#FFFFFF', padx=20, pady=10)
    exit_button.grid(row=0, column=1, padx=10)

    settings_button = Button(root, text="Settings", command=open_settings, font=("Arial", 12), bg='#4CAF50', fg='#FFFFFF', padx=20, pady=10)
    settings_button.pack(pady=10)

    contact_button = Button(root, text="Contact Developer", command=open_contact_developer, font=("Arial", 12), bg='#FF5722', fg='#FFFFFF', padx=20, pady=10)
    contact_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
