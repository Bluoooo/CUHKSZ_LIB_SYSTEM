# 开发者：李哎呦的蓝盆友
# 设备：HUAWEI MATEBOOK 16S
# 亲爱的PYTHON玩家，请开始你的表演！
# 冒号别忘记打！！！


from tkinter import messagebox, simpledialog
from pypinyin import pinyin,Style
import tkinter as tk
import bcrypt
import pymysql
import login
import user_page


class admin_page:
    """ADMIN main page of CUHKSZ Library System"""

    def __init__(self, master,id):
        self.root = master
        self.id = id
        self.root.title("CUHKSZ Library System - Admin Page")
        self.root.geometry("600x400")
        self.root.config(bg="#e0f7fa")
        self.setup_ui()

    def setup_ui(self):
        # WELCOME
        self.label = tk.Label(self.root, text=f"Dear Administrator {self.id} , Welcome to the CUHKSZ Library!", font=("Times New Roman", 16), bg="#e0f7fa", fg="#333")
        self.label.pack(pady=20)

        # functiion button
        self.add_button = tk.Button(self.root, text="Add book", font=("Arial", 12), width=15, command=self.add)
        self.add_button.pack(pady=10)

        self.delete_button = tk.Button(self.root, text="Delete Book", font=("Arial", 12), width=15, command=self.delete)
        self.delete_button.pack(pady=10)

        self.search_button = tk.Button(self.root, text="Search Book", font=("Arial", 12), width=15,command=self.search)
        self.search_button.pack(pady=10)

        self.manage_button = tk.Button(self.root, text="Manage User", font=("Arial", 12), width=15,command=self.manage)
        self.manage_button.pack(pady=10)

        self.account_button = tk.Button(self.root, text="My Account", font=("Arial", 12), width=15,command=self.account)
        self.account_button.pack(pady=10)


        self.logout_button = tk.Button(self.root, text="Log out", font=("Arial", 15), width=10, command=self.logout)
        self.logout_button.place(x=470, y=350)

    def add(self):
        """Open add book window"""
        self.add_window = tk.Toplevel(self.root)
        self.add_window.title("Add Book")
        self.add_window.geometry("400x400")

        tk.Label(self.add_window, text="Book Name:").pack(pady=5)
        self.book_name_entry = tk.Entry(self.add_window, width=30)
        self.book_name_entry.pack()

        tk.Label(self.add_window, text="Author:").pack(pady=5)
        self.author_entry = tk.Entry(self.add_window, width=30)
        self.author_entry.pack()

        tk.Label(self.add_window, text="Publisher:").pack(pady=5)
        self.publisher_entry = tk.Entry(self.add_window, width=30)
        self.publisher_entry.pack()

        tk.Label(self.add_window, text="Price:").pack(pady=5)
        self.price_entry = tk.Entry(self.add_window, width=30)
        self.price_entry.pack()

        tk.Label(self.add_window, text="Category:").pack(pady=5)
        self.category_entry = tk.Entry(self.add_window, width=30)
        self.category_entry.pack()

        tk.Button(self.add_window, text="Add Book", command=self.process_add).pack(pady=20)

    def generate_book_id(self, author_name):
        """Generate new book ID"""
        # use pinyin if it is chinese characters and ow use English
        if all('\u4e00' <= char <= '\u9fff' for char in author_name):
            initials = ''.join([word[0].upper() for word in pinyin(author_name, style=Style.FIRST_LETTER)])
        else:
            initials = ''.join([word[0].upper() for word in author_name.split()])  # English process

        # Link the database to get the number of books of the same writer
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="zzq040306",
            database="csc3170_proj"
        )
        cursor = connection.cursor()
        try:
            query = "SELECT COUNT(*) FROM books WHERE book_id LIKE %s"
            cursor.execute(query, (f"{initials}%",))

            count = cursor.fetchone()[0] + 1  # add 1
        finally:
            cursor.close()
            connection.close()

        # return same formatted book_id，like "YH001"
        return f"{initials}{count:03}"

    def capitalize_if_english(self,text):
        """capitalize the first letter"""
        if text.isascii():  # to judge if it is all in English
            return text.title()
        return text

    def process_add(self):
        """Add to the database"""
        book_name = self.capitalize_if_english(self.book_name_entry.get().strip())
        author = self.capitalize_if_english(self.author_entry.get().strip())
        publisher = self.capitalize_if_english(self.publisher_entry.get().strip())
        price = self.price_entry.get().strip()
        category = self.capitalize_if_english(self.category_entry.get().strip())

        if not all([book_name, author, publisher, price, category]):
            messagebox.showwarning("Warning", "Please fill in all fields.")
            return

        try:
            book_id = self.generate_book_id(author)

            connection = pymysql.connect(
                host="localhost",
                user="root",
                password="zzq040306",
                database="csc3170_proj"
                )
            cursor = connection.cursor()

            query = """
            INSERT INTO books (book_id, book_name, author, publisher, price, catagory, statu, reader)
            VALUES (%s, %s, %s, %s, %s, %s, DEFAULT, DEFAULT)
                """
            cursor.execute(query, (book_id, book_name, author, publisher, float(price), category))
            connection.commit()

            messagebox.showinfo("Success", f"Book '{book_name}' added successfully with Book ID: {book_id}")

            # to clean the lable
            self.book_name_entry.delete(0, tk.END)
            self.author_entry.delete(0, tk.END)
            self.publisher_entry.delete(0, tk.END)
            self.price_entry.delete(0, tk.END)
            self.category_entry.delete(0, tk.END)

        except Exception as e:
            connection.rollback()
            messagebox.showerror("Error", f"Failed to add book: {e}")
        finally:
            cursor.close()
            connection.close()

    def delete(self):
        """open the delete window"""
        self.delete_window = tk.Toplevel(self.root)
        self.delete_window.title("Delete Book")
        self.delete_window.geometry("400x300")

        tk.Label(self.delete_window, text="Enter Book Title or Author:", font=("Arial", 12)).pack(pady=10)
        self.borrow_entry = tk.Entry(self.delete_window, font=("Arial", 12), width=30)
        self.borrow_entry.pack(pady=10)

        tk.Button(self.delete_window, text="Search", font=("Arial", 12), command=self.search_books_to_delete).pack(
            pady=10)

        self.borrow_result_text = tk.Text(self.delete_window, font=("Arial", 10), width=40, height=10)
        self.borrow_result_text.pack(pady=10)

    def search_books_to_delete(self):
        """search the books and show available books"""
        self.borrow_result_text.delete("1.0",tk.END)
        search_query = self.borrow_entry.get().strip()
        if not search_query:
            messagebox.showwarning("Warning", "Please enter a search keyword.")
            return

        # link to the database
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="zzq040306",
            database="csc3170_proj"
        )
        cursor = connection.cursor()

        # find the availabel books
        query = "SELECT * FROM books WHERE (book_name LIKE %s OR author LIKE %s OR book_id like %s) and statu=1"
        cursor.execute(query, (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"))
        results_a = cursor.fetchall()
        query = "SELECT * FROM books WHERE (book_name LIKE %s OR author LIKE %s OR book_id like %s) and statu=0"
        cursor.execute(query, (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"))
        results_u = cursor.fetchall()

        # show the query results
        #self.borrow_result_text.delete(1.0, tk.END)
        if results_a or results_u:
            num = 1
            for row in results_a:
                book_id, title, author, publisher, price, category, status, reader = row
                availability = "Available" if status == 1 else "Borrowed"
                self.borrow_result_text.insert(tk.END,
                                               f"···{num}:\nID: {book_id},\nTitle: {title},\nAuthor: {author},\nStatus: {availability}\n\n")
                num += 1
            if results_u:
                self.borrow_result_text.insert(tk.END, "--------------------------------------------------\n"
                                                   "The following books are borrowed and undeletable")
            for row in results_u:
                book_id, title, author, publisher, price, category, status, reader = row
                availability = "Available" if status == 1 else "Borrowed"
                self.borrow_result_text.insert(tk.END,
                                               f"ID: {book_id},\nTitle: {title},\nAuthor: {author},\nStatus: {availability}\n\n")
            self.select_book_to_delete(results_a)
        else:
            messagebox.showinfo("No Results", "No books available for deleting with that title or author.")

        cursor.close()
        connection.close()

    def select_book_to_delete(self, books):
        """select a book to delete"""
        book_ids = [str(book[0]) for book in books]  # 获取书籍ID列表

        # pop up a window for selecting books
        flag=True
        while flag:
            # enter Book ID
            selected_id = simpledialog.askstring("Select Book", "Enter Book Index Number to delete:")
            # if no input or cancelled, tthen break the loop
            if not selected_id:
                messagebox.showinfo("Cancelled", "Delete process has been cancelled.")
                return
            selected_id = selected_id.split(",")
            # check if the input id is correct
            for id in selected_id:
                if int(id) <= len(book_ids):
                    if  self.process_delete(str(books[int(id) - 1][0]), id):
                        flag=False
                else:
                    messagebox.showwarning("Warning", f"Invalid Book ID {id}. Please try again.")

    def process_delete(self, book_id, index):
        """the delete process"""
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="zzq040306",
            database="csc3170_proj"
        )
        cursor = connection.cursor()

        # update the status and delete the record in the database
        try:
            cursor.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
            connection.commit()
            messagebox.showinfo("Success", f"Book{index} {book_id} was deleted successfully!")
            cursor.close()
            connection.close()
            return True
        except Exception as e:
            connection.rollback()
            messagebox.showerror("Error", f"Failed to delete book: {e}")
            cursor.close()
            connection.close()
            return False

    def search(self):
        """open a window to di searching"""
        self.search_window = tk.Toplevel(self.root)
        self.search_window.title("Search Books")
        self.search_window.geometry("500x400")
        self.search_window.config(bg="#f0f8ff")

        # search lable and entry
        tk.Label(self.search_window, text="Search by Title or Author:", font=("Arial", 12), bg="#f0f8ff").pack(pady=10)
        self.search_entry = tk.Entry(self.search_window, font=("Arial", 12), width=30)
        self.search_entry.pack(pady=10)

        # search botton
        self.search_button = tk.Button(self.search_window, text="Search", font=("Arial", 12),
                                       command=self.perform_search)
        self.search_button.pack(pady=10)

        # the textbox for the result
        self.result_text = tk.Text(self.search_window, font=("Arial", 10), width=40, height=15)
        self.result_text.pack(pady=10)

        # to show all the books initially
        self.perform_search(show_all=True)

    def manage(self):
        """open a new window for user management"""
        self.manage_window = tk.Toplevel(self.root)
        self.manage_window.title("Manage User Information")
        self.manage_window.geometry("600x500")
        self.manage_window.config(bg="#f0f8ff")

        # search lable and entry
        tk.Label(self.manage_window, text="Enter User ID or Name:", font=("Arial", 12), bg="#f0f8ff").pack(pady=10)
        self.user_search_entry = tk.Entry(self.manage_window, font=("Arial", 12), width=30)
        self.user_search_entry.pack(pady=10)

        # the textbox for the result
        self.user_result_text = tk.Text(self.manage_window, font=("Arial", 10), width=50, height=20)
        self.user_result_text.pack(pady=10)

        # to place the button
        button_frame = tk.Frame(self.manage_window, bg="#f0f8ff")
        button_frame.pack(pady=10)

        # button for current records
        tk.Button(button_frame, text="Show Current Borrowed Books", font=("Arial", 12),
                  command=self.show_current_borrowed).pack(side=tk.LEFT, padx=10)

        # button for history records
        tk.Button(button_frame, text="Show History Records", font=("Arial", 12),
                  command=self.show_history_records).pack(side=tk.LEFT, padx=10)

        # the button for c changing password
        self.change_password_button = tk.Button(self.manage_window, text="!Change Password!", font=("Arial", 12),
                                                command=self.change_password)
        self.change_password_button.place(x=445,y=50)

        #the button for all users
        self.see_all_user_button = tk.Button(self.manage_window, text="See All users", font=("Arial", 12),
                                                command=self.see_all_user)
        self.see_all_user_button.place(x=25, y=50)

    def show_current_borrowed(self):
        """show current recordings"""
        user_query = self.user_search_entry.get().strip()

        if not user_query:
            messagebox.showwarning("Warning", "Please enter a user ID or name.")
            return

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
            cursor.execute(query_borrow, (f"%{user_query}%", ))
            borrow_results = cursor.fetchall()

            self.user_result_text.delete(1.0, tk.END)
            num=1
            if borrow_results:
                self.user_result_text.insert(tk.END, "Current Borrowed Books:\n")
                for book_id, book_name, reader_name, borrow_date,return_date in borrow_results:
                    self.user_result_text.insert(tk.END,
                                                 f"···{num}:\nBook ID: {book_id},\nTitle: {book_name},\nBorrowed On: {borrow_date}\n\n")
                    num+=1
            else:
                messagebox.showinfo("No Results", "No current borrowed books found for this user.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve current borrowed books: {e}")
        finally:
            self.user_result_text.insert(tk.END, f"__________________________________\n{num - 1} books in total")
            cursor.close()
            connection.close()

    def show_history_records(self):
        """show history recordings"""
        user_query = self.user_search_entry.get().strip()

        if not user_query:
            messagebox.showwarning("Warning", "Please enter a user ID or name.")
            return

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
            cursor.execute(query_history, (f"%{user_query}%", ))
            history_results = cursor.fetchall()

            self.user_result_text.delete(1.0, tk.END)
            num=1
            if history_results:
                self.user_result_text.insert(tk.END, "History Records:\n")
                for book_id, book_name, reader_name, borrow_date, return_date in history_results:
                    return_date = return_date if return_date else "Not Returned"
                    self.user_result_text.insert(tk.END,
                                                 f"···{num}: \nBook ID: {book_id},\n"
                                                 f"Title: {book_name},\nBorrowed On: {borrow_date},\nReturned On: {return_date}\n\n")
                    num+=1
            else:
                messagebox.showinfo("No Results", "No history records found for this user.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve history records: {e}")
        finally:
            self.user_result_text.insert(tk.END, f"__________________________________\n{num-1} books in total")
            cursor.close()
            connection.close()

    def change_password(self):
        """open a new window for changing users' password"""
        self.password_window = tk.Toplevel(self.root)
        self.password_window.title("Change User Password")
        self.password_window.geometry("400x400")
        self.password_window.config(bg="#f0f8ff")

        tk.Label(self.password_window, text="Enter User ID:", font=("Arial", 12), bg="#f0f8ff").pack(pady=10)
        self.user_id_entry = tk.Entry(self.password_window, font=("Arial", 12), width=30)
        self.user_id_entry.pack(pady=5)

        tk.Label(self.password_window, text="New Password:", font=("Arial", 12), bg="#f0f8ff").pack(pady=10)
        self.new_password_entry = tk.Entry(self.password_window, font=("Arial", 12), width=30, show="*")
        self.new_password_entry.pack(pady=5)

        tk.Label(self.password_window, text="Confirm Password:", font=("Arial", 12), bg="#f0f8ff").pack(pady=10)
        self.confirm_password_entry = tk.Entry(self.password_window, font=("Arial", 12), width=30, show="*")
        self.confirm_password_entry.pack(pady=5)

        tk.Button(self.password_window, text="Update Password", font=("Arial", 12), command=self.update_password).pack(
            pady=20)

    def update_password(self):
        """update the password"""
        user_id = self.user_id_entry.get().strip()
        new_password = self.new_password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()

        if not user_id or not new_password or not confirm_password:
            messagebox.showwarning("Warning", "Please fill in all fields.")
            return

        if new_password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match. Please try again.")
            return

        # hash the new password for security
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="zzq040306",
            database="csc3170_proj"
        )
        cursor = connection.cursor()

        try:
            # check if the user ecists
            query_check_user = "SELECT * FROM all_user WHERE name = %s"
            cursor.execute(query_check_user, (user_id,))
            user = cursor.fetchone()

            if not user:
                messagebox.showwarning("Warning", f"User ID {user_id} not found.")
                return

            # uodate the user password
            query_update_password = "UPDATE all_user SET password = %s WHERE name = %s"
            cursor.execute(query_update_password, (hashed_password, user_id))
            connection.commit()

            if cursor.rowcount > 0:
                messagebox.showinfo("Success", f"Password updated successfully for User ID: {user_id}")
            else:
                messagebox.showerror("Error", "Failed to update the password.")
        except Exception as e:
            connection.rollback()
            messagebox.showerror("Error", f"Failed to update password: {e}")
        finally:
            cursor.close()
            connection.close()

    def see_all_user(self):
        """search and show all the users"""
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="zzq040306",
            database="csc3170_proj"
        )
        cursor = connection.cursor()

        try:
            # search the informatpn of the users
            query = "SELECT name FROM all_user order by name"
            cursor.execute(query)
            users = cursor.fetchall()

            # clear the textbox and show
            self.user_result_text.delete(1.0, tk.END)
            if users:
                self.user_result_text.insert(tk.END, "All Users:\n")
                num=1
                for username in users:
                    if username[0][:5].upper()=="ADMIN":
                        type="Admin"
                    else:
                        type="Reader"
                    self.user_result_text.insert(tk.END, f"···{num}:\nUsername: {username}\nType: {type}\n\n")
                    num+=1
            else:
                self.user_result_text.insert(tk.END, "No users found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve users: {e}")
        finally:
            self.user_result_text.insert(tk.END, f"__________________________________\n{num-1} users in total")
            cursor.close()
            connection.close()

    def account(self):
        """Create an account page that displays only the user name and provides the ability to change the password"""
        self.account_window = tk.Toplevel(self.root)
        self.account_window.title("My Account")
        self.account_window.geometry("400x300")
        self.account_window.config(bg="#f0f8ff")

        # show username
        tk.Label(self.account_window, text=f"User ID: {self.id}", font=("Arial", 14), bg="#f0f8ff").pack(pady=20)

        # button for changing password
        tk.Button(self.account_window, text="Change Password", font=("Arial", 12),
                  command=self.change_own_password).pack(pady=20)

    def change_own_password(self):
        """open a new window for chaging tthe admin's password"""
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
        """update own password"""
        new_password = self.new_password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()

        if not new_password or not confirm_password:
            messagebox.showwarning("Warning", "Please fill in both password fields.")
            return

        if new_password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match. Please try again.")
            return

        # hash the new password for sequrity
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

    def perform_search(self, show_all=False):
        """Performs the book search functionality"""
        search_query = self.search_entry.get().strip()

        # Check if a search keyword is entered; if not and it's not an initial load, show a warning
        if not search_query and not show_all:
            messagebox.showwarning("Warning", "Please enter a search keyword.")
            return

        # Connect to the database
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="zzq040306",
            database="csc3170_proj"
        )
        cursor = connection.cursor()

        # Query all books or search by keyword based on conditions
        if show_all or not search_query:
            query = "SELECT * FROM books"
            cursor.execute(query)
        else:
            query = "SELECT * FROM books WHERE book_name LIKE %s OR author LIKE %s OR book_id LIKE %s"
            cursor.execute(query, (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"))

        results = cursor.fetchall()

        # Clear and display the search results
        self.result_text.delete(1.0, tk.END)  # Clear previous results
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
                                        f"Status: {availability}\n"
                                        f"Reader: {reader}\n\n")
        else:
            messagebox.showinfo("No Results", "No books found matching your query.")

        # Close the database connection
        cursor.close()
        connection.close()

    def logout(self):
        messagebox.showerror("Logout Successful", "Thank you for using CUHKSZ LIB SYSTEM")
        self.root.destroy()  # Close the login window
        main_root = tk.Tk()  # Create a new main window
        login.LoginPage(main_root)  # Navigate to the main interface
        main_root.mainloop()

