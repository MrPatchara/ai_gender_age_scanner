import cv2
import numpy as np
import webbrowser
import tkinter as tk
from tkinter import Label, Button, Frame, Menu, Toplevel, Entry, StringVar, messagebox
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

# Load ad URLs from file
def load_ad_urls():
    global ad_urls
    try:
        with open('ad_urls.json', 'r') as file:
            ad_urls = json.load(file)
    except FileNotFoundError:
        ad_urls = {gender: {age: "" for age in AGE_LIST} for gender in GENDER_LIST}
    except json.JSONDecodeError:
        ad_urls = {gender: {age: "" for age in AGE_LIST} for gender in GENDER_LIST}

# Save ad URLs to file
def save_ad_urls():
    global ad_urls
    with open('ad_urls.json', 'w') as file:
        json.dump(ad_urls, file, indent=4)
    messagebox.showinfo("Save Settings", "Ad URLs have been saved successfully.")

# Initialize the ad URLs
load_ad_urls()

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
    ad_delay = 10  # delay in seconds before allowing another ad to open

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gender, age = detect_age_gender(frame)

        label = f'{gender}, {age}'
        cv2.putText(frame, label, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.imshow("Age and Gender Detection", frame)

        current_time = time.time()

        if not ad_opened or (current_time - last_ad_time > ad_delay):
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
    settings_window.geometry("500x700")
    settings_window.configure(bg='#2E2E2E')

    Label(settings_window, text="Set Ad URLs", font=("Arial", 16), bg='#2E2E2E', fg='#FFFFFF').grid(row=0, column=0, columnspan=2, pady=10)

    row = 1
    entries = {}
    for gender in GENDER_LIST:
        Label(settings_window, text=f"Ad URLs for {gender}", font=("Arial", 14), bg='#2E2E2E', fg='#FFFFFF').grid(row=row, column=0, columnspan=2, pady=10)
        row += 1
        for age in AGE_LIST:
            Label(settings_window, text=f"{gender} {age}: ", font=("Arial", 10), bg='#2E2E2E', fg='#FFFFFF').grid(row=row, column=0, padx=10, pady=5, sticky='e')

            entry_var = StringVar()
            entry_var.set(ad_urls[gender][age])
            entry = Entry(settings_window, textvariable=entry_var, width=60)
            entry.grid(row=row, column=1, padx=10, pady=5, sticky='w')

            entries[(gender, age)] = entry_var
            row += 1

    def save_entries():
        global ad_urls
        for (gender, age), var in entries.items():
            ad_urls[gender][age] = var.get()
        save_ad_urls()

    save_button = Button(settings_window, text="Save", command=save_entries, font=("Arial", 12), bg='#008CBA', fg='#FFFFFF', padx=20, pady=10)
    save_button.grid(row=row, column=1, padx=10, pady=20, sticky='e')

def create_gui():
    global root
    root = tk.Tk()
    root.title("Age and Gender Detection with Ads")
    root.geometry("500x350")
    root.configure(bg='#2E2E2E')

    menu_bar = Menu(root)
    root.config(menu=menu_bar)

    settings_menu = Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Settings", menu=settings_menu)
    settings_menu.add_command(label="Ad URLs", command=open_settings)

    title_label = Label(root, text="Age and Gender Detection", font=("Arial", 16), bg='#2E2E2E', fg='#FFFFFF')
    title_label.pack(pady=20)

    button_frame = Frame(root, bg='#2E2E2E')
    button_frame.pack(pady=20)

    # Add icons for buttons
    start_icon = Image.open("start_icon.png")
    start_icon = start_icon.resize((40, 40), Image.LANCZOS)
    start_icon = ImageTk.PhotoImage(start_icon)

    exit_icon = Image.open("exit_icon.png")
    exit_icon = exit_icon.resize((40, 40), Image.LANCZOS)
    exit_icon = ImageTk.PhotoImage(exit_icon)

    start_button = Button(button_frame, text="Start", image=start_icon, compound="left", command=start_detection, font=("Arial", 12), bg='#008CBA', fg='#FFFFFF', padx=20, pady=10)
    start_button.grid(row=0, column=0, padx=10)

    exit_button = Button(button_frame, text="Exit", image=exit_icon, compound="left", command=close_program, font=("Arial", 12), bg='#F44336', fg='#FFFFFF', padx=20, pady=10)
    exit_button.grid(row=0, column=1, padx=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
