import sys
import os
import json

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QListWidget, QPushButton,
    QLabel, QLineEdit, QTextEdit, QFileDialog, QMessageBox,
    QVBoxLayout, QHBoxLayout, QFormLayout, QSplitter, QFrame
)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "recipes.json")


class RecipeBook(QMainWindow):
    def __init__(self):
        super().__init__()
        self.recipes = {}
        self.current_recipe = None
        self.photo_path = ""

        self.setWindowTitle("Кулинарная книга")
        self.resize(1100, 700)

        self.load_data()
        self.init_ui()
        self.refresh_list()

    def init_ui(self):
        root = QWidget()
        self.setCentralWidget(root)

        self.list_widget = QListWidget()
        self.list_widget.currentTextChanged.connect(self.load_recipe_from_list)
        self.list_widget.setMinimumWidth(360)

        title = QLabel("Кулинарная книга")
        title.setObjectName("MainTitle")

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Название рецепта")

        self.ingredients_edit = QTextEdit()
        self.ingredients_edit.setPlaceholderText("Ингредиенты по строкам")

        self.steps_edit = QTextEdit()
        self.steps_edit.setPlaceholderText("Шаги приготовления")

        self.photo_label = QLabel("Фото блюда")
        self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo_label.setFixedSize(330, 230)
        self.photo_label.setStyleSheet("""
            QLabel {
                border: 2px solid #9d7cff;
                border-radius: 16px;
                background: rgba(255, 255, 255, 0.92);
                color: #6d55a7;
                font-size: 15px;
                font-weight: 600;
            }
        """)

        self.choose_photo_button = QPushButton("Выбрать фото")
        self.choose_photo_button.clicked.connect(self.choose_photo)

        self.new_button = QPushButton("Новый")
        self.new_button.clicked.connect(self.new_recipe)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_recipe)

        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_recipe)

        left_panel = QFrame()
        left_panel.setObjectName("leftPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(QLabel("Рецепты"))
        left_layout.addWidget(self.list_widget)

        left_buttons = QHBoxLayout()
        left_buttons.addWidget(self.new_button)
        left_buttons.addWidget(self.delete_button)
        left_layout.addLayout(left_buttons)

        right_panel = QFrame()
        right_panel.setObjectName("rightPanel")
        right_layout = QVBoxLayout(right_panel)

        right_layout.addWidget(title)

        form = QFormLayout()
        form.addRow("Название:", self.name_edit)
        form.addRow("Ингредиенты:", self.ingredients_edit)
        form.addRow("Приготовление:", self.steps_edit)
        right_layout.addLayout(form)
        right_layout.addWidget(self.photo_label)
        right_layout.addWidget(self.choose_photo_button)
        right_layout.addWidget(self.save_button)

        splitter = QSplitter()
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([380, 720])

        layout = QHBoxLayout(root)
        layout.addWidget(splitter)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #ece7fb;
            }

            QFrame#leftPanel {
                background-color: rgba(255, 255, 255, 0.92);
                border: 1px solid #c9bdf5;
                border-radius: 18px;
            }

            QFrame#rightPanel {
                background-color: rgba(255, 255, 255, 0.88);
                border: 1px solid #c9bdf5;
                border-radius: 18px;
            }

            QLabel {
                color: #4f397a;
                font-size: 14px;
                font-weight: 600;
            }

            QLabel#MainTitle {
                font-size: 22px;
                font-weight: 700;
                color: #5f3fd1;
                padding: 4px 0px 10px 0px;
            }

            QListWidget {
                background-color: white;
                border: 1px solid #d3c6fa;
                border-radius: 14px;
                padding: 6px;
                font-size: 14px;
            }

            QLineEdit, QTextEdit {
                background-color: white;
                border: 1px solid #d3c6fa;
                border-radius: 12px;
                padding: 8px;
                font-size: 14px;
                color: #2e2147;
            }

            QPushButton {
                background-color: #8f6df2;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 10px 14px;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #7e5ee9;
            }

            QPushButton:pressed {
                background-color: #6e4fd9;
            }
        """)

    def refresh_list(self):
        self.list_widget.clear()
        self.list_widget.addItems(sorted(self.recipes.keys()))

    def new_recipe(self):
        self.current_recipe = None
        self.name_edit.clear()
        self.ingredients_edit.clear()
        self.steps_edit.clear()
        self.photo_path = ""
        self.photo_label.setPixmap(QPixmap())
        self.photo_label.setText("Фото блюда")

    def load_recipe_from_list(self, name):
        if not name or name not in self.recipes:
            return

        self.current_recipe = name
        data = self.recipes[name]

        self.name_edit.setText(name)
        self.ingredients_edit.setPlainText(data.get("ingredients", ""))
        self.steps_edit.setPlainText(data.get("steps", ""))
        self.photo_path = data.get("photo", "")
        self.update_photo_preview()

    def choose_photo(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите фото",
            BASE_DIR,
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_name:
            self.photo_path = file_name
            self.update_photo_preview()

    def update_photo_preview(self):
        if self.photo_path and os.path.exists(self.photo_path):
            pixmap = QPixmap(self.photo_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    self.photo_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.photo_label.setPixmap(scaled)
                self.photo_label.setText("")
                return

        self.photo_label.setPixmap(QPixmap())
        self.photo_label.setText("Фото блюда")

    def save_recipe(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название рецепта")
            return

        old_name = self.current_recipe
        self.recipes[name] = {
            "ingredients": self.ingredients_edit.toPlainText().strip(),
            "steps": self.steps_edit.toPlainText().strip(),
            "photo": self.photo_path
        }

        if old_name and old_name != name and old_name in self.recipes:
            del self.recipes[old_name]

        self.current_recipe = name
        self.save_data()
        self.refresh_list()
        self.list_widget.setCurrentText(name)

    def delete_recipe(self):
        item = self.list_widget.currentItem()
        if not item:
            return

        name = item.text()
        reply = QMessageBox.question(self, "Удаление", f"Удалить рецепт '{name}'?")
        if reply == QMessageBox.StandardButton.Yes and name in self.recipes:
            del self.recipes[name]
            self.save_data()
            self.new_recipe()
            self.refresh_list()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.recipes = json.load(f)

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.recipes, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = RecipeBook()
    window.show()
    sys.exit(app.exec())