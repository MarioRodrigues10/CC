import sqlite3
from datetime import datetime
from typing import Any

class Database:

    def create_connection(self, db_file: str) -> Any:
        """Create a database connection to a SQLite database."""
        conn = None
        try:
            conn = sqlite3.connect(db_file, check_same_thread=False)
            print(f"Connected to the database: {db_file}")
        except sqlite3.Error as e:
            print(f"Error connecting to the database: {e}")
        return conn

    def execute_sql(self, conn: Any, sql: Any, data: Any=None) -> None:
        """Execute a single SQL statement."""
        try:
            c = conn.cursor()
            if data:
                c.execute(sql, data)
            else:
                c.execute(sql)
            conn.commit()
            print(f"Executed SQL:\n{sql}")
        except sqlite3.Error as e:
            print(f"Error executing SQL:\n{sql}\nError: {e}")

    def create_table(self, conn: Any) -> None:
        """Create the command_output table if it doesn't exist."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS command_output (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT,
            command_type TEXT,
            interface_name TEXT,
            connectivity TEXT,
            tx_bytes INTEGER,
            tx_packets INTEGER,
            rx_bytes INTEGER,
            rx_packets INTEGER,
            target TEXT,
            jitter REAL,
            bandwidth REAL,
            loss REAL,
            targets TEXT,
            transport TEXT,
            time REAL,
            jitter_alert REAL,
            loss_alert REAL,
            bandwidth_alert REAL,
            alert_down INTEGER,
            avg_latency REAL,
            stdev_latency REAL,
            cpu REAL,
            memory REAL,
            timestamp TEXT
        );
        """
        self.execute_sql(conn, create_table_sql)

    def insert_data(self, conn: Any, command_data: Any) -> None:
        """Insert data into the command_output table."""
        sql = """INSERT INTO command_output (
                    task_id, command_type, interface_name, connectivity, tx_bytes, tx_packets, 
                    rx_bytes, rx_packets, target, jitter, bandwidth, loss, targets, 
                    transport, time, jitter_alert, loss_alert, bandwidth_alert, 
                    alert_down, avg_latency, stdev_latency, cpu, memory, timestamp)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

        data = (
            command_data.get("task_id", ""),
            command_data.get("command_type", "unknown"),
            command_data.get("interface_name", ""),
            command_data.get("connectivity", ""),
            command_data.get("tx_bytes", 0),
            command_data.get("tx_packets", 0),
            command_data.get("rx_bytes", 0),
            command_data.get("rx_packets", 0),
            command_data.get("jitter", 0.0),
            command_data.get("bandwidth", 0.0),
            command_data.get("loss", 0.0),
            ", ".join(command_data.get("targets", [])),
            command_data.get("transport", ""),
            command_data.get("time", 0.0),
            command_data.get("jitter_alert", 0.0),
            command_data.get("loss_alert", 0.0),
            command_data.get("bandwidth_alert", 0.0),
            command_data.get("alert_down", 0),
            command_data.get("avg_latency", 0.0),
            command_data.get("stdev_latency", 0.0),
            command_data.get("cpu", 0.0),
            command_data.get("memory", 0.0),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        self.execute_sql(conn, sql, data)
        print(f"Inserted data: {data}")
