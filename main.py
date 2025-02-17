import tkinter as tk
import sys
from tkinter import messagebox, filedialog, ttk, simpledialog
import subprocess
from tkinter.constants import DISABLED
from tkinter.font import NORMAL

from ttkthemes import ThemedTk
import threading


def check_root_password(password):
    try:
        result = subprocess.run(
            ["sudo", "-S", "echo", "root_access_granted"],
            input=password.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return "root_access_granted" in result.stdout.decode()
    except Exception as e:
        return False


def ask_for_password():
    while True:
        root = tk.Tk()
        root.withdraw()

        password = simpledialog.askstring("Root Access Required", "Enter root password:", show="*")

        if password is None:
            sys.exit()

        if check_root_password(password):
            root.destroy()
            return
        else:
            messagebox.showerror("Authentication Failed", "Incorrect password. Try again.")


def get_gnome_theme():
    try:
        output = subprocess.check_output([
            "gsettings", "get", "org.gnome.desktop.interface", "color-scheme"
        ], text=True).strip()
        return "dark" if "dark" in output else "light"
    except Exception:
        return "light"


def run_command():
    filename = e1.get()
    if not filename:
        messagebox.showerror("Error", "No file selected.")
        return

    def execute_install():
        try:
            progress_window = tk.Toplevel()
            progress_window.title("Installing Package")
            x = root.winfo_x()
            y = root.winfo_y()
            progress_window.geometry(f"+{x}+{y}")
            progress_bar = ttk.Progressbar(progress_window, orient="horizontal", length=300, mode="indeterminate")
            progress_bar.grid(row=0, column=0, padx=20, pady=20)
            progress_bar.start()
            process = subprocess.Popen(
                ["sudo", "dpkg", "-i", filename],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            for line in process.stdout:
                t2.config(state=tk.NORMAL)
                t2.insert(tk.END, line)
                t2.config(state=tk.DISABLED)
                t2.see(tk.END)

            for line in process.stderr:
                t2.config(state=tk.NORMAL)
                t2.insert(tk.END, line)
                t2.config(state=tk.DISABLED)
                t2.see(tk.END)

            process.stdout.close()
            process.stderr.close()
            process.wait()
            progress_bar.stop()
            progress_window.destroy()

            if process.returncode == 0:
                messagebox.showinfo("Success", "Package installed successfully.")
            else:
                messagebox.showerror("Error", "Package installation failed.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    threading.Thread(target=execute_install, daemon=True).start()


def open_file():
    filepath = filedialog.askopenfilename(filetypes=[("Debian Packages", "*.deb")])
    if filepath:
        e1.delete(0, tk.END)
        e1.insert(tk.END, filepath)


def get_package_info():
    deb_file = e1.get()
    try:
        result = subprocess.run(
            ["dpkg-deb", "-I", deb_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            messagebox.showerror("Error", f"Failed to read package info:\n{result.stderr}")
            return

        package_info = {}
        for line in result.stdout.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                package_info[key.strip()] = value.strip()

        formatted_info = (
            f"Package: {package_info.get('Package', 'N/A')}\n"
            f"Version: {package_info.get('Version', 'N/A')}\n"
            f"Architecture: {package_info.get('Architecture', 'N/A')}\n"
            f"Maintainer: {package_info.get('Maintainer', 'N/A')}\n"
            f"Description:\n{package_info.get('Description', 'N/A')}"
        )

        t3.config(state=tk.NORMAL)
        t3.delete("1.0", tk.END)
        t3.insert(tk.END, formatted_info)
        t3.config(state=tk.DISABLED)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


def search_packages():
    rl1.config(state=tk.NORMAL)
    search_query = e3.get()

    if search_query.strip() == "":
        rl1.delete(0, tk.END)
        return

    try:
        result = subprocess.run(
            ["apt-cache", "search", search_query],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )


        rl1.delete(0, tk.END)
        packages = result.stdout.splitlines()
        matched_packages = [pkg.split()[0] for pkg in packages if search_query.lower() in pkg.lower()]
        if not matched_packages:
            rl1.insert(tk.END, "No package found matching the keyword")
            rl1.config(state=DISABLED)
        else:
            for package in matched_packages:
                if package.lower().startswith(search_query.lower()):
                    rl1.insert(tk.END, package)
    except Exception:
        rl1.delete(0, tk.END)
        rl1.insert(tk.END, "Error: Unable to search packages")



def search_installed_packages():
    rl2.config(state=NORMAL)
    search_query = e4.get()

    if search_query.strip() == "":
        rl2.delete(0, tk.END)
        return

    try:
        result = subprocess.run(
            ["dpkg", "--get-selections"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        packages = result.stdout.splitlines()
        matched_packages = [pkg.split()[0] for pkg in packages if search_query.lower() in pkg.lower()]

        rl2.delete(0, tk.END)
        if not matched_packages:
            rl2.insert(tk.END, "No package found matching the keyword")
            rl2.config(state=DISABLED)
        else:
            for package in matched_packages:
                if package.lower().startswith(search_query.lower()):
                    rl2.insert(tk.END, package)
    except Exception as e:
        rl2.delete(0, tk.END)
        rl2.insert(tk.END, "Error: Unable to search installed packages")


def install_selected_package():
    selected_package = rl1.get(tk.ACTIVE)
    if selected_package:
        package_name = selected_package.split(" ")[0]

        def execute_install():
            progress_window = tk.Toplevel()
            progress_window.title("Installing Package")
            x = root.winfo_x()
            y = root.winfo_y()
            progress_window.geometry(f"+{x}+{y}")
            progress_bar = ttk.Progressbar(progress_window, orient="horizontal", length=300, mode="indeterminate")
            progress_bar.grid(row=0, column=0, padx=20, pady=20)
            progress_bar.start()
            process = subprocess.Popen(
                ["sudo", "DEBIAN_FRONTEND=noninteractive", "apt-get", "install", package_name, "-y"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            output, error = process.communicate()
            progress_bar.stop()
            progress_window.destroy()
            t2.config(state=tk.NORMAL)
            t2.insert(tk.END, output + "\n" + error + "\n")
            t2.config(state=tk.DISABLED)

            if process.returncode == 0:
                t2.after(0, messagebox.showinfo, "Success", f"Package '{package_name}' installed successfully.")
            else:
                t2.after(0, messagebox.showerror, "Error", f"Failed to install '{package_name}'.\n{error}")
            search_packages()
        threading.Thread(target=execute_install, daemon=True).start()


def uninstall_selected_package():
    global op
    selected_package = rl2.get(tk.ACTIVE)
    if selected_package:
        package_name = selected_package.split(" ")[0]

        def execute_uninstall():
            progress_window = tk.Toplevel()
            progress_window.title("Uninstalling Package")
            x = root.winfo_x()
            y = root.winfo_y()
            progress_window.geometry(f"+{x}+{y}")
            progress_bar = ttk.Progressbar(progress_window, orient="horizontal", length=300, mode="indeterminate")
            progress_bar.grid(row=0, column=0, padx=20, pady=20)
            progress_bar.start()
            process = subprocess.Popen(
                ["sudo", "apt-get", "remove" if choice == 1 else "purge", package_name, "-y"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            output, error = process.communicate()
            progress_bar.stop()
            progress_window.destroy()
            t2.config(state=tk.NORMAL)
            t2.insert(tk.END, output + "\n" + error + "\n")
            t2.config(state=tk.DISABLED)
            t2.see(tk.END)

            if process.returncode == 0:
                messagebox.showinfo("Success", f"Package '{package_name}' removed successfully.")
            else:
                messagebox.showerror("Error", f"Failed to remove '{package_name}'.\n{error}")

            search_installed_packages()

        threading.Thread(target=execute_uninstall, daemon=True).start()





ask_for_password()
theme = get_gnome_theme()
root = ThemedTk(theme="arc" if theme == "light" else "equilux")
root.title("GDeb Installer")
root.geometry("400x350")
notebook = ttk.Notebook(root)
root.resizable(False, False)

tab1 = tk.Frame(notebook)
notebook.add(tab1, text="Deb Install")
tab2 = tk.Frame(notebook)
notebook.add(tab2, text="APT Install")
tab3 = tk.Frame(notebook)
notebook.add(tab3, text="APT Uninstall")
tab4 = tk.Frame(notebook)
notebook.add(tab4, text="Output")
b1 = tk.Button(tab1, text="Open file", command=open_file)
e1 = tk.Entry(tab1, width=40)
t2 = tk.Text(tab4, width=40, height=8)
t2.config(state=tk.DISABLED)
c1 = tk.Label(tab4, text="\nOutput")
l1 = tk.Button(tab1, text="Install", command=run_command)
l3 = tk.Label(tab1, text="File path: ")
notebook.pack(padx=10, pady=10, fill='both', expand=True)
b4 = tk.Button(tab1, text="Package Info", command=get_package_info)
t3 = tk.Text(tab1, width=50, height=8)
t3.config(state=tk.DISABLED)
b1.pack()
l3.pack()
e1.pack()
l1.pack()
c1.pack()
t2.pack()
b4.pack()
t3.pack()


l2 = tk.Label(tab2, text="Search from installable packages: ")
scrollbar = tk.Scrollbar(tab2, orient=tk.VERTICAL)
rl1 = tk.Listbox(tab2, selectmode=tk.SINGLE, height=5, width=50)
rl1.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=rl1.yview)
e3 = tk.Entry(tab2)
b2 = tk.Button(tab2, text="Search", command=search_packages)
b3 = tk.Button(tab2, text="Install", command=install_selected_package)
l2.pack()
e3.pack()
b2.pack()
b3.pack()
scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
rl1.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

l4 = tk.Label(tab3, text="Search from installed packages: ")
scrollbar2 = tk.Scrollbar(tab3, orient=tk.VERTICAL)
rl2 = tk.Listbox(tab3, selectmode=tk.SINGLE, height=3, width=50)
rl2.config(yscrollcommand=scrollbar2.set)
scrollbar2.config(command=rl2.yview)
choice = tk.IntVar(value=1)
rb1 = tk.Radiobutton(tab3, text="Remove", variable=choice, value=1)
rb2 = tk.Radiobutton(tab3, text="Purge", variable=choice, value=2)
e4 = tk.Entry(tab3)
b5 = tk.Button(tab3, text="Search", command=search_installed_packages)
b6 = tk.Button(tab3, text="Uninstall", command=uninstall_selected_package)
l4.pack()
e4.pack()
b5.pack()
rb1.pack()
rb2.pack()
b6.pack()
scrollbar2.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
rl2.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
root.mainloop()
