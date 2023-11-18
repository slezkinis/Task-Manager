import sqlite3
import datetime


class DataBase:
    def __init__(self) -> None:
        self.conn = sqlite3.connect("tasks.db", check_same_thread=False)
        self.cursor = self.conn.cursor()

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT,
            description TEXT,
            created_at TEXT,
            level TEXT,
            make_to_data TEXT,
            completed BOOL)''')

        self.conn.commit()

    def close_conn(self):
        self.conn.close()

    def get_all_tasks(self) -> list:
        self.cursor.execute("SELECT * FROM tasks")
        return self.cursor.fetchall()

    def create_task(self, task, description, level, make_to_data):
        created_at = datetime.datetime.now().strftime('%d.%m.%Y')
        self.cursor.execute("INSERT INTO tasks (task, description, created_at, level, make_to_data, completed) VALUES (?, ?, ?, ?, ?, ?)",
                            (task, description, created_at, level, make_to_data, False))
        self.conn.commit()

    def delete_task(self, task_id):
        self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()

    def update_complete_task(self, task_id):
        self.cursor.execute("UPDATE tasks SET completed=True WHERE id = ?", (task_id,))
        self.conn.commit()