from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QGroupBox, QLabel, QPushButton, QLineEdit, QMessageBox,
    QListWidget, QSplitter, QHeaderView, QFileDialog, QApplication, QMenu
)
from PyQt5.QtCore import Qt
import xml.etree.ElementTree as ET

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Check XML Boardhistory")
        self.setFixedSize(1000, 925)
        self.move(
            (QApplication.desktop().screen().width() - self.width()) // 2,
            (QApplication.desktop().screen().height() - self.height()) // 2
        )

        # Widget và layout chính
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)  # Layout dọc cho toàn bộ cửa sổ

        # Splitter ngang: bên trái là tab, bên phải là panel chức năng
        splitter = QSplitter(Qt.Horizontal)

        # Tab Pickup/Placement (bên trái)
        tab_widget = QTabWidget()
        tab_widget.addTab(self.create_pickup_tab(), "Pickup")
        tab_widget.addTab(self.create_placement_tab(), "Placement")
        tab_widget.setFixedWidth(780)
        tab_widget.setFixedHeight(880)
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #90caf9;
                border-radius: 8px;
                background: #fafdff;
                margin-top: 4px;
            }
            QTabBar::tab {
                background: #e3f2fd;
                color: #1565c0;
                border: 1px solid #90caf9;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                min-width: 120px;
                min-height: 32px;
                font-size: 15px;
                font-weight: bold;
                margin-right: 4px;
                margin-left: 2px;
                padding: 3px 130px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                color: #1976d2;
                border-bottom: 2px solid #ffffff;
            }
            QTabBar::tab:!selected {
                margin-top: 4px;
            }
        """)
        splitter.addWidget(tab_widget)

        # Panel chức năng (bên phải)
        find_board_panel = self.create_find_board_panel()
        find_board_panel.setFixedWidth(200)
        find_board_panel.setStyleSheet("""
            QGroupBox {
                border: none;
            }
        """)
        splitter.addWidget(find_board_panel)
        splitter.setStretchFactor(0, 3)  # Tab chiếm nhiều diện tích hơn
        splitter.setStretchFactor(1, 1)
        splitter.setHandleWidth(0)

        # Thêm splitter vào layout chính
        main_layout.addWidget(splitter)

        # Footer (hiện đường dẫn file XML)
        self.footer_label = QLabel("Check XML Boardhistory by DVA")
        self.footer_label.setStyleSheet("""
            QLabel {
                color: #1976d2;
                font-weight: bold;
                font-size: 13px;
                border-top: 1px solid #90caf9;
                padding: 5px 20px;
                font-style: italic;
                letter-spacing: 0.5px;
            }
        """)
        self.footer_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)  # Căn phải và giữa theo chiều dọc
        main_layout.addWidget(self.footer_label)

        self.setCentralWidget(main_widget)

        # Thêm các biến để lưu trữ dữ liệu đã phân tích
        self.xml_data = {}  # Dictionary lưu dữ liệu theo barcode
        self.current_barcode = None

    def set_table_column_ratio(self, table):
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        total_width = table.viewport().width()
        table.setColumnWidth(0, int(total_width * 0.35))
        table.setColumnWidth(1, int(total_width * 0.3))
        table.setColumnWidth(2, int(total_width * 0.35))

        # Ensure the ratio is maintained when resizing
        def resizeEvent(event):
            total_width = table.viewport().width()
            table.setColumnWidth(0, int(total_width * 0.35))
            table.setColumnWidth(1, int(total_width * 0.3))
            table.setColumnWidth(2, int(total_width * 0.35))
            QTableWidget.resizeEvent(table, event)
        table.resizeEvent = resizeEvent

    def create_pickup_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        table = QTableWidget()
        items = [
            ("Time", "", "取料动作发生的时间"),
            ("Machine_Name_SN", "", "设备名称及序列号"),
            ("Head", "", "取料头"),
            ("Segment", "", "料段"),
            ("Nozzle", "", "吸嘴编号"),
            ("Conponent", "", "元件名称"),
            ("Repick", "", "实际重复取料次数"),
            ("Feeder Location/Track", "", "料站"),
            ("Feeder Pitch", "", "Feeder步进距离(mm)"),
            ("Feed Time (ms)", "", "送料时间(ms)"),
            ("Z Move Down Profile", "", "Z轴下运动曲线：TP"),
            ("Z Move Up Profile", "", "Z轴上运动曲线：TP"),
            ("Dp Target Angle (degree)", "", "取料时，DP的目标角度"),
            ("Vacuum before pick", "", "取料前，吸嘴的真空值"),
            ("Vacuum after pick", "", "取料后，吸嘴的真空值"),
            ("Holding value", "", "当前保持值"),
            ("Pick ErrorInZ", "", "取料时，元件与贴片高度的误差"),
            ("Pick Stay Time (ms)", "", "取料时，吸嘴停留在取料位置的时间(ms)"),
            ("MeasureHeight (mm)", "", "元件厚度(mm)")
        ]
        table.setRowCount(len(items))
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Pickup_Process", "Pickup_Data", "Description"])
        table.setStyleSheet("""
            QTableWidget {
                border: none;
            }
            QTableWidget::item {
                padding: 4px 8px;
            }
        """)
        for row, (name, value, desc) in enumerate(items):
            table.setItem(row, 0, QTableWidgetItem(name))
            table.setItem(row, 1, QTableWidgetItem(value))
            table.setItem(row, 2, QTableWidgetItem(desc))
            if name == "Time":
                self.pickup_time_row = row
            if name == "Machine_Name_SN":
                self.pickup_machine_row = row
            if name == "Head":
                self.pickup_head_row = row  # Lưu lại vị trí dòng Head
            if name == "Segment":
                self.pickup_segment_row = row
            if name == "Nozzle":
                self.pickup_nozzle_row = row
            if name == "Conponent":
                self.pickup_conponent_row = row
            if name == "Repick":
                self.pickup_repick_row = row
            if name == "Feeder Location/Track":
                self.pickup_track_row = row
            if name == "Feeder Pitch":
                self.pickup_pitck_row = row
            if name == "Feed Time (ms)":
                self.pickup_feeder_time_row = row
            if name == "Z Move Down Profile":
                self.pickup_z_down_row = row
            if name == "Z Move Up Profile":
                self.pickup_z_up_row = row
            if name == "Dp Target Angle (degree)":
                self.pickup_dp_angle_row = row
            if name == "Vacuum before pick":
                self.pickup_vacuum_before_row = row
            if name == "Vacuum after pick":
                self.pickup_vacuum_after_row = row
            if name == "Holding value":
                self.pickup_holding_row = row
            if name == "Pick ErrorInZ":
                self.pickup_error_in_z_row = row
            if name == "Pick Stay Time (ms)":
                self.pickup_stay_time_row = row
            if name == "MeasureHeight (mm)":
                self.pickup_measure_height_row = row
        layout.addWidget(table)
        self.pickup_table = table  # Lưu lại table để cập nhật sau
        self.pickup_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.set_table_column_ratio(table)
        return widget

    def create_placement_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        table = QTableWidget()
        items = [
            ("Time", "", "贴片动作发生的时间"),
            ("Machine_Name_SN", "", "设备名称及序列号"),
            ("Lane NO.", "", "传送轨道"),
            ("Head", "", "贴片头"),
            ("Segment", "", "料段"),
            ("Nozzle", "", "吸嘴编号"),
            ("Conponent", "", "元件名称"),
            ("Measure Centering X", "", "元件实际吸取中心与理论中心的X距离"),
            ("Measure Centering Y", "", "元件实际吸取中心与理论中心的Y距离"),
            ("Measure Centering Angle (degree)", "", "元件实际吸取中心与理论中心的角度"),
            ("Theroy Size Length x Width x Thickness", "", "元件理论尺寸"),
            ("Actual Size Length x Width x Thickness", "", "元件实际尺寸"),
            ("Place ErrorInZ", "", "元件实际吸取贴片高度与理论高度的误差"),
            ("Place Z EndPosition", "", "元件实际贴片高度"),
            ("Z Move Down Profile", "", "Z轴下运动曲线：TP"),
            ("Z Move Up Profile", "", "Z轴上运动曲线：TP"),
            ("Vacuum before Place", "", "贴片前，吸嘴的真空值"),
            ("Vacuum after Place", "", "贴片后，吸嘴的真空值"),
            ("Holding", "", "当前保持值"),
            ("Airkiss in Pro", "", "Pro平台空气吹气"),
            ("Airkiss in Machine", "", "设备空气吹气"),
            ("Airkiss Measured", "", "空气吹气测量值"),
            ("Air Kiss Time (ms)", "", "空气吹气时间(ms)"),
            ("Place Stay Time (ms)", "", "贴片时，吸嘴停留在贴片位置的时间(ms)"),
            ("Place order in current machine", "", "当前设备贴片顺序"),
            ("Recipe", "", "程序名称")
        ]
        table.setRowCount(len(items))
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Place_Process", "Place_Data", "Description"])
        table.setStyleSheet("""
            QTableWidget {
                border: none;
            }
            QTableWidget::item {
                padding: 4px 8px;
            }
        """)
        for row, (name, value, desc) in enumerate(items):
            table.setItem(row, 0, QTableWidgetItem(name))
            table.setItem(row, 1, QTableWidgetItem(value))
            table.setItem(row, 2, QTableWidgetItem(desc))
            if name == "Time":
                self.placement_time_row = row
            if name == "Machine_Name_SN":
                self.placement_machine_row = row
            if name == "Lane NO.":
                self.placement_lane_row = row
            if name == "Head":
                self.placement_head_row = row  # Lưu lại vị trí dòng Head
            if name == "Segment":
                self.placement_segment_row = row
            if name == "Nozzle":
                self.placement_nozzle_row = row
            if name == "Conponent":
                self.placement_conponent_row = row
            if name == "Measure Centering X":
                self.placement_measure_x_row = row
            if name == "Measure Centering Y":
                self.placement_measure_y_row = row
            if name == "Measure Centering Angle (degree)":
                self.placement_measure_phi_row = row
            if name == "Theroy Size Length x Width x Thickness":
                self.placement_theroy_size_row = row
            if name == "Actual Size Length x Width x Thickness":
                self.placement_actual_size_row = row
            if name == "Place ErrorInZ":
                self.placement_error_in_z_row = row
            if name == "Place Z EndPosition":
                self.placement_z_end_row = row
            if name == "Z Move Down Profile":
                self.placement_z_down_row = row
            if name == "Z Move Up Profile":
                self.placement_z_up_row = row
            if name == "Vacuum before Place":
                self.placement_vacuum_before_row = row
            if name == "Vacuum after Place":
                self.placement_vacuum_after_row = row
            if name == "Holding":
                self.placement_holding_row = row
            if name == "Airkiss in Pro":
                self.placement_airkiss_pro_row = row
            if name == "Airkiss Measured":
                self.placement_airkiss_measured_row = row
            if name == "Air Kiss Time (ms)":
                self.placement_airkiss_time_row = row
            if name == "Airkiss in Machine":
                self.placement_airkiss_machine_row = row
            if name == "Place Stay Time (ms)":
                self.placement_stay_time_row = row
            if name == "Place order in current machine":
                self.placement_order_current_machine_row = row
            if name == "Recipe":
                self.placement_recipe_row = row
        layout.addWidget(table)
        self.placement_table = table  # Lưu lại table để cập nhật sau
        self.placement_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.set_table_column_ratio(table)
        return widget

    def create_find_board_panel(self):
        group = QGroupBox()
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Định nghĩa các hàm filter trước
        def filter_barcode_list(text):
            self.barcode_list.clear()
            for item in self.barcode_items:
                if text.lower() in item.lower():
                    self.barcode_list.addItem(item)

        def filter_ref_list(text):
            self.ref_list.clear()
            for item in self.ref_items:
                if text.lower() in item.lower():
                    self.ref_list.addItem(item)

        def filter_panel_list(text):
            self.panel_list.clear()
            for item in self.panel_items:
                if text.lower() in item.lower():
                    self.panel_list.addItem(item)

        # Thêm nút Import Board (xml)
        import_btn = QPushButton("Import Board (xml)")
        import_btn.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                font-size: 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e3f2fd, stop:1 #90caf9);
                border: 1px solid #64b5f6;
                border-radius: 6px;
                padding: 8px 0;
                height: 60px;
            }
            QPushButton:hover {
                background: #bbdefb;
            }
        """)
        layout.addWidget(import_btn)

        # Thêm các thuộc tính vào self
        self.barcode_items = []
        self.ref_items = []
        self.panel_items = []

        # Barcode (filter)
        layout.addWidget(QLabel("Barcode (filter)"))
        self.barcode_filter = QLineEdit()
        self.barcode_filter.setStyleSheet("background: #f5f5f5; border-radius: 4px; padding: 4px; border: 1px solid #64b5f6;")
        self.barcode_filter.setEnabled(False)
        layout.addWidget(self.barcode_filter)
        self.barcode_filter.textChanged.connect(filter_barcode_list)  # Kết nối signal sau khi đã định nghĩa hàm

        # Barcode list
        self.barcode_list = QListWidget()
        self.barcode_list.setStyleSheet("""
            QListWidget {
                background: #ffffff;
                border: 1px solid #90caf9;
                border-radius: 4px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 4px;
            }
            QListWidget::item:selected {
                background: #e3f2fd;
                color: #1565c0;
            }
        """)
        layout.addWidget(self.barcode_list)

        # Ref (filter)
        layout.addWidget(QLabel("Ref (filter)"))
        self.ref_filter = QLineEdit()
        self.ref_filter.setStyleSheet("background: #f5f5f5; border-radius: 4px; padding: 4px; border: 1px solid #64b5f6;")
        self.ref_filter.setEnabled(False)
        layout.addWidget(self.ref_filter)
        self.ref_filter.textChanged.connect(filter_ref_list)  # Kết nối signal sau khi đã định nghĩa hàm

        # Ref list
        self.ref_list = QListWidget()
        self.ref_list.setStyleSheet(self.barcode_list.styleSheet())
        layout.addWidget(self.ref_list)

        # Panel (filter)
        layout.addWidget(QLabel("Panel (filter)"))
        self.panel_filter = QLineEdit()
        self.panel_filter.setStyleSheet("background: #f5f5f5; border-radius: 4px; padding: 4px; border: 1px solid #64b5f6;")
        self.panel_filter.setEnabled(False)
        layout.addWidget(self.panel_filter)
        self.panel_filter.textChanged.connect(filter_panel_list)  # Kết nối signal sau khi đã định nghĩa hàm

        # Panel list
        self.panel_list = QListWidget()
        self.panel_list.setStyleSheet(self.barcode_list.styleSheet())
        layout.addWidget(self.panel_list)

        # Kết nối signals cho filters
        self.barcode_filter.textChanged.connect(filter_barcode_list)
        self.ref_filter.textChanged.connect(filter_ref_list) 
        self.panel_filter.textChanged.connect(filter_panel_list)

        # Các hàm filter sử dụng self
        def filter_barcode_list(text):
            self.barcode_list.clear()
            for item in self.barcode_items:
                if text.lower() in item.lower():
                    self.barcode_list.addItem(item)

        def filter_ref_list(text):
            self.ref_list.clear()
            for item in self.ref_items:
                if text.lower() in item.lower():
                    self.ref_list.addItem(item)

        def filter_panel_list(text):
            self.panel_list.clear()
            for item in self.panel_items:
                if text.lower() in item.lower():
                    self.panel_list.addItem(item)

        # Thêm hàm kiểm tra và cập nhật trạng thái filter
        def update_filter_states():
            self.barcode_filter.setEnabled(len(self.barcode_items) > 0)
            self.ref_filter.setEnabled(len(self.ref_items) > 0)
            self.panel_filter.setEnabled(len(self.panel_items) > 0)

        # Cập nhật khi import file
        def import_xml():
            # Cho phép chọn nhiều file XML
            files, _ = QFileDialog.getOpenFileNames(
                group,
                "Select XML Files",
                "",
                "XML Files (*.xml)"
            )
            
            if files:
                for file_path in files:
                    try:
                        tree = ET.parse(file_path)
                        root = tree.getroot()
                        
                        # Lấy barcode và ID từ file XML
                        barcode = root.findtext(".//Barcode", "")
                        board_id = root.findtext(".//Id", "")
                        
                        if not barcode or not board_id:
                            continue

                        # Tạo key unique từ ID và barcode
                        unique_key = f"{board_id}___{barcode}"
                        
                        # Kiểm tra nếu đã tồn tại
                        if unique_key in self.barcode_items:
                            continue
                        
                        # Thêm vào danh sách nếu chưa tồn tại
                        self.barcode_items.append(unique_key)
                        self.xml_files.append(file_path)
                        self.xml_roots.append(root)
                        
                        # Cập nhật barcode_list
                        self.barcode_list.clear()
                        self.barcode_list.addItems(self.barcode_items)
        

                    except Exception as e:
                        QMessageBox.critical(
                            self,
                            "Error",
                            f"Error reading XML file {file_path}:\n{e}"
                        )
            update_filter_states()

        def on_barcode_selected(index):
            """Xử lý khi chọn barcode"""
            if index >= 0 and index < len(self.xml_roots):
                # Reset filter content first
                self.barcode_filter.clear()
                self.ref_filter.clear() 
                self.panel_filter.clear()

                # Cập nhật xml_root theo barcode được chọn 
                self.xml_root = self.xml_roots[index]
                root = self.xml_root

                # Lấy các thông tin cơ bản
                time_node = root.find(".//BoardHistory/CreationTime")
                machine_node = root.find(".//MachineId")  
                head_node = root.find(".//PlaceHeads/PlaceHead/GantryId")
                lane_node = root.find(".//Lane")

                # Cập nhật bảng Pickup
                if hasattr(self, "pickup_table"):
                    if time_node is not None:
                        self.pickup_table.setItem(self.pickup_time_row, 1, 
                            QTableWidgetItem(time_node.text))
                    if machine_node is not None:
                        self.pickup_table.setItem(self.pickup_machine_row, 1,
                            QTableWidgetItem(machine_node.text))
                    if head_node is not None:
                        self.pickup_table.setItem(self.pickup_head_row, 1,
                            QTableWidgetItem(head_node.text))

                # Cập nhật bảng Placement
                if hasattr(self, "placement_table"):
                    if time_node is not None:
                        self.placement_table.setItem(self.placement_time_row, 1,
                            QTableWidgetItem(time_node.text))
                    if machine_node is not None:
                        self.placement_table.setItem(self.placement_machine_row, 1,
                            QTableWidgetItem(machine_node.text))
                    if lane_node is not None:
                        self.placement_table.setItem(self.placement_lane_row, 1,
                            QTableWidgetItem(lane_node.text))
                    if head_node is not None:
                        self.placement_table.setItem(self.placement_head_row, 1,
                            QTableWidgetItem(head_node.text))

                # Cập nhật ref_mapping và panel_mapping
                self.ref_items = []
                self.panel_items = []
                self.ref_mapping = {}
                self.panel_mapping = {}

                # Cập nhật ref_mapping
                for pos_node in root.findall(".//PlacePositions/PlacePosition"):
                    name_node = pos_node.find("Name")
                    id_attr = pos_node.get("Id")
                    if name_node is not None and name_node.text and id_attr:
                        self.ref_mapping.setdefault(name_node.text, []).append(id_attr)
                        if name_node.text not in self.ref_items:
                            self.ref_items.append(name_node.text)

                # Cập nhật panel_mapping
                for child_img_node in root.findall(".//SubBoards/SubBoard/ChildImage/ChildImages/ChildImage/ChildImages/ChildImage"):
                    name_node = child_img_node.find("Name")
                    pos_nodes = child_img_node.findall("PlacePositions/PlacePosition")
                    for pos_node in pos_nodes:
                        id_attr = pos_node.get("Id")
                        if name_node is not None and name_node.text and id_attr:
                            self.panel_mapping.setdefault(name_node.text, []).append(id_attr)
                            if name_node.text not in self.panel_items:
                                self.panel_items.append(name_node.text)

                # Cập nhật UI
                self.ref_list.clear()
                self.ref_list.addItems(self.ref_items)
                self.panel_list.clear()
                self.panel_list.addItems(self.panel_items)
                
                # Cập nhật trạng thái filter
                self.barcode_filter.setEnabled(len(self.barcode_items) > 0)
                self.ref_filter.setEnabled(len(self.ref_items) > 0)
                self.panel_filter.setEnabled(len(self.panel_items) > 0)

            update_filter_states()

        # Kết nối signals
        import_btn.clicked.connect(import_xml)
        self.barcode_list.currentRowChanged.connect(on_barcode_selected)
        self.ref_list.itemSelectionChanged.connect(self.show_data_for_selection)
        self.panel_list.itemSelectionChanged.connect(self.show_data_for_selection)

        # Thêm context menu cho barcode_list
        self.barcode_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.barcode_list.customContextMenuRequested.connect(self.show_barcode_context_menu)

        # Khai báo mapping ở self để dùng lại
        self.ref_mapping = {}
        self.panel_mapping = {}
        self.xml_root = None

        # Thay đổi khai báo biến để lưu trữ nhiều file XML
        self.xml_files = []  # Lưu đường dẫn các file
        self.xml_roots = []  # Lưu XML root của các file
        self.barcode_items = [] # Lưu danh sách barcode
        self.current_xml_index = -1 # Index của file XML hiện tại

        
        # Stretch to fill
        layout.addStretch()
        return group

    def clear_pickup_placement_tables(self):
        """Xóa dữ liệu trong cột Data của bảng Pickup và Placement"""
        # Xóa cột Pickup_Data (cột 1)
        if hasattr(self, "pickup_table"):
            for row in range(self.pickup_table.rowCount()):
                self.pickup_table.setItem(row, 1, QTableWidgetItem(""))
                
        # Xóa cột Place_Data (cột 1)
        if hasattr(self, "placement_table"):
            for row in range(self.placement_table.rowCount()):
                self.placement_table.setItem(row, 1, QTableWidgetItem(""))

    def show_data_for_selection(self):
        """Hiển thị dữ liệu Pickup/Placement khi chọn ref và panel"""
        ref_name = self.ref_list.currentItem().text() if self.ref_list.currentItem() else None
        panel_name = self.panel_list.currentItem().text() if self.panel_list.currentItem() else None
        
        if not ref_name or not panel_name or self.xml_root is None:
            return

        ref_ids = self.ref_mapping.get(ref_name, [])
        panel_ids = self.panel_mapping.get(panel_name, [])
        matched_ids = set(ref_ids) & set(panel_ids)

        # Khởi tạo giá trị rỗng cho dữ liệu
        pickup_data = {
            "segment": "", "nozzle": "", "conponent": "", "repick": "", 
            "pickup_track_row": "", "feeder_pitch": "", "error_in_z": "",
            "z_down": "", "z_up": "", "dp_angle": "", "vacuum_before": "",
            "vacuum_after": "", "holding": "", "measure_height": ""
        }
        
        placement_data = {
            "segment": "", "nozzle": "", "conponent": "", "measure_x": "",
            "measure_y": "", "measure_phi": "", "theroy_thickness": "",
            "actual_thickness": "", "error_in_z": "", "z_end": "",
            "z_down_profile": "", "z_up_profile": "", "vacuum_before_place": "",
            "vacuum_after_place": "", "holding": "", "airkiss_pro": "",
            "airkiss_machine": "", "airkiss_measured": "", "recipe": ""
        }

        # Tìm node khớp trong XML hiện tại
        for matched_id in matched_ids:
            pos_node = self.xml_root.find(f".//PlacePositions/PlacePosition[@Id='{matched_id}']")
            if pos_node is not None:
                component_node = pos_node.find("Component")
                if component_node is not None:
                    # Lấy dữ liệu pickup
                    pickup_data["segment"] = component_node.findtext("Segment", "")
                    pickup_data["nozzle"] = component_node.findtext("Nozzle", "")
                    # Xử lý component name từ VisionDump
                    raw_conponent = component_node.findtext("Measure/VisionDump", "")
                    if raw_conponent:
                        parts = raw_conponent.split("_", 6)
                        if len(parts) >= 7:
                            value = parts[6].replace(".svdmp", "")
                            pickup_data["conponent"] = value
                            placement_data["conponent"] = value
                    pickup_data["repick"] = component_node.findtext("RetryCount", "")
                    pickup_data["pickup_track_row"] = component_node.findtext("Pick/FeederData/locationKey", "")
                    pickup_data["feeder_pitch"] = component_node.findtext("Pick/FeederData/pitch", "")
                    pickup_data["z_down"] = component_node.findtext("Pick/ZMovementDown/TravelProfile", "")
                    pickup_data["z_up"] = component_node.findtext("Pick/ZMovementUp/TravelProfile", "")
                    pickup_data["dp_angle"] = component_node.findtext("Pick/DpMovement/TargetPosition", "")
                    pickup_data["vacuum_before"] = component_node.findtext("Pick/VacuumSystem/MeasuredBefore", "")
                    pickup_data["vacuum_after"] = component_node.findtext("Pick/VacuumSystem/MeasuredAfter", "")
                    pickup_data["holding"] = component_node.findtext("Pick/VacuumSystem/HoldingCircuit", "")
                    pickup_data["measure_height"] = component_node.findtext("Pick/FeederData/ComponentHeight", "")

                    # Lấy dữ liệu placement
                    placement_data["segment"] = component_node.findtext("Segment", "")
                    placement_data["nozzle"] = component_node.findtext("Nozzle", "")
                    placement_data["measure_x"] = component_node.findtext("Measure/MeasuredPose/Y", "")
                    placement_data["measure_y"] = component_node.findtext("Measure/MeasuredPose/X", "")
                    placement_data["measure_phi"] = component_node.findtext("Measure/MeasuredPose/Phi", "")
                    placement_data["theroy_thickness"] = component_node.findtext("FilteredHeight", "")
                    placement_data["actual_thickness"] = component_node.findtext("Pick/ComponentSensor/MeasuredHeight", "")
                    placement_data["error_in_z"] = pos_node.findtext("ErrorInZ", "")
                    placement_data["z_end"] = component_node.findtext("Place/ZMovementDown/EndPosition", "")
                    placement_data["z_down_profile"] = component_node.findtext("Place/ZMovementDown/TravelProfile", "")
                    placement_data["z_up_profile"] = component_node.findtext("Place/ZMovementUp/TravelProfile", "")
                    placement_data["vacuum_before_place"] = component_node.findtext("Place/VacuumSystem/MeasuredBefore", "")
                    placement_data["vacuum_after_place"] = component_node.findtext("Place/VacuumSystem/MeasuredAfter", "")
                    placement_data["holding"] = component_node.findtext("Pick/VacuumSystem/HoldingCircuit", "")
                    placement_data["airkiss_pro"] = component_node.findtext("Place/VacuumSystem/ParamDown", "")
                    placement_data["airkiss_machine"] = component_node.findtext("Place/VacuumSystem/ParamThresholdDown", "")
                    placement_data["airkiss_measured"] = component_node.findtext("Place/VacuumSystem/MeasuredDown", "")
                    
                    recipe_node = self.xml_root.find(".//Recipe")
                    placement_data["recipe"] = recipe_node.text if recipe_node is not None else ""
                    break

        # Cập nhật bảng Pickup
        if hasattr(self, "pickup_table"):
            self.pickup_table.setItem(self.pickup_segment_row, 1, QTableWidgetItem(pickup_data["segment"]))
            self.pickup_table.setItem(self.pickup_nozzle_row, 1, QTableWidgetItem(pickup_data["nozzle"]))
            self.pickup_table.setItem(self.pickup_conponent_row, 1, QTableWidgetItem(pickup_data["conponent"]))
            self.pickup_table.setItem(self.pickup_repick_row, 1, QTableWidgetItem(pickup_data["repick"]))
            
            # Xử lý track value
            track_value = pickup_data["pickup_track_row"]
            if track_value and len(track_value) >= 4:
                track_value = track_value[2:4]
            self.pickup_table.setItem(self.pickup_track_row, 1, QTableWidgetItem(track_value))
            
            self.pickup_table.setItem(self.pickup_pitck_row, 1, QTableWidgetItem(pickup_data["feeder_pitch"]))
            self.pickup_table.setItem(self.pickup_z_down_row, 1, QTableWidgetItem(pickup_data["z_down"]))
            self.pickup_table.setItem(self.pickup_z_up_row, 1, QTableWidgetItem(pickup_data["z_up"]))
            self.pickup_table.setItem(self.pickup_dp_angle_row, 1, QTableWidgetItem(pickup_data["dp_angle"]))
            self.pickup_table.setItem(self.pickup_vacuum_before_row, 1, QTableWidgetItem(pickup_data["vacuum_before"]))
            self.pickup_table.setItem(self.pickup_vacuum_after_row, 1, QTableWidgetItem(pickup_data["vacuum_after"]))
            self.pickup_table.setItem(self.pickup_holding_row, 1, QTableWidgetItem(pickup_data["holding"]))
            self.pickup_table.setItem(self.pickup_measure_height_row, 1, QTableWidgetItem(pickup_data["measure_height"]))

        # Cập nhật bảng Placement  
        if hasattr(self, "placement_table"):
            self.placement_table.setItem(self.placement_segment_row, 1, QTableWidgetItem(placement_data["segment"]))
            self.placement_table.setItem(self.placement_nozzle_row, 1, QTableWidgetItem(placement_data["nozzle"]))
            self.placement_table.setItem(self.placement_conponent_row, 1, QTableWidgetItem(placement_data["conponent"]))
            self.placement_table.setItem(self.placement_measure_x_row, 1, QTableWidgetItem(placement_data["measure_x"]))
            self.placement_table.setItem(self.placement_measure_y_row, 1, QTableWidgetItem(placement_data["measure_y"]))
            self.placement_table.setItem(self.placement_measure_phi_row, 1, QTableWidgetItem(placement_data["measure_phi"]))
            self.placement_table.setItem(self.placement_theroy_size_row, 1, QTableWidgetItem(placement_data["theroy_thickness"]))
            self.placement_table.setItem(self.placement_actual_size_row, 1, QTableWidgetItem(placement_data["actual_thickness"]))
            self.placement_table.setItem(self.placement_error_in_z_row, 1, QTableWidgetItem(placement_data["error_in_z"]))
            self.placement_table.setItem(self.placement_z_end_row, 1, QTableWidgetItem(placement_data["z_end"]))
            self.placement_table.setItem(self.placement_z_down_row, 1, QTableWidgetItem(placement_data["z_down_profile"]))
            self.placement_table.setItem(self.placement_z_up_row, 1, QTableWidgetItem(placement_data["z_up_profile"]))
            self.placement_table.setItem(self.placement_vacuum_before_row, 1, QTableWidgetItem(placement_data["vacuum_before_place"]))
            self.placement_table.setItem(self.placement_vacuum_after_row, 1, QTableWidgetItem(placement_data["vacuum_after_place"]))
            self.placement_table.setItem(self.placement_holding_row, 1, QTableWidgetItem(placement_data["holding"]))
            self.placement_table.setItem(self.placement_airkiss_pro_row, 1, QTableWidgetItem(placement_data["airkiss_pro"]))
            self.placement_table.setItem(self.placement_airkiss_machine_row, 1, QTableWidgetItem(placement_data["airkiss_machine"]))
            self.placement_table.setItem(self.placement_airkiss_measured_row, 1, QTableWidgetItem(placement_data["airkiss_measured"]))
            self.placement_table.setItem(self.placement_recipe_row, 1, QTableWidgetItem(placement_data["recipe"]))

    def import_xml(self):
        """Import và phân tích file XML"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select XML Files",
            "",
            "XML Files (*.xml)"
        )
        
        if files:
            for file_path in files:
                try:
                    tree = ET.parse(file_path)
                    root = tree.getroot()
                    
                    # Lấy barcode và ID từ file XML
                    barcode = root.findtext(".//Barcode", "")
                    board_id = root.findtext(".//Id", "")
                    
                    if not barcode or not board_id:
                        continue

                    # Tạo key unique từ ID và barcode
                    unique_key = f"{board_id}___{barcode}"
                    
                    # Kiểm tra nếu đã tồn tại
                    if unique_key in self.barcode_items:
                        QMessageBox.warning(
                            self,
                            "Warning",
                            f"File với Barcode {barcode} và ID {board_id} đã tồn tại!"
                        )
                        continue
                    
                    # Thêm vào danh sách nếu chưa tồn tại
                    self.barcode_items.append(unique_key)
                    self.xml_files.append(file_path)
                    self.xml_roots.append(root)
                    
                    # Cập nhật barcode_list
                    self.barcode_list.clear()
                    self.barcode_list.addItems(self.barcode_items)
                    
                    # Cập nhật đường dẫn file
                    self.footer_label.setText(f"Path: {', '.join(self.xml_files)}")

                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Error reading XML file {file_path}:\n{e}"
                    )

        # Reset các list và bảng
        self.ref_list.clear()
        self.panel_list.clear() 
        self.clear_pickup_placement_tables()

    def show_barcode_context_menu(self, position):
        """Hiển thị context menu khi click chuột phải vào barcode_list"""
        menu = QMenu()
        
        # Thêm action xóa item đang chọn
        delete_action = None
        current_item = self.barcode_list.currentItem()
        if current_item:
            delete_action = menu.addAction("Delete Selected Item")
        
        # Thêm action xóa tất cả
        clear_all_action = None
        if self.barcode_list.count() > 0:
            clear_all_action = menu.addAction("Delete All Items")
        
        # Hiện context menu
        action = menu.exec_(self.barcode_list.mapToGlobal(position))
        
        if action:
            if action == delete_action:
                current_row = self.barcode_list.currentRow()
                if current_row >= 0:
                    # Xóa khỏi các danh sách
                    self.barcode_items.pop(current_row)
                    self.xml_files.pop(current_row)
                    self.xml_roots.pop(current_row)
                    
                    # Xóa khỏi UI
                    self.barcode_list.takeItem(current_row)
                    
                    # Reset các list và bảng
                    self.ref_list.clear()
                    self.panel_list.clear()
                    self.clear_pickup_placement_tables()
                    
                    # Cập nhật đường dẫn file và chọn item mới
                    if self.xml_files:
                        self.footer_label.setText(f"Path: {', '.join(self.xml_files)}")
                        
                        # Xác định row mới để chọn
                        new_row = min(current_row, self.barcode_list.count() - 1)
                        
                        # Cập nhật xml_root và chọn item mới
                        if new_row >= 0:
                            self.xml_root = self.xml_roots[new_row]
                            self.barcode_list.setCurrentRow(new_row)  # Trigger currentRowChanged
                            
                            # Cập nhật dữ liệu cho item mới được chọn
                            root = self.xml_root
                            time_node = root.find(".//BoardHistory/CreationTime")
                            machine_node = root.find(".//MachineId")
                            head_node = root.find(".//PlaceHeads/PlaceHead")
                            lane_node = root.find(".//Lane")

                            # Cập nhật bảng Pickup
                            if hasattr(self, "pickup_table"):
                                if time_node is not None:
                                    self.pickup_table.setItem(self.pickup_time_row, 1, 
                                        QTableWidgetItem(time_node.text))
                                if machine_node is not None:
                                    self.pickup_table.setItem(self.pickup_machine_row, 1,
                                        QTableWidgetItem(machine_node.text))
                                if head_node is not None:
                                    self.pickup_table.setItem(self.pickup_head_row, 1,
                                        QTableWidgetItem(head_node.get("Id")))

                            # Cập nhật bảng Placement
                            if hasattr(self, "placement_table"):
                                if time_node is not None:
                                    self.placement_table.setItem(self.placement_time_row, 1,
                                        QTableWidgetItem(time_node.text))
                                if machine_node is not None:
                                    self.placement_table.setItem(self.placement_machine_row, 1,
                                        QTableWidgetItem(machine_node.text))
                                if lane_node is not None:
                                    self.placement_table.setItem(self.placement_lane_row, 1,
                                        QTableWidgetItem(lane_node.text))
                                if head_node is not None:
                                    self.placement_table.setItem(self.placement_head_row, 1,
                                        QTableWidgetItem(head_node.get("Id")))

                            # Cập nhật ref và panel mapping
                            self.update_ref_panel_mapping(root)
                    else:
                        self.footer_label.setText("by DVA")
                        self.xml_root = None

            elif action == clear_all_action:
                # Xóa tất cả items
                self.barcode_items.clear()
                self.xml_files.clear()
                self.xml_roots.clear()
                self.xml_root = None  # Reset xml_root
                if hasattr(self, 'xml_data'):
                    self.xml_data.clear()
            
                # Xóa khỏi UI
                self.barcode_list.clear()
                self.ref_list.clear()
                self.panel_list.clear()
                self.clear_pickup_placement_tables()
                
                # Reset footer
                self.footer_label.setText("by DVA")

    def update_ref_panel_mapping(self, root):
        """Cập nhật ref và panel mapping từ XML root"""
        self.ref_items = []
        self.panel_items = []
        self.ref_mapping = {}
        self.panel_mapping = {}

        # Cập nhật ref_mapping
        for pos_node in root.findall(".//PlacePositions/PlacePosition"):
            name_node = pos_node.find("Name")
            id_attr = pos_node.get("Id")
            if name_node is not None and name_node.text and id_attr:
                self.ref_mapping.setdefault(name_node.text, []).append(id_attr)
                if name_node.text not in self.ref_items:
                    self.ref_items.append(name_node.text)

        # Cập nhật panel_mapping
        for child_img_node in root.findall(".//SubBoards/SubBoard/ChildImage/ChildImages/ChildImage/ChildImages/ChildImage"):
            name_node = child_img_node.find("Name")
            pos_nodes = child_img_node.findall("PlacePositions/PlacePosition")
            for pos_node in pos_nodes:
                id_attr = pos_node.get("Id")
                if name_node is not None and name_node.text and id_attr:
                    self.panel_mapping.setdefault(name_node.text, []).append(id_attr)
                    if name_node.text not in self.panel_items:
                        self.panel_items.append(name_node.text)

        # Cập nhật UI
        self.ref_list.clear()
        self.ref_list.addItems(self.ref_items)
        self.panel_list.clear()
        self.panel_list.addItems(self.panel_items)