import sys
import logging
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel, QTextEdit, QPushButton, QFileDialog

from logic.return_file_from_cybs import return_file_from_cybs_main
from logic.send_file_to_cybs import to_send_files_to_cybs_main
from logic.summary import summary_analysis
from logic.import_iPay88_token_to_secondary_token import import_iPay88_token_to_secondary_token_main
from logic.import_NCT_and_EG_to_secondary_token import import_NCT_EG_to_secondary_token_main
from logic.import_iPay88_token_to_main_token import import_iPay88_token_to_main_token_main
from logic.send_file_to_iPay88 import send_file_to_iPay88_main

class QTextEditLogger(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        # Format the log message
        msg = self.format(record)
        # Append the message to the QTextEdit
        self.text_widget.append(msg)

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_folder = None  # Initialize variable to store the selected folder path
        self.function_mapping = {
            'Send Files To Cybersource': self.process_cyb,
            'Remap Cybersource Token To Original File': self.process_sf,
            'Cybersource Token File Analysis': self.summary,
            'To Import iPay88 Token To Secondary Token Field' : self.iPay88_to_secondary_token,
            'To Import NCT and EG To Secondary Token Field' : self.NCT_and_EG_to_secondary_token,
            'Send File To iPay88' : self.send_file_to_ipay88,
            'Import iPay88 Token To Main Token Field' : self.import_iPay88_token_to_main_token

        }

        # Initialize UI
        self.initUI()

    def initUI(self):
        # Create widgets
        self.label = QLabel('Select an item from the dropdown', self)  # The label at the top
        self.combo = QComboBox(self)  # The dropdown menu
        self.text_display = QTextEdit(self)  # QTextEdit for displaying output
        self.text_display.setReadOnly(True)  # Make it read-only for display purposes
        
        # Button to browse folder
        self.browse_button = QPushButton('Browse Folder', self)
        self.browse_button.clicked.connect(self.browse_folder)
        self.browse_button.setEnabled(False)  # Disable the button initially

        # Add items to combo box
        self.combo.addItems(
            ['', 'Send Files To Cybersource', 'Remap Cybersource Token To Original File', 
             'Cybersource Token File Analysis', 'To Import iPay88 Token To Secondary Token Field',
             'To Import NCT and EG To Secondary Token Field',
             'Send File To iPay88', 'Import iPay88 Token To Main Token Field'
            ])  # Blank option at the top

        # Connect signal to slot
        self.combo.currentIndexChanged.connect(self.on_dropdown_select)

        # Set up layout: Label, Dropdown, Browse Button, and Text Display (in that order)
        layout = QVBoxLayout()
        layout.addWidget(self.label)  # The label at the top
        layout.addWidget(self.combo)  # The dropdown below the label
        layout.addWidget(self.browse_button)  # The button to browse for a folder
        layout.addWidget(self.text_display)  # Text display area below the dropdown

        self.setLayout(layout)
        
        # Set window properties
        self.setWindowTitle('CYB SF Module')
        self.setGeometry(100, 100, 400, 300)

    def setup_logging(self):
        """Set up logging to display messages in the QTextEdit."""
        self.log_handler = QTextEditLogger(self.text_display)
        self.log_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.log_handler.setFormatter(formatter)

        # Add the custom handler to the root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(self.log_handler)
        root_logger.setLevel(logging.INFO)
    
    def on_dropdown_select(self):
        selected_item = self.combo.currentText()

        # Only update the label and text display if a valid item is selected (non-blank)
        if selected_item:
            self.label.setText(f'Selected: {selected_item}')
            self.text_display.append(f'You selected: {selected_item}')  # Append output to the QTextEdit
            self.browse_button.setEnabled(True)  # Enable the button after a selection
        else:
            self.label.setText('Select an item from the dropdown')
            self.browse_button.setEnabled(False)  # Disable the button if no selection

    def browse_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder_path:
            self.selected_folder = folder_path  # Store the selected folder path
            self.text_display.append(f'\nSelected Folder: {self.selected_folder}')  # Append selected folder path to QTextEdit
            
            selected_item = self.combo.currentText()  # Get the selected item
            if selected_item in self.function_mapping:
                self.function_mapping[selected_item](self.selected_folder)  # Call the appropriate function

    def process_cyb(self, folder_path):
        # Processing logic for "Prepare File For CYB"
        
        end_result = to_send_files_to_cybs_main(folder_path)
        self.text_display.append(end_result)
        

    def process_sf(self, folder_path):
        # Processing logic for "Remap To SF"
        
        end_result2 = return_file_from_cybs_main(folder_path)
        self.text_display.append(end_result2)

    def summary(self, folder_path):
        # Processing logic for "SUMMARY"
        
        end_result3 = summary_analysis(folder_path)
        self.text_display.append(end_result3)

    def iPay88_to_secondary_token(self, folder_path):
        # processing logic for ipay88 to secondary token
        end_result4 = import_iPay88_token_to_secondary_token_main(folder_path)
        self.text_display.append(end_result4)

    def NCT_and_EG_to_secondary_token(self, folder_path):

        end_result5 = import_NCT_EG_to_secondary_token_main(folder_path)
        self.text_display.append(end_result5)

    def send_file_to_ipay88(self, folder_path):
        end_result6 = send_file_to_iPay88_main(folder_path)
        self.text_display.append(end_result6)

    def import_iPay88_token_to_main_token(self, folder_path):
        end_result7 = import_iPay88_token_to_main_token_main(folder_path)
        self.text_display.append(end_result7)

        


