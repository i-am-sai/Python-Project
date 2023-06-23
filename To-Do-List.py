import tkinter as tk
from tkinter import messagebox
import smtplib
from email.message import EmailMessage
from pymongo import MongoClient


class ToDoListApp:
    def __init__(self):
        self.current_user = None
        self.tasks = []
        self.username = []

        # Connect to MongoDB
        client = MongoClient("mongodb://localhost:27017/")
        db = client["To_Do_List"]
        self.collection = db["Tasks_"]
        self.username_collection = db["Users"]  # Collection for storing users

        # Create the main window
        self.window = tk.Tk()
        self.window.title("To-Do List")
        self.window.geometry("500x400")

        # Create the GUI elements
        frame = tk.Frame(self.window)
        frame.pack(pady=10)

        self.listbox = tk.Listbox(
            frame,
            width=50,
            height=10,
            font=("Courier New", 12),
            bd=0,
            selectbackground="#a6a6a6",
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)

        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)

        self.entry = tk.Entry(
            self.window,
            font=("Courier New", 12)
        )
        self.entry.pack(pady=10)

        button_frame = tk.Frame(self.window)
        button_frame.pack()

        self.add_button = tk.Button(
            button_frame,
            text="Add Task",
            font=("Courier New", 12),
            command=self.add_task
        )
        self.add_button.pack(side=tk.LEFT, padx=10)

        self.delete_button = tk.Button(
            button_frame,
            text="Delete Task",
            font=("Courier New", 12),
            command=self.delete_task
        )
        self.delete_button.pack(side=tk.LEFT, padx=10)

        self.email_button = tk.Button(
            button_frame,
            text="Send Email",
            font=("Courier New", 12),
            command=self.send_email
        )
        self.email_button.pack(side=tk.LEFT, padx=10)

        self.login_button = tk.Button(
            button_frame,
            text="Login",
            font=("Courier New", 12),
            command=self.toggle_login_logout
        )
        self.login_button.pack(side=tk.LEFT, padx=10)

        self.error_label = tk.Label(
            self.window,
            text="",
            font=("Courier New", 12),
            fg="red"
        )
        self.error_label.pack(pady=10)

        self.update_login_logout_button()

    def showLoginDialog(self):
        login_dialog = tk.Toplevel(self.window)
        login_dialog.title("Login")
        login_dialog.geometry('300x150')

        username_label = tk.Label(login_dialog, text="Username:")
        username_label.pack()
        username_entry = tk.Entry(login_dialog)
        username_entry.pack(pady=10)

        login_btn = tk.Button(login_dialog, text="Login",command=lambda: self.login(username_entry.get(), login_dialog))
        login_btn.pack()

    def login(self, username, login_dialog):
        if username != "":
            self.current_user = username
            messagebox.showinfo("Notification", f"Login successful! Welcome, {username}!")
            login_dialog.destroy()

            # Retrieve tasks for the current user from MongoDB
            self.tasks = list(self.collection.find({'user': self.current_user}))

            # Update the listbox with the user's tasks
            self.updateListBox()

            # Update the login/logout button
            self.update_login_logout_button()
        else:
            messagebox.showwarning("Warning", "Please enter a username.")

    def logout(self):
        self.current_user = None
        messagebox.showinfo("Notification", "Logout successful!")

        # Clear the tasks list and listbox
        self.tasks = []
        self.listbox.delete(0, 'end')

        self.update_login_logout_button()

    def toggle_login_logout(self):
        if self.current_user:
            self.logout()
        else:
            self.showLoginDialog()

    def update_login_logout_button(self):
        if self.current_user:
            self.login_button.config(text='Logout', command=self.logout)
            self.add_button.config(state=tk.NORMAL)
            self.delete_button.config(state=tk.NORMAL)
            self.email_button.config(state=tk.NORMAL)
        else:
            self.login_button.config(text='Login', command=self.showLoginDialog)
            self.add_button.config(state=tk.DISABLED)
            self.delete_button.config(state=tk.DISABLED)
            self.email_button.config(state=tk.DISABLED)

    def send_email(self):
        if self.listbox.curselection():  # Check if a task is selected
            try:
                index = self.listbox.curselection()  # Get the index of the selected task
                selected_task = self.listbox.get(index)  # Get the text of the selected task

                # Configure your email settings
                sender_email = "p69021603@gmail.com"
                sender_password = "ipltrukffusawvnq"
                receiver_email = "saiswaroopkdevarmane@gmail.com"

                # Create an EmailMessage object
                message = EmailMessage()
                message["Subject"] = "Reminder: Task"
                message["From"] = sender_email
                message["To"] = receiver_email
                message.set_content(selected_task)

                # Connect to the SMTP server
                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login(sender_email, sender_password)

                    # Send the email
                    server.send_message(message)

                self.show_success("Email sent successfully!")
            except Exception as e:
                self.show_error(f"Failed to send email. Error: {str(e)}")
        else:
            self.show_error("No task selected!")

    def add_task(self):
        task = self.entry.get()  # Get the task entered in the text entry box
        if task:
            self.listbox.insert(tk.END, task)  # Add the task to the listbox
            self.entry.delete(0, tk.END)  # Clear the text entry box

            # Save the task to MongoDB
            task_data = {"task": task, "user": self.current_user}
            self.collection.insert_one(task_data)
        else:
            self.show_error("Task cannot be empty!")

    def delete_task(self):
        try:
            index = self.listbox.curselection()  # Get the index of the selected task
            selected_task = self.listbox.get(index)  # Get the text of the selected task
            self.listbox.delete(index)  # Remove the selected task from the listbox

            # Delete the task from MongoDB
            self.collection.delete_one({"task": selected_task, "user": self.current_user})
        except tk.TclError:
            self.show_error("No task selected!")

    def show_error(self, message):
        self.error_label.config(text=message, fg="red")

    def show_success(self, message):
        self.error_label.config(text=message, fg="green")

    def updateListBox(self):
        self.listbox.delete(0, tk.END)
        for task in self.tasks:
            self.listbox.insert(tk.END, task['task'])

    def run(self):
        self.window.mainloop()


app = ToDoListApp()
app.run()


