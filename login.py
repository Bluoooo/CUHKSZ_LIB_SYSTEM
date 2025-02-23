# 开发者：李哎呦的蓝盆友
# 设备：HUAWEI MATEBOOK 16S
# 亲爱的PYTHON玩家，请开始你的表演！
# 冒号别忘记打！！！

import tkinter as tk
from tkinter import messagebox
import pymysql
import bcrypt
import user_page
import admin_page
import random
import string

class LoginPage:
    """Login page for the Library Management System"""

    def __init__(self, master):
        self.root = master
        self.root.title("CUHKSZ Library System - Login")
        self.root.geometry("500x320")
        self.root.config(bg="#f7f7f7")
        self.setup_ui()

    def setup_ui(self):
        self.welcome_label = tk.Label(self.root, text="Welcome to CUHKSZ Library System!!!", font=("Times New Roman", 16), bg="#f7f7f7", fg="#333")
        self.welcome_label.pack(pady=20)

        # Username label and entry
        self.username_label = tk.Label(self.root, text="User ID:", font=("Times New Roman", 12), bg="#f7f7f7")
        self.username_label.place(x=50, y=80)
        self.username_entry = tk.Entry(self.root, font=("Times New Roman", 12), width=25)
        self.username_entry.place(x=230, y=80)

        # Password label and entry
        self.password_label = tk.Label(self.root, text="PASSWORD:", font=("Arial", 12), bg="#f7f7f7")
        self.password_label.place(x=50, y=120)
        self.password_entry = tk.Entry(self.root, font=("Times New Roman", 12), width=25, show="*")
        self.password_entry.place(x=230, y=120)

        # Captcha label and entry
        self.captcha_label = tk.Label(self.root, text="Verification Code:", font=("Arial", 12), bg="#f7f7f7")
        self.captcha_label.place(x=50, y=160)
        self.captcha_entry = tk.Entry(self.root, font=("Arial", 12), width=10)
        self.captcha_entry.place(x=230, y=160)

        # Generate random captcha
        self.captcha_text = self.generate_captcha()
        self.captcha_display = tk.Label(self.root, text=self.captcha_text, font=("Arial", 12, "bold"), fg="blue", bg="#f7f7f7")
        self.captcha_display.place(x=330, y=160)

        # Refresh captcha button
        self.refresh_button = tk.Button(self.root, text="Refresh", font=("Arial", 10), command=self.refresh_captcha)
        self.refresh_button.place(x=395, y=160)

        # Login button
        self.login_button = tk.Button(self.root, text="Log in", font=("Arial", 15), width=10, command=self.login)
        self.login_button.place(x=320, y=230)

        # Sign in button
        self.signin_button = tk.Button(self.root, text="Sign in", font=("Arial", 15), width=10, command=self.signin)
        self.signin_button.place(x=70, y=230)

    def generate_captcha(self):
        """Generate a random captcha"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

    def refresh_captcha(self):
        """Refresh the captcha"""
        self.captcha_text = self.generate_captcha()
        self.captcha_display.config(text=self.captcha_text)

    def login(self):
        """Functionality for login button"""
        username = self.username_entry.get()
        password = self.password_entry.get()  # Encode password as bytes

        if not username or not password:
            messagebox.showerror("Error", "Username and password cannot be empty")
        elif self.captcha_entry.get().upper() != self.captcha_text:
            messagebox.showerror("Error", "Incorrect captcha, please try again")
            self.refresh_captcha()
        else:
            try:
                conn = pymysql.connect(
                    host="localhost",
                    user="root",
                    password="zzq040306",
                    database="csc3170_proj"
                )
                cursor = conn.cursor()
                query = "SELECT password FROM all_user WHERE name = %s"
                cursor.execute(query, (username,))
                result = cursor.fetchone()

                # Check if password in database is in bcrypt hash format
                if result[0].startswith("$2b$"):
                    # bcrypt hash match
                    if bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
                        messagebox.showinfo("Login Successful", f"Welcome, {username}, to the Library Management System")
                        self.root.destroy()  # Close login window
                        main_root = tk.Tk()  # Create new main window
                        if username[:5] == "admin":
                            admin_page.admin_page(main_root, username.upper())  # Enter admin
                        else:
                            user_page.user_page(main_root, username.upper())  # Enter user
                        main_root.mainloop()
                    else:
                        messagebox.showerror("Login Failed", "Incorrect username or password")
                        return
                else:
                    # Plain text match
                    if result[0] == password:
                        messagebox.showinfo("Login Successful", f"Welcome, {username}, to the Library Management System")
                        self.root.destroy()  # Close login window
                        main_root = tk.Tk()  # Create new main window
                        if username[:5].upper() == "ADMIN":
                            admin_page.admin_page(main_root, username.upper())  # Enter admin
                        else:
                            user_page.user_page(main_root, username.upper())  # Enter user
                        main_root.mainloop()
                    else:
                        messagebox.showerror("Login Failed", "Incorrect username or password")
                        return

                cursor.close()
                conn.close()
            except pymysql.Error as err:
                messagebox.showerror("Error", f"Database connection failed: {err}")

    def signin(self):
        """Create registration window"""
        signin_window = tk.Toplevel()
        signin_window.title("Sign In - Register")
        signin_window.geometry("500x300")
        signin_window.config(bg="#f7f7f7")

        # Username label and entry
        username_label = tk.Label(signin_window, text="Username:", font=("Arial", 12), bg="#f7f7f7")
        username_label.place(x=50, y=50)
        username_entry = tk.Entry(signin_window, font=("Arial", 12), width=25)
        username_entry.place(x=200, y=50)

        # Password label and entry
        password_label = tk.Label(signin_window, text="Password:", font=("Arial", 12), bg="#f7f7f7")
        password_label.place(x=50, y=100)
        password_entry = tk.Entry(signin_window, font=("Arial", 12), width=25, show="*")
        password_entry.place(x=200, y=100)

        # Confirm password label and entry
        confirm_label = tk.Label(signin_window, text="Confirm Password:", font=("Arial", 12), bg="#f7f7f7")
        confirm_label.place(x=50, y=150)
        confirm_entry = tk.Entry(signin_window, font=("Arial", 12), width=25, show="*")
        confirm_entry.place(x=200, y=150)

        def register_user():
            """Functionality to register user"""
            username = username_entry.get()
            password = password_entry.get().encode('utf-8')
            confirm_password = confirm_entry.get().encode('utf-8')

            # Check if input is valid
            if not username or not password or not confirm_password:
                messagebox.showerror("Error", "All fields are required")
                return
            if username[:5].upper() == "ADMIN":
                messagebox.showerror("Error", "Admin accounts cannot be registered")
                return
            if password != confirm_password:
                messagebox.showerror("Error", "Passwords do not match, please try again")
                return

            # Generate hashed password
            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

            try:
                conn = pymysql.connect(
                    host="localhost",
                    user="root",
                    password="zzq040306",
                    database="csc3170_proj"
                )
                cursor = conn.cursor()

                # Check if username already exists
                cursor.execute("SELECT * FROM all_user WHERE name = %s", (username,))
                if cursor.fetchone():
                    messagebox.showerror("Error", "Username already exists, please choose another")
                else:
                    # Insert new user data
                    cursor.execute("INSERT INTO all_user (name, password) VALUES (%s, %s)", (username, hashed_password.decode('utf-8')))
                    conn.commit()
                    messagebox.showinfo("Success", "Registration successful!")
                    signin_window.destroy()  # Close registration window

                cursor.close()
                conn.close()
            except pymysql.Error as err:
                messagebox.showerror("Database Error", f"Unable to connect to the database: {err}")

        # Register button
        register_button = tk.Button(signin_window, text="Register", font=("Arial", 14), command=register_user, width=20)
        register_button.place(x=200, y=240)

if __name__ == '__main__':
    root = tk.Tk()
    LoginPage(root)
    root.mainloop()
