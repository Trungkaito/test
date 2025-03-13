# data_export_dialog.py
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import csv

class DataExportDialog:
    def __init__(self, table_widget):
        self.table = table_widget  # Truyền đối tượng QTableWidget vào class

    def export_data(self):
        """Xử lý logic xuất dữ liệu từ bảng ra file CSV"""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            None,  # Không cần parent nếu dùng dialog độc lập
            "Save CSV", 
            "", 
            "CSV Files (*.csv);;All Files (*)", 
            options=options
        )
        
        if not file_name:
            return
        
        try:
            with open(file_name, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Lấy headers từ bảng
                headers = [self.table.horizontalHeaderItem(i).text() 
                          for i in range(self.table.columnCount())]
                writer.writerow(headers)
                
                # Lấy dữ liệu từ các hàng được chọn
                selected_ranges = self.table.selectedRanges()
                for selection in selected_ranges:
                    for row in range(selection.topRow(), selection.bottomRow() + 1):
                        row_data = [
                            self.table.item(row, col).text() 
                            if self.table.item(row, col) else "" 
                            for col in range(selection.leftColumn(), selection.rightColumn() + 1)
                        ]
                        writer.writerow(row_data)
            
            QMessageBox.information(None, "Thành công", "Xuất dữ liệu thành công!")
        
        except Exception as e:
            QMessageBox.critical(None, "Lỗi", f"Không thể xuất file:\n{str(e)}")