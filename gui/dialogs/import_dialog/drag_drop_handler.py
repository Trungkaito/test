from PyQt5.QtCore import Qt

def enable_drag_drop(widget):
    widget.setAcceptDrops(True)

    def dragEnterEvent(event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            # Kiểm tra tồn tại và trạng thái widget
            if hasattr(widget, 'placeholder_label') and widget.placeholder_label:
                try:
                    widget.placeholder_label.setText("Thả file vào đây để import")
                except RuntimeError:
                    # Xử lý trường hợp widget đã bị xóa
                    widget.placeholder_label = None

    def dragLeaveEvent(event):
        if hasattr(widget, 'placeholder_label') and widget.placeholder_label:
            try:
                widget.placeholder_label.setText("Kéo thả file CSV/TXT vào đây để bắt đầu")
            except RuntimeError:
                widget.placeholder_label = None

    def dropEvent(event):
        """Xử lý sự kiện thả file"""
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
            # Gọi phương thức xử lý file chính thức của widget
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if hasattr(widget, 'handle_dropped_file'):
                    widget.handle_dropped_file(file_path)
                    if hasattr(widget, '_update_file_list'):
                        widget._update_file_list(file_path)
        else:
            event.ignore()

    widget.dragEnterEvent = dragEnterEvent
    widget.dragLeaveEvent = dragLeaveEvent
    widget.dropEvent = dropEvent