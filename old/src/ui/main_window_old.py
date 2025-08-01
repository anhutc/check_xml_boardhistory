from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QGroupBox, QLabel, QPushButton, QLineEdit,
    QListWidget, QSplitter, QHeaderView, QFileDialog, QApplication
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
                margin-right: 2px;
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
        self.footer_label = QLabel("Path: No XML file selected yet")
        self.footer_label.setStyleSheet("""
            QLabel {
                color: #1976d2;
                font-weight: bold;
                font-size: 13px;
                border-top: 1px solid #90caf9;
                padding: 0 20px;
                font-style: italic;
                letter-spacing: 0.5px;
            }
        """)
        main_layout.addWidget(self.footer_label)

        self.setCentralWidget(main_widget)

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

        # Nút Import Board (xml)
        import_btn = QPushButton("Import Board (xml)")
        import_btn.setCursor(Qt.PointingHandCursor)
        import_btn.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                font-size: 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e3f2fd, stop:1 #90caf9);
                border: 1px solid #64b5f6;
                border-radius: 6px;
                padding: 50px 10px;
            }
            QPushButton:hover {
                background: #bbdefb;
            }
        """)
        layout.addWidget(import_btn)
        

        # Barcode value
        barcode_value = QLineEdit()
        barcode_value.setText("")
        barcode_value.setReadOnly(True)
        barcode_value.setStyleSheet("background: #f5f5f5; border-radius: 4px; padding: 4px; border: 1px solid #64b5f6;")
        layout.addWidget(QLabel("Barcode"))
        layout.addWidget(barcode_value)

        # Ref (filter)
        layout.addWidget(QLabel("Ref (filter)"))
        ref_filter = QLineEdit()
        ref_filter.setStyleSheet("background: #f5f5f5; border-radius: 4px; padding: 4px; border: 1px solid #64b5f6;")
        layout.addWidget(ref_filter)
        ref_list = QListWidget()
        ref_list.setMinimumHeight(80)
        ref_list.setStyleSheet("background: #fff; border: 1px solid #b3d7ff; border-radius: 4px; border: 1px solid #64b5f6;")
        ref_items = []
        ref_list.addItems(ref_items)
        layout.addWidget(ref_list)

        # Lọc ref_list theo ref_filter
        def filter_ref_list(text):
            ref_list.clear()
            for item in ref_items:
                if text.lower() in item.lower():
                    ref_list.addItem(item)
        ref_filter.textChanged.connect(filter_ref_list)

        # Panel (filter)
        layout.addWidget(QLabel("Panel (filter)"))
        panel_filter = QLineEdit()
        panel_filter.setStyleSheet("background: #f5f5f5; border-radius: 4px; padding: 4px; border: 1px solid #64b5f6;")
        layout.addWidget(panel_filter)
        panel_list = QListWidget()
        panel_list.setMinimumHeight(80)
        panel_list.setStyleSheet("background: #fff; border: 1px solid #b3d7ff; border-radius: 4px; border: 1px solid #64b5f6;")
        panel_items = []
        panel_list.addItems(panel_items)
        layout.addWidget(panel_list)

        # Lọc panel_list theo panel_filter
        def filter_panel_list(text):
            panel_list.clear()
            for item in panel_items:
                if text.lower() in item.lower():
                    panel_list.addItem(item)
        panel_filter.textChanged.connect(filter_panel_list)

        # --- Giới thiệu tác giả ---
        author_label = QLabel(
            "<b>Create by</b><br><br>"
            "<span style='color:#1976d2;'>Deng WenYing</span><br><br>"
            "<a href='https://anhutc.github.io'>anhutc.github.io</a>"
        )
        author_label.setOpenExternalLinks(True)
        author_label.setAlignment(Qt.AlignCenter)
        author_label.setWordWrap(True)
        author_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e3f2fd, stop:1 #bbdefb);
                border: 1px solid #90caf9;
                border-radius: 10px;
                color: #1565c0;
                font-size: 14px;
                margin-top: 18px;
                margin-bottom: 10px;
                padding: 14px 8px 14px 8px;
                font-weight: bold;
                letter-spacing: 0.5px;
                box-shadow: 0 2px 8px rgba(90,180,255,0.08);
            }
            a { color: #388e3c; text-decoration: none; }
            a:hover { text-decoration: underline; }
        """)
        layout.addWidget(author_label)

        # Khai báo mapping ở self để dùng lại
        self.ref_mapping = {}
        self.panel_mapping = {}
        self.xml_root = None

        # Xử lý chọn file xml
        def import_xml():
            file_path, _ = QFileDialog.getOpenFileName(group, "Select file XML", "", "XML Files (*.xml)")
            if file_path:
                try:
                    tree = ET.parse(file_path)
                    root = tree.getroot()
                    self.xml_root = root

                    # Tạo mapping sau khi đã có root
                    self.ref_mapping = {}    # Name -> list of Id
                    for pos_node in root.findall(".//PlacePositions/PlacePosition"):
                        name_node = pos_node.find("Name")
                        id_attr = pos_node.get("Id")
                        if name_node is not None and name_node.text and id_attr:
                            self.ref_mapping.setdefault(name_node.text, []).append(id_attr)

                    self.panel_mapping = {}  # Name -> list of Id
                    for child_img_node in root.findall(".//SubBoards/SubBoard/ChildImage/ChildImages/ChildImage/ChildImages/ChildImage"):
                        name_node = child_img_node.find("Name")
                        pos_nodes = child_img_node.findall("PlacePositions/PlacePosition")
                        for pos_node in pos_nodes:
                            id_attr = pos_node.get("Id")
                            if name_node is not None and name_node.text and id_attr:
                                self.panel_mapping.setdefault(name_node.text, []).append(id_attr)

                    # Lấy giá trị của node Barcode
                    barcode_node = root.find(".//Barcode")
                    if barcode_node is not None:
                        barcode_value.setText(barcode_node.text)
                    else:
                        barcode_value.setText("")
                    # Lấy toàn bộ /PlacePositions/PlacePosition/Name, loại trùng lặp
                    ref_items.clear()
                    ref_id_map = {}  # Name -> Id
                    unique_names = set()
                    for pos_node in root.findall(".//PlacePositions/PlacePosition"):
                        name_node = pos_node.find("Name")
                        id_attr = pos_node.get("Id")
                        if name_node is not None and name_node.text and name_node.text not in unique_names:
                            unique_names.add(name_node.text)
                            ref_items.append(name_node.text)
                            ref_id_map[name_node.text] = id_attr
                    filter_ref_list(ref_filter.text())  # Cập nhật lại ref_list theo filter hiện tại

                    # Lấy toàn bộ /SubBoards/SubBoard/ChildImage/ChildImages/ChildImage/ChildImages/ChildImage, loại trùng lặp
                    panel_items.clear()
                    panel_id_map = {}  # Name -> Id
                    unique_panels = set()
                    for child_img_node in root.findall(".//SubBoards/SubBoard/ChildImage/ChildImages/ChildImage/ChildImages/ChildImage"):
                        name_node = child_img_node.find("Name")
                        pos_node = child_img_node.find("PlacePositions/PlacePosition")
                        id_attr = pos_node.get("Id") if pos_node is not None else None
                        if name_node is not None and name_node.text and name_node.text not in unique_panels:
                            unique_panels.add(name_node.text)
                            panel_items.append(name_node.text)
                            panel_id_map[name_node.text] = id_attr
                    filter_panel_list(panel_filter.text())  # Cập nhật lại panel_list theo filter hiện tại


                    ######### # Cập nhật các giá trị vào bảng Pickup

                    # Lấy giá trị Time
                    end_picking_node = root.find(".//BoardHistory/ProcessingHistory/ProcessingPosition/EndPicking")
                    if end_picking_node is not None and hasattr(self, "pickup_table") and hasattr(self, "pickup_time_row"):
                        self.pickup_table.setItem(self.pickup_time_row, 1, QTableWidgetItem(end_picking_node.text or ""))

                    # Lấy giá trị MachineId
                    machine_id_node = root.find(".//MachineId")
                    if machine_id_node is not None and hasattr(self, "pickup_table") and hasattr(self, "pickup_machine_row"):
                        self.pickup_table.setItem(self.pickup_machine_row, 1, QTableWidgetItem(machine_id_node.text or ""))
                    if machine_id_node is not None and hasattr(self, "placement_table") and hasattr(self, "placement_machine_row"):
                        self.placement_table.setItem(self.placement_machine_row, 1, QTableWidgetItem(machine_id_node.text or ""))

                    # Lấy giá trị GantryId
                    gantry_id_node = root.find(".//PlaceHeads/PlaceHead/GantryId")
                    if gantry_id_node is not None and hasattr(self, "pickup_table") and hasattr(self, "pickup_head_row"):
                        self.pickup_table.setItem(self.pickup_head_row, 1, QTableWidgetItem(gantry_id_node.text or ""))
                    if gantry_id_node is not None and hasattr(self, "placement_table") and hasattr(self, "placement_lane_row"):
                        self.placement_table.setItem(self.placement_lane_row, 1, QTableWidgetItem(gantry_id_node.text or ""))
                    if gantry_id_node is not None and hasattr(self, "placement_table") and hasattr(self, "placement_head_row"):
                        self.placement_table.setItem(self.placement_head_row, 1, QTableWidgetItem(gantry_id_node.text or ""))
                        
                    ###################################################################
                    ####### Cập nhật các giá trị vào bảng Placement
                    
                    # Lấy giá trị Time
                    end_placing_node = root.find(".//BoardHistory/ProcessingHistory/ProcessingPosition/EndPlacing")
                    if end_placing_node is not None and hasattr(self, "placement_table") and hasattr(self, "placement_time_row"):
                        self.placement_table.setItem(self.placement_time_row, 1, QTableWidgetItem(end_placing_node.text or ""))

                    #QMessageBox.information(group, "Success", "File import successful")
                    self.footer_label.setText(f"XML: {file_path}")  # Cập nhật đường dẫn file XML
                    self.footer_label.setStyleSheet("""
                    QLabel {
                        color: #28a745;
                        font-weight: bold;
                        font-size: 13px;
                        border-top: 1px solid #90caf9;
                        padding: 0 20px;
                        font-style: italic;
                        letter-spacing: 0.5px;
                    }
                """)
                except Exception as e:
                    self.footer_label.setText(f"XML: Error reading XML file")
                    self.footer_label.setStyleSheet("""
                    QLabel {
                        color: #dc3545;
                        font-weight: bold;
                        font-size: 13px;
                        border-top: 1px solid #90caf9;
                        padding: 0 20px;
                        font-style: italic;
                        letter-spacing: 0.5px;
                    }
                    """)
                    #QMessageBox.critical(group, "Error", f"Error reading XML file:\n{e}")

        def show_data_for_selection():
            ref_name = ref_list.currentItem().text() if ref_list.currentItem() else None
            panel_name = panel_list.currentItem().text() if panel_list.currentItem() else None
            if not ref_name or not panel_name or self.xml_root is None:
                return

            ref_ids = self.ref_mapping.get(ref_name, [])
            panel_ids = self.panel_mapping.get(panel_name, [])
            matched_ids = set(ref_ids) & set(panel_ids)

            # Khởi tạo giá trị rỗng
            pickup_data = {
                "segment": "", "nozzle": "", "conponent": "", "repick": "", "pickup_track_row": "", "feeder_pitch": "",
                "error_in_z": "", "z_down": "", "z_up": "", "dp_angle": "", "vacuum_before": "", "vacuum_after": "",
                "holding": "", "measure_height": ""
            }
            placement_data = {
                "segment": "", "nozzle": "", "conponent": "", "measure_x": "", "measure_y": "", "measure_phi": "",
                "theroy_thickness": "", "actual_thickness": "", "error_in_z": "", "z_end": "", "z_down_profile": "", "z_up_profile": "",
                "vacuum_before_place": "", "vacuum_after_place": "", "holding": "",
                "airkiss_pro": "", "airkiss_machine": "", "airkiss_measured": "", "recipe": ""
            }

            for matched_id in matched_ids:
                pos_node = self.xml_root.find(f".//PlacePositions/PlacePosition[@Id='{matched_id}']")
                if pos_node is not None:
                    component_node = pos_node.find("Component")
                    # Pickup data
                    if component_node is not None:
                        pickup_data["segment"] = component_node.findtext("Segment", "")
                        pickup_data["nozzle"] = component_node.findtext("Nozzle", "")
                        # Khi cập nhật giá trị cho pickup_data["conponent"] và placement_data["conponent"]
                        raw_conponent = component_node.findtext("Measure/VisionDump", "")
                        if raw_conponent:
                            parts = raw_conponent.split("_", 6)
                            if len(parts) >= 7:
                                value = parts[6]
                                # Nếu còn đuôi .svdmp thì loại bỏ luôn nếu muốn
                                if value.endswith(".svdmp"):
                                    value = value[:-6]
                                pickup_data["conponent"] = value
                                placement_data["conponent"] = value
                            else:
                                pickup_data["conponent"] = ""
                                placement_data["conponent"] = ""
                        else:
                            pickup_data["conponent"] = ""
                            placement_data["conponent"] = ""
                        pickup_data["repick"] = component_node.findtext("RetryCount", "")
                        pickup_data["pickup_track_row"] = component_node.findtext("Pick/FeederData/locationKey", "")
                        pickup_data["feeder_pitch"] = component_node.findtext("Pick/FeederData/pitch", "")
                        #pickup_data["error_in_z"] = pos_node.findtext("ErrorInZ", "")
                        pickup_data["z_down"] = component_node.findtext("Pick/ZMovementDown/TravelProfile", "")
                        pickup_data["z_up"] = component_node.findtext("Pick/ZMovementUp/TravelProfile", "")
                        pickup_data["dp_angle"] = component_node.findtext("Pick/DpMovement/TargetPosition", "")
                        pickup_data["vacuum_before"] = component_node.findtext("Pick/VacuumSystem/MeasuredBefore", "")
                        pickup_data["vacuum_after"] = component_node.findtext("Pick/VacuumSystem/MeasuredAfter", "")
                        pickup_data["holding"] = component_node.findtext("Pick/VacuumSystem/HoldingCircuit", "")
                        pickup_data["measure_height"] = component_node.findtext("Pick/FeederData/ComponentHeight", "")

                        # Placement data
                        placement_data["segment"] = component_node.findtext("Segment", "")
                        placement_data["nozzle"] = component_node.findtext("Nozzle", "")
                        #placement_data["conponent"] = component_node.findtext("Measure/VisionDump", "")
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
                    break  # Chỉ lấy giá trị đầu tiên nếu có nhiều id trùng

            # Cập nhật lên bảng Pickup
            if hasattr(self, "pickup_table"):
                self.pickup_table.setItem(self.pickup_segment_row, 1, QTableWidgetItem(pickup_data["segment"]))
                self.pickup_table.setItem(self.pickup_nozzle_row, 1, QTableWidgetItem(pickup_data["nozzle"]))
                self.pickup_table.setItem(self.pickup_conponent_row, 1, QTableWidgetItem(pickup_data["conponent"]))
                self.pickup_table.setItem(self.pickup_repick_row, 1, QTableWidgetItem(pickup_data["repick"]))
                track_value = pickup_data["pickup_track_row"]
                if track_value and len(track_value) >= 4:
                    track_value = track_value[2:4]
                else:
                    track_value = ""
                self.pickup_table.setItem(self.pickup_track_row, 1, QTableWidgetItem(track_value))
                self.pickup_table.setItem(self.pickup_pitck_row, 1, QTableWidgetItem(pickup_data["feeder_pitch"]))
                #self.pickup_table.setItem(self.pickup_error_in_z_row, 1, QTableWidgetItem(pickup_data["error_in_z"]))
                self.pickup_table.setItem(self.pickup_z_down_row, 1, QTableWidgetItem(pickup_data["z_down"]))
                self.pickup_table.setItem(self.pickup_z_up_row, 1, QTableWidgetItem(pickup_data["z_up"]))
                self.pickup_table.setItem(self.pickup_dp_angle_row, 1, QTableWidgetItem(pickup_data["dp_angle"]))
                self.pickup_table.setItem(self.pickup_vacuum_before_row, 1, QTableWidgetItem(pickup_data["vacuum_before"]))
                self.pickup_table.setItem(self.pickup_vacuum_after_row, 1, QTableWidgetItem(pickup_data["vacuum_after"]))
                self.pickup_table.setItem(self.pickup_holding_row, 1, QTableWidgetItem(pickup_data["holding"]))
                self.pickup_table.setItem(self.pickup_measure_height_row, 1, QTableWidgetItem(pickup_data["measure_height"]))

            # Cập nhật lên bảng Placement
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

        ref_list.itemSelectionChanged.connect(show_data_for_selection)
        panel_list.itemSelectionChanged.connect(show_data_for_selection)
        
        import_btn.clicked.connect(import_xml)
        
        # Stretch to fill
        layout.addStretch()
        return group