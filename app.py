"""
Main application module for the Todo List app.
"""

import tkinter as tk
from tkinter import messagebox, Toplevel
from typing import List
from datetime import datetime
import re

from models import Task
from storage import load_tasks, save_tasks


class TodoApp:
    """Main application class for the Todo List."""
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the TodoApp.
        
        Args:
            root: The main Tkinter window
        """
        self.root = root
        self.root.title("📝 Mi Lista de Tareas")
        self.root.geometry("500x400")
        self.root.configure(bg='#f0f0f0')
        
        # Task storage
        self.tasks: List[Task] = []
        
        # Create UI components
        self._create_widgets()
        
        # Load existing tasks
        self._load_tasks()
        self._update_display()
    
    def _create_widgets(self) -> None:
        """Create and configure all UI widgets."""
        # Title
        title_label = tk.Label(
            self.root, 
            text="📝 Mi Lista de Tareas", 
            font=("Arial", 16, "bold"),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        title_label.pack(pady=10)
        
        # Input frame
        input_frame = tk.Frame(self.root, bg='#f0f0f0')
        input_frame.pack(pady=10, padx=20, fill='x')
        
        # Task text entry
        tk.Label(
            input_frame, 
            text="Nueva tarea:", 
            font=("Arial", 10, "bold"),
            bg='#f0f0f0',
            fg='#2c3e50'
        ).pack(anchor='w')
        
        self.task_entry = tk.Entry(
            input_frame, 
            width=50, 
            font=("Arial", 11),
            relief='solid',
            borderwidth=2
        )
        self.task_entry.pack(pady=5, fill='x')
        self.task_entry.bind('<Return>', lambda e: self._add_task())
        
        # Date entry frame
        date_frame = tk.Frame(input_frame, bg='#f0f0f0')
        date_frame.pack(fill='x', pady=5)
        
        tk.Label(
            date_frame, 
            text="Fecha (DD/MM/YYYY):", 
            font=("Arial", 10, "bold"),
            bg='#f0f0f0',
            fg='#2c3e50'
        ).pack(side='left')
        
        self.date_entry = tk.Entry(
            date_frame, 
            width=12, 
            font=("Arial", 10),
            relief='solid',
            borderwidth=2
        )
        self.date_entry.pack(side='left', padx=10)
        self.date_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        # Calendar button
        calendar_button = tk.Button(
            date_frame, 
            text="📅 Calendario", 
            command=self._open_calendar,
            bg='#FF7043',
            fg='white',
            font=("Arial", 9, "bold"),
            relief='raised',
            borderwidth=2,
            padx=10,
            pady=2
        )
        calendar_button.pack(side='left', padx=5)
        
        # Add button
        add_button = tk.Button(
            input_frame, 
            text="➕ Agregar", 
            command=self._add_task,
            bg='#27ae60',
            fg='white',
            font=("Arial", 11, "bold"),
            relief='raised',
            borderwidth=2,
            padx=20,
            pady=5
        )
        add_button.pack(pady=10)
        
        # Tasks listbox
        list_frame = tk.Frame(self.root, bg='#f0f0f0')
        list_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        tk.Label(
            list_frame, 
            text="Tareas:", 
            font=("Arial", 10, "bold"),
            bg='#f0f0f0',
            fg='#2c3e50'
        ).pack(anchor='w')
        
        # Listbox with scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.tasks_listbox = tk.Listbox(
            list_frame, 
            yscrollcommand=scrollbar.set,
            height=12,
            font=("Arial", 10),
            relief='solid',
            borderwidth=2
        )
        self.tasks_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.tasks_listbox.yview)
        
        # Bind double-click to toggle task status
        self.tasks_listbox.bind('<Double-Button-1>', 
                               lambda e: self._toggle_task())
        
        # Control buttons frame
        control_frame = tk.Frame(self.root, bg='#f0f0f0')
        control_frame.pack(pady=10)
        
        # Delete button
        delete_button = tk.Button(
            control_frame, 
            text="🗑️ Eliminar", 
            command=self._delete_task,
            bg='#D32F2F',
            fg='white',
            font=("Arial", 10, "bold"),
            relief='raised',
            borderwidth=2,
            padx=15,
            pady=5
        )
        delete_button.pack(side='left', padx=5)
    
    def _validate_date(self, date_str: str) -> bool:
        """
        Validate date format DD/MM/YYYY.
        
        Args:
            date_str: Date string to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not date_str.strip():
            return True  # Empty date is allowed
            
        pattern = r'^\d{2}/\d{2}/\d{4}$'
        if not re.match(pattern, date_str):
            return False
            
        try:
            datetime.strptime(date_str, "%d/%m/%Y")
            return True
        except ValueError:
            return False
    
    def _add_task(self) -> None:
        """Add a new task to the list with overdue detection."""
        task_text = self.task_entry.get().strip()
        date_str = self.date_entry.get().strip()
        
        # Validate task text
        if not task_text:
            messagebox.showwarning("Advertencia", "Por favor ingresa una tarea.")
            return
        
        # Validate date format
        if date_str and not self._validate_date(date_str):
            messagebox.showerror("Error", 
                               "Formato de fecha inválido. Usa DD/MM/YYYY")
            return
        
        # Check if task is overdue
        is_overdue = False
        if date_str:
            try:
                from datetime import timedelta
                fecha_tarea = datetime.strptime(date_str, "%d/%m/%Y").date()
                hoy = datetime.now().date()
                is_overdue = fecha_tarea < hoy
            except ValueError:
                # If date parsing fails, continue without overdue check
                pass
        
        # Create new task
        new_task = Task(
            text=task_text,
            date_str=date_str if date_str else None,
            status=False
        )
        
        # Add to list and save
        self.tasks.append(new_task)
        self._save_tasks()
        self._update_display()
        
        # Clear inputs
        self.task_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        # Show appropriate message
        if is_overdue:
            messagebox.showwarning("Tarea Vencida", 
                                 f"⚠️ Tarea agregada (VENCIDA): {task_text}")
        else:
            messagebox.showinfo("Éxito", f"Tarea agregada: {task_text}")
    
    def _delete_task(self) -> None:
        """Delete the selected task with confirmation."""
        selection = self.tasks_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona una tarea para eliminar.")
            return
        
        index = selection[0]
        task = self.tasks[index]
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar la tarea: '{task.text}'?"):
            del self.tasks[index]
            self._save_tasks()
            self._update_display()
            messagebox.showinfo("Éxito", "Tarea eliminada correctamente.")
    
    def _open_calendar(self) -> None:
        """Open a calendar popup to select a date."""
        def select_date():
            selected_date = f"{day_var.get()}/{month_var.get()}/{year_var.get()}"
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, selected_date)
            calendar_window.destroy()
        
        # Create calendar window
        calendar_window = Toplevel(self.root)
        calendar_window.title("Seleccionar Fecha")
        calendar_window.geometry("300x200")
        calendar_window.resizable(False, False)
        calendar_window.configure(bg='#f0f0f0')
        
        # Center the calendar window
        calendar_window.transient(self.root)
        calendar_window.grab_set()
        
        # Get current date
        today = datetime.now()
        
        # Create lists for selectors
        days = [f"{i:02d}" for i in range(1, 32)]
        months = [f"{i:02d}" for i in range(1, 13)]
        years = [str(i) for i in range(2020, 2031)]
        
        # Variables for selectors
        day_var = tk.StringVar(value=f"{today.day:02d}")
        month_var = tk.StringVar(value=f"{today.month:02d}")
        year_var = tk.StringVar(value=str(today.year))
        
        # Title
        tk.Label(calendar_window, text="Selecciona una fecha:", 
                 font=("Arial", 12, "bold"), bg='#f0f0f0', fg='#2c3e50').pack(pady=10)
        
        # Frame for selectors
        selector_frame = tk.Frame(calendar_window, bg='#f0f0f0')
        selector_frame.pack(pady=10)
        
        # Selectors
        tk.Label(selector_frame, text="Día:", bg='#f0f0f0', fg='#2c3e50').grid(row=0, column=0, padx=5)
        tk.Label(selector_frame, text="Mes:", bg='#f0f0f0', fg='#2c3e50').grid(row=0, column=1, padx=5)
        tk.Label(selector_frame, text="Año:", bg='#f0f0f0', fg='#2c3e50').grid(row=0, column=2, padx=5)
        
        tk.OptionMenu(selector_frame, day_var, *days).grid(row=1, column=0, padx=5)
        tk.OptionMenu(selector_frame, month_var, *months).grid(row=1, column=1, padx=5)
        tk.OptionMenu(selector_frame, year_var, *years).grid(row=1, column=2, padx=5)
        
        # Buttons
        button_frame = tk.Frame(calendar_window, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Seleccionar", command=select_date,
                  bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                  relief='raised', borderwidth=2, padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancelar", command=calendar_window.destroy,
                  bg="#D32F2F", fg="white", font=("Arial", 10, "bold"),
                  relief='raised', borderwidth=2, padx=15, pady=5).pack(side=tk.LEFT, padx=5)
    
    def _edit_task(self) -> None:
        """
        Edit the selected task.
        
        TODO: Implement edit functionality with dialog window
        """
        # TODO: Add edit task functionality
        # selection = self.tasks_listbox.curselection()
        # if selection:
        #     index = selection[0]
        #     task = self.tasks[index]
        #     # Open edit dialog with current task data
        #     # Update task and save
        pass
    
    def _toggle_task(self) -> None:
        """Toggle the status of the selected task."""
        selection = self.tasks_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona una tarea.")
            return
        
        index = selection[0]
        self.tasks[index].status = not self.tasks[index].status
        self._save_tasks()
        self._update_display()
    
    def _update_display(self) -> None:
        """Update the listbox display with current tasks and color coding."""
        self.tasks_listbox.delete(0, tk.END)
        
        for task in self.tasks:
            # Check if task is overdue
            is_overdue = False
            if task.date_str and not task.status:
                try:
                    fecha_tarea = datetime.strptime(task.date_str, "%d/%m/%Y").date()
                    hoy = datetime.now().date()
                    is_overdue = fecha_tarea < hoy
                except ValueError:
                    # If date parsing fails, continue without overdue check
                    pass
            
            # Format task display with appropriate icons
            if task.status:
                status_icon = "✅"
            elif is_overdue:
                status_icon = "🔴"
            else:
                status_icon = "🟢"
            
            display_text = f"{status_icon} {task.text}"
            
            if task.date_str:
                if is_overdue:
                    display_text += f" | 📅 {task.date_str} (VENCIDA)"
                else:
                    display_text += f" | 📅 {task.date_str}"
            
            self.tasks_listbox.insert(tk.END, display_text)
            
            # Color coding based on status and overdue state
            if task.status:
                # Completed tasks in light green
                self.tasks_listbox.itemconfig(tk.END, {'bg': '#d5f4e6', 'fg': '#27ae60'})
            elif is_overdue:
                # Overdue tasks in light red
                self.tasks_listbox.itemconfig(tk.END, {'bg': '#ffebee', 'fg': '#d32f2f'})
            else:
                # Pending tasks in light green
                self.tasks_listbox.itemconfig(tk.END, {'bg': '#e8f5e8', 'fg': '#2e7d32'})
    
    def _load_tasks(self) -> None:
        """Load tasks from storage."""
        self.tasks = load_tasks()
    
    def _save_tasks(self) -> None:
        """Save tasks to storage."""
        if not save_tasks(self.tasks):
            messagebox.showerror("Error", 
                               "No se pudieron guardar las tareas.")
    
    def run(self) -> None:
        """Start the application main loop."""
        self.root.mainloop()


def main() -> None:
    """Main entry point for the application."""
    root = tk.Tk()
    app = TodoApp(root)
    app.run()


if __name__ == "__main__":
    main()
