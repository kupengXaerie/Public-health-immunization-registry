import sqlite3
from tkinter import *
from tkinter import messagebox, simpledialog, ttk

conn = sqlite3.connect('immunization_registry.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS individuals (
                name TEXT PRIMARY KEY,
                dob TEXT
            )''')

c.execute('''CREATE TABLE IF NOT EXISTS vaccinations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                individual_name TEXT,
                vaccine_name TEXT,
                date_administered TEXT,
                FOREIGN KEY (individual_name) REFERENCES individuals(name)
            )''')

conn.commit()
class Individual:
    def __init__(self, name, dob):
        self.name = name
        self.dob = dob

    def save(self):
        with conn:
            c.execute("INSERT OR REPLACE INTO individuals (name, dob) VALUES (?, ?)", (self.name, self.dob))

    @staticmethod
    def get(name):
        c.execute("SELECT name, dob FROM individuals WHERE name = ?", (name,))
        row = c.fetchone()
        return Individual(row[0], row[1]) if row else None

    @staticmethod
    def delete(name):
        with conn:
            c.execute("DELETE FROM vaccinations WHERE individual_name = ?", (name,))
            c.execute("DELETE FROM individuals WHERE name = ?", (name,))

    def add_vaccination(self, vaccine_name, date_administered):
        with conn:
            c.execute("INSERT INTO vaccinations (individual_name, vaccine_name, date_administered) VALUES (?, ?, ?)",
                      (self.name, vaccine_name, date_administered))

    def update_vaccination(self, vaccine_name, date_administered):
        with conn:
            c.execute("UPDATE vaccinations SET date_administered = ? WHERE individual_name = ? AND vaccine_name = ?",
                      (date_administered, self.name, vaccine_name))

    def delete_vaccination(self, vaccine_name):
        with conn:
            c.execute("DELETE FROM vaccinations WHERE individual_name = ? AND vaccine_name = ?", (self.name, vaccine_name))

    def get_vaccination_history(self):
        c.execute("SELECT individual_name, vaccine_name, date_administered FROM vaccinations WHERE individual_name = ?", (self.name,))
        rows = c.fetchall()
        return rows
class ImmunizationRegistry:
    def add_individual(self, individual):
        individual.save()

    def update_individual_vaccination(self, name, vaccine_name, date_administered):
        individual = Individual.get(name)
        if individual:
            individual.update_vaccination(vaccine_name, date_administered)
        else:
            messagebox.showerror("Error", f"{name} is not in the registry.")

    def delete_individual_vaccination(self, name, vaccine_name):
        individual = Individual.get(name)
        if individual:
            individual.delete_vaccination(vaccine_name)
        else:
            messagebox.showerror("Error", f"{name} is not in the registry.")

    def delete_individual(self, name):
        individual = Individual.get(name)
        if individual:
            Individual.delete(name)
        else:
            messagebox.showerror("Error", f"{name} is not in the registry.")

    def get_individual_vaccination_history(self, name):
        individual = Individual.get(name)
        if individual:
            return individual.get_vaccination_history()
        else:
            return []

registry = ImmunizationRegistry()
class Application(Tk):
    def __init__(self):
        super().__init__()
        self.title("Immunization Registry")
        self.geometry("700x500")
        self.create_widgets()

    def create_widgets(self):
        self.menu_label = Label(self, text="Options:", font=("Arial", 14))
        self.menu_label.pack(pady=10)

        self.add_individual_button = Button(self, text="Add Individual to Registry", command=self.add_individual_to_registry, width=30)
        self.add_individual_button.pack(pady=5)

        self.add_vaccination_button = Button(self, text="Add Vaccination Record", command=self.add_vaccination_record, width=30)
        self.add_vaccination_button.pack(pady=5)

        self.update_vaccination_button = Button(self, text="Update Vaccination Record", command=self.update_vaccination_record, width=30)
        self.update_vaccination_button.pack(pady=5)

        self.delete_vaccination_button = Button(self, text="Delete Vaccination Record", command=self.delete_vaccination_record, width=30)
        self.delete_vaccination_button.pack(pady=5)

        self.delete_individual_button = Button(self, text="Delete Individual", command=self.delete_individual, width=30)
        self.delete_individual_button.pack(pady=5)

        self.get_history_button = Button(self, text="Get Vaccination History", command=self.get_vaccination_history, width=30)
        self.get_history_button.pack(pady=5)

        self.exit_button = Button(self, text="Exit", command=self.quit, width=30)
        self.exit_button.pack(pady=5)
        self.tree = ttk.Treeview(self, columns=("Name", "Vaccine", "Date"), show="headings")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Vaccine", text="Vaccine")
        self.tree.heading("Date", text="Date Administered")
        self.tree.pack(pady=20, fill=BOTH, expand=True)

    def add_individual_to_registry(self):
        name = simpledialog.askstring("Input", "Enter the name of the individual:")
        if name:
            dob = simpledialog.askstring("Input", "Enter the date of birth (YYYY-MM-DD):")
            if dob:
                individual = Individual(name, dob)
                registry.add_individual(individual)
                messagebox.showinfo("Info", f"{name} has been added to the registry.")

    def add_vaccination_record(self):
        name = simpledialog.askstring("Input", "Enter the name of the individual:")
        if name:
            vaccine_name = simpledialog.askstring("Input", "Enter the name of the vaccine:")
            if vaccine_name:
                date_administered = simpledialog.askstring("Input", "Enter the date the vaccine was administered (YYYY-MM-DD):")
                if date_administered:
                    individual = Individual.get(name)
                    if individual:
                        individual.add_vaccination(vaccine_name, date_administered)
                        messagebox.showinfo("Info", f"Vaccination record added for {name}.")
                    else:
                        messagebox.showerror("Error", f"{name} is not in the registry.")

    def update_vaccination_record(self):
        name = simpledialog.askstring("Input", "Enter the name of the individual:")
        if name:
            vaccine_name = simpledialog.askstring("Input", "Enter the name of the vaccine:")
            if vaccine_name:
                date_administered = simpledialog.askstring("Input", "Enter the updated date the vaccine was administered (YYYY-MM-DD):")
                if date_administered:
                    individual = Individual.get(name)
                    if individual:
                        registry.update_individual_vaccination(name, vaccine_name, date_administered)
                        messagebox.showinfo("Info", f"Vaccination record updated for {name}.")
                    else:
                        messagebox.showerror("Error", f"{name} is not in the registry.")

    def delete_vaccination_record(self):
        name = simpledialog.askstring("Input", "Enter the name of the individual:")
        if name:
            vaccine_name = simpledialog.askstring("Input", "Enter the name of the vaccine to delete:")
            if vaccine_name:
                individual = Individual.get(name)
                if individual:
                    registry.delete_individual_vaccination(name, vaccine_name)
                    messagebox.showinfo("Info", f"Vaccination record for {vaccine_name} deleted for {name}.")
                else:
                    messagebox.showerror("Error", f"{name} is not in the registry.")

    def delete_individual(self):
        name = simpledialog.askstring("Input", "Enter the name of the individual to delete:")
        if name:
            individual = Individual.get(name)
            if individual:
                registry.delete_individual(name)
                messagebox.showinfo("Info", f"{name} has been deleted from the registry.")
            else:
                messagebox.showerror("Error", f"{name} is not in the registry.")

    def get_vaccination_history(self):
        name = simpledialog.askstring("Input", "Enter the name of the individual:")
        if name:
            history = registry.get_individual_vaccination_history(name)
            if history:
                for record in self.tree.get_children():
                    self.tree.delete(record)

                for record in history:
                    self.tree.insert("", "end", values=record)
            else:
                messagebox.showerror("Error", f"{name} is not in the registry or has no vaccination records.")

if __name__ == "__main__":
    app = Application()
    app.mainloop()
