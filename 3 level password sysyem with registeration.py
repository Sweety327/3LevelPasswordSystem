import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont  # Removed Resampling
import hashlib
import pickle
import random
import os
import cv2
import numpy as np
from skimage.metrics import structural_similarity as compare_ssim

# Path to store user credentials
USER_DB_FILE = 'user_database.pkl'

# Initialize user database
if os.path.exists(USER_DB_FILE):
    with open(USER_DB_FILE, 'rb') as f:
        user_database = pickle.load(f)
else:
    user_database = {
        'harini': {
            'password': '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',  # admin123
        },
        'rulishi': {
            'password': 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f',  # password123
        }
    }

# Global variables for Captcha
captcha_code = ""
captcha_image_label = None

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def save_user_database():
    with open(USER_DB_FILE, 'wb') as f:
        pickle.dump(user_database, f)

def register_user(username, password, root):
    if username in user_database:
        messagebox.showerror("Registration Failed", "Username already exists.")
    else:
        user_database[username] = {'password': hash_password(password)}
        save_user_database()
        messagebox.showinfo("Registration Successful", "You have registered successfully.")
        root.destroy()
        initial_choice_ui()  # Redirect back to initial choice after registration

def login(username, password, root):
    if username in user_database:
        stored_password = user_database[username]['password']
        if stored_password == hash_password(password):
            messagebox.showinfo("Login Successful", "Login successful")
            root.destroy()
            level_2_image_checker()
        else:
            messagebox.showerror("Login Failed", "Incorrect password")
    else:
        messagebox.showerror("Login Failed", "User not found")

def generate_captcha():
    global captcha_code
    captcha_code = ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(6))

def create_captcha_image(captcha_code):
    image = Image.new('RGB', (200, 80), color=(255, 255, 0))
    d = ImageDraw.Draw(image)
    try:
        # Attempt to use a truetype font
        fnt = ImageFont.truetype("arial.ttf", 40)
    except IOError:
        # Fallback to default font if truetype font not found
        fnt = ImageFont.load_default()
    d.text((10, 10), captcha_code, fill=(0, 0, 0), font=fnt)
    return image

def verify_captcha(input_text, root):
    global captcha_code
    if input_text.upper() == captcha_code.upper():
        messagebox.showinfo("Captcha Verification", "Captcha matched successfully.")
        root.destroy()
        open_major_project_folder()
    else:
        messagebox.showerror("Captcha Verification", "Captcha mismatch.")
    generate_captcha()
    update_captcha_image()

def update_captcha_image():
    global captcha_image_label, captcha_code
    captcha_image = create_captcha_image(captcha_code)
    photo = ImageTk.PhotoImage(captcha_image)
    captcha_image_label.config(image=photo)
    captcha_image_label.image = photo

def capture_image():
    cap = cv2.VideoCapture(0)
    ret, image = cap.read()
    cap.release()
    if ret:
        return image
    else:
        messagebox.showerror("Image Capture Error", "Failed to capture an image from the camera.")
        return None

def compare_images(image1, image2):
    gray_image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray_image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    if gray_image1.shape != gray_image2.shape:
        height, width = max(gray_image1.shape[0], gray_image2.shape[0]), max(gray_image1.shape[1], gray_image2.shape[1])
        gray_image1 = cv2.resize(gray_image1, (width, height))
        gray_image2 = cv2.resize(gray_image2, (width, height))
    similarity = compare_ssim(gray_image1, gray_image2)
    return similarity

def initial_choice_ui():
    """
    New initial window allowing users to choose between Register and Login.
    """
    root = tk.Tk()
    root.title("Welcome")
    root.geometry("300x150")

    welcome_label = tk.Label(root, text="Welcome! Please choose an option:", font=("Helvetica", 12))
    welcome_label.pack(pady=20)

    register_button = tk.Button(root, text="Register", width=10, command=lambda: [root.destroy(), registration_ui()])
    register_button.pack(pady=5)

    login_button = tk.Button(root, text="Login", width=10, command=lambda: [root.destroy(), level_1_ui()])
    login_button.pack(pady=5)

    root.mainloop()

def registration_ui():
    """
    Registration window where new users can create an account.
    """
    root = tk.Tk()
    root.title("Register")
    root.geometry("300x250")

    username_label = tk.Label(root, text="Choose Username:")
    username_label.pack(pady=5)
    username_entry = tk.Entry(root)
    username_entry.pack(pady=5)

    password_label = tk.Label(root, text="Choose Password:")
    password_label.pack(pady=5)
    password_entry = tk.Entry(root, show="*")
    password_entry.pack(pady=5)

    confirm_password_label = tk.Label(root, text="Confirm Password:")
    confirm_password_label.pack(pady=5)
    confirm_password_entry = tk.Entry(root, show="*")
    confirm_password_entry.pack(pady=5)

    def handle_registration():
        username = username_entry.get().strip()
        password = password_entry.get()
        confirm_password = confirm_password_entry.get()

        if not username or not password:
            messagebox.showerror("Registration Failed", "Username and password cannot be empty.")
            return
        if password != confirm_password:
            messagebox.showerror("Registration Failed", "Passwords do not match.")
            return
        register_user(username, password, root)

    register_button = tk.Button(root, text="Register", command=handle_registration)
    register_button.pack(pady=10)

    root.mainloop()

def level_1_ui():
    """
    Modified Login UI accessed after choosing 'Login' from the initial choice window.
    """
    root = tk.Tk()
    root.title("Login - Username and Password")
    root.geometry("300x200")

    username_label = tk.Label(root, text="Username:")
    username_label.pack(pady=5)
    username_entry = tk.Entry(root)
    username_entry.pack(pady=5)

    password_label = tk.Label(root, text="Password:")
    password_label.pack(pady=5)
    password_entry = tk.Entry(root, show="*")
    password_entry.pack(pady=5)

    login_button = tk.Button(root, text="Login", width=10, command=lambda: login(username_entry.get().strip(), password_entry.get(), root))
    login_button.pack(pady=10)

    root.mainloop()

def level_2_image_checker():
    root = tk.Tk()
    root.title("Level 2 - Graphical Password Authentication")
    app = ImagePasswordAuth(root, proceed_to_level_3)
    root.mainloop()

def proceed_to_level_3():
    level_3_captcha_ui()

class ImagePasswordAuth:
    def __init__(self, root, callback):
        self.root = root
        self.callback = callback
        self.root.title("Image Password Authentication")
        self.image_label = tk.Label(root)
        self.image_label.pack()
        self.register_button = tk.Button(root, text="Register", command=self.register)
        self.register_button.pack()
        self.login_button = tk.Button(root, text="Login", command=self.login)
        self.login_button.pack()
        self.clicks = []
        self.image_path = ""
        self.user_data_file = 'user_data.pkl'
        self.load_user_data()

    def load_user_data(self):
        try:
            with open(self.user_data_file, 'rb') as f:
                self.user_data = pickle.load(f)
        except FileNotFoundError:
            self.user_data = {}

    def save_user_data(self):
        with open(self.user_data_file, 'wb') as f:
            pickle.dump(self.user_data, f)

    def register(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if not self.image_path:
            return
        self.display_image(self.image_path)
        self.clicks = []
        self.image_label.bind("<Button-1>", self.record_click)
        messagebox.showinfo("Register Clicks", "Please click on 4 points on the image to set your graphical password.")

    def login(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if not self.image_path:
            return
        if self.image_path not in self.user_data:
            messagebox.showerror("Error", "No registration found for this image.")
            return
        self.display_image(self.image_path)
        self.clicks = []
        self.image_label.bind("<Button-1>", self.verify_click)
        messagebox.showinfo("Login Clicks", "Please click on your 4 registered points on the image.")

    def display_image(self, image_path):
        try:
            img = Image.open(image_path)
            # Fix for PIL.Image.ANTIALIAS error
            img = img.resize((500, 500), Image.LANCZOS)  # Use Image.LANCZOS instead of Image.ANTIALIAS
            self.img = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.img)
            self.image_label.image = self.img
        except Exception as e:
            messagebox.showerror("Image Error", f"Failed to process image: {e}")

    def record_click(self, event):
        self.clicks.append((event.x, event.y))
        if len(self.clicks) == 4:
            self.user_data[self.image_path] = self.clicks
            self.save_user_data()
            self.image_label.unbind("<Button-1>")
            messagebox.showinfo("Success", "Graphical password registered successfully.")

    def verify_click(self, event):
        self.clicks.append((event.x, event.y))
        if len(self.clicks) == 4:
            stored_clicks = self.user_data.get(self.image_path)
            if self.verify_coordinates(stored_clicks, self.clicks):
                messagebox.showinfo("Success", "Graphical Login successful.")
                self.root.destroy()
                self.callback()
            else:
                messagebox.showerror("Error", "Graphical Login failed.")
            self.image_label.unbind("<Button-1>")

    def verify_coordinates(self, stored_clicks, current_clicks, tolerance=20):
        if len(stored_clicks) != len(current_clicks):
            return False
        for (x1, y1), (x2, y2) in zip(stored_clicks, current_clicks):
            if abs(x1 - x2) > tolerance or abs(y1 - y2) > tolerance:
                return False
        return True

def level_3_captcha_ui():
    global captcha_image_label
    root = tk.Tk()
    root.title("Level 3 - Captcha")
    generate_captcha()
    captcha_image = create_captcha_image(captcha_code)
    photo = ImageTk.PhotoImage(captcha_image)
    captcha_image_label = tk.Label(root, image=photo)
    captcha_image_label.pack(pady=10)
    entry_label = tk.Label(root, text="Enter Captcha:")
    entry_label.pack(pady=5)
    captcha_entry = tk.Entry(root)
    captcha_entry.pack(pady=5)
    verify_button = tk.Button(root, text="Verify", command=lambda: verify_captcha(captcha_entry.get(), root))
    verify_button.pack(pady=5)
    regenerate_button = tk.Button(root, text="Regenerate Captcha", command=update_captcha_image)
    regenerate_button.pack(pady=5)
    root.mainloop()

def open_major_project_folder():
    folder_path = r'D:\Major Project'  # Use raw string to handle backslashes
    if not os.path.exists(folder_path):
        messagebox.showerror("Error", f"Folder path does not exist: {folder_path}")
        return
    try:
        os.startfile(folder_path)
    except Exception as e:
        messagebox.showerror("Error Opening Major Project Folder", str(e))    

if __name__ == "__main__":
    initial_choice_ui()  # Start with the initial choice window
