import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, \
    QLineEdit, QTableWidget, QTableWidgetItem, QComboBox, QCalendarWidget, QDateEdit, QTextEdit, QDateTimeEdit
import datetime
import time
import threading
import os
import platform
from plyer import notification
import chime

from db import DataBase


TASKS = dict()


def notify(message, title):
    if platform.system() == 'Darwin':
        os.system("osascript -e 'display notification \"{}\" with title \"{}\"'".format(message, title))
    else:
        notification.notify(
            title=title,
            message=message,
            app_icon='python.ico')


def check_tasks_to_do():
    global TASKS
    while True:
        need_update_task = []
        time.sleep(3)
        for task_id, task in TASKS.items():
            task_data = datetime.datetime.strptime(
                task['do_before_time'],
                '%d.%m.%Y %H:%M'
            )
            now = datetime.datetime.now()
            if not task['is_ready'] and now > task_data:
                chime.info()
                notify('Время выполнения задачи пришло)', f'Пора выполнить задачу {task["name"]}')
                need_update_task.append(task_id)
        for task in need_update_task:
            db.update_complete_task(task)
            TASKS[task]['is_ready'] = True
        if need_update_task:
            scheduler.load_tasks()


class TaskScheduler(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Планировщик задач")
        self.setGeometry(200, 100, 1000, 600)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            'ID',
            'Задача',
            'Коментарии',
            'Создано',
            'Выполнить до',
            'Уровень важности',
            'Время настало?'
        ])
        self.table.setColumnHidden(0, True)
        self.task_input = QLineEdit()
        self.description_input = QLineEdit()

        self.add_button = QPushButton("Добавить задачу")
        self.add_button.clicked.connect(self.add_task)

        self.delete_button = QPushButton("Удалить задачу")
        self.delete_button.clicked.connect(self.delete_task)

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.table)

        form_layout = QHBoxLayout()
        form_layout.addWidget(QLabel("Задача:"))
        form_layout.addWidget(self.task_input)
        form_layout.addWidget(QLabel("Описание:"))
        form_layout.addWidget(self.description_input)
        form_layout.addWidget(QLabel("Важность:"))
        self.combo = QComboBox(self)
        self.combo.addItems(["Низкая", "Средняя",
                             "Высокая"])

        form_layout.addWidget(self.combo)
        now = datetime.datetime.now() + datetime.timedelta(minutes=1)
        self.dateedit = QDateTimeEdit(now)
        self.dateedit.setDisplayFormat("dd.MM.yyyy HH:mm")
        self.dateedit.setCalendarPopup(False)

        form_layout.addWidget(QLabel('До:'))
        form_layout.addWidget(self.dateedit)

        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.add_button)
        main_layout.addWidget(self.delete_button)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.load_tasks()

    def load_tasks(self):
        global TASKS
        self.table.setRowCount(0)
        tasks = db.get_all_tasks()

        for task in tasks:
            TASKS[task[0]] = {
                'name': task[1],
                'description': task[2],
                'do_before_time': task[5],
                'is_ready': bool(task[6])
            }
            task_status = str(task[6]).replace('1', '✅').replace('0', '')
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(task[0])))
            self.table.setItem(row, 1, QTableWidgetItem(task[1]))
            self.table.setItem(row, 2, QTableWidgetItem(task[2]))
            self.table.setItem(row, 3, QTableWidgetItem(task[3]))
            self.table.setItem(row, 4, QTableWidgetItem(task[5]))
            self.table.setItem(row, 5, QTableWidgetItem(task[4]))
            self.table.setItem(row, 6, QTableWidgetItem(task_status))

        self.table.resizeColumnsToContents()

    def add_task(self):
        task = self.task_input.text()
        description = self.description_input.text()
        level = self.combo.currentText()
        due_date = self.dateedit.dateTime().toString('dd.MM.yyyy HH:mm')
        db.create_task(task, description, level, due_date)
        self.task_input.clear()
        self.description_input.clear()
        self.combo.clearFocus()

        self.load_tasks()

    def delete_task(self):
        rows = sorted(set(index.row() for index in self.table.selectedIndexes()), reverse=True)

        for row in rows:
            task_id = self.table.item(row, 0).text()
            db.delete_task(task_id)
        self.load_tasks()

    def closeEvent(self, event):
        db.close_conn()
        chime.success()
        event.accept()


if __name__ == "__main__":
    db = DataBase()
    thread = threading.Thread(target=check_tasks_to_do, daemon=True)
    thread.start()
    app = QApplication(sys.argv)
    scheduler = TaskScheduler()
    scheduler.show()
    sys.exit(app.exec_())
