import os
import yaml
from PyQt5.QtWidgets import (
    QGridLayout, QLabel, QComboBox, QLineEdit, QHBoxLayout,
    QDateTimeEdit, QPushButton, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import QDateTime, Qt

def load_properties(file_type, config_path="config\properties"):
    """Đọc file YAML và trả về cấu hình"""
    try:
        config_file = os.path.join(config_path, f"{file_type}.yaml")
        with open(config_file, 'r', encoding='utf-8') as f:
            props = yaml.safe_load(f)
            return props
    except Exception as e:
        raise ValueError(f"Lỗi đọc cấu hình: {str(e)}")

def create_form(config):
    """Tạo form động từ cấu hình YAML"""
    grid = QGridLayout()
    grid.setSpacing(10)
    grid.setContentsMargins(10, 10, 10, 10)
    widgets = {}

    # Thêm các trường từ YAML bắt đầu từ hàng 2
    for row, (field, props) in enumerate(config.items(), start=2):
        label = QLabel(props.get('label', field))
        widget = _create_widget(props)
        
        grid.addWidget(label, row, 0)
        grid.addWidget(widget, row, 1, 1, 2)
        widgets[field] = widget

    return grid, widgets

def _create_widget(props):
    """Tạo widget từ cấu hình YAML"""
    widget_type = props.get("type", "QLineEdit")
    readonly = props.get("readonly", False)  # Lấy giá trị read-only từ config

    # Tạo widget
    if widget_type == "QComboBox":
        widget = QComboBox()
        widget.addItems(props.get("options", []))
        # QComboBox không hỗ trợ setReadOnly, dùng setEnabled để vô hiệu hóa theo trang thai trong YAML
        widget.setEnabled(not readonly)

    elif widget_type == "QDateTimeEdit":
        widget = QDateTimeEdit()
        widget.setDisplayFormat(props.get("format", "yyyy-MM-dd HH:mm:ss"))
        widget.setCalendarPopup(True)
        widget.setDateTime(QDateTime.currentDateTime())
        widget.setReadOnly(readonly)

    else:  # Mặc định là QLineEdit
        widget = QLineEdit()
        widget.setReadOnly(readonly)
    
    # Thiết lập placeholder text nếu có
    if "placeholder" in props:
        widget.setPlaceholderText(props["placeholder"])
    
    return widget

def add_default_fields(grid, widgets, start_row):
    """Thêm các trường mặc định"""
    # Thêm nút Upload và Cancel vào hàng 0
    btn_upload = QPushButton("Upload")
    btn_cancel = QPushButton("Cancel")
    button_layout = QHBoxLayout()
    button_layout.addWidget(btn_upload)
    button_layout.addWidget(btn_cancel)

    # Thêm nút vào grid (hàng 0)
    grid.addLayout(button_layout, 0, 0, 1, 2)
    widgets.update({
        'btn_upload': btn_upload,
        'btn_cancel': btn_cancel
    })
    button_layout.setAlignment(Qt.AlignLeft) # Canh 2 nút sang trái

    # File Path vào hàng 1
    file_path_edit = QLineEdit()
    file_path_edit.setPlaceholderText("Kéo thả file hoặc nhấn nút chọn file")
    grid.addWidget(QLabel("File Path"), 1, 0)
    grid.addWidget(file_path_edit, 1, 1)
    widgets['file_path'] = file_path_edit

    # Open File Button vào hàng 1
    btn_open_file = QPushButton("Open File")
    grid.addWidget(btn_open_file, 1, 2)
    widgets['btn_open_file'] = btn_open_file

    return grid, widgets