import tkinter as tk
from tkinter import ttk, Menu, simpledialog, messagebox
import threading
import time
from ttkthemes import ThemedTk

from nodes import Node, NodeManager
from helper import *

class MainGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("XMRIG Node Monitor by n0ctu")
        self.root.geometry("1024x600")
        self.refresh_interval = 5

        # Initialize Node Manager with default config file
        self.filename = "config.json"
        self.node_manager = NodeManager(self.filename)
        self.nodes = self.node_manager.nodes

        # Menu
        self.create_menu()

        # Frame for to contain the scrollable content
        self.frame = ttk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Canvas for the scrollable content
        self.canvas = tk.Canvas(self.frame)
        self.scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.table_grid = ttk.Frame(self.canvas)

        self.table_grid.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.table_grid, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Initialize the table
        self.init_table()

        # Start background thread to update nodes
        self.updater_thread = threading.Thread(target=self.table_interval, daemon=True)
        self.updater_thread.start()

    # UI helpers

    def create_menu(self):
        self.menu = Menu(self.root)
        self.file_menu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Select config file", command=self.select_config_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)

        self.settings_menu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Settings", menu=self.settings_menu)
        self.settings_menu.add_command(label="Add Node", command=self.add_node)
        self.settings_menu.add_separator()
        self.settings_menu.add_command(label="Refresh all", command=self.init_table)
        self.settings_menu.add_command(label="Set refresh interval", command=self.set_refresh_interval)

        self.menu.add_command(label="?", command=self.show_help)
        self.root.config(menu=self.menu)

    def show_help(self):
        messagebox.showinfo("Help", "This is a simple XMRIG Monitoring GUI.\n\n"
                                    "Add nodes to the list to monitor their hashrate and status.\n"
                                    "Nodes are updated every few seconds.\n\n"
                                    "You can add, edit, and remove nodes from the list, and change the refresh interval.\n"
                                    "The nodes are saved to a config file in the same directory as the program was launched in.\n\n"
                                    "Author: n0ctu\nGitHub: https://github.com/n0ctu")

    def resize_root(self):
        # Resize the root window to fit the table
        width = max(self.table_grid.winfo_reqwidth() + self.scrollbar.winfo_width(), self.root.winfo_width())
        height = root.winfo_height()
        self.root.geometry(f"{width}x{height}")

    # Table functions

    def add_table_titles(self):
        # Add title row to the table
        titles = ["Status", "Host", "Hardware", "Hashrate", "Algorithm", "Results", "Options", ""]
        for col_index, title in enumerate(titles):
            title_label = ttk.Label(self.table_grid, text=title, font=('Helvetica', 10, 'bold'), anchor='w')
            title_label.grid(row=0, column=col_index, padx=10, pady=5, sticky='w')

    # Table rows: Each node, updated every refresh_interval seconds

    def table_interval(self):
        while True:
            self.table_update()
            self.resize_root()
            time.sleep(self.refresh_interval)

    def init_table(self):
        # Clear the table grid
        for widget in self.table_grid.winfo_children():
            widget.destroy()
        
        # Add the title row
        self.add_table_titles()

        # Add a row for each node in the list
        for index, node in enumerate(self.nodes):
            
            # Create a new status label, col 0
            status_label = ttk.Label(self.table_grid, text="Online" if node.online else "Offline", font=('Helvetica', 10), anchor='center', width="7", background="green" if node.online else "red", foreground="white") 
            status_label.grid(row=index + 1, column=0, padx=10, pady=5, sticky='nw')

            # Create a new name label, col 1
            name_frame = ttk.Frame(self.table_grid)
            name_label = ttk.Label(name_frame, text=node.name, font=('Helvetica', 10, 'bold'), anchor='w')
            name_label.pack(side="top", fill="x")
            name_label._identifier = "name_label"
            host_label = ttk.Label(name_frame, text=f"{node.host} : {node.port}", font=('Helvetica', 10), anchor='w')
            host_label.pack(side="top", fill="x")
            name_frame.grid(row=index + 1, column=1, padx=10, pady=5, sticky='nw')
            host_label._identifier = "host_label"

            # Create a new hardware label, col 2
            hardware_frame = ttk.Frame(self.table_grid)
            cpu_label = ttk.Label(hardware_frame, text=f"{shorten_string(node.cpu_name, 25)}\nCores: {node.cores} / Threads: {node.threads}", font=('Helvetica', 10), anchor='w')
            cpu_label.pack(side="top", fill="x")
            cpu_label._identifier = "cpu_label"
            memory_label = ttk.Label(hardware_frame, text=f"Memory Free: {(node.memory_free/1024/1024/1024):.2f} / {(node.memory_total/1024/1024/1024):.2f} GB", font=('Helvetica', 10), anchor='w')
            memory_label.pack(side="top", fill="x")
            memory_label._identifier = "memory_label"
            hardware_frame.grid(row=index + 1, column=2, padx=10, pady=5, sticky='nw')

            # Create a new hashrate label, col 3
            hashrate_frame = ttk.Frame(self.table_grid)
            hashrate_10s_label = ttk.Label(hashrate_frame, text=f"{node.hashrate_10s} (10s)", font=('Helvetica', 10, 'bold'), anchor='w')
            hashrate_10s_label.pack(side="top", fill="x")
            hashrate_10s_label._identifier = "hashrate_10s_label"
            hashrate_1m_label = ttk.Label(hashrate_frame, text=f"{node.hashrate_1m} (1m)", font=('Helvetica', 10), anchor='w')
            hashrate_1m_label.pack(side="top", fill="x")
            hashrate_1m_label._identifier = "hashrate_1m_label"
            hashrate_15m_label = ttk.Label(hashrate_frame, text=f"{node.hashrate_15m} (15m)", font=('Helvetica', 10), anchor='w')
            hashrate_15m_label.pack(side="top", fill="x")
            hashrate_15m_label._identifier = "hashrate_15m_label"
            hashrate_frame.grid(row=index + 1, column=3, padx=10, pady=5, sticky='nw')

            # Create a new algo label, col 4
            algo_frame = ttk.Frame(self.table_grid)
            algo_label = ttk.Label(algo_frame, text=node.algo, font=('Helvetica', 10), anchor='w')
            algo_label.pack(side="top", fill="x")
            algo_label._identifier = "algo_label"
            xmrig_version_label = ttk.Label(algo_frame, text=shorten_string(node.ua, 15), font=('Helvetica', 10), anchor='w')
            xmrig_version_label.pack(side="top", fill="x")
            xmrig_version_label._identifier = "xmrig_version_label"
            algo_frame.grid(row=index + 1, column=4, padx=10, pady=5, sticky='nw')

            # Create a new results label, col 5
            results_frame = ttk.Frame(self.table_grid)
            shares_label = ttk.Label(results_frame, text=f"Blocks or Shares: {node.shares_good}/{node.shares_total}", font=('Helvetica', 10), anchor='w')
            shares_label.pack(side="top", fill="x")
            shares_label._identifier = "shares_label"
            avg_time_label = ttk.Label(results_frame, text=f"Avg Time: {seconds_to_string(node.avg_time)}", font=('Helvetica', 10), anchor='w')
            avg_time_label.pack(side="top", fill="x")
            avg_time_label._identifier = "avg_time_label"
            results_frame.grid(row=index + 1, column=5, padx=10, pady=5, sticky='nw')

            # Create Option Buttons, col 6 - 7
            edit_button = ttk.Button(self.table_grid, text="Edit", width="4", command=lambda idx=index: self.edit_node(idx))
            edit_button.grid(row=index + 1, column=6, padx=10, pady=5, sticky='nw')
            delete_button = ttk.Button(self.table_grid, text="Delete", width="6", command=lambda idx=index: self.remove_node(idx))
            delete_button.grid(row=index + 1, column=7, padx=10, pady=5, sticky='nw')

    def table_update(self):
        for index, node in enumerate(self.nodes):
            self.node_manager.refresh_node(index)
            self.table_update_status(index, node, 0)
            self.table_update_name(index, node, 1)
            self.table_update_hardware(index, node, 2)
            self.table_update_hashrate(index, node, 3)
            self.table_update_algo(index, node, 4)
            self.table_update_results(index, node, 5)

    # Update Table cols individually: Status, Hashrate, Algorithm

    def table_update_status(self, index, node, col=0):
        for field in self.table_grid.winfo_children():
            if field.grid_info()["row"] == index + 1 and field.grid_info()["column"] == col:
                # Update the status label
                field.config(text="Online" if node.online else "Offline", background="green" if node.online else "red")
                return

    def table_update_name(self, index, node, col=1):
        for field in self.table_grid.winfo_children():
            if field.grid_info()["row"] == index + 1 and field.grid_info()["column"] == col:
                for child in field.winfo_children():
                    if child._identifier == "name_label":
                        child.config(text=node.name)
                    elif child._identifier == "host_label":
                        child.config(text=f"{node.host} : {node.port}")
                break
        
    def table_update_hardware(self, index, node, col=2):
        for field in self.table_grid.winfo_children():
            if field.grid_info()["row"] == index + 1 and field.grid_info()["column"] == col:
                for child in field.winfo_children():
                    if child._identifier == "cpu_label":
                        child.config(text=f"{shorten_string(node.cpu_name, 25)}\nCores: {node.cores} / Threads: {node.threads}")
                    elif child._identifier == "memory_label":
                        child.config(text=f"Memory Free: {(node.memory_free/1024/1024/1024):.2f} / {(node.memory_total/1024/1024/1024):.2f} GB")
                break

    def table_update_hashrate(self, index, node, col=3):
        for field in self.table_grid.winfo_children():
            if field.grid_info()["row"] == index + 1 and field.grid_info()["column"] == col:
                for child in field.winfo_children():
                    if child._identifier == "hashrate_10s_label":
                        child.config(text=f"{node.hashrate_10s} (10s)")
                    elif child._identifier == "hashrate_1m_label":
                        child.config(text=f"{node.hashrate_1m} (1m)")
                    elif child._identifier == "hashrate_15m_label":
                        child.config(text=f"{node.hashrate_15m} (15m)")
                break

    def table_update_algo(self, index, node, col=4):
        for field in self.table_grid.winfo_children():
            if field.grid_info()["row"] == index + 1 and field.grid_info()["column"] == col:
                for child in field.winfo_children():
                    if child._identifier == "algo_label":
                        child.config(text=node.algo)
                    elif child._identifier == "xmrig_version_label":
                        child.config(text=shorten_string(node.ua, 15))
                break
    
    def table_update_results(self, index, node, col=5):
        for field in self.table_grid.winfo_children():
            if field.grid_info()["row"] == index + 1 and field.grid_info()["column"] == col:
                for child in field.winfo_children():
                    if child._identifier == "shares_label":
                        child.config(text=f"Blocks or Shares: {node.shares_good}/{node.shares_total}")
                        if node.shares_good > 0:
                            child.config(foreground="green", font=('Helvetica', 10, 'bold'))
                    elif child._identifier == "avg_time_label":
                        child.config(text=f"Avg Time: {seconds_to_string(node.avg_time)}")
                break

    # Node Management

    def add_node(self):
        # Add a new node to the list
        new_node = Node(id=len(self.nodes) + 1, host="127.0.0.1", port=8080)
        self.nodes.append(new_node)
        self.init_table()
        self.node_manager.save_nodes()
    
    def edit_node(self, index):
        # Edit the node at the given index
        if 0 <= index < len(self.nodes):
            node = self.nodes[index]
            new_host = simpledialog.askstring("Edit Node", "Enter the new host address:", initialvalue=node.host)
            new_port = simpledialog.askinteger("Edit Node", "Enter the new port number:", initialvalue=node.port)
            if new_host and new_port:
                node.host = new_host
                node.port = new_port
                self.init_table()
                self.node_manager.save_nodes()
    
    def remove_node(self, index):
        # Remove the node at the given index
        if 0 <= index < len(self.nodes):
            confirm = messagebox.askyesno("Delete Node", f"Are you sure you want to delete node {index + 1}?")
            if confirm:
                del self.nodes[index]
                self.init_table()
                self.node_manager.save_nodes()
    
    def set_refresh_interval(self):
        # Set the refresh interval
        new_interval = simpledialog.askinteger("Set Refresh Interval", "Enter the new refresh interval in seconds:", initialvalue=self.refresh_interval)
        if new_interval and new_interval > 0:
            self.refresh_interval = new_interval
        return
    
    def select_config_file(self):
        # Select a new config file, todo
        return

if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    app = MainGUI(root)
    root.mainloop()