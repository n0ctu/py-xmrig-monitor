import json
import requests
import os
import time

class Node:
    def __init__(self, id, host, port):
        self.id = id
        self.host = host
        self.port = port
        self.name = "N/A"
        self.online = False
        self.success_count = 0
        self.ua = "N/A"
        self.uptime = 0
        self.algo = "N/A"
        self.pool = "N/A"
        self.ping = 0
        self.failures = 0
        self.difficulty = 0
        self.hashrate = []
        self.hashrate_10s = 0
        self.hashrate_1m = 0
        self.hashrate_15m = 0
        self.highest_hashrate = 0
        self.cpu_name = "N/A"
        self.cores = 0
        self.threads = 0
        self.memory_free = 0
        self.memory_total = 0
        self.shares_good = 0
        self.shares_total = 0
        self.avg_time = 0
        self.last_update = 0

    def update_node(self):
        try:
            url = f"http://{self.host}:{self.port}/2/summary"
            response = requests.get(url)
            if response.status_code == 200:
                res = response.json()

                self.name = res.get("worker_id", "No Title")
                self.online = True
                self.success_count += 1
                self.ua = res.get("ua", "Unknown")
                self.uptime = res.get("uptime", 0)
                self.algo = res.get("algo", "Unknown")
                self.pool = res.get("connection", {}).get("pool", "Unknown")
                self.ping = res.get("connection", {}).get("ping", 0)
                self.failures = res.get("connection", {}).get("failures", 0)
                self.difficulty = res.get("connection", {}).get("diff", 0)
                self.hashrate_10s = res.get("hashrate", {}).get("total", [])[0]
                self.hashrate_1m = res.get("hashrate", {}).get("total", [])[1]
                self.hashrate_15m = res.get("hashrate", {}).get("total", [])[2]
                self.highest_hashrate = res.get("hashrate", {}).get("highest", 0)
                self.cpu_name = res.get("cpu", {}).get("brand", "Unknown")
                self.cores = res.get("cpu", {}).get("cores", 0)
                self.threads = res.get("cpu", {}).get("threads", 0)
                self.memory_free = res.get("resources", {}).get("memory", {}).get("free", 0)
                self.memory_total = res.get("resources", {}).get("memory", {}).get("total", 0)
                self.shares_good = res.get("results", {}).get("shares_good", 0)
                self.shares_total = res.get("results", {}).get("shares_total", 0)
                self.avg_time = res.get("results", {}).get("avg_time", 0)
                self.last_update = time.time()
                print(f"{self.name} current hashrate: {self.hashrate_10s}, blocks or shares: {self.shares_good}/{self.shares_total}")
            else:
                self.online = False
        except requests.RequestException:
            self.online = False
            print(f"Failed to connect to {url}")

    def to_dict(self):
        return {
            "id": self.id,
            "host": self.host,
            "port": self.port,
            "name": self.name,
            "online": self.online,
            "success_count": self.success_count,
            "ua": self.ua,
            "uptime": self.uptime,
            "algo": self.algo,
            "pool": self.pool,
            "ping": self.ping,
            "failures": self.failures,
            "difficulty": self.difficulty,
            "hashrate_10s": self.hashrate_10s,
            "hashrate_1m": self.hashrate_1m,
            "hashrate_15m": self.hashrate_15m,
            "highest_hashrate": self.highest_hashrate,
            "cpu_name": self.cpu_name,
            "cores": self.cores,
            "threads": self.threads,
            "memory_free": self.memory_free,
            "memory_total": self.memory_total,
            "shares_good": self.shares_good,
            "shares_total": self.shares_total,
            "avg_time": self.avg_time
        }

class NodeManager:
    def __init__(self, filename):
        self.filename = filename
        self.nodes = self.load_nodes()
        if not self.nodes:
            print("Warning: No nodes were loaded. The node list is empty.")

    def load_nodes(self):
        if not os.path.exists(self.filename) or os.stat(self.filename).st_size == 0:
            print(f"File '{self.filename}' not found or is empty. Creating a new file.")
            self.nodes = []
            self.save_nodes()  # Create an empty nodes file if none exists
            return []
        
        try:
            with open(self.filename, "r") as file:
                nodes = json.load(file).get("nodes", [])
                if not nodes:
                    print("Warning: Loaded nodes list is empty.")
                input = []
                for node in nodes:
                    new_node = Node(id=node["id"], host=node["host"], port=node["port"])
                    input.append(new_node)
                return input
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading nodes: {e}")
            return []

    def save_nodes(self):
        out = []
        for node in self.nodes:
            result = { "id": node.id, "host": node.host, "port": node.port }
            out.append(result)
        
        try:
            with open(self.filename, "w") as file:
                json.dump({"nodes": out}, file, indent=4)
        except IOError as e:
            print(f"Error saving nodes to file '{self.filename}': {e}")

    def refresh_node(self, index):
        try:
            index = int(index)
            if 0 <= index < len(self.nodes):
                self.nodes[index].update_node()
            else:
                print(f"Error: Index {index} is out of bounds. Please provide a valid index between 0 and {len(self.nodes) - 1}.")
        except ValueError:
            print(f"Error: Provided index '{index}' is not a valid integer.")