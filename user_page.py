# 开发者：李哎呦的蓝盆友
# 设备：HUAWEI MATEBOOK 16S
# 亲爱的PYTHON玩家，请开始你的表演！
# 冒号别忘记打！！！


from datetime import datetime
from tkinter import messagebox
from tkinter import simpledialog
import tkinter as tk
import bcrypt
import pymysql
import login
import admin_page

class user_page:
    """User main page for the CUHKSZ Library Management System"""

    def __init__(self, master, id):
        self.root = master
        self.id = id
        self.root.title("CUHKSZ Library System - User Page")
        self.root.geometry("600x350")
        self.root.config(bg="#e0f7fa")
        self.setup_ui()

    def setup_ui(self):
        # Welcome message
        self.label = tk.Label(self.root, text=f" Dear {self.id}, Welcome to the CUHKSZ LIBRARY!", font=("Times New Roman", 16), bg="#e0f7fa", fg="#333")
        self.label.pack(pady=20)

        # Function buttons
        self.borrow_button = tk.Button(self.root, text="Borrow Book", font=("Arial", 12), width=15, command=self.borrow)
        self.borrow_button.pack(pady=10)

        self.return_button = tk.Button(self.root, text="Return Book", font=("Arial", 12), width=15, command=self.returN)
        self.return_button.pack(pady=10)

        self.search_button = tk.Button(self.root, text="Search Books", font=("Arial", 12), width=15, command=self.search)
        self.search_button.pack(pady=10)

        self.account_button = tk.Button(self.root, text="My Account", font=("Arial", 12), width=15, command=self.account)
        self.account_button.pack(pady=10)

        self.logout_button = tk.Button(self.root, text="Log out", font=("Arial", 15), width=10, command=self.logout)
        self.logout_button.place(x=470, y=300)

    def borrow(self):
        """Open borrow book window"""
        self.borrow_window = tk.Toplevel(self.root)
        self.borrow_window.title("Borrow Book")
        self.borrow_window.geometry("400x300")

        tk.Label(self.borrow_window, text="Enter Book Title or Author:", font=("Arial", 12)).pack(pady=10)
        self.borrow_entry = tk.Entry(self.borrow_window, font=("Arial", 12), width=30)
        self.borrow_entry.pack(pady=10)

        tk.Button(self.borrow_window, text="Search", font=("Arial", 12), command=self.search_books_to_borrow).pack(
            pady=10)

        self.borrow_result_text = tk.Text(self.borrow_window, font=("Arial", 10), width=40, height=10)
        self.borrow_result_text.pack(pady=10)

    def search_books_to_borrow(self):
        """Perform book search and display available books"""
        search_query = self.borrow_entry.get().strip()
        if not search_query:
            messagebox.showwarning("Warning", "Please enter a search keyword.")
            return

        # Connect to database
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="zzq040306",
            database="csc3170_proj"
        )
        cursor = connection.cursor()

        # Search for available books
        query = "SELECT * FROM books WHERE (book_name LIKE %s OR author LIKE %s OR book_id LIKE %s) AND statu=1"
        cursor.execute(query, (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"))
        results_a = cursor.fetchall()
        query = "SELECT * FROM books WHERE (book_name LIKE %s OR author LIKE %s OR book_id LIKE %s) AND statu=0"
        cursor.execute(query, (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"))
        results_u = cursor.fetchall()

        # Display search results
        self.borrow_result_text.delete(1.0, tk.END)
        if results_a or results_u:
            num = 1
            for row in results_a:
                book_id, title, author, publisher, price, category, status, reader = row
                availability = "Available" if status == 1 else "Borrowed"
                self.borrow_result_text.insert(tk.END,
                                               f"···{num}:\nID: {book_id},\nTitle: {title},\nAuthor: {author},\nStatus: {availability}\n\n")
                num += 1
            self.borrow_result_text.insert(tk.END, "--------------------------------------------------\n"
                                                   "The following books are borrowed and unavailable")
            for row in results_u:
                book_id, title, author, publisher, price, category, status, reader = row
                availability = "Available" if status == 1 else "Borrowed"
                self.borrow_result_text.insert(tk.END,
                                               f"ID: {book_id},\nTitle: {title},\nAuthor: {author},\nStatus: {availability}\n\n")
            self.select_book_to_borrow(results_a)
        else:
            messagebox.showinfo("No Results", "No books available for borrowing with that title or author.")

        cursor.close()
        connection.close()

    def select_book_to_borrow(self, books):
        """Allow user to select a book to borrow"""
        book_ids = [str(book[0]) for book in books]  # Get book ID list

        # Prompt user to select book ID
        flag = True
        while flag:
            selected_id = simpledialog.askstring("Select Book", "Enter Book Index Number to borrow:")
            if not selected_id:
                messagebox.showinfo("Cancelled", "Borrowing process has been cancelled.")
                return
            selected_id = selected_id.split(",")
            # Validate Book ID
            for id in selected_id:
                if int(id) <= len(book_ids):
                    if self.process_borrow(str(books[int(id)-1][0]), self.id, id):
                        flag = False
                else:
                    messagebox.showwarning("Warning", f"Invalid Book ID {id}. Please try again.")

    def process_borrow(self, book_id, reader_id, index):
        """Process book borrowing operation"""
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="zzq040306",
            database="csc3170_proj"
        )
        cursor = connection.cursor()

        try:
            borrow_date = datetime.now().strftime("%Y-%m-%d %H:%M")
            cursor.execute("INSERT INTO borrow_records (book_id, reader_name, borrow_date) VALUES (%s, %s, %s)",
                           (book_id, reader_id, borrow_date))
            cursor.execute("UPDATE books SET statu = 0 WHERE book_id = %s", (book_id,))
            cursor.execute("UPDATE books SET reader= %s WHERE book_id = %s", (reader_id, book_id))
            connection.commit()
            messagebox.showinfo("Success", f"Book{index} {book_id} borrowed successfully!")
            cursor.close()
            connection.close()
            return True
        except Exception as e:
            connection.rollback()
            messagebox.showerror("Error", f"Failed to borrow book: {e}")
            cursor.close()
            connection.close()
            return False

    def returN(self):
        """Open return book window and display currently borrowed books"""
        self.return_window = tk.Toplevel(self.root)
        self.return_window.title("Return Book")
        self.return_window.geometry("400x300")

        tk.Label(self.return_window, text="Enter Book ID to Return:", font=("Arial", 12)).pack(pady=10)
        self.return_entry = tk.Entry(self.return_window, font=("Arial", 12), width=30)
        self.return_entry.pack(pady=10)

        tk.Button(self.return_window, text="Return", font=("Arial", 12), command=self.process_return).pack(pady=10)

        self.return_result_text = tk.Text(self.return_window, font=("Arial", 10), width=40, height=10)
        self.return_result_text.pack(pady=10)

        self.show_borrowed_books()

    def show_borrowed_books(self):
        """Display list of currently borrowed books by the user"""
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="zzq040306",
            database="csc3170_proj"
        )
        cursor = connection.cursor()

        query = "SELECT books.book_id, books.book_name, books.author, borrow_records.borrow_date FROM books " \
                "JOIN borrow_records ON books.book_id = borrow_records.book_id " \
                "WHERE borrow_records.reader_name = %s"
        cursor.execute(query, (self.id,))
        borrowed_books = cursor.fetchall()

        self.return_result_text.delete(1.0, tk.END)
        self.index_to_book_id = {}
        num = 1
        if borrowed_books:
            for book in borrowed_books:
                book_id, title, author, borrow_date = book
                self.return_result_text.insert(tk.END,
                                               f"···{num}\nID: {book_id},\nTitle: {title},\nAuthor: {author},\nBorrowed on: {borrow_date}\n\n")
                self.index_to_book_id[num] = book_id
                num += 1
        else:
            self.return_result_text.insert(tk.END, "You have no borrowed books.")

        cursor.close()
        connection.close()

    def process_return(self):
        """Execute book return process using index number"""
        index_numbers = self.return_entry.get().strip()
        if not index_numbers:
            messagebox.showwarning("Warning", "Please enter Book Index Numbers to return, separated by commas.")
            return

        index_list = [int(index.strip()) for index in index_numbers.split(",") if index.strip().isdigit()]

        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="zzq040306",
            database="csc3170_proj"
        )
        cursor = connection.cursor()

        success_count = 0
        failed_indexes = []

        for index in index_list:
            book_id = self.index_to_book_id.get(index)
            if not book_id:
                failed_indexes.append(str(index))
                continue

            check_query = "SELECT * FROM borrow_records WHERE book_id = %s AND reader_name = %s"
            cursor.execute(check_query, (book_id, self.id))
            record = cursor.fetchone()

            if record:
                try:
                    borrow_date = record[3]
                    return_date = datetime.now().strftime("%Y-%m-%d %H:%M")

                    cursor.execute(
                        "INSERT INTO history_records (book_id, reader_name, borrow_date, return_date) VALUES (%s, %s, %s, %s)",
                        (book_id, self.id, borrow_date, return_date)
                    )

                    cursor.execute("UPDATE books SET statu = 1, reader = NULL WHERE book_id = %s", (book_id,))
                    cursor.execute("DELETE FROM borrow_records WHERE book_id = %s AND reader_name = %s",
                                   (book_id, self.id))

                    connection.commit()
                    success_count += 1

                except Exception as e:
                    connection.rollback()
                    print(f"Error for book {book_id}: {e}")
                    failed_indexes.append(str(index))
            else:
                failed_indexes.append(str(index))

        cursor.close()
        connection.close()

        if success_count:
            messagebox.showinfo("Success", f"{success_count} books returned successfully!")
            self.show_borrowed_books()
        if failed_indexes:
            failed_list = ", ".join(failed_indexes)
            messagebox.showwarning("Warning", f"Some books could not be returned for index numbers: {failed_list}")

    def account(self):
        """Create account page, displaying user ID, current borrow records, history, and password change option"""
        self.account_window = tk.Toplevel(self.root)
        self.account_window.title("My Account")
        self.account_window.geometry("600x500")
        self.account_window.config(bg="#f0f8ff")

        tk.Label(self.account_window, text=f"User ID: {self.id}", font=("Arial", 14), bg="#f0f8ff").pack(pady=10)

        button_frame = tk.Frame(self.account_window, bg="#f0f8ff")
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Show Borrowed Books", font=("Arial", 12),
                  command=self.show_user_borrowed_books).pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text="Show History Records", font=("Arial", 12),
                  command=self.show_user_history_records).pack(side=tk.LEFT, padx=10)

        tk.Button(self.account_window, text="Change Password", font=("Arial", 12),
                  command=self.change_own_password).pack(pady=10)

        self.user_result_text = tk.Text(self.account_window, font=("Arial", 10), width=60, height=15)
        self.user_result_text.pack(pady=10)

    def show_user_borrowed_books(self):
        """Display user's current borrow records"""
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="zzq040306",
            database="csc3170_proj"
        )
        cursor = connection.cursor()

        try:
            query_borrow = """
            SELECT b.book_id, b.book_name, r.reader_name, r.borrow_date, r.return_date 
            FROM borrow_records r
            JOIN books b ON r.book_id = b.book_id
            WHERE  r.reader_name LIKE %s
            """
            cursor.execute(query_borrow, (f"%{self.id}%",))
            borrow_results = cursor.fetchall()

            self.user_result_text.delete(1.0, tk.END)
            num = 1
            if borrow_results:
                self.user_result_text.insert(tk.END, "Current Borrowed Books:\n")
                for book_id, book_name, reader_name, borrow_date, return_date in borrow_results:
                    self.user_result_text.insert(tk.END,
                                                 f"···{num}:\nBook ID: {book_id},\nTitle: {book_name},\nBorrowed On: {borrow_date}\n\n")
                    num += 1
            else:
                messagebox.showinfo("No Results", "No current borrowed books found for this user.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve current borrowed books: {e}")
        finally:
            self.user_result_text.insert(tk.END, f"__________________________________\n{num - 1} books in total")
            cursor.close()
            connection.close()

    def show_user_history_records(self):
        """Display user's borrow history records"""
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="zzq040306",
            database="csc3170_proj"
        )
        cursor = connection.cursor()

        try:
            query_history = """
            SELECT b.book_id, b.book_name, r.reader_name, r.borrow_date, r.return_date 
            FROM history_records r
            JOIN books b ON r.book_id = b.book_id
            WHERE  r.reader_name LIKE %s
            """
            cursor.execute(query_history, (f"%{self.id}%",))
            history_results = cursor.fetchall()

            self.user_result_text.delete(1.0, tk.END)
            num = 1
            if history_results:
                self.user_result_text.insert(tk.END, "History Records:\n")
                for book_id, book_name, reader_name, borrow_date, return_date in history_results:
                    return_date = return_date if return_date else "Not Returned"
                    self.user_result_text.insert(tk.END,
                                                 f"···{num}: \nBook ID: {book_id},\n"
                                                 f"Title: {book_name},\nBorrowed On: {borrow_date},\nReturned On: {return_date}\n\n")
                    num += 1
            else:
                messagebox.showinfo("No Results", "No history records found for this user.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve history records: {e}")
        finally:
            self.user_result_text.insert(tk.END, f"__________________________________\n{num - 1} records in total")
            cursor.close()
            connection.close()

    def change_own_password(self):
        """Open a new window to allow user to change password"""
        self.password_window = tk.Toplevel(self.root)
        self.password_window.title("Change Password")
        self.password_window.geometry("400x300")
        self.password_window.config(bg="#f0f8ff")

        tk.Label(self.password_window, text="New Password:", font=("Arial", 12), bg="#f0f8ff").pack(pady=10)
        self.new_password_entry = tk.Entry(self.password_window, font=("Arial", 12), width=30, show="*")
        self.new_password_entry.pack(pady=5)

        tk.Label(self.password_window, text="Confirm Password:", font=("Arial", 12), bg="#f0f8ff").pack(pady=10)
        self.confirm_password_entry = tk.Entry(self.password_window, font=("Arial", 12), width=30, show="*")
        self.confirm_password_entry.pack(pady=5)

        tk.Button(self.password_window, text="Update Password", font=("Arial", 12),
                  command=self.update_own_password).pack(pady=20)

    def update_own_password(self):
        """Update user's password"""
        new_password = self.new_password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()

        if not new_password or not confirm_password:
            messagebox.showwarning("Warning", "Please fill in both password fields.")
            return

        if new_password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match. Please try again.")
            return

        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="zzq040306",
            database="csc3170_proj"
        )
        cursor = connection.cursor()

        try:
            query_update_password = "UPDATE all_user SET password = %s WHERE name = %s"
            cursor.execute(query_update_password, (hashed_password, self.id))
            connection.commit()

            if cursor.rowcount > 0:
                messagebox.showinfo("Success", "Password updated successfully.")
            else:
                messagebox.showerror("Error", "Failed to update the password.")
        except Exception as e:
            connection.rollback()
            messagebox.showerror("Error", f"Failed to update password: {e}")
        finally:
            cursor.close()
            connection.close()

    def search(self):
        """Open a new window to perform book search"""
        self.search_window = tk.Toplevel(self.root)
        self.search_window.title("Search Books")
        self.search_window.geometry("500x400")
        self.search_window.config(bg="#f0f8ff")

        tk.Label(self.search_window, text="Search by Title or Author:", font=("Arial", 12), bg="#f0f8ff").pack(pady=10)
        self.search_entry = tk.Entry(self.search_window, font=("Arial", 12), width=30)
        self.search_entry.pack(pady=10)

        self.search_button = tk.Button(self.search_window, text="Search", font=("Arial", 12),
                                       command=self.perform_search)
        self.search_button.pack(pady=10)

        self.result_text = tk.Text(self.search_window, font=("Arial", 10), width=40, height=15)
        self.result_text.pack(pady=10)

        self.perform_search(show_all=True)

    def perform_search(self, show_all=False):
        """Perform book search function"""
        search_query = self.search_entry.get().strip()

        if not search_query and not show_all:
            messagebox.showwarning("Warning", "Please enter a search keyword.")
            return

        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="zzq040306",
            database="csc3170_proj"
        )
        cursor = connection.cursor()

        if show_all or not search_query:
            query = "SELECT * FROM books"
            cursor.execute(query)
        else:
            query = "SELECT * FROM books WHERE book_name LIKE %s OR author LIKE %s OR book_id LIKE %s"
            cursor.execute(query, (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"))

        results = cursor.fetchall()

        self.result_text.delete(1.0, tk.END)
        if results:
            for row in results:
                book_id, book_name, author, publisher, price, category, status, reader = row
                availability = "Available" if status == 1 else "Borrowed"
                self.result_text.insert(tk.END,
                                        f"Book ID: {book_id}\n"
                                        f"Book Name: {book_name}\n"
                                        f"Author: {author}\n"
                                        f"Publisher: {publisher}\n"
                                        f"Price: {price}\n"
                                        f"Category: {category}\n"
                                        f"Status: {availability}\n\n")
        else:
            messagebox.showinfo("No Results", "No books found matching your query.")
        cursor.close()
        connection.close()

    def logout(self):
        messagebox.showerror("Exit Successful", "Thank you for using CUHKSZ Library System. See you next time!")
        self.root.destroy()
        main_root = tk.Tk()
        login.LoginPage(main_root)
        main_root.mainloop()


