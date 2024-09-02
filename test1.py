from PIL import Image, ImageTk
import tkinter as tk
from tkinter import Label, Button, Frame, Menu, Toplevel, Entry, StringVar, IntVar, messagebox
import json
import webbrowser
import time
import platform
import os
import cv2  # ตรวจสอบว่ามีการนำเข้า OpenCVแล้ว
import numpy as np
import os
os.system("taskkill /F /IM chrome.exe /T")
os.system("taskkill /F /IM firefox.exe /T")

import os
os.system("pkill -f chrome")
os.system("pkill -f firefox")


# Load pre-trained models for AgeNet and GenderNet
age_net = cv2.dnn.readNetFromCaffe('deploy_age.prototxt', 'age_net.caffemodel')
gender_net = cv2.dnn.readNetFromCaffe('deploy_gender.prototxt', 'gender_net.caffemodel')

# กำหนดรายการอายุและเพศ
AGE_LIST = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
GENDER_LIST = ['Male', 'Female']

# เริ่มต้นพจนานุกรม URL โฆษณาและดีเลย์
ad_urls = {gender: {age: "" for age in AGE_LIST} for gender in GENDER_LIST}
delay_seconds = 10  # ค่าเริ่มต้นของดีเลย์
ad_opened = False  # กำหนดค่าเริ่มต้นสำหรับตัวแปร ad_opened

# โหลด URL โฆษณาและดีเลย์จากไฟล์
def load_settings():
    global ad_urls, delay_seconds
    try:
        with open('settings.json', 'r') as file:
            settings = json.load(file)
            ad_urls = settings.get('ad_urls', ad_urls)
            delay_seconds = settings.get('delay_seconds', delay_seconds)
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        pass

# บันทึก URL โฆษณาและดีเลย์ลงในไฟล์
def save_settings():
    global ad_urls, delay_seconds
    settings = {
        'ad_urls': ad_urls,
        'delay_seconds': delay_seconds
    }
    with open('settings.json', 'w') as file:
        json.dump(settings, file, indent=4)
    messagebox.showinfo("บันทึกการตั้งค่า", "การตั้งค่าได้รับการบันทึกเรียบร้อยแล้ว")

# โหลดการตั้งค่าจากไฟล์
load_settings()

def close_browsers():
    """ปิดเบราว์เซอร์ทั้งหมดก่อนเปิดลิงก์ใหม่"""
    system = platform.system()
    if system == "Windows":
        os.system("taskkill /F /IM chrome.exe")  # เปลี่ยนเป็นเบราว์เซอร์ที่ใช้
        os.system("taskkill /F /IM firefox.exe")
    elif system == "Linux" or system == "Darwin":
        os.system("pkill chrome")  # เปลี่ยนเป็นเบราว์เซอร์ที่ใช้
        os.system("pkill firefox")
    else:
        messagebox.showerror("ข้อผิดพลาด", "ไม่สามารถระบุระบบปฏิบัติการ")

def countdown_and_display_age(root, age, gender):
    countdown_window = Toplevel(root)
    countdown_window.title("อายุที่ตรวจพบ")
    countdown_window.geometry("300x200")
    countdown_window.configure(bg='#2E2E2E')

    Label(countdown_window, text=f"คุณอายุ {age} ปี", font=("Arial", 14), bg='#2E2E2E', fg='#FFFFFF').pack(pady=20)

    countdown_label = Label(countdown_window, text="", font=("Arial", 16), bg='#2E2E2E', fg='#FFFFFF')
    countdown_label.pack(pady=20)

    for i in range(3, 0, -1):
        countdown_label.config(text=f"เปิดโฆษณาใน {i} วินาที...")
        countdown_window.update()
        time.sleep(1)

    countdown_window.destroy()

    # ปิดเบราว์เซอร์และเปิดโฆษณาตามอายุและเพศ
    close_browsers()
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
    global ad_opened  # ใช้ตัวแปรระดับทั่วทั้งโปรแกรม
    cap = cv2.VideoCapture(0)
    ad_opened = False
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
    cv2.destroyAllWindows()  # ปิดหน้าต่าง OpenCV
    root.destroy()

def open_settings():
    global male_entries, female_entries
    male_entries = {age: StringVar() for age in AGE_LIST}
    female_entries = {age: StringVar() for age in AGE_LIST}

    def save_entries():
        global ad_urls, delay_seconds
        ad_urls['Male'] = {age: male_entries[age].get() for age in AGE_LIST}
        ad_urls['Female'] = {age: female_entries[age].get() for age in AGE_LIST}
        try:
            delay_seconds = int(delay_entry.get())
        except ValueError:
            messagebox.showerror("ข้อผิดพลาด", "กรุณากรอกค่าเป็นตัวเลข")
            return
        save_settings()

    def create_gender_window(gender):
        settings_window = Toplevel(root)
        settings_window.title(f"การตั้งค่า - {gender}")
        settings_window.geometry("600x400")
        settings_window.configure(bg='#2E2E2E')

        Label(settings_window, text=f"การตั้งค่า URL โฆษณาสำหรับ {gender}", font=("Arial", 16), bg='#2E2E2E', fg='#FFFFFF').pack(pady=10)

        settings_frame = Frame(settings_window, bg='#2E2E2E')
        settings_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        for grid_row, age in enumerate(AGE_LIST):
            Label(settings_frame, text=f"{age}: ", font=("Arial", 12), bg='#2E2E2E', fg='#FFFFFF').grid(row=grid_row, column=0, padx=10, pady=5, sticky='e')

            entry_var = male_entries[age] if gender == 'Male' else female_entries[age]
            entry = Entry(settings_frame, textvariable=entry_var, width=50)
            entry.grid(row=grid_row, column=1, padx=10, pady=5, sticky='w')

        button_frame = Frame(settings_window, bg='#2E2E2E')
        button_frame.pack(pady=20, side=tk.BOTTOM, fill=tk.X)

        save_button = Button(button_frame, text="บันทึก", command=save_entries, font=("Arial", 12), bg='#008CBA', fg='#FFFFFF', padx=20, pady=10)
        save_button.pack(side=tk.LEFT, padx=10)

        exit_button = Button(button_frame, text="ออก", command=settings_window.destroy, font=("Arial", 12), bg='#F44336', fg='#FFFFFF', padx=20, pady=10)
        exit_button.pack(side=tk.RIGHT, padx=10)

    def open_male_settings():
        create_gender_window('Male')

    def open_female_settings():
        create_gender_window('Female')

    settings_window = Toplevel(root)
    settings_window.title("การตั้งค่า")
    settings_window.geometry("600x400")
    settings_window.configure(bg='#2E2E2E')

    Label(settings_window, text="การตั้งค่า URL โฆษณาและดีเลย์", font=("Arial", 16), bg='#2E2E2E', fg='#FFFFFF').pack(pady=10)

    settings_frame = Frame(settings_window, bg='#2E2E2E')
    settings_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

    Button(settings_frame, text="การตั้งค่า URL โฆษณาสำหรับชาย", command=open_male_settings, font=("Arial", 12), bg='#4CAF50', fg='#FFFFFF').pack(pady=5)
    Button(settings_frame, text="การตั้งค่า URL โฆษณาสำหรับหญิง", command=open_female_settings, font=("Arial", 12), bg='#F44336', fg='#FFFFFF').pack(pady=5)

    Label(settings_frame, text="ดีเลย์ในการตรวจจับ (วินาที):", font=("Arial", 12), bg='#2E2E2E', fg='#FFFFFF').pack(pady=10)
    delay_entry = Entry(settings_frame, width=10)
    delay_entry.insert(0, delay_seconds)
    delay_entry.pack(pady=10)

    button_frame = Frame(settings_window, bg='#2E2E2E')
    button_frame.pack(pady=20, side=tk.BOTTOM, fill=tk.X)

    save_button = Button(button_frame, text="บันทึก", command=save_entries, font=("Arial", 12), bg='#008CBA', fg='#FFFFFF', padx=20, pady=10)
    save_button.pack(side=tk.LEFT, padx=10)

    exit_button = Button(button_frame, text="ออก", command=settings_window.destroy, font=("Arial", 12), bg='#F44336', fg='#FFFFFF', padx=20, pady=10)
    exit_button.pack(side=tk.RIGHT, padx=10)

def create_gui():
    global root
    root = tk.Tk()
    root.title("Age and Gender Scanner")
    root.geometry("600x400")
    root.configure(bg='#2E2E2E')

    menu_bar = Menu(root)
    root.config(menu=menu_bar)

    settings_menu = Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="การตั้งค่า", menu=settings_menu)
    settings_menu.add_command(label="การตั้งค่า", command=open_settings)

    button_frame = Frame(root, bg='#2E2E2E')
    button_frame.pack(pady=20)

    start_icon = Image.open("start_icon.png")
    start_icon = start_icon.resize((40, 40), Image.LANCZOS)
    start_icon = ImageTk.PhotoImage(start_icon)

    exit_icon = Image.open("exit_icon.png")
    exit_icon = exit_icon.resize((40, 40), Image.LANCZOS)
    exit_icon = ImageTk.PhotoImage(exit_icon)

    start_button = Button(button_frame, text="เริ่มต้น", image=start_icon, compound=tk.LEFT, command=start_detection, font=("Arial", 12), bg='#4CAF50', fg='#FFFFFF', padx=20, pady=10)
    start_button.pack(side=tk.LEFT, padx=10)

    exit_button = Button(button_frame, text="ออก", image=exit_icon, compound=tk.LEFT, command=close_program, font=("Arial", 12), bg='#F44336', fg='#FFFFFF', padx=20, pady=10)
    exit_button.pack(side=tk.LEFT, padx=10)

    root.mainloop()

create_gui()
