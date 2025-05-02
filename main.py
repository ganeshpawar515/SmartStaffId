import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
import sqlite3
import shutil
import os
import threading
import facerecognition
from functools import partial
is_recognizing=False


class edb:
    def __init__(self):
        # Set up SQLite database connection
        self.conn = sqlite3.connect('employee.db')
        self.cursor = self.conn.cursor()

        # Create table if it doesn't exist
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS employees (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT,
                            age INTEGER,
                            position TEXT,
                            salary REAL,
                            image_path TEXT)''')
        self.conn.commit()

        # Global variable to store the selected image path
        self.selected_image_path = None
        self.e_register()

    # Function to select an image
    def select_image(self):
        self.selected_image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
        if self.selected_image_path:
            self.label_image_path.config(text=self.selected_image_path)

    # Function to insert employee data into SQLite
    def submit(self):

        name = self.entry_name.get()
        age = self.entry_age.get()
        position = self.entry_position.get()
        salary = self.entry_salary.get()
        
        if not name or not age or not position or not salary or not self.selected_image_path:
            messagebox.showerror("Input Error", "All fields and image are required")
            return
        
        try:
            age = int(age)
            salary = float(salary)
        except ValueError:
            messagebox.showerror("Input Error", "Age must be an integer and Salary must be a number")
            return
        
        # Insert the employee data into the database and get the new employee ID
        employee = (name, age, position, salary, "")
        self.cursor.execute("INSERT INTO employees (name, age, position, salary, image_path) VALUES (?, ?, ?, ?, ?)", employee)
        employee_id = self.cursor.lastrowid
        
        # Create the "images" directory if it doesn't exist
        images_directory = os.path.join(os.getcwd(), "images")
        if not os.path.exists(images_directory):
            os.makedirs(images_directory)
        
        # Copy the selected image to the "images" directory with the new name
        try:
            image_extension = os.path.splitext(self.selected_image_path)[1]
            new_image_filename = f"{employee_id}{image_extension}"
            new_image_path = os.path.join(images_directory, new_image_filename)
            shutil.copy(self.selected_image_path, new_image_path)
            
            # Update the employee record with the new image path
            self.cursor.execute("UPDATE employees SET image_path = ? WHERE id = ?", (new_image_path, employee_id))
            self.conn.commit()
        except Exception as e:
            messagebox.showerror("File Error", f"Failed to copy image: {e}")
            return
        
        messagebox.showinfo("Success", "Employee data inserted successfully")
        self.clear_entries()

    # Function to clear entries after submission
    def clear_entries(self):

        self.entry_name.delete(0, tk.END)
        self.entry_age.delete(0, tk.END)
        self.entry_position.delete(0, tk.END)
        self.entry_salary.delete(0, tk.END)
        self.label_image_path.config(text="")
        self.selected_image_path = None
        #self.conn.close()
    #READ
    def get_emp(self):
        self.extra_window2 = tk.Toplevel()
        self.extra_window2.title("Get Employee")
        self.extra_window2.geometry("300x400")
        ttk.Label(self.extra_window2, text="Enter employee name").pack(padx=10,pady=10)
        self.emp_name_inp=ttk.Entry(self.extra_window2)
        self.emp_name_inp.pack(padx=10,pady=10)
        ttk.Button(self.extra_window2, text="Search", command=self.id_results).pack(padx=10, pady=10)
    def id_results(self):
        employee_name=self.emp_name_inp.get().strip()
        self.cursor.execute("SELECT * FROM employees WHERE LOWER(name) LIKE LOWER(?)", ('%'+employee_name+'%',))
        employee_info = self.cursor.fetchall()
        if employee_info:
            print(employee_info)
            messagebox.showinfo(title="ids found", message=f"data found : {employee_info}")
        
    #CREATE
    def e_register(self):
        print("inside register")
        # Name
        tk.Label(window, text="Name:").pack()
        self.entry_name = tk.Entry(window)
        self.entry_name.pack(fill="x")

        # Age
        tk.Label(window, text="Age:").pack(padx=10, pady=10)
        self.entry_age = tk.Entry(window)
        self.entry_age.pack( padx=10, pady=10,fill="x")

        # Position
        tk.Label(window, text="Position:").pack(padx=10, pady=10)
        self.entry_position = tk.Entry(window)
        self.entry_position.pack(padx=10, pady=10,fill="x")

        # Salary
        tk.Label(window, text="Salary:").pack(padx=10, pady=10)
        self.entry_salary = tk.Entry(window)
        #entry_salary.insert(tk.END,"10")
        self.entry_salary.pack( padx=10, pady=10,fill="x")

        # Image selection
        tk.Button(window, text="Select Image", command=self.select_image).pack(padx=10, pady=10)
        self.label_image_path = tk.Label(window, text="", wraplength=250)
        self.label_image_path.pack( padx=10, pady=10,fill="x")

        # Submit button
        submit_button = tk.Button(window, text="Submit", command=self.submit)
        submit_button.pack( padx=10, pady=20,fill="x")

        clear_button = tk.Button(window, text="Clear", command=self.clear_entries)
        clear_button.pack( padx=10,fill="x")
        print("at end")

    #DELETE EMPLOYEE
    def e_delete(self):
        self.extra_window = tk.Toplevel()
        self.extra_window.title("Delete Employee")
        self.extra_window.geometry("300x400")
        ttk.Label(self.extra_window, text="Enter employee id").pack(padx=10,pady=10)
        self.emp_id=ttk.Entry(self.extra_window)
        self.emp_id.pack(padx=10,pady=10)
        ttk.Button(self.extra_window, text="Delete", command=self.confirm_delete).pack(padx=10, pady=10)
    def confirm_delete(self):
        employee_id=self.emp_id.get().strip()
        self.cursor.execute("SELECT * FROM employees WHERE id=?", (employee_id,))
        employee_info = self.cursor.fetchone()
        if employee_info:
            if messagebox.askokcancel(title="delete data", message=f"{employee_info} this data will be deleted permanently!"):
                image_path=employee_info[5]
                print("Img path:",image_path)
                self.cursor.execute("DELETE FROM employees WHERE id=?", (employee_id,))
                self.conn.commit()
                if os.path.exists(image_path):
                    os.remove(image_path)
                    print(f"image {image_path} deleted")
                else:
                    print(f"image not found {image_path}")
                messagebox.showinfo(title="alert", message="data deleted!")
        else:
            messagebox.showerror(title="id not found", message="employee with given id not found in database")
    def close_window(self):
        self.extra_window.destroy()

    def e_update(self):
        print("opened Employee update")
        tk.Label(window, text="Update Employee", font=("Arial",33)).pack( padx=10, pady=10)
        tk.Label(window, text="Employee id :", font=("Arial",16)).pack( padx=10, pady=10)
        
        self.textbox= tk.Text(window, height=1, font=("Arial", 16))
        self.textbox.pack(padx=10, pady=10)
       
        e_id = self.textbox.get('1.0', tk.END).strip()

        print("E:",e_id)
        tk.Button(window, text="Search", command=lambda: self.get_e()).pack()
    def get_e(self):
        e_id = self.textbox.get('1.0', tk.END).strip()
        print("e id:",e_id)
        self.cursor.execute("SELECT * FROM employees WHERE id=?", (e_id,))
        employee_info = self.cursor.fetchone()
        print("e info:", employee_info)
        self.update(employee_info)
    def update(self,e_info):
        print("update form")
        tk.Label(window, text="Name:").pack(padx=10, pady=10)
        self.entry_name = tk.Entry(window)
        self.entry_name.pack(padx=10, pady=10)

        # Age
        tk.Label(window, text="Age:").pack( padx=10, pady=10)
        self.entry_age = tk.Entry(window)
        self.entry_age.pack(padx=10, pady=10)

        # Position
        tk.Label(window, text="Position:").pack( padx=10, pady=10)
        self.entry_position = tk.Entry(window)
        self.entry_position.pack(padx=10, pady=10)

        # Salary
        tk.Label(window, text="Salary:").pack( padx=10, pady=10)
        self.entry_salary = tk.Entry(window)
        #entry_salary.insert(tk.END,"10")
        self.entry_salary.pack(padx=10, pady=10)

        # Image selection
        tk.Button(window, text="Select Image", command=self.select_image).pack( padx=10, pady=10)
        self.label_image_path = tk.Label(window, text="", wraplength=250)
        self.label_image_path.pack( padx=10, pady=10)

        # Submit button
        submit_button = tk.Button(window, text="Update", command=self.update_it)
        submit_button.pack( padx=10, pady=20)
        print("at end")
    def update_it(self):
        print("ddone")

#inheriting
class ui(edb):
    facerecognition=facerecognition
    def __init__(self) -> None:
        mainmenu=tk.Menu(window)
        
        option_menu=tk.Menu(mainmenu, tearoff=False)
        option_menu.add_command(label='Employee Info', command=self.get_emp)
        option_menu.add_command(label="Remove Employee", command=self.e_delete)

        mainmenu.add_cascade(menu=option_menu,label="Options")
        mainmenu.add_command(label="quit", command=exit)
        mainmenu.add_command(label="recognize", command=self.recognize_thread_work)
        mainmenu.add_command(label="stop recognition", command=self.stop)
        window.config(menu=mainmenu)
        window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.conn = sqlite3.connect('employee.db')
        self.cursor = self.conn.cursor()
    def on_closing(self):
        print("Hello world")
        if messagebox.askyesno(title="Quit?", message="Do you really wants to quit?"):
            window.destroy()
    def recognize_thread_work(self):
        self.t1=threading.Thread(target=self.recognize_thread)
        self.t1.start()
    def recognize_thread(self):
        global is_recognizing
        print("inside recognition thread function")
        global face_recognition
        if is_recognizing==False:
            print("inside if is_recognition:",is_recognizing)
            is_recognizing=True
            print("inside if is_recognition:",is_recognizing)
            face_recognition=self.facerecognition.recognition()
            face_recognition.start_recognition()
        else:
            print("inside else")
            messagebox.showwarning(title="Recognition warning", message="recognition already in progess!")
    def stop(self):
        global is_recognizing
        if is_recognizing: face_recognition.stop_recognition()
        is_recognizing=False
        print("recognition stopped")
# Create Tkinter window
window = tk.Tk()
window.title("Employee Information")
window.geometry("500x500")
ui()
edb()
print("edb called")
# Run the application
window.mainloop()

