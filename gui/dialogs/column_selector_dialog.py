# ColumnSelectorDialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QPushButton

class ColumnSelectorDialog(QDialog):
    def __init__(self, parent, column_names, visible_columns):
        super().__init__(parent)
        self.setWindowTitle("Select Columns")
        self.setGeometry(100, 100, 300, 400)
        
        self.layout = QVBoxLayout()
        self.checkboxes = {}

        for col in column_names:
            checkbox = QCheckBox(col)
            checkbox.setChecked(visible_columns[col])
            self.checkboxes[col] = checkbox
            self.layout.addWidget(checkbox)

        self.ok_button = QPushButton("Apply")
        self.ok_button.clicked.connect(self.apply_changes)
        self.layout.addWidget(self.ok_button)

        self.setLayout(self.layout)
    
    def apply_changes(self):
        self.selected_columns = {col: cb.isChecked() for col, cb in self.checkboxes.items()}
        self.accept()