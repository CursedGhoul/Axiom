import sys
import os
import shutil
import json
from PySide6.QtCore import Qt, QDir
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTreeView, QFileSystemModel, QHBoxLayout, QLabel, QMessageBox

# Define the path to the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PIN_FILE_PATH = os.path.join(SCRIPT_DIR, "pin.json")

class FileManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Axiom")
        self.setGeometry(300, 100, 800, 600)

        # Set up the layout
        self.layout = QVBoxLayout()

        # Horizontal layout for breadcrumb navigation
        self.breadcrumb_layout = QHBoxLayout()
        self.layout.addLayout(self.breadcrumb_layout)

        # Set up the file system model
        self.file_system_model = QFileSystemModel()
        self.file_system_model.setRootPath('')

        # Set the filter to show only directories (no files in the home page)
        self.file_system_model.setFilter(QDir.Dirs | QDir.NoDotAndDotDot)  # Show directories only (excluding '.' and '..')

        # Set up the tree view for the file system
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_system_model)
        self.tree_view.setRootIndex(self.file_system_model.index(os.path.expanduser("~")))  # Set default directory to home    
        self.tree_view.setColumnWidth(0, 250)
        self.layout.addWidget(self.tree_view)

        # Buttons for file operations
        self.buttons_layout = QHBoxLayout()

        self.open_button = QPushButton('Open')
        self.open_button.clicked.connect(self.open_file)
        self.buttons_layout.addWidget(self.open_button)

        self.delete_button = QPushButton('Delete')
        self.delete_button.clicked.connect(self.delete_item)
        self.buttons_layout.addWidget(self.delete_button)

        # Pin button
        self.pin_button = QPushButton('Pin Selected Item')
        self.pin_button.clicked.connect(self.pin_item)
        self.buttons_layout.addWidget(self.pin_button)

        self.layout.addLayout(self.buttons_layout)

        # Set the layout of the window
        self.setLayout(self.layout)

        # Store the navigation path as a list of directories
        self.path_history = [os.path.expanduser("~")]
        self.update_breadcrumb()

        # Connect tree view double click signal to update the path display
        self.tree_view.doubleClicked.connect(self.update_current_path_from_double_click)

        # Load pinned items
        self.pinned_items = self.load_pinned_items()

        # Initialize the pinned section layout
        self.pinned_layout = QVBoxLayout()
        self.update_pinned_section()  # Update pinned items display

    def update_breadcrumb(self):
        """Update the breadcrumb navigation at the top of the window."""
        for i in reversed(range(self.breadcrumb_layout.count())):
            widget = self.breadcrumb_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        for i, folder in enumerate(self.path_history):
            button = QPushButton(folder.split("/")[-1])
            button.setStyleSheet("padding: 0; margin: 0;")  
            button.clicked.connect(lambda checked, folder=folder: self.set_path(folder))
            self.breadcrumb_layout.addWidget(button)

            if i < len(self.path_history) - 1:
                separator = QLabel(" / ")
                separator.setStyleSheet("padding: 0; margin: 0;")  
                self.breadcrumb_layout.addWidget(separator)

    def set_path(self, path):
        full_path = os.path.abspath(path)
        if os.path.isdir(full_path):
            self.path_history = self.path_history[:self.path_history.index(self.path_history[-1]) + 1]
            self.path_history.append(full_path)
            self.update_breadcrumb()
            self.tree_view.setRootIndex(self.file_system_model.index(full_path))

    def update_current_path_from_double_click(self, index):
        selected_path = self.file_system_model.filePath(index)  
        if os.path.isdir(selected_path):
            self.path_history.append(selected_path)
            self.update_breadcrumb()
            self.tree_view.setRootIndex(self.file_system_model.index(selected_path))
        elif os.path.isfile(selected_path):
            self.open_file()

    def open_file(self):
        selected_index = self.tree_view.selectedIndexes()
        if selected_index:
            selected_path = selected_index[0].data()
            if os.path.isfile(selected_path):
                os.startfile(selected_path)  
            elif os.name == 'posix':  
                os.system(f'open "{selected_path}"' if sys.platform == "darwin" else f'xdg-open "{selected_path}"')

    def delete_item(self):
        selected_index = self.tree_view.selectedIndexes()
        if selected_index:
            selected_path = selected_index[0].data()
            if os.path.isfile(selected_path):
                confirm = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete the file '{selected_path}'? ",
                                               QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if confirm == QMessageBox.Yes:
                    os.remove(selected_path)
                    self.refresh_directory()
            elif os.path.isdir(selected_path):
                confirm = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete the folder '{selected_path}'? ",
                                               QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if confirm == QMessageBox.Yes:
                    shutil.rmtree(selected_path)
                    self.refresh_directory()

    def refresh_directory(self):
        current_path = self.path_history[-1]
        self.tree_view.setRootIndex(self.file_system_model.index(current_path))

    def pin_item(self):
        """Pin the selected file or folder, not the current location."""
        selected_index = self.tree_view.selectedIndexes()
        if selected_index:
            selected_path = selected_index[0].data()  # Get the selected item
            if os.path.isdir(selected_path) or os.path.isfile(selected_path):
                pinned_folder = os.path.basename(selected_path)  # Store only the item name
                if pinned_folder not in self.pinned_items:
                    self.pinned_items.append(pinned_folder)
                    self.save_pinned_items()
                    self.update_pinned_section()

    def load_pinned_items(self):
        if os.path.exists(PIN_FILE_PATH):
            try:
                with open(PIN_FILE_PATH, 'r') as file:
                    return json.load(file)
            except (json.JSONDecodeError, ValueError):
                return []
        else:
            return []

    def save_pinned_items(self):
        if not os.path.exists(SCRIPT_DIR):
            os.makedirs(SCRIPT_DIR, exist_ok=True)
        
        with open(PIN_FILE_PATH, 'w') as file:
            json.dump(self.pinned_items, file)

    def delete_pinned_item(self, pinned_folder):
        if pinned_folder in self.pinned_items:
            self.pinned_items.remove(pinned_folder)
            self.save_pinned_items()
            self.update_pinned_section()

    def update_pinned_section(self):
        """Update the pinned items section in the UI."""
        for i in reversed(range(self.pinned_layout.count())):
            widget = self.pinned_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.pinned_layout = QVBoxLayout()  # Recreate the layout for pinned items
        pinned_label = QLabel("Pinned Items:")
        self.pinned_layout.addWidget(pinned_label)

        for pinned_folder in self.pinned_items:
            full_path = os.path.join(os.path.expanduser("~"), pinned_folder)
            row_layout = QHBoxLayout()

            button = QPushButton(pinned_folder)
            button.clicked.connect(lambda checked, path=full_path: self.set_path(path))  
            row_layout.addWidget(button)

            trash_button = QPushButton("🗑️")
            trash_button.clicked.connect(lambda checked, folder=pinned_folder: self.delete_pinned_item(folder))
            row_layout.addWidget(trash_button)

            self.pinned_layout.addLayout(row_layout)

        self.layout.addLayout(self.pinned_layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FileManager()
    window.show()
    sys.exit(app.exec())
