import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QVBoxLayout, QComboBox, QFileDialog, 
    QDateTimeEdit, QMessageBox, QSplitter, QListWidget 
)
from PyQt5.QtCore import Qt, pyqtSignal, QDateTime
from .drag_drop_handler import enable_drag_drop  # Import enable_drag_drop từ drag_drop_handler
from .dynamic_form_builder import load_properties, create_form, add_default_fields
from .valid_extensions import VALID_EXTENSIONS  # Import VALID_EXTENSIONS từ valid_extensions

class DataImportTab(QWidget):
    upload_started = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.widgets = {}
        self.form_loaded = False  
        self.file_history = [] 
        self.current_file_index = -1 
        self.init_ui()
        enable_drag_drop(self)
        
    def init_ui(self):
        """Khởi tạo giao diện chia đôi màn hình"""
        self.main_splitter = QSplitter(Qt.Vertical)

        """Phần trên: Form và controls"""
        self.form_container = QWidget()
        self.form_layout = QVBoxLayout(self.form_container)
        self.placeholder_label = QLabel("Kéo thả file vào đây để bắt đầu")
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.form_layout.addWidget(self.placeholder_label)

        """Phần dưới: Danh sách file"""
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self._on_file_selected)

        self.main_splitter.addWidget(self.form_container)
        self.main_splitter.addWidget(self.file_list)
        self.main_splitter.setSizes([400, 200])

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.main_splitter)
        self.setLayout(main_layout)

    def _update_file_list(self, file_path):
        """Cập nhật danh sách file vào QListWidget"""
        self.file_history.append(file_path)
        self.file_list.addItem(file_path)

    def _on_file_selected(self, item):
        """Xử lý khi chọn file từ danh sách"""
        file_path = item.text()
        self.current_file_index = self.file_list.row(item)
        self._update_file_info(file_path)  

    def load_form(self, file_path):
        """Tải form và cập nhật danh sách file"""
        try:
            if hasattr(self, 'placeholder_label') and self.placeholder_label:
                self.form_layout.removeWidget(self.placeholder_label)
                self.placeholder_label.deleteLater()
                self.placeholder_label = None

            config = load_properties("csv")
            form_grid, self.widgets = create_form(config)
            form_grid, self.widgets = add_default_fields(form_grid, self.widgets, len(config))
            
            self.form_layout.addLayout(form_grid)
            self._connect_events()
            self._map_widgets()
            
            self._update_file_info(file_path)
            self.form_loaded = True

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def handle_dropped_file(self, file_path):
        """Xử lý file được thả vào"""
        ext = Path(file_path).suffix.lower()
        if ext in VALID_EXTENSIONS:
            if not self.form_loaded:
                self.load_form(file_path)
            else:
                self._update_file_info(file_path)
            self._update_file_list(file_path)
        else:
            QMessageBox.warning(self, "Lỗi", "File không hợp lệ. Hãy kiểm tra lại định dạng file.")

    def open_file_dialog(self):
        """Xử lý mở file"""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "All Files (*.*)"
        )
        if file_name:
            ext = Path(file_name).suffix.lower()
            if ext in VALID_EXTENSIONS:
                self._update_file_info(file_name)
                self._update_file_list(file_name)
            else:
                QMessageBox.warning(self, "Lỗi", "File không hợp lệ. Hãy kiểm tra lại định dạng file.")

    def _update_file_type(self, file_path):
        """Cập nhật loại dữ liệu dựa trên đuôi file"""
        EXTENSION_MAPPING = {
            '.csv': 'Zone',
            '.txt': 'WellPath',
            '.las': 'WellLog',
            '.xlsx': 'Marker',
        }
        
        file_extension = Path(file_path).suffix.lower()
        
        file_type = EXTENSION_MAPPING.get(file_extension, None)
        
        if file_type:
            index = self.combo_type_data.findText(file_type, Qt.MatchFixedString)
            if index >= 0:
                self.combo_type_data.setCurrentIndex(index)

    def _update_file_info(self, file_path):
        """Cập nhật thông tin file"""
        if 'file_path' in self.widgets: 
            self.widgets['file_path'].setText(file_path)
        
        if 'record_id' in self.widgets:
            self.widgets['record_id'].setText(os.path.basename(file_path))
        
        if 'date_upload' in self.widgets:
            self.widgets['date_upload'].setDateTime(QDateTime.currentDateTime())

        self._update_file_type(file_path)

    def _map_widgets(self):
        """Ánh xạ các widget"""
        self.combo_type_data = self.widgets.get('schema_type', QComboBox())
        self.file_path_edit = self.widgets.get('file_path', QLineEdit())
        self.file_name_edit = self.widgets.get('record_id', QLineEdit())
        self.date_upload_edit = self.widgets.get('date_upload', QDateTimeEdit())
        
    def _connect_events(self):
        """Kết nối sự kiện"""
        if 'btn_open_file' in self.widgets:
            self.widgets['btn_open_file'].clicked.connect(self.open_file_dialog)
        if 'btn_upload' in self.widgets:
            self.widgets['btn_upload'].clicked.connect(self.confirm_import)
        if 'btn_cancel' in self.widgets:
            self.widgets['btn_cancel'].clicked.connect(self.cancel_import)

    def confirm_import(self):
        """Khi nhấn Upload, gửi tín hiệu upload_started."""
        file_path = self.file_path_edit.text()
        self.upload_started.emit(file_path)

        print(self.get_import_info())
    
    def get_import_info(self):
        """Trả về thông tin import dưới dạng dict."""
        return {
            "schema_type": self.combo_type_data.currentText(),
            "record_id": self.file_name_edit.text(),
            "file_path": self.file_path_edit.text(),
            "date_upload": self.date_upload_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
        }
    
    def cancel_import(self):
        """Reset các trường về trạng thái ban đầu."""
        self.reset_fields()
    
    def reset_fields(self):
        self.combo_type_data.setCurrentIndex(0)
        self.file_path_edit.clear()
        self.file_name_edit.clear()
        self.date_upload_edit.setDateTime(QDateTime.fromString("2000-01-01 00:00:00", "yyyy-MM-dd HH:mm:ss"))

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = DataImportTab()
    w.show()
    sys.exit(app.exec_())