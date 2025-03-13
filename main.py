import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QAction,
    QTableWidgetItem, QVBoxLayout, QWidget, QPushButton, QHBoxLayout,
    QToolBar, QComboBox, QLabel, QLineEdit, QMessageBox, QTabWidget
)
from PyQt5.QtGui import QFont
from gui.dialogs.column_selector_dialog import ColumnSelectorDialog
from gui.dialogs.data_export_dialog import DataExportDialog
from gui.data_loader import DataLoader
from gui.dialogs.import_dialog.data_import_dialog import DataImportTab

class OSDUApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OSDU Desktop App")
        self.setGeometry(100, 100, 900, 600)
        
        # Khởi tạo cấu trúc dữ liệu
        self._initialize_data_structures()
        
        # Khởi tạo GUI
        self._init_ui()
        
        # Kết nối sự kiện
        self._connect_events()

    # Khởi tạo dữ liệu
    def _initialize_data_structures(self):
        self.columns_by_type = {
            "Select Data Type": [],
            "WellLog": ["WellBore Name", "File Name", "Start Depth", "Stop Depth", 
                      "Log Run", "Log Type", "Date", "Logging Service", "Fluid Type", 
                      "Log Class", "Logging Mode"],
            "Marker": ["Well Name", "Marker Name", "Depth", "Confidence Level", "Source"],
            "WellPath": ["Well Name", "Measured Depth", "Inclination", "Azimuth"],
            "Seismic 2D": ["Survey Name", "Line Name", "Shot Points", "Processing Status"],
            "Seismic 3D": ["Survey Name", "Volume Name", "Inline Count", "Crossline Count", 
                          "Processing Status"],
            "Seismic Location": ["Seismic Name", "Latitude", "Longitude"],
            "Document": ["Document Name", "Type", "Date", "Author"]
        }
        
        self.visible_columns = {key: {col: True for col in cols} 
                               for key, cols in self.columns_by_type.items()}
        self.current_data_type = "Select Data Type"
        self.original_data = {}
        self.filtered_data = []
        self.all_data = []
        self.current_page = 0
        self.rows_per_page = 50

    # Khởi tạo GUI
    def _init_ui(self):
        # Tạo menu bar
        self._create_menu_bar()
        
        # Tạo tabs và layout chính
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Thêm tabs
        self.tabs = QTabWidget()
        self._setup_query_tab()
        self._setup_import_tab()
        main_layout.addWidget(self.tabs)

    def _create_menu_bar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        new_action = QAction("New", self)
        close_action = QAction("Close", self)

        file_menu.addAction(new_action)
        file_menu.addAction(close_action)

        close_action.triggered.connect(self.close)

        menu_menu = menubar.addMenu("Menu")
        about_action = QAction("About", self)
        menu_menu.addAction(about_action)

    def _setup_query_tab(self):
        """Thiết lập tab Query"""
        query_tab = QWidget()
        layout = QVBoxLayout(query_tab)
        
        # Thêm upper toolbar
        layout.addWidget(self._create_upper_toolbar())
        
        # Thêm bảng dữ liệu
        layout.addWidget(self._create_table_view())
        
        # Thêm lower toolbar
        layout.addWidget(self._create_lower_toolbar())
        
        self.tabs.addTab(query_tab, "Query")

    def _setup_import_tab(self):
        """Thiết lập tab Import"""
        self.import_tab = DataImportTab()
        self.tabs.addTab(self.import_tab, "Import")

    def _create_upper_toolbar(self):
        toolbar = QToolBar("Filter Toolbar")
        
        # Combo box chọn loại dữ liệu
        self.data_type_selector = QComboBox()
        self.data_type_selector.addItems(self.columns_by_type.keys())
        toolbar.addWidget(self.data_type_selector)
        
        # Ô tìm kiếm
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        toolbar.addWidget(self.search_input)
        
        # Nút filter
        self.btn_filter = QPushButton("Filter")
        toolbar.addWidget(self.btn_filter)
        
        return toolbar

    def _create_table_view(self):
        """Tạo bảng dữ liệu và phân trang"""
        container = QWidget()
        layout = QVBoxLayout(container)
        
        # Bảng dữ liệu
        self.table = QTableWidget()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        layout.addWidget(self.table)
        
        # Phân trang
        pagination_widget = QWidget()
        pagination_layout = QHBoxLayout(pagination_widget)
        self.prev_btn = QPushButton("Previous")
        self.next_btn = QPushButton("Next")
        self.page_label = QLabel("Page 1")
        
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.prev_btn)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_btn)
        pagination_layout.addStretch()
        
        layout.addWidget(pagination_widget)

        # Kết nối sự kiện khi chọn dữ liệu
        self.table.itemSelectionChanged.connect(self._update_export_button_state)

        return container

    def _create_lower_toolbar(self):
        """Toolbar dưới cùng"""
        toolbar = QToolBar("Actions")
        self.btn_export = QPushButton("Export")
        self.btn_columns = QPushButton("Select Columns")
        
        self.btn_export.setEnabled(False)
        toolbar.addWidget(self.btn_export)
        toolbar.addWidget(self.btn_columns)
        
        return toolbar

    # Kết nối sự kiện
    def _connect_events(self):
        """Kết nối tất cả sự kiện"""
        # Query tab
        self.btn_filter.clicked.connect(self.apply_filter)
        self.data_type_selector.currentIndexChanged.connect(self.handle_data_type_change)
        self.btn_export.clicked.connect(self.export_data)
        self.btn_columns.clicked.connect(self.open_column_selector)
        self.prev_btn.clicked.connect(self.prev_page)
        self.next_btn.clicked.connect(self.next_page)
        
        # Import tab
        self.import_tab.upload_started.connect(self.handle_file_upload)

    def handle_file_upload(self, file_path):
        """Xử lý upload file từ tab Import"""
        print(f"Đang xử lý file: {file_path}")
        # Thêm logic xử lý file thực tế tại đây
        # Ví dụ: self.handle_imported_data(data)

    # Xử lý dữ liệu
    def handle_data_type_change(self):
        self.current_data_type = self.data_type_selector.currentText()
        if self.current_data_type == "Select Data Type":
            self.table.clearContents()
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return
        # Reset bảng dữ liệu
        self.table.setRowCount(0)
        self.table.setColumnCount(0)

    def apply_filter(self):
        """Xử lý logic filter dữ liệu"""
        # Kiểm tra đã chọn loại dữ liệu chưa
        if self.current_data_type == "Select Data Type":
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn loại dữ liệu trước!")
            return

        # Load dữ liệu nếu chưa có
        if self.current_data_type not in self.original_data:
            self._load_data_to_memory()

        # Lấy từ khóa tìm kiếm
        keyword = self.search_input.text().strip().lower()
        raw_data = self.original_data.get(self.current_data_type, [])

        # Lọc dữ liệu
        if keyword:
            self.filtered_data = [
                row for row in raw_data 
                if any(keyword in str(cell).lower() for cell in row)
            ]
        else:
            self.filtered_data = raw_data.copy()  # Hiển thị toàn bộ nếu không có keyword

        # Cập nhật bảng
        self.all_data = self.filtered_data
        self.current_page = 0
        self._update_table()

        # Hiển thị thông báo nếu không có kết quả
        if not self.filtered_data:
            QMessageBox.warning(self, "Thông báo", "Không tìm thấy dữ liệu phù hợp!")

    def _update_table(self):
        start_idx = self.current_page * self.rows_per_page
        end_idx = start_idx + self.rows_per_page
        paginated_data = self.all_data[start_idx:end_idx]
        
        # Cập nhật tiêu đề cột
        visible_cols = [
            col for col in self.columns_by_type[self.current_data_type]
            if self.visible_columns[self.current_data_type][col]
        ]
        
        self.table.setRowCount(len(paginated_data))
        self.table.setColumnCount(len(visible_cols))
        self.table.setHorizontalHeaderLabels(visible_cols)
        
        # Đổ dữ liệu
        for row_idx, row in enumerate(paginated_data):
            for col_idx, col in enumerate(visible_cols):
                data_idx = self.columns_by_type[self.current_data_type].index(col)
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(row[data_idx])))
        
        # Cập nhật phân trang
        total_pages = max(1, (len(self.all_data) + self.rows_per_page - 1) // self.rows_per_page)
        self.page_label.setText(f"Page {self.current_page + 1}/{total_pages}")
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < total_pages - 1)

    def _update_export_button_state(self):
        """Enable or disable the export button based on table selection."""
        self.btn_export.setEnabled(bool(self.table.selectedItems()))

    def export_data(self):
        DataExportDialog(self.table).export_data()

    def open_column_selector(self):
        if self.current_data_type == "Select Data Type": return
        
        dialog = ColumnSelectorDialog(
            self,
            self.columns_by_type[self.current_data_type],
            self.visible_columns[self.current_data_type]
        )
        if dialog.exec_():
            self.visible_columns[self.current_data_type] = dialog.selected_columns
            self._update_table()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._update_table()

    def next_page(self):
        if (self.current_page + 1) * self.rows_per_page < len(self.all_data):
            self.current_page += 1
            self._update_table()

    def _load_data_to_memory(self):
        loader_map = {
            "WellLog": DataLoader.load_well_log_data,
            "Marker": DataLoader.load_marker_data,
            "WellPath": DataLoader.load_well_path_data,
            "Seismic 2D": DataLoader.load_seismic_2d_data,
            "Seismic 3D": DataLoader.load_seismic_3d_data,
            "Seismic Location": DataLoader.load_seismic_location_data,
            "Document": DataLoader.load_document_data
        }
        if self.current_data_type in loader_map:
            self.original_data[self.current_data_type] = loader_map[self.current_data_type]()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Arial", 9))
    window = OSDUApp()
    window.show()
    sys.exit(app.exec_())