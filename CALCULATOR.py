
import customtkinter as ctk
import tkinter as tk
from tkinter import Tk, Canvas, PhotoImage, messagebox, Toplevel
import sqlite3
import math
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk


# Database setup
conn = sqlite3.connect('mangrove_data.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS measurements
             (light_intensity REAL, height REAL)''')
#conn.commit()

# Function to calculate height
def calculate_height():
    try:
        adjacent = float(adjacent_entry.get())
        angle = float(angle_entry.get())
        angle_in_radians = math.radians(angle)
        height = adjacent * math.tan(angle_in_radians)
        height_result_label.configure(text=f"Calculated Height: {height:.2f} units")
        height_entry.delete(0, ctk.END)
        height_entry.insert(0, f"{height:.2f}")
    except ValueError:
        messagebox.showerror("Input error", "Please enter valid numbers for adjacent and angle.")

# Function to add data to the database
def add_to_database():
    try:
        light_intensity = float(light_intensity_entry.get())
        height = float(height_entry.get())
        c.execute("INSERT INTO measurements (light_intensity, height) VALUES (?, ?)", 
                  (light_intensity, height))
        conn.commit()
        messagebox.showinfo("Success", "Data added to database.")
    except ValueError:
        messagebox.showerror("Input error", "Please enter valid numbers for light intensity and height.")
    adjacent_entry.delete(0, ctk.END)
    angle_entry.delete(0, ctk.END)
    height_entry.delete(0, ctk.END)
    light_intensity_entry.delete(0, ctk.END)
    height_result_label.configure(text="Calculated Height: N/A")
    adjacent_entry.focus_set()

# Function to generate scatter plot with trendline
def generate_plot():
    c.execute("SELECT * FROM measurements")
    data = c.fetchall()
    if not data:
        messagebox.showerror("No data", "No data available in the database.")
        adjacent_entry.focus_set()
        return

    heights = [row[1] for row in data]
    light_intensities = [row[0] for row in data]
    
    fig, ax = plt.subplots(figsize=(10, 6))  # Adjust the figsize to make the plot larger
    ax.scatter(heights, light_intensities, color='blue', label='Data points')
    
    # Calculate and plot trendline
    z = np.polyfit(heights, light_intensities, 1)
    p = np.poly1d(z)
    ax.plot(heights, p(heights), color='red', linestyle='--', label='Trendline')
    
    # Extract the gradient (slope) and intercept
    gradient = z[0]
    intercept = z[1]
    equation = f"y = {gradient:.2f}x + {intercept:.2f}"
    
    # Display the gradient and equation on the plot
    ax.text(0.05, 0.95, f"Gradient: {gradient:.2f}", transform=ax.transAxes, fontsize=12, verticalalignment='top')
    ax.text(0.05, 0.90, f"Equation: {equation}", transform=ax.transAxes, fontsize=12, verticalalignment='top')

    ax.set_xlabel('Height')
    ax.set_ylabel('Light Intensity')
    ax.set_title('The Relationship between Illuminosity and the Height of Mangrove Plant')
    ax.legend()
    
    # Embed plot in CustomTkinter window
    global canvas
    if canvas:
        canvas.get_tk_widget().destroy()
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().place(x=800, y=800, width=1200, height=800)

          # Function to clear all input fields
def clear_inputs():
    adjacent_entry.delete(0, ctk.END)
    angle_entry.delete(0, ctk.END)
    height_entry.delete(0, ctk.END)
    light_intensity_entry.delete(0, ctk.END)
    height_result_label.configure(text="Calculated Height: N/A")
    adjacent_entry.focus_set()
    
# Function to delete the graph
def delete_graph():
    global canvas
    if canvas:
        canvas.get_tk_widget().destroy()
        canvas = None    
    adjacent_entry.focus_set()

# Function to reset the database
def reset_database():
    if messagebox.askokcancel("Reset Database", "Are you sure you want to delete all data in the database?"):
        c.execute("DELETE FROM measurements")
        conn.commit()
        messagebox.showinfo("Success", "All data has been deleted.")
    adjacent_entry.focus_set()

# Function to open the database editor window
def open_database_editor():
    editor_window = Toplevel(window)
    editor_window.title("Edit Database Records")
    editor_window.geometry("600x450")
    # Function to load data into the listbox
    def load_data():
        c.execute("SELECT rowid, * FROM measurements")
        records = c.fetchall()
        for record in records:
            listbox.insert(tk.END, record)
    
    # Function to delete a selected record
    def delete_record():
        selected = listbox.curselection()
        if selected:
            record_id = listbox.get(selected[0])[0]
            c.execute("DELETE FROM measurements WHERE rowid=?", (record_id,))
            conn.commit()
            listbox.delete(selected)
            messagebox.showinfo("Success", "Record deleted.")
        else:
            messagebox.showerror("Selection error", "No record selected.")
    
    # Function to update a selected record
    def update_record():
        selected = listbox.curselection()
        if selected:
            record_id = listbox.get(selected[0])[0]
            new_light_intensity_str = light_intensity_editor_entry.get()
            new_height_str = height_editor_entry.get()

            if not new_light_intensity_str or not new_height_str:
                messagebox.showerror("Input Error", "Please enter values for both light intensity and height.")
                return

            try:
                new_light_intensity = float(new_light_intensity_str)
                new_height = float(new_height_str)

            except ValueError:
                messagebox.showerror("Input Error", "Invalid input for light intensity or height. Please enter valid numbers.")
                return

            c.execute("UPDATE measurements SET light_intensity=?, height=? WHERE rowid=?", 
                  (new_light_intensity, new_height, record_id))
            conn.commit()
            listbox.delete(selected)
            listbox.insert(selected, (record_id, new_light_intensity, new_height))
            messagebox.showinfo("Success", "Record updated.")
        else:
            messagebox.showerror("Selection error", "No record selected.")
    
    # Listbox to display records
    listbox = tk.Listbox(editor_window, width=50, height=15)
    listbox.pack(pady=20)
    load_data()

    # Entry fields for editing
    # create the text box Username
    def on_enter(e):
       lighted.delete(0, 'end')


    def on_leave(e):
       name = lighted.get()
       if name == '':
           lighted.insert(0, 'Light Intensity')
               
    lighted = tk.Entry(editor_window, width=25)
    lighted.pack(pady=5)
    lighted.bind('<FocusIn>', on_enter)
    lighted.bind('<FocusOut>', on_leave)

    def on_enter(e):
       heighted.delete(0, 'end')

    def on_leave(e):
       name = heighted.get()
       if name == '':
           heighted.insert(0, 'Tree Height')
           
    heighted = tk.Entry(editor_window, width=25)
    heighted.pack(pady=5)
    heighted.bind('<FocusIn>', on_enter)
    heighted.bind('<FocusOut>', on_leave)

    # Buttons for delete and update actions
    delete_button = tk.Button(editor_window, text="Delete Record", command=delete_record)
    delete_button.pack(pady=5)
    update_button = tk.Button(editor_window, text="Update Record", command=update_record)
    update_button.pack(pady=5)
    
# Set up the main window
ctk.set_appearance_mode("System")  # Modes: system (default), light, dark
ctk.set_default_color_theme("green")  # Themes: blue (default), dark-blue, green

window = ctk.CTk()
window.title("Mangrove Plant Data")
window.geometry('1920x1080')

canvas = None  # Initialize the global canvas variable

# Create and place the labels and entry widgets for the height calculator
adjacent_label = ctk.CTkLabel(window, text="Base length (Adjacent):", width=200, height=25)
adjacent_label.place(x=500, y=30)

adjacent_entry = ctk.CTkEntry(window, width=100, height=25, placeholder_text="Enter")
adjacent_entry.place(x=700, y=30)

angle_label = ctk.CTkLabel(window, text="Angle (in degrees):", width=200, height=25)
angle_label.place(x=500, y=70)

angle_entry = ctk.CTkEntry(window, width=100, height=25, placeholder_text="Enter")
angle_entry.place(x=700, y=70)

calculate_button = ctk.CTkButton(window, text="Calculate Height", command=calculate_height, width=150, height=25)
calculate_button.place(x=570, y=120)

height_result_label = ctk.CTkLabel(window, text="Calculated Height: N/A", width=250, height=25)
height_result_label.place(x=550, y=160)

# Create and place the labels and entry widgets for the database and plot
light_intensity_label = ctk.CTkLabel(window, text="Light Intensity:", width=200, height=25)
light_intensity_label.place(x=500, y=200)

light_intensity_entry = ctk.CTkEntry(window, width=100, height=25, placeholder_text="Enter")
light_intensity_entry.place(x=700, y=200)

height_label = ctk.CTkLabel(window, text="Height:", width=200, height=25)
height_label.place(x=500, y=250)

height_entry = ctk.CTkEntry(window, width=100, height=25, placeholder_text="TBD")
height_entry.place(x=700, y=250)

clear_button = ctk.CTkButton(window, text="Clear Inputs", command=clear_inputs, width=150, height=25, fg_color="transparent", border_color="#006769", border_width=2)
clear_button.place(x=790, y=350)

add_button = ctk.CTkButton(window, text="Add to Database", command=add_to_database, width=150, height=25, fg_color="transparent", border_color="#FFCC70", border_width=2)
add_button.place(x=500, y=300)

reset_button = ctk.CTkButton(window, text="Reset Database", command=reset_database, width=150, height=25, fg_color="transparent", border_color="#FFCC70", border_width=2)
reset_button.place(x=790, y=300)

edit_button = ctk.CTkButton(window, text="Edit Database", command=open_database_editor, width=100, height=25, fg_color="transparent", border_color="#FFCC70", border_width=2)
edit_button.place(x=670, y=300)

plot_button = ctk.CTkButton(window, text="Generate Plot", command=generate_plot, width=150, height=25, fg_color="transparent", border_color="#006769", border_width=2)
plot_button.place(x=500, y=350)

delete_plot_button = ctk.CTkButton(window, text="Delete Graph", command=delete_graph, width=100, height=25, fg_color="transparent", border_color="#006769", border_width=2)
delete_plot_button.place(x=670, y=350)

# Start the CustomTkinter event loop
window.mainloop()

# Close the database connection when the window is closed
conn.close()
