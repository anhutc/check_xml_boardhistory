import os
from tokenize import group
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QPushButton, QFileDialog, QListWidget, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QLineEdit, QMessageBox, QWidget, QApplication,
    QToolTip,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import  QMenu

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_variables()
        self.init_ui()

    def init_variables(self):
        """Khởi tạo các biến thành viên"""
        self.setWindowTitle("ASM BoardHistory (https://anhutc.github.io)")
        self.setFixedSize(1200, 920)
        self.move(
            (QApplication.desktop().screen().width() - self.width()) // 2, 0
        )
        # Biến lưu trữ dữ liệu
        self.xml_data = {}  # {barcode: {file_path, basic_info}}
        self.current_barcode = None
        self.barcode_items = []
        self.ref_items = []
        self.panel_items = []
        self.ref_mapping = {}
        self.panel_mapping = {}

    def init_ui(self):
        """Khởi tạo giao diện người dùng với bố cục hài hòa"""
        # Widget chính
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout chính với tỷ lệ 25:75 cho panel trái và phải
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 10, 0, 10)
        
        # Panel trái (tìm board) - chiếm 25% chiều rộng
        find_board_panel = self.create_find_board_panel()
        main_layout.addWidget(find_board_panel, 25)
        
        # Panel phải (thông tin chi tiết) - chiếm 75% chiều rộng
        detail_panel = self.create_detail_panel()
        main_layout.addWidget(detail_panel, 75)
    

    def create_find_board_panel(self):
        """Tạo panel tìm kiếm board"""
        group = QGroupBox()
        layout = QVBoxLayout(group)

        # Custom style cho panel trái
        group.setStyleSheet("""
            QGroupBox {
                background: white;
                border-radius: 10px;
                padding: 15px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #2196F3, stop:1 #E91E63);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #1976D2, stop:1 #D81B60);
            }
            QLineEdit {
                border: 1px solid #2196F3;
                border-radius: 5px;
                padding: 8px;
                font-size: 13px;
                margin-top: 5px;
                margin-bottom: 5px;
            }
            QListWidget {
                border: 1px solid #E91E63;
                border-radius: 5px;
                padding: 5px;
                font-size: 13px;
                background: white;
                margin-bottom: 15px;
                selection-background-color: #E91E63;
                selection-color: white;
            }
            QLabel {
                color: #333333;
                font-size: 13px;
                font-weight: bold;
                margin: 5px 0;
            }
        """)
        
        # Button Import với icon
        import_btn = QPushButton("Import Board (xml)")
        import_btn.setMinimumHeight(40)
        layout.addWidget(import_btn)
        import_btn.clicked.connect(self.import_xml)
        
        # Barcode section
        
        self.barcode_label = QLabel("Barcode")
        layout.addWidget(self.barcode_label)

        self.barcode_filter = QLineEdit()
        self.barcode_filter.setPlaceholderText("Filter barcodes...")
        self.barcode_filter.textChanged.connect(self.filter_barcodes)
        self.barcode_filter.setEnabled(False)
        layout.addWidget(self.barcode_filter)
        
        self.barcode_list = QListWidget()
        self.barcode_list.setMinimumHeight(150)
        self.barcode_list.currentRowChanged.connect(self.on_barcode_selected)
        layout.addWidget(self.barcode_list)
        
        # Ref section
        self.ref_label = QLabel("Ref")
        layout.addWidget(self.ref_label)
        self.ref_filter = QLineEdit()
        self.ref_filter.setPlaceholderText("Filter refs...")
        self.ref_filter.textChanged.connect(self.filter_refs)
        self.ref_filter.setEnabled(False)
        layout.addWidget(self.ref_filter)
        
        self.ref_list = QListWidget()
        self.ref_list.setMinimumHeight(150)
        self.ref_list.currentItemChanged.connect(self.show_data_for_selection)
        layout.addWidget(self.ref_list)
        
        # Panel section
        self.panel_label = QLabel("Panel")
        layout.addWidget(self.panel_label)
        self.panel_filter = QLineEdit()
        self.panel_filter.setPlaceholderText("Filter panels...")
        self.panel_filter.textChanged.connect(self.filter_panels)
        self.panel_filter.setEnabled(False)
        layout.addWidget(self.panel_filter)
        
        self.panel_list = QListWidget()
        self.panel_list.setMinimumHeight(150)
        self.panel_list.currentItemChanged.connect(self.show_data_for_selection)
        layout.addWidget(self.panel_list)
        
        # Add context menu to barcode list
        self.barcode_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.barcode_list.customContextMenuRequested.connect(self.show_barcode_context_menu)
        
        return group
    def create_detail_panel(self):
        """Tạo panel hiển thị thông tin chi tiết"""
        group = QGroupBox()
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 10, 10, 30)
        
        # Create tables first
        self.pickup_table = QTableWidget(15, 2)
        self.placement_table = QTableWidget(19, 2)
        
        # Style cho các bảng và groupbox
        group.setStyleSheet("""
            QGroupBox {
                background: transparent;
                border: none;
                padding: 0px;
            }
        """)

        # Style cho tables
        table_style = """
            QTableWidget {
                background: white;
                border: none;
                gridline-color: #ecf0f1;
            }
            QTableWidget::item {
                padding: 5px;
                border: none;
                color: #2c3e50;
                font-size: 50px;
            }
            QTableWidget::item:selected {
                background: rgba(52, 152, 219, 0.1);
                color: #2c3e50;
            }
            QHeaderView::section {
                background: #34495e;
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 8px;
                border: none;
            }
        """
        
        # Enable alternating row colors
        self.pickup_table.setAlternatingRowColors(True)
        self.placement_table.setAlternatingRowColors(True)
        
        # Set up tables
        for table in [self.pickup_table, self.placement_table]:
            table.setShowGrid(False)
            table.setStyleSheet(table_style)
            table.horizontalHeader().setStretchLastSection(True)
            table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
            table.verticalHeader().setVisible(False)
            table.verticalHeader().setDefaultSectionSize(40)
            table.setColumnWidth(0, 200)
            table.setColumnWidth(1, 200)
        
        # Tables layout
        tables_layout = QHBoxLayout()
        tables_layout.setSpacing(10)
        
        # Pickup table
        pickup_group = QGroupBox("Pickup")
        pickup_group.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                padding: 20px;
            }
        """)
        pickup_layout = QVBoxLayout(pickup_group)
        pickup_layout.setContentsMargins(5, 5, 5, 5)
        self.setup_pickup_table()
        pickup_layout.addWidget(self.pickup_table)
        tables_layout.addWidget(pickup_group)
        
        # Placement table
        placement_group = QGroupBox("Placement")
        placement_group.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                padding: 20px;
            }
        """)
        placement_layout = QVBoxLayout(placement_group)
        pickup_layout.setContentsMargins(5, 5, 5, 5)
        self.setup_placement_table()
        placement_layout.addWidget(self.placement_table)
        tables_layout.addWidget(placement_group)
        
        layout.addLayout(tables_layout)
        
        return group

    def setup_pickup_table(self):
        """Thiết lập bảng pickup"""
         # Set read-only flags
        self.pickup_table.setEditTriggers(QTableWidget.NoEditTriggers)
        # Make cells non-selectable
        self.pickup_table.setSelectionMode(QTableWidget.NoSelection)
        # Disable drag and drop
        self.pickup_table.setDragDropMode(QTableWidget.NoDragDrop)
    
        # Set headers
        self.pickup_table.setHorizontalHeaderLabels(["Process", "Data"])
        header = self.pickup_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        # Define row indices
        self.pickup_time_row = 0
        self.pickup_machine_row = 1
        self.pickup_head_row = 2
        self.pickup_segment_row = 3
        self.pickup_nozzle_row = 4
        self.pickup_conponent_row = 5
        self.pickup_repick_row = 6
        self.pickup_track_row = 7
        self.pickup_pitck_row = 8
        self.pickup_feeder_time_row = 9
        self.pickup_z_down_row = 10
        self.pickup_z_up_row = 11
        self.pickup_dp_angle_row = 12
        self.pickup_vacuum_before_row = 13
        self.pickup_vacuum_after_row = 14
        self.pickup_holding_row = 15
        self.pickup_error_in_z_row = 16
        self.pickup_stay_time_row = 17
        self.pickup_measure_height_row = 18
        
        # Set row labels
        row_labels = [
            "Time", "Machine", "Head", "Segment", "Nozzle",
            "Component", "Repick", "Track", "Pitch", "Feeder Time",
            "Z Down", "Z Up", "DP Angle", "Vacuum Before",
            "Vacuum After", "Holding", "Error In Z", "Stay Time",
            "Measure Height"
        ]
        for i, label in enumerate(row_labels):
            self.pickup_table.setItem(i, 0, QTableWidgetItem(label))

    def setup_placement_table(self):
        """Thiết lập bảng placement"""
        # Set read-only flags  
        self.placement_table.setEditTriggers(QTableWidget.NoEditTriggers)
        # Make cells non-selectable
        self.placement_table.setSelectionMode(QTableWidget.NoSelection)
        # Disable drag and drop
        self.placement_table.setDragDropMode(QTableWidget.NoDragDrop)
        
        # Set headers
        self.placement_table.setHorizontalHeaderLabels(["Process", "Data"])
        header = self.placement_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        # Define row indices
        self.placement_time_row = 0
        self.placement_machine_row = 1
        self.placement_head_row = 2
        self.placement_lane_row = 3
        self.placement_segment_row = 4
        self.placement_nozzle_row = 5
        self.placement_conponent_row = 6
        self.placement_measure_x_row = 7
        self.placement_measure_y_row = 8
        self.placement_measure_phi_row = 9
        self.placement_theroy_size_row = 10
        self.placement_actual_size_row = 11
        self.placement_error_in_z_row = 12
        self.placement_z_end_row = 13
        self.placement_z_down_row = 14
        self.placement_z_up_row = 15
        self.placement_vacuum_before_row = 16
        self.placement_vacuum_after_row = 17
        self.placement_holding_row = 18
        self.placement_airkiss_pro_row = 19
        self.placement_airkiss_machine_row = 20
        self.placement_airkiss_measured_row = 21
        self.placement_airkiss_time_row = 22
        self.placement_stay_time_row = 23
        self.placement_order_current_machine_row = 24
        self.placement_recipe_row = 25
        
        # Set row labels
        row_labels = [
            "Time", "Machine", "Head", "Lane", "Segment", "Nozzle",
            "Component", "Measure X", "Measure Y", "Measure Phi",
            "Theory Size", "Actual Size", "Error In Z", "Z End",
            "Z Down Profile", "Z Up Profile", "Vacuum Before",
            "Vacuum After", "Holding", "Airkiss Profile",
            "Airkiss Machine", "Airkiss Measured", "Airkiss Time",
            "Stay Time", "Order Current Machine", "Recipe"
        ]
        for i, label in enumerate(row_labels):
            self.placement_table.setItem(i, 0, QTableWidgetItem(label))

    def import_xml(self):
        """Import và phân tích file XML"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select XML Files",
            "",
            "XML Files (*.xml)"
        )
        
        if files:
            current_barcode = self.barcode_list.currentItem().text() if self.barcode_list.currentItem() else None
            
            for file_path in files:
                try:
                    tree = ET.parse(file_path)
                    root = tree.getroot()
                    
                    # Check for board ID first
                    board_id = root.findtext(".//Id", "")
                    if not board_id:
                        QMessageBox.warning(
                            self,
                            "Invalid File",
                            f"File {os.path.basename(file_path)} does not contain a board ID.",
                            QMessageBox.Ok
                        )
                        continue
                    
                    # Get basic info
                    basic_info = {
                        'EndPicking': root.findtext(".//BoardHistory/ProcessingHistory/ProcessingPosition/EndPicking", ""),
                        'EndPlacing': root.findtext(".//BoardHistory/ProcessingHistory/ProcessingPosition/EndPlacing", ""),
                        'MachineId': root.findtext(".//MachineId", ""),
                        'GantryId': root.findtext(".//PlaceHeads/PlaceHead/GantryId", ""),
                        'Lane': root.findtext(".//Lane", "")
                    }
                    
                    # Get barcode
                    barcode = root.findtext(".//Barcode", "")
                    if barcode:
                        unique_key = f"{board_id}__{barcode}"
                        if unique_key not in self.barcode_items:
                            self.barcode_items.append(unique_key)
                            self.xml_data[unique_key] = {
                                'file_path': file_path,
                                'basic_info': basic_info
                            }
                    else:
                        QMessageBox.warning(
                            self,
                            "Invalid File",
                            f"File {os.path.basename(file_path)} does not contain a barcode.",
                            QMessageBox.Ok
                        )
                        
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Error processing file {os.path.basename(file_path)}:\n{str(e)}",
                        QMessageBox.Ok
                    )

            # Update UI
            self.barcode_list.clear()
            self.barcode_list.addItems(sorted(self.barcode_items))
            
            # Restore selection
            if current_barcode and current_barcode in self.barcode_items:
                for i in range(self.barcode_list.count()):
                    if self.barcode_list.item(i).text() == current_barcode:
                        self.barcode_list.setCurrentItem(self.barcode_list.item(i))
                        break
                        
            self.barcode_filter.setEnabled(True)

    def filter_barcodes(self, text):
        """Lọc danh sách barcode"""
        for i in range(self.barcode_list.count()):
            item = self.barcode_list.item(i)
            item.setHidden(text.upper() not in item.text().upper())

    def filter_refs(self, text):
        """Lọc danh sách ref"""
        for i in range(self.ref_list.count()):
            item = self.ref_list.item(i)
            item.setHidden(text.upper() not in item.text().upper())

    def filter_panels(self, text):
        """Lọc danh sách panel"""
        for i in range(self.panel_list.count()):
            item = self.panel_list.item(i)
            item.setHidden(text.upper() not in item.text().upper())

    def show_data_for_selection(self):
        """Hiển thị dữ liệu khi chọn ref và panel"""
        ref_item = self.ref_list.currentItem()
        panel_item = self.panel_list.currentItem()
        
        # Cập nhật labels ngay khi chọn
        if ref_item:
            self.ref_label.setText(f"Ref: {ref_item.text()}")
            
        if panel_item:    
            self.panel_label.setText(f"Panel: {panel_item.text()}")

        # Chỉ xử lý khi đã chọn cả ref và panel
        if not (ref_item and panel_item and self.xml_root is not None):
            return

        try:
            # Lưu lại basic_info trước khi clear
            basic_info = {}
            if self.current_barcode and self.current_barcode in self.xml_data:
                basic_info = self.xml_data[self.current_barcode]['basic_info']

            # Clear chỉ những dòng không phải basic info
            if hasattr(self, "pickup_table"):
                for row in range(self.pickup_table.rowCount()):
                    if row not in [self.pickup_time_row, self.pickup_machine_row, self.pickup_head_row]:
                        self.pickup_table.setItem(row, 1, QTableWidgetItem(""))

            if hasattr(self, "placement_table"):
                for row in range(self.placement_table.rowCount()):
                    if row not in [self.placement_time_row, self.placement_machine_row, 
                                 self.placement_head_row, self.placement_lane_row]:
                        self.placement_table.setItem(row, 1, QTableWidgetItem(""))

            ref_name = ref_item.text()
            panel_name = panel_item.text()

            # Lấy ID của ref và panel từ mapping
            ref_ids = self.ref_mapping.get(ref_name, [])
            panel_ids = self.panel_mapping.get(panel_name, [])

            # Tìm ID khớp giữa ref và panel
            matched_ids = set(ref_ids) & set(panel_ids)

            if matched_ids:
                for matched_id in matched_ids:
                    pos_node = self.xml_root.find(f".//PlacePositions/PlacePosition[@Id='{matched_id}']")
                    if pos_node is not None:
                        component_node = pos_node.find("Component")
                        if component_node is not None:
                            # Update pickup table
                            if hasattr(self, "pickup_table"):
                                self.pickup_table.setItem(self.pickup_segment_row, 1,
                                    QTableWidgetItem(component_node.findtext("Segment", "")))
                                self.pickup_table.setItem(self.pickup_nozzle_row, 1,
                                    QTableWidgetItem(component_node.findtext("Nozzle", "")))
                                
                                # Xử lý component name từ VisionDump
                                raw_component = component_node.findtext("Measure/VisionDump", "")
                                if raw_component:
                                    parts = raw_component.split("_", 6)
                                    if len(parts) >= 7:
                                        component_name = parts[6].replace(".svdmp", "")
                                        self.pickup_table.setItem(self.pickup_conponent_row, 1,
                                            QTableWidgetItem(component_name))
                                        self.pickup_table.setItem(self.pickup_repick_row, 1,
                                            QTableWidgetItem(component_node.findtext("RetryCount", "")))
                                        self.pickup_table.setItem(self.pickup_track_row, 1,
                                            QTableWidgetItem(component_node.findtext("Pick/FeederData/locationKey", "")))
                                                    
                                        ram_pitch = component_node.findtext("Pick/FeederData/pitch", "")
                                        if ram_pitch:
                                            self.pickup_table.setItem(self.pickup_pitck_row, 1,
                                                QTableWidgetItem(ram_pitch.replace(".", "")))

                                        self.pickup_table.setItem(self.pickup_feeder_time_row, 1,
                                            QTableWidgetItem("N/A"))
                                        self.pickup_table.setItem(self.pickup_z_down_row, 1,
                                            QTableWidgetItem(component_node.findtext("Pick/ZMovementDown/TravelProfile", "")))
                                        self.pickup_table.setItem(self.pickup_z_up_row, 1,
                                            QTableWidgetItem(component_node.findtext("Pick/ZMovementUp/TravelProfile", "")))
                                        self.pickup_table.setItem(self.pickup_dp_angle_row, 1,
                                            QTableWidgetItem(component_node.findtext("Pick/DpMovement/TargetPosition", "")))
                                        self.pickup_table.setItem(self.pickup_vacuum_before_row, 1,
                                            QTableWidgetItem(component_node.findtext("Pick/VacuumSystem/MeasuredBefore", "")))
                                        self.pickup_table.setItem(self.pickup_vacuum_after_row, 1,
                                            QTableWidgetItem(component_node.findtext("Pick/VacuumSystem/MeasuredAfter", "")))
                                        self.pickup_table.setItem(self.pickup_holding_row, 1,
                                            QTableWidgetItem(component_node.findtext("Pick/VacuumSystem/HoldingCircuit", "")))
                                        self.pickup_table.setItem(self.pickup_error_in_z_row, 1,
                                            QTableWidgetItem("N/A"))
                                        self.pickup_table.setItem(self.pickup_stay_time_row, 1,
                                            QTableWidgetItem("N/A"))
                                        self.pickup_table.setItem(self.pickup_measure_height_row, 1,
                                            QTableWidgetItem(component_node.findtext("Pick/ComponentSensor/MeasuredHeight", "")))

                            # Update placement table
                            if hasattr(self, "placement_table"):
                                self.placement_table.setItem(self.placement_segment_row, 1,
                                    QTableWidgetItem(component_node.findtext("Segment", "")))
                                self.placement_table.setItem(self.placement_nozzle_row, 1,
                                    QTableWidgetItem(component_node.findtext("Nozzle", "")))
                                self.placement_table.setItem(self.placement_conponent_row, 1,
                                    QTableWidgetItem(component_name if 'component_name' in locals() else ""))
                                
                                measure_x = component_node.findtext("Measure/MeasuredPose/X", "")
                                if measure_x:
                                    try:
                                        measure_x = f"{float(measure_x):.6f}"
                                    except (ValueError, TypeError):
                                        pass
                                self.placement_table.setItem(self.placement_measure_x_row, 1,
                                    QTableWidgetItem(measure_x))
                                    
                                measure_y = component_node.findtext("Measure/MeasuredPose/Y", "")
                                if measure_y:
                                    try:
                                        measure_y = f"{float(measure_y):.6f}"
                                    except (ValueError, TypeError):
                                        pass
                                self.placement_table.setItem(self.placement_measure_y_row, 1,
                                    QTableWidgetItem(measure_y))
                                    
                                measure_phi = component_node.findtext("Measure/MeasuredPose/Phi", "")
                                if measure_phi:
                                    try:
                                        measure_phi = f"{float(measure_phi):.6f}"
                                    except (ValueError, TypeError):
                                        pass
                                self.placement_table.setItem(self.placement_measure_phi_row, 1,
                                    QTableWidgetItem(measure_phi))
                                    
                                self.placement_table.setItem(self.placement_theroy_size_row, 1,
                                    QTableWidgetItem(component_node.findtext("Pick/FeederData/ComponentHeight", "")))
                                self.placement_table.setItem(self.placement_actual_size_row, 1,
                                    QTableWidgetItem(component_node.findtext("Pick/ComponentSensor/MeasuredHeight", "")))
                                    
                                error_in_z = pos_node.findtext("ErrorInZ", "")
                                if error_in_z:
                                    try:
                                        error_in_z = f"{float(error_in_z):.6f}"
                                    except (ValueError, TypeError):
                                        pass
                                self.placement_table.setItem(self.placement_error_in_z_row, 1,
                                    QTableWidgetItem(error_in_z))
                                    
                                self.placement_table.setItem(self.placement_z_end_row, 1,
                                    QTableWidgetItem(component_node.findtext("Place/ZMovementDown/EndPosition", "")))
                                self.placement_table.setItem(self.placement_z_down_row, 1,
                                    QTableWidgetItem(component_node.findtext("Place/ZMovementDown/TravelProfile", "")))
                                self.placement_table.setItem(self.placement_z_up_row, 1,
                                    QTableWidgetItem(component_node.findtext("Place/ZMovementUp/TravelProfile", "")))
                                self.placement_table.setItem(self.placement_vacuum_before_row, 1,
                                    QTableWidgetItem(component_node.findtext("Place/VacuumSystem/MeasuredBefore", "")))
                                self.placement_table.setItem(self.placement_vacuum_after_row, 1,
                                    QTableWidgetItem(component_node.findtext("Place/VacuumSystem/MeasuredAfter", "")))
                                self.placement_table.setItem(self.placement_holding_row, 1,
                                    QTableWidgetItem(component_node.findtext("Pick/VacuumSystem/HoldingCircuit", "")))
                                self.placement_table.setItem(self.placement_airkiss_pro_row, 1,
                                    QTableWidgetItem(component_node.findtext("Place/VacuumSystem/ParamDown", "")))
                                self.placement_table.setItem(self.placement_airkiss_machine_row, 1,
                                    QTableWidgetItem(component_node.findtext("Place/VacuumSystem/ParamThresholdDown", "")))
                                self.placement_table.setItem(self.placement_airkiss_measured_row, 1,
                                    QTableWidgetItem(component_node.findtext("Place/VacuumSystem/MeasuredDown", "")))
                                self.placement_table.setItem(self.placement_airkiss_time_row, 1,
                                    QTableWidgetItem("N/A"))
                                self.placement_table.setItem(self.placement_stay_time_row, 1,
                                    QTableWidgetItem("N/A"))
                                self.placement_table.setItem(self.placement_order_current_machine_row, 1,
                                    QTableWidgetItem("N/A"))
                                    
                                recipe_node = self.xml_root.find(".//Recipe")
                                self.placement_table.setItem(self.placement_recipe_row, 1,
                                    QTableWidgetItem(recipe_node.text if recipe_node is not None else ""))

                            break

        except Exception as e:
            print(f"Error showing data: {e}")

    def clear_pickup_placement_tables(self):
        """Xóa dữ liệu trong các bảng pickup và placement"""
        if hasattr(self, "pickup_table"):
            for row in range(self.pickup_table.rowCount()):
                self.pickup_table.setItem(row, 1, QTableWidgetItem(""))
                
        if hasattr(self, "placement_table"):
            for row in range(self.placement_table.rowCount()):
                self.placement_table.setItem(row, 1, QTableWidgetItem(""))

    def copy_cell_value(self, item):
        """Copy giá trị của cell vào clipboard"""
        if item and item.column() == 1:  # Chỉ copy cột Value
            value = item.text()
            QApplication.clipboard().setText(value)
            QToolTip.showText(QCursor.pos(), "Copied!")

    def on_barcode_selected(self, index):
        """Xử lý khi chọn barcode"""
        # Clear all data first
        self.clear_pickup_placement_tables()
        
        # Clear lists
        self.ref_list.clear()
        self.panel_list.clear()
        
        # Reset labels
        self.ref_label.setText("Ref")
        self.panel_label.setText("Panel")
        self.barcode_label.setText("Barcode")
        
        # Clear mappings
        self.ref_mapping.clear()
        self.panel_mapping.clear()
        self.ref_items.clear()
        self.panel_items.clear()
        
        if index >= 0:
            selected_item = self.barcode_list.item(index)
            if selected_item:
                selected_barcode = selected_item.text()
                self.current_barcode = selected_barcode
                self.barcode_label.setText(f"Barcode: {selected_barcode}")
                
                # Get file data
                file_data = self.xml_data.get(selected_barcode)
                if file_data:
                    try:
                         # Check if file exists
                        if not os.path.exists(file_data['file_path']):
                            raise FileNotFoundError(f"XML file not found: {file_data['file_path']}")
                            
                        # Parse XML file
                        tree = ET.parse(file_data['file_path'])
                        self.xml_root = tree.getroot()
                        
                        
                        # Update basic info only
                        basic_info = file_data['basic_info']
                        if hasattr(self, "pickup_table"):
                            self.pickup_table.setItem(self.pickup_time_row, 1,
                                QTableWidgetItem(basic_info.get('EndPicking', '')))
                            self.pickup_table.setItem(self.pickup_machine_row, 1,
                                QTableWidgetItem(basic_info.get('MachineId', '')))
                            self.pickup_table.setItem(self.pickup_head_row, 1,
                                QTableWidgetItem(basic_info.get('GantryId', '')))

                        if hasattr(self, "placement_table"):
                            self.placement_table.setItem(self.placement_time_row, 1,
                                QTableWidgetItem(basic_info.get('EndPlacing', '')))
                            self.placement_table.setItem(self.placement_machine_row, 1,
                                QTableWidgetItem(basic_info.get('MachineId', '')))
                            self.placement_table.setItem(self.placement_head_row, 1,
                                QTableWidgetItem(basic_info.get('GantryId', '')))
                            self.placement_table.setItem(self.placement_lane_row, 1,
                                QTableWidgetItem(basic_info.get('Lane', '')))

                        # Build mappings and update lists
                        self.update_ref_panel_mappings()

                    except Exception as e:
                        # Show error message
                        QMessageBox.critical(
                            self,
                            "File Error",
                            f"Error loading barcode {selected_barcode}:\n{str(e)}\n\nThis barcode will be removed."
                        )
                        
                        # Remove invalid barcode
                        self.remove_invalid_barcode(selected_barcode)
                        
                    except Exception as e:
                        QMessageBox.critical(
                            self,
                            "XML Error",
                            f"Error parsing XML for barcode {selected_barcode}:\n{str(e)}"
                        )
                        print(f"Error parsing XML: {e}")
                    finally:
                        import gc
                        gc.collect()
    
    def remove_invalid_barcode(self, barcode):
        """Remove invalid barcode from all data structures"""
        # Remove from data dictionary
        if barcode in self.xml_data:
            del self.xml_data[barcode]
        
        # Remove from items list
        if barcode in self.barcode_items:
            self.barcode_items.remove(barcode)
        
        # Remove from list widget
        items = self.barcode_list.findItems(barcode, Qt.MatchExactly)
        for item in items:
            self.barcode_list.takeItem(self.barcode_list.row(item))
        
        # Clear selection if no items left
        if self.barcode_list.count() == 0:
            self.barcode_filter.setEnabled(False)
            self.barcode_filter.clear()
                        
    def update_ref_panel_mappings(self):
        """Update ref and panel mappings separately"""
        try:
            # Build ref mappings
            for pos_node in self.xml_root.findall(".//PlacePositions/PlacePosition"):
                pos_id = pos_node.get('Id')
                name = pos_node.findtext('Name')
                if pos_id and name:
                    if name not in self.ref_mapping:
                        self.ref_mapping[name] = set()
                        self.ref_items.append(name)
                    self.ref_mapping[name].add(pos_id)

            # Build panel mappings
            for panel in self.xml_root.findall(".//SubBoards/SubBoard/ChildImage/ChildImages/ChildImage/ChildImages/ChildImage"):
                panel_name = panel.findtext("Name")
                if panel_name:
                    for pos in panel.findall("PlacePositions/PlacePosition"):
                        pos_id = pos.get("Id")
                        if pos_id:
                            if panel_name not in self.panel_mapping:
                                self.panel_mapping[panel_name] = set()
                                self.panel_items.append(panel_name)
                            self.panel_mapping[panel_name].add(pos_id)

            # Update UI lists
            self.ref_list.addItems(sorted(self.ref_items))
            self.panel_list.addItems(sorted(self.panel_items))
            
            # Enable filters
            self.ref_filter.setEnabled(True)
            self.panel_filter.setEnabled(True)
            
        except Exception as e:
            print(f"Error updating mappings: {e}")

    def show_barcode_context_menu(self, position):
        """Show context menu for barcode list"""
        menu = QMenu()
        current_item = self.barcode_list.currentItem()
        
        # Copy action
        copy_action = menu.addAction("Copy Current Barcode")
        copy_action.setEnabled(current_item is not None)
        
        # Clear all action
        clear_action = menu.addAction("Clear All Barcodes")
        clear_action.setEnabled(self.barcode_list.count() > 0)
        
        # Show menu and handle actions
        action = menu.exec_(self.barcode_list.viewport().mapToGlobal(position))
        
        if action == copy_action and current_item:
            QApplication.clipboard().setText(current_item.text())
            QToolTip.showText(QCursor.pos(), "Copied!")
        elif action == clear_action:
            reply = QMessageBox.question(
                self, 
                'Clear All Barcodes',
                'Are you sure you want to clear all barcodes?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Clear everything
                self.barcode_list.clear()
                self.ref_list.clear()
                self.panel_list.clear()
                self.xml_data.clear()
                self.barcode_items.clear()
                self.clear_pickup_placement_tables()
                
                # Reset labels
                self.ref_label.setText("Ref")
                self.panel_label.setText("Panel")
                self.barcode_label.setText("Barcode")
                
                # Disable filters
                self.barcode_filter.setEnabled(False)
                self.ref_filter.setEnabled(False)
                self.panel_filter.setEnabled(False)
                
                # Clear filters
                self.barcode_filter.clear()
                self.ref_filter.clear()
                self.panel_filter.clear()