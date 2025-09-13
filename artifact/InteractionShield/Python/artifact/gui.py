import sys
import random
import re
from collections import defaultdict
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QComboBox,
    QFileDialog,
    QLabel,
    QMessageBox,
    QCheckBox,
    QGroupBox,
    QGridLayout,
    QRadioButton,
    QLineEdit,
    QFormLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QHeaderView,
    QSplitter,
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
)
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QBrush, QDoubleValidator
from PySide6.QtCore import Qt, QDir, Signal, QRect, Slot

from Python.utils.simulation import get_all_rules
from Python.utils.miscellaneous import (
    read_json,
    print_seconds_to_readable,
    print_memory_usage,
    format_nd_array,
)
from Python.utils.detector import ConflictDetectorClass
from Python.utils.resolver import ConflictResolverClass
from Python.utils.application import ApplicationClass
from Python.utils.enums import AppTypeEnum, ConflictEnum
from Python.utils.constant import (
    BUNDLE_APPS_D,
    HOMEGUARD_APPS_D,
    DATASETS_SMARTTHINGS_PATH_S,
    FILES_DATASETS_PATH_S,
    FILES_EXAMPLES_PATH_S,
    FILES_REFERENCE_PATH_S,
    DETERMINISTIC,
    CONDITIONAL,
    CONFLICTS_ID_D,
    LOW,
    MEDIUM,
    HIGH,
    DEVICE_STATES_D,
    DEFAULT_PROPERTIES,
    ROOM_PARAMETERS_D,
    DEVICE_SPECIFIC_DEFAULTS_D,
)


THREAT_HEADERS_L = [
    "No.",
    "Type",
    "Ranking",
    "Rules",
    "Action",
    "Risk Score",
    "Violation",
    "Possibility",
    "Penalty",
    "Weighted Penalty",
]
RULE_HEADERS_L = ["Rule", "Category", "Trigger", "Action"]
NUM_RISK_MAPPING_D = {LOW: "Low", MEDIUM: "Medium", HIGH: "High"}
RISK_NUM_MAPPING_D = {"Low": LOW, "Medium": MEDIUM, "High": HIGH}

class AppSelectorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Application Selector")
        self.rule_editor_window = None
        self.room_layout_window = None
        self.result_window = None
        # self.setGeometry(200, 200, 600, 400)
        self.applications = []
        self.display_to_apps_map = {}
        self.properties = []
        self.risk_level = MEDIUM
        self.layouts = {}
        self.room_parameters = ROOM_PARAMETERS_D
        self.selected_apps_flag = 0  # 0: from group, 1: from folder
        self.waiting_for_properties = False
        self.waiting_for_layout = False
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.init_ui()

    def init_ui(self):
        # self.central_widget.setMinimumWidth(600)
        main_layout = QVBoxLayout(self.central_widget)

        selection_panel = QGroupBox()
        panel_layout = QVBoxLayout(selection_panel)

        top_controls_layout = QHBoxLayout()
        top_controls_layout.setContentsMargins(0, 0, 0, 0)

        mode_groupbox = QGroupBox("Add Interaction Rules from Apps:")
        mode_layout = QHBoxLayout()
        self.radio_select_from_group = QRadioButton("Select apps from preset groups")
        self.radio_select_from_folder = QRadioButton("Select apps from folder")
        mode_layout.addWidget(self.radio_select_from_group)
        mode_layout.addWidget(self.radio_select_from_folder)
        mode_layout.addStretch()
        mode_groupbox.setLayout(mode_layout)

        self.radio_select_from_group.toggled.connect(self.update_selection_ui)
        self.radio_select_from_folder.toggled.connect(self.update_selection_ui)

        risk_level_groupbox = QGroupBox("Set Risk Level:")
        risk_level_layout = QHBoxLayout()
        self.risk_level_combo = QComboBox()
        self.risk_level_combo.addItems(["Low", "Medium", "High"])
        self.risk_level_combo.setCurrentText("Medium")
        self.risk_level_combo.currentTextChanged.connect(self.update_risk_level)
        risk_level_layout.addWidget(self.risk_level_combo)
        risk_level_layout.addStretch()
        risk_level_groupbox.setLayout(risk_level_layout)

        top_controls_layout.addWidget(mode_groupbox)
        top_controls_layout.addWidget(risk_level_groupbox)
        top_controls_layout.addStretch()

        self.group_selection_widget = QWidget()
        group_layout = QHBoxLayout(self.group_selection_widget)
        group_layout.setContentsMargins(0, 0, 0, 0)
        group_label = QLabel("Select a preset app group:")
        self.group_combo = QComboBox()
        self.group_combo.addItem("--Please select a group--")
        self.populate_group_combo()
        self.group_combo.currentTextChanged.connect(self.load_app_group)
        group_layout.addWidget(group_label)
        group_layout.addWidget(self.group_combo)
        group_layout.addStretch()
        self.group_selection_widget.hide()

        self.folder_selection_widget = QWidget()
        add_app_layout = QHBoxLayout(self.folder_selection_widget)
        add_app_layout.setContentsMargins(0, 0, 0, 0)
        add_app_label = QLabel("Select apps from folder:")
        self.add_button = QPushButton("Add Apps from Folder...")
        self.add_button.clicked.connect(self.add_apps_from_folder)
        add_app_layout.addWidget(add_app_label)
        add_app_layout.addWidget(self.add_button)
        add_app_layout.addStretch()
        self.folder_selection_widget.hide()

        options_groupbox = QGroupBox("Options:")
        options_layout = QHBoxLayout()
        self.add_props_checkbox = QCheckBox("Add behavior properties (negative rules)?")
        self.gen_layout_checkbox = QCheckBox("Add layout?")
        options_layout.addWidget(self.add_props_checkbox)
        options_layout.addWidget(self.gen_layout_checkbox)
        options_layout.addStretch()
        options_groupbox.setLayout(options_layout)

        list_label = QLabel("Currently Selected Apps:")
        self.app_list_widget = QListWidget()
        self.app_list_widget.setSelectionMode(QListWidget.ExtendedSelection)

        bottom_button_layout = QHBoxLayout()
        self.clear_button = QPushButton("Clear Selection")
        self.clear_button.clicked.connect(self.clear_selection)
        self.confirm_button = QPushButton("Confirm Selection")
        self.confirm_button.clicked.connect(self.confirm_selection)
        bottom_button_layout.addStretch()
        bottom_button_layout.addWidget(self.clear_button)
        bottom_button_layout.addWidget(self.confirm_button)
        bottom_button_layout.addStretch()

        panel_layout.addLayout(top_controls_layout)
        panel_layout.addWidget(self.group_selection_widget)
        panel_layout.addWidget(self.folder_selection_widget)

        main_layout.addWidget(selection_panel)
        main_layout.addWidget(options_groupbox)
        main_layout.addWidget(list_label)
        main_layout.addWidget(self.app_list_widget)
        main_layout.addLayout(bottom_button_layout)

    def update_risk_level(self, text):
        self.risk_level = RISK_NUM_MAPPING_D[text]

    def populate_group_combo(self):
        app_group_names = []

        for group_num in sorted(BUNDLE_APPS_D.keys()):
            apps_list = BUNDLE_APPS_D[group_num]
            display_name = f"BUNDLE # {group_num}"
            app_group_names.append(display_name)
            self.display_to_apps_map[display_name] = apps_list

        for group_num in sorted(HOMEGUARD_APPS_D.keys()):
            apps_list = HOMEGUARD_APPS_D[group_num]
            display_name = f"HOMEGUARD # {group_num}"
            app_group_names.append(display_name)
            self.display_to_apps_map[display_name] = apps_list

        self.group_combo.addItems(app_group_names)

    def update_selection_ui(self):
        self.app_list_widget.clear()

        if self.radio_select_from_group.isChecked():
            self.group_selection_widget.show()
            self.folder_selection_widget.hide()
        elif self.radio_select_from_folder.isChecked():
            self.group_selection_widget.hide()
            self.folder_selection_widget.show()
        else:
            self.group_selection_widget.hide()
            self.folder_selection_widget.hide()

    def load_app_group(self, group_name):
        if group_name == "--Please select a group--":
            return

        self.app_list_widget.clear()
        self.selected_apps_flag = 0
        example_apps = self.display_to_apps_map.get(group_name, [])
        if example_apps:
            self.app_list_widget.addItems(example_apps)

    def add_apps_from_folder(self):
        file_filter = "All Files (*.groovy)"

        self.selected_apps_flag = 1
        self.app_list_widget.clear()

        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select two or more applications",
            DATASETS_SMARTTHINGS_PATH_S,
            file_filter,
        )

        if file_paths:
            current_items = set(
                self.app_list_widget.item(i).text()
                for i in range(self.app_list_widget.count())
            )

            added_count = 0
            for path in file_paths:
                if path not in current_items:
                    idx = path.rfind("/")
                    app_name = path[idx + 1 :]
                    self.app_list_widget.addItem(app_name)
                    added_count += 1

    def clear_selection(self):
        self.app_list_widget.clear()
        self.group_combo.setCurrentIndex(0)
        print("Selection list has been cleared.")

    def get_applications(self):
        applications_l: list = []
        app_path_s = f"{FILES_EXAMPLES_PATH_S}/SmartThings.json"
        dev_path_s = f"{FILES_REFERENCE_PATH_S}/Examples_Devices.json"
        if self.selected_apps_flag == 1:
            app_path_s = f"{FILES_DATASETS_PATH_S}/SmartThings.json"
            dev_path_s = f"{FILES_REFERENCE_PATH_S}/Datasets_Devices.json"
        apps_d: dict = read_json(app_path_s)
        devs_d: dict = read_json(dev_path_s)

        for appname_s in self.selected_apps:
            if appname_s not in apps_d:
                continue
            detail_d = apps_d.get(appname_s, {})
            appdevs_d = devs_d.get(appname_s, {})
            application_u: ApplicationClass = ApplicationClass(
                appname_s, detail_d, AppTypeEnum.SMARTTHINGS, appdevs_d
            )
            applications_l.append(application_u)
        return applications_l

    def confirm_selection(self):
        self.selected_apps = [
            self.app_list_widget.item(i).text()
            for i in range(self.app_list_widget.count())
        ]

        if not self.selected_apps:
            QMessageBox.warning(
                self, "Notice", "You have not selected any applications!"
            )
            return

        self.applications = self.get_applications()

        self.rules, _, _ = get_all_rules(self.applications)

        # QMessageBox.information(
        #     self,
        #     "Selection Confirmed",
        #     f"You have successfully selected {len(self.selected_apps)} application(s).\n"
        #     f"Please see the console output for the detailed list."
        # )
        self.waiting_for_properties = self.add_props_checkbox.isChecked()
        self.waiting_for_layout = self.gen_layout_checkbox.isChecked()

        print(f"Option 'Need to add properties?': {self.waiting_for_properties}")
        print(f"Option 'Need to generate layout?': {self.waiting_for_layout}")

        if self.waiting_for_properties:
            print("Checkbox is checked, opening Rule Editor...")
            if self.rule_editor_window is None:
                self.rule_editor_window = RuleEditorWindow()
                self.rule_editor_window.properties_ready.connect(
                    self.on_properties_received
                )

            self.rule_editor_window.show()

        if self.waiting_for_layout:
            print("Checkbox is checked, opening Room Layout...")
            if self.room_layout_window is None:
                self.room_layout_window = RoomLayoutApp(self.applications, self.rules)
                self.room_layout_window.layout_ready.connect(self.on_layout_received)

            self.room_layout_window.show()

        self.check_and_show_results()

    def on_properties_received(self, props):
        self.properties = props
        self.waiting_for_properties = False
        self.check_and_show_results()

    def on_layout_received(self, layout):
        self.layouts = layout
        self.waiting_for_layout = False
        self.check_and_show_results()

    def check_and_show_results(self):
        if self.waiting_for_properties or self.waiting_for_layout:
            print(
                f"Still waiting for... Properties: {self.waiting_for_properties}, Layout: {self.waiting_for_layout}"
            )
            return

        print("\n--- All data collected, proceeding to Results ---")

        if self.layouts:
            self.update_layouts()

        print("\n---Final Confirmed Application List---")
        for rule in self.rules:
            print(rule)
        print("------------------------------------\n")

        if self.result_window is None:
            self.result_window = ResultsWindow(
                self.rules, self.properties, self.risk_level, self.room_parameters
            )
        self.result_window.update_data(
            self.rules, self.properties, self.risk_level, self.room_parameters
        )
        self.result_window.show()

    def update_layouts(self):
        if not self.layouts:
            return
        room_parameters = self.layouts.get("room_params", {})
        for param_s, value_f in room_parameters.items():
            if param_s in self.room_parameters:
                self.room_parameters[param_s] = value_f
        app_parameters_d = self.layouts.get("app_params", {})
        dev_parameters_d = self.layouts.get("device_params", {})
        for rule_u in self.rules:
            rule_u.update_parameters(
                app_parameters_d.get(rule_u.appname, {}),
                dev_parameters_d.get(rule_u.appname, {}),
            )


class RuleEditorWindow(QMainWindow):
    properties_ready = Signal(list)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Behavior Properties")
        # self.setGeometry(300, 300, 800, 500)
        self.properties = []

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.init_ui()
        self.load_default_rule()

    def init_ui(self):
        main_layout = QVBoxLayout(self.central_widget)

        input_layout = QHBoxLayout()
        dont_label = QLabel("DON'T")
        dont_label.setStyleSheet("font-weight: bold;")

        self.action_device_combo = QComboBox()
        self.action_device_combo.addItems(sorted(DEVICE_STATES_D.keys()))

        self.action_state_combo = QComboBox()
        # self.action_state_combo.setMinimumWidth(120)
        self.action_device_combo.currentTextChanged.connect(self.update_action_states)

        when_label = QLabel("WHEN")
        when_label.setStyleSheet("font-weight: bold;")

        self.condition_device_combo = QComboBox()
        self.condition_device_combo.addItems(sorted(DEVICE_STATES_D.keys()))

        self.condition_state_combo = QComboBox()
        # self.condition_state_combo.setMinimumWidth(120)
        self.condition_device_combo.currentTextChanged.connect(
            self.update_condition_states
        )

        self.add_button = QPushButton("Add Behavior Property")
        self.add_button.clicked.connect(self.add_rule)

        input_layout.addWidget(dont_label)
        input_layout.addWidget(self.action_device_combo)
        input_layout.addWidget(QLabel("."))
        input_layout.addWidget(self.action_state_combo)
        input_layout.addStretch(1)
        input_layout.addWidget(when_label)
        input_layout.addWidget(self.condition_device_combo)
        input_layout.addWidget(QLabel("."))
        input_layout.addWidget(self.condition_state_combo)
        input_layout.addStretch(1)
        input_layout.addWidget(self.add_button)

        list_label = QLabel("Current Behavior Properties:")
        self.rule_list_widget = QListWidget()
        self.rule_list_widget.setSelectionMode(QListWidget.SingleSelection)

        bottom_button_layout = QHBoxLayout()
        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_selected_rule)

        self.clear_all_button = QPushButton("Clear All")
        self.clear_all_button.clicked.connect(self.clear_all_rules)

        self.confirm_button = QPushButton("Confirm and Close")
        self.confirm_button.clicked.connect(self.confirm_rules)
        # self.confirm_button.setStyleSheet("font-size: 16px; padding: 5px; background-color: #4CAF50; color: white;")

        bottom_button_layout.addStretch()
        bottom_button_layout.addWidget(self.delete_button)
        bottom_button_layout.addWidget(self.clear_all_button)
        bottom_button_layout.addWidget(self.confirm_button)
        bottom_button_layout.addStretch()

        main_layout.addLayout(input_layout)
        main_layout.addWidget(list_label)
        main_layout.addWidget(self.rule_list_widget)
        main_layout.addLayout(bottom_button_layout)

        self.update_action_states(self.action_device_combo.currentText())
        self.update_condition_states(self.condition_device_combo.currentText())

    def update_action_states(self, device):
        self.action_state_combo.clear()
        states = DEVICE_STATES_D.get(device, [])
        self.action_state_combo.addItems(states)

    def update_condition_states(self, device):
        self.condition_state_combo.clear()
        states = DEVICE_STATES_D.get(device, [])
        self.condition_state_combo.addItems(states)

    def load_default_rule(self):
        for action, condition in DEFAULT_PROPERTIES:
            default_rule = f"DON'T {action} WHEN {condition}"
            self.rule_list_widget.addItem(default_rule)
        print("Default rule loaded.")

    def add_rule(self):
        action_device = self.action_device_combo.currentText()
        action_state = self.action_state_combo.currentText()
        condition_device = self.condition_device_combo.currentText()
        condition_state = self.condition_state_combo.currentText()

        if not all([action_device, action_state, condition_device, condition_state]):
            QMessageBox.warning(
                self, "Input Error", "All fields must have a selection."
            )
            return

        action = f"{action_device}.{action_state}"
        condition = f"{condition_device}.{condition_state}"
        new_rule = f"DON'T {action} WHEN {condition}"

        items = self.rule_list_widget.findItems(new_rule, Qt.MatchExactly)
        if items:
            QMessageBox.warning(
                self, "Duplicate Rule", "This rule already exists in the list."
            )
            return

        self.rule_list_widget.addItem(new_rule)
        print(f"New rule added: {new_rule}")

    def delete_selected_rule(self):
        selected_item = self.rule_list_widget.currentItem()
        if not selected_item:
            QMessageBox.information(
                self, "Notice", "Please select a rule from the list to delete."
            )
            return

        row = self.rule_list_widget.row(selected_item)
        self.rule_list_widget.takeItem(row)

    def clear_all_rules(self):
        if self.rule_list_widget.count() == 0:
            QMessageBox.information(self, "Notice", "The rule list is already empty.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Action",
            "Are you sure you want to clear all rules?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.rule_list_widget.clear()
            print("All rules have been cleared.")

    def confirm_rules(self):
        # if self.rule_list_widget.count() == 0:
        #     QMessageBox.warning(self, "No Rules", "There are no rules in the list to confirm.")
        #     return

        all_rules = [
            self.rule_list_widget.item(i).text()
            for i in range(self.rule_list_widget.count())
        ]
        all_rules = list(set(all_rules))

        for rule in all_rules:
            extracted = self.extract_action_and_condition(rule)
            if extracted:
                action, condition = extracted
                self.properties.append((action, condition))
        self.properties_ready.emit(self.properties)

        print("\n---Final Confirmed Rule List---")
        for rule in all_rules:
            print(rule)
        print("-----------------------------\n")

        # QMessageBox.information(
        #     self,
        #     "Rules Confirmed",
        #     f"{len(all_rules)} rule(s) have been confirmed.\n"
        #     "Please see the console output for the detailed list.",
        # )
        self.close()

    def extract_action_and_condition(self, sentence):
        match = re.search(r"DON'T\s+(.+?)\s+WHEN\s+(.+)", sentence, re.IGNORECASE)

        if match:
            return list(match.groups())
        else:
            return []


CANVAS_PADDING = 30

APP_COLORS = [
    QColor("#3498db"),
    QColor("#2ecc71"),
    QColor("#e74c3c"),
    QColor("#9b59b6"),
    QColor("#f1c40f"),
    QColor("#e67e22"),
    QColor("#1abc9c"),
]

PARAM_METADATA = {
    "source_temperature": {
        "label": "Source Temperature (°F)",
        "validator": QDoubleValidator(0, 1000, 2),
    },
    "temperature_delta": {
        "label": "Temperature Change Rate (°F/min)",
        "validator": QDoubleValidator(-5, 5, 4),
    },
    "illuminance": {
        "label": "Luminosity (lux)",
        "validator": QDoubleValidator(0, 10000, 2),
    },
    "sound_level": {
        "label": "Sound Level (dB)",
        "validator": QDoubleValidator(0, 150, 2),
    },
    "water_vapor": {
        "label": "Water Vapor (g/min)",
        "validator": QDoubleValidator(-100, 100, 4),
    },
    "smoke_generate": {
        "label": "Smoke Generate Rate (OD/m/s)",
        "validator": QDoubleValidator(0, 1, 4),
    },
    "smoke_clearance": {
        "label": "Smoke Clearance Rate (1/s)",
        "validator": QDoubleValidator(0, 1, 4),
    },
    "power": {
        "label": "Rated Power (Watts)",
        "validator": QDoubleValidator(0, 5000, 2),
    },
}


class DrawingCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setMinimumSize(400, 400)
        self.devices_by_app = {}
        self.room_width_m = ROOM_PARAMETERS_D["width"]
        self.room_length_m = ROOM_PARAMETERS_D["length"]

    def update_layout(self, room_width, room_length, devices_by_app):
        self.room_width_m = room_width
        self.room_length_m = room_length
        self.devices_by_app = devices_by_app
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), Qt.white)

        canvas_w = self.width() - 2 * CANVAS_PADDING
        canvas_h = self.height() - 2 * CANVAS_PADDING
        if self.room_width_m == 0 or self.room_length_m == 0:
            return

        scale = min(canvas_w / self.room_width_m, canvas_h / self.room_length_m)
        drawing_w_px = self.room_width_m * scale
        drawing_h_px = self.room_length_m * scale
        offset_x = (self.width() - drawing_w_px) / 2
        offset_y = (self.height() - drawing_h_px) / 2

        painter.setPen(QPen(Qt.black, 2))
        painter.drawRect(
            int(offset_x), int(offset_y), int(drawing_w_px), int(drawing_h_px)
        )

        painter.setFont(QFont("Arial", 10))
        painter.setPen(Qt.black)
        top_rect = QRect(int(offset_x), int(offset_y - 20), int(drawing_w_px), 20)
        painter.drawText(top_rect, Qt.AlignCenter, f"{self.room_width_m} m")
        left_rect = QRect(int(offset_x - 50), int(offset_y), 50, int(drawing_h_px))
        painter.drawText(
            left_rect, Qt.AlignVCenter | Qt.AlignRight, f"{self.room_length_m} m "
        )

        locations = {}
        app_color_indices = {
            app_name: i for i, app_name in enumerate(self.devices_by_app.keys())
        }

        for app_name, devices_in_app in self.devices_by_app.items():
            for varname_l, device_l in devices_in_app.items():
                coord_key = tuple(device_l[1:])
                if coord_key not in locations:
                    locations[coord_key] = {"types": set(), "apps": []}
                locations[coord_key]["types"].add(device_l[0])
                if app_name not in locations[coord_key]["apps"]:
                    locations[coord_key]["apps"].append(app_name)

        for (x_str, y_str), data in locations.items():
            try:
                x_m, y_m = float(x_str), float(y_str)
                px = offset_x + x_m * scale
                py = offset_y + y_m * scale
                radius = 12

                num_apps = len(data["apps"])
                if num_apps == 1:
                    app_name = data["apps"][0]
                    color_index = app_color_indices.get(app_name, 0)
                    color = APP_COLORS[color_index % len(APP_COLORS)]
                    painter.setBrush(QBrush(color))
                    painter.setPen(QPen(color.darker(120), 1))
                    painter.drawEllipse(
                        int(px - radius / 2), int(py - radius / 2), radius, radius
                    )
                else:
                    angle_span = (360 * 16) / num_apps
                    rect = QRect(
                        int(px - radius / 2), int(py - radius / 2), radius, radius
                    )
                    for i, app_name in enumerate(data["apps"]):
                        color_index = app_color_indices.get(app_name, 0)
                        color = APP_COLORS[color_index % len(APP_COLORS)]
                        painter.setBrush(QBrush(color))
                        painter.setPen(QPen(color.darker(120), 1))
                        start_angle = i * angle_span
                        painter.drawPie(rect, int(start_angle), int(angle_span))

                painter.setPen(Qt.black)
                type_label = ", ".join(sorted(list(data["types"])))
                painter.drawText(int(px + radius), int(py + radius), type_label)
            except (ValueError, KeyError):
                continue


class DeviceInputDialog(QDialog):
    def __init__(self, device_name, device_params, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Set Parameters for {device_name}")
        self.layout = QFormLayout(self)

        self.params = device_params.keys()
        self.inputs = [None] * len(self.params)
        for i, param in enumerate(self.params):
            line_edit = QLineEdit(str(device_params[param]))
            line_edit.setValidator(PARAM_METADATA[param]["validator"])
            self.layout.addRow(f"{PARAM_METADATA[param]['label']}:", line_edit)
            self.inputs[i] = line_edit

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def get_values(self):
        return {
            param: float(self.inputs[i].text()) for i, param in enumerate(self.params)
        }


class RoomLayoutApp(QMainWindow):
    layout_ready = Signal(dict)

    def __init__(self, applications, rules):
        super().__init__()
        self.applications = applications
        self.rules = rules
        self.setWindowTitle("Room Layout Designer")
        # self.setGeometry(100, 100, 1200, 800)

        self.is_populating_tree = False
        self.all_device_types = self._get_unique_device_types()

        self.device_extra_params = defaultdict(dict)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)
        self.canvas = DrawingCanvas()
        right_pane = QWidget()
        right_layout = QVBoxLayout(right_pane)
        room_params_group = QGroupBox("Room Parameters")
        room_params_layout = QGridLayout(room_params_group)
        self.length_input = QLineEdit(str(ROOM_PARAMETERS_D["length"]))
        self.length_input.setValidator(QDoubleValidator(0.1, 100.0, 2))
        room_params_layout.addWidget(QLabel("Length (m):"), 0, 0)
        room_params_layout.addWidget(self.length_input, 0, 1)
        self.width_input = QLineEdit(str(ROOM_PARAMETERS_D["width"]))
        self.width_input.setValidator(QDoubleValidator(0.1, 100.0, 2))
        room_params_layout.addWidget(QLabel("Width (m):"), 0, 2)
        room_params_layout.addWidget(self.width_input, 0, 3)
        self.height_input = QLineEdit(str(ROOM_PARAMETERS_D["height"]))
        self.height_input.setValidator(QDoubleValidator(0.1, 100.0, 2))
        room_params_layout.addWidget(QLabel("Height (m):"), 0, 4)
        room_params_layout.addWidget(self.height_input, 0, 5)
        self.time_input = QLineEdit(str(ROOM_PARAMETERS_D["time"]))
        self.time_input.setValidator(QDoubleValidator(0.0, 10000.0, 2))
        room_params_layout.addWidget(QLabel("Time (min):"), 0, 6)
        room_params_layout.addWidget(self.time_input, 0, 7)
        self.temp_input = QLineEdit(str(ROOM_PARAMETERS_D["temperature"]))
        self.temp_input.setValidator(QDoubleValidator(-100.0, 200.0, 2))
        room_params_layout.addWidget(QLabel("Temperature (°F):"), 1, 0)
        room_params_layout.addWidget(self.temp_input, 1, 1)
        self.humidity_input = QLineEdit(str(ROOM_PARAMETERS_D["humidity"]))
        self.humidity_input.setValidator(QDoubleValidator(0.0, 100.0, 2))
        room_params_layout.addWidget(QLabel("Humidity (g/m^3):"), 1, 2)
        room_params_layout.addWidget(self.humidity_input, 1, 3)
        self.smoke_input = QLineEdit(str(ROOM_PARAMETERS_D["smoke"]))
        self.smoke_input.setValidator(QDoubleValidator(0.0, 100.0, 2))
        room_params_layout.addWidget(QLabel("Smoke (OD/m):"), 1, 4)
        room_params_layout.addWidget(self.smoke_input, 1, 5)
        self.power_input = QLineEdit(str(ROOM_PARAMETERS_D["power"]))
        self.power_input.setValidator(QDoubleValidator(0.0, 10000.0, 2))
        room_params_layout.addWidget(QLabel("Power (W):"), 1, 6)
        room_params_layout.addWidget(self.power_input, 1, 7)
        self.device_tree = QTreeWidget()
        self.device_tree.setColumnCount(4)
        self.device_tree.setHeaderLabels(
            ["App Name / Variables", "Device Type", "X (m)", "Y (m)"]
        )
        self.device_tree.header().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.generate_button = QPushButton("Confirm and Close")
        right_layout.addWidget(QLabel("Device List (Editable)"))
        right_layout.addWidget(self.device_tree)
        right_layout.addWidget(room_params_group)
        right_layout.addWidget(self.generate_button)
        splitter.addWidget(self.canvas)
        splitter.addWidget(right_pane)
        splitter.setSizes([700, 500])

        self.generate_button.clicked.connect(self.confirm_and_close)
        self.width_input.editingFinished.connect(self.reset_and_regenerate_layout)
        self.length_input.editingFinished.connect(self.reset_and_regenerate_layout)
        self.device_tree.itemChanged.connect(self._redraw_canvas_from_tree)

        self.reset_and_regenerate_layout()

    def get_final_layout_data(self):
        room_params = {
            "length": float(self.length_input.text() or ROOM_PARAMETERS_D["length"]),
            "width": float(self.width_input.text() or ROOM_PARAMETERS_D["width"]),
            "height": float(self.height_input.text() or ROOM_PARAMETERS_D["height"]),
            "time": float(self.time_input.text() or ROOM_PARAMETERS_D["time"]),
            "temperature": float(
                self.temp_input.text() or ROOM_PARAMETERS_D["temperature"]
            ),
            "humidity": float(
                self.humidity_input.text() or ROOM_PARAMETERS_D["humidity"]
            ),
            "smoke": float(self.smoke_input.text() or ROOM_PARAMETERS_D["smoke"]),
            "power": float(self.power_input.text() or ROOM_PARAMETERS_D["power"]),
            "physical": True,
        }
        return {
            "room_params": room_params,
            "app_params": self.read_tree_data_as_dict(),
            "device_params": self.device_extra_params,
        }

    @Slot()
    def confirm_and_close(self):
        final_layout_data = self.get_final_layout_data()
        self.layout_ready.emit(final_layout_data)
        self.close()

    @Slot(QTreeWidgetItem)
    def handle_device_type_change(self, device_item):
        if not device_item:
            return

        device_name = device_item.text(0)
        app_item = device_item.parent()
        app_name = app_item.text(0)
        combo = self.device_tree.itemWidget(device_item, 1)
        device_type = combo.currentText() if combo else ""
        device_params = DEVICE_SPECIFIC_DEFAULTS_D.get(device_type, {})
        if device_params:
            dialog = DeviceInputDialog(device_name, device_params, self)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_values = dialog.get_values()
                self.device_extra_params[app_name][device_name] = new_values

    def populate_tree(self, app_data):
        self.is_populating_tree = True
        self.device_tree.clear()
        for app_name, devices in app_data.items():
            app_item = QTreeWidgetItem([app_name])
            self.device_tree.addTopLevelItem(app_item)
            for device in devices:
                device_item = QTreeWidgetItem(
                    [device["name"], "", str(device["x"]), str(device["y"])]
                )
                device_item.setFlags(device_item.flags() | Qt.ItemFlag.ItemIsEditable)
                app_item.addChild(device_item)

                combo = QComboBox()
                combo.addItems(self.all_device_types)
                if device["type"] in self.all_device_types:
                    combo.setCurrentText(device["type"])

                combo.activated.connect(
                    lambda _, item=device_item: self.handle_device_type_change(item)
                )

                self.device_tree.setItemWidget(device_item, 1, combo)

        self.device_tree.expandAll()
        self.is_populating_tree = False

    def _get_unique_device_types(self):
        unique_types = set()
        for app in self.applications:
            for dev_type in app.vardevs.values():
                if dev_type not in ["location", "time"]:
                    unique_types.add(dev_type)
        # unique_types.update(list(DEVICE_SPECIFIC_DEFAULTS_D.keys()))
        unique_types.update(sorted(DEVICE_STATES_D.keys()))
        return sorted(list(unique_types))

    @Slot()
    def reset_and_regenerate_layout(self):
        room_w = float(self.width_input.text() or ROOM_PARAMETERS_D["width"])
        room_l = float(self.length_input.text() or ROOM_PARAMETERS_D["length"])
        app_data = self.generate_random_app_data(room_w, room_l)
        self.populate_tree(app_data)
        self._redraw_canvas()

    @Slot()
    def _redraw_canvas(self):
        if self.is_populating_tree:
            return
        room_w = float(self.width_input.text() or ROOM_PARAMETERS_D["width"])
        room_l = float(self.length_input.text() or ROOM_PARAMETERS_D["length"])
        devices_by_app = self.read_tree_data_as_dict()
        self.canvas.update_layout(room_w, room_l, devices_by_app)

    @Slot(QTreeWidgetItem, int)
    def _redraw_canvas_from_tree(self, item, column):
        self._redraw_canvas()

    def read_tree_data_as_dict(self):
        app_data = defaultdict(dict)
        for i in range(self.device_tree.topLevelItemCount()):
            app_item = self.device_tree.topLevelItem(i)
            app_name = app_item.text(0)
            app_data[app_name] = defaultdict(list)
            for j in range(app_item.childCount()):
                device_item = app_item.child(j)
                type_widget = self.device_tree.itemWidget(device_item, 1)
                dev_type = type_widget.currentText() if type_widget else ""
                app_data[app_name][device_item.text(0)] = [
                    dev_type,
                    float(device_item.text(2)),
                    float(device_item.text(3)),
                ]
        return app_data

    def generate_random_app_data(self, max_w, max_l):
        app_data = {}
        same_dev = {}
        for app in self.applications:
            if app.appname in app_data:
                continue
            app_name = app.appname
            app_data[app_name] = []
            for varname_s, dev_type in app.vardevs.items():
                if dev_type in ["location", "time"]:
                    continue
                coords = same_dev.get(dev_type, {})
                if not coords:
                    coords = {
                        "x": f"{random.uniform(0.1, max_w - 0.1):.2f}",
                        "y": f"{random.uniform(0.1, max_l - 0.1):.2f}",
                    }
                    same_dev[dev_type] = coords
                app_data[app_name].append(
                    {
                        "name": varname_s,
                        "type": dev_type,
                        "x": coords["x"],
                        "y": coords["y"],
                    }
                )
        return app_data


class ResultsWindow(QMainWindow):
    COLOR_PALETTE = [
        QColor(255, 255, 224),
        QColor(230, 243, 255),
        QColor(230, 255, 230),
        QColor(255, 240, 245),
        QColor(245, 245, 245),
    ]

    def __init__(
        self, rules, properties=[], risk_level=MEDIUM, room_parameters=ROOM_PARAMETERS_D
    ):
        super().__init__()
        self.setWindowTitle("Threat Detection and Resolution Results")
        # self.setGeometry(100, 100, 900, 700)

        self.rules = rules
        self.properties = properties
        self.risk_level = risk_level
        self.room_parameters = room_parameters
        self.rules_id, self.origin_rules = self.set_rules_number()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)

        # self.main_layout.addWidget(self.create_original_rules_group())
        # self.main_layout.addWidget(self.create_detector_group())
        # self.main_layout.addWidget(self.create_optimized_rules_group())
        # self.main_layout.addWidget(self.create_resolver_group())

    def update_data(
        self, rules, properties=[], risk_level=MEDIUM, room_parameters=ROOM_PARAMETERS_D
    ):
        self.rules = rules
        self.properties = properties
        if self.risk_level != risk_level:
            self.risk_level = risk_level
        self.room_parameters = room_parameters
        self.rules_id, self.origin_rules = self.set_rules_number()

        for i in reversed(range(self.main_layout.count())):
            widget_to_remove = self.main_layout.itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.setParent(None)
        self.detector_results = self.get_detector_results()
        self.main_layout.addWidget(self.create_original_rules_group())
        self.main_layout.addWidget(self.create_detector_group())
        self.detector_results.clear()

        self.optimized_rules, self.resolver_results = self.get_resolver_results()
        self.main_layout.addWidget(self.create_optimized_rules_group())
        self.main_layout.addWidget(self.create_resolver_group())
        self.resolver_results.clear()

    def set_rules_number(self):
        rules_id = {}
        origin_rules = []
        for i, rule in enumerate(self.rules):
            triggers_l = [str(trigger_u) for trigger_u in rule.triggers]
            triggers_s = ", ".join(triggers_l)
            action_s = str(rule.action)
            rule_l = [f"r{i+1}", rule.category, triggers_s, action_s]
            rules_id[rule] = rule_l
            origin_rules.append(rule_l)
        return rules_id, origin_rules

    def parse_conflicts(self, conflicts):
        conflicts.sort(key=lambda x: CONFLICTS_ID_D[x.type])
        conflicts_results = []
        for i, conflict_u in enumerate(conflicts):
            id_s = f"L{i+1}"
            rules_l, actions_l, risks_l, violations_l = [], [], [], []
            type_e = conflict_u.type
            possible_s = (
                "Deterministic"
                if conflict_u.possible == DETERMINISTIC
                else "Conditional"
            )
            type_id_s = f"{str(type_e)}(C.{CONFLICTS_ID_D[type_e]})"
            ranking_s = NUM_RISK_MAPPING_D[conflict_u.ranking]
            penalty_f, weighted_penalty_f = conflict_u.calculate_penalty()
            penalty_s, weighted_penalty_s = str(penalty_f), str(weighted_penalty_f)

            for rule_u in conflict_u.rules:
                rules_l.append(self.rules_id[rule_u][0])
                actions_l.append(str(rule_u.action))
                risks_l.append(NUM_RISK_MAPPING_D[rule_u.action.action_risk])
                violations_l.append(str(rule_u.action.action_violations))

            rules_s = "\n".join(rules_l)
            actions_s = "\n".join(actions_l)
            risks_s = "\n".join(risks_l)
            violations_s = "\n".join(violations_l)
            if type_e in [ConflictEnum.ENABLE, ConflictEnum.DISABLE]:
                rules_s = "→".join(rules_l)
                actions_s = actions_l[-1]
                risks_s = risks_l[-1]
                violations_s = violations_l[-1]
            elif type_e in [ConflictEnum.LOOP]:
                rules_s = "→".join(rules_l) + "→" + rules_l[0]

            conflicts_results.append(
                [
                    id_s,
                    type_id_s,
                    ranking_s,
                    rules_s,
                    actions_s,
                    risks_s,
                    violations_s,
                    possible_s,
                    penalty_s,
                    weighted_penalty_s,
                ]
            )
        return conflicts_results

    def get_detector_results(self):
        detector_u = ConflictDetectorClass(
            self.rules, self.properties, self.risk_level, self.room_parameters
        )
        return detector_u

    def get_resolver_results(self):

        resolver_u = ConflictResolverClass(
            self.rules,
            self.properties,
            self.risk_level,
            self.room_parameters,
            lambda_f=0.14 * len(self.rules) + 0.04,
        )

        optimized_rules, final_penalty, final_f_value = resolver_u.resolve()
        resolved_u = ConflictDetectorClass(
            optimized_rules, self.properties, self.risk_level, self.room_parameters
        )
        # resolved_u.clear()
        return optimized_rules, resolved_u

    def create_table_from_data(self, headers, data, color_groups=None):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(data))

        column_to_color = {}
        if color_groups:
            for i, group in enumerate(color_groups):
                color = self.COLOR_PALETTE[i % len(self.COLOR_PALETTE)]
                for col_idx in group:
                    column_to_color[col_idx] = color

        for row_idx, row_data in enumerate(data):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data))
                item.setTextAlignment(Qt.AlignCenter)
                if col_idx in column_to_color:
                    item.setBackground(column_to_color[col_idx])

                table.setItem(row_idx, col_idx, item)

        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.resizeRowsToContents()
        return table

    def create_original_rules_group(self):
        group_box = QGroupBox("Original Rules:")
        layout = QVBoxLayout()

        rule_table = self.create_table_from_data(RULE_HEADERS_L, self.origin_rules)

        layout.addWidget(rule_table)
        group_box.setLayout(layout)
        return group_box

    def create_detector_group(self):
        group_box = QGroupBox(f"Conflicts Detected with Risk Level {NUM_RISK_MAPPING_D[self.risk_level]}:")
        layout = QVBoxLayout()
        detector_results = self.parse_conflicts(self.detector_results.conflicts)
        threat_table = self.create_table_from_data(
            THREAT_HEADERS_L,
            detector_results,
            color_groups=[[0], [1, 2], [3, 4, 5, 6], [7], [8, 9]],
        )
        threat_table.resizeRowsToContents()

        layout.addWidget(threat_table)
        group_box.setLayout(layout)
        return group_box

    def create_optimized_rules_group(self):
        group_box = QGroupBox("Rules Remaining after Conflict Resolution:")
        layout = QVBoxLayout()

        optimized_rules_l = []
        for rule_u in self.optimized_rules:
            if rule_u in self.rules_id:
                optimized_rules_l.append(self.rules_id[rule_u])

        resolved_table = self.create_table_from_data(RULE_HEADERS_L, optimized_rules_l)

        layout.addWidget(resolved_table)
        group_box.setLayout(layout)
        return group_box

    def create_resolver_group(self):
        group_box = QGroupBox("Conflicts Remaining for Mitigation:")
        layout = QVBoxLayout()

        resolver_results = self.parse_conflicts(self.resolver_results.conflicts)
        resolver_table = self.create_table_from_data(THREAT_HEADERS_L, resolver_results)
        resolver_table.resizeRowsToContents()

        layout.addWidget(resolver_table)
        group_box.setLayout(layout)
        return group_box


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppSelectorWindow()
    window.show()
    sys.exit(app.exec())
