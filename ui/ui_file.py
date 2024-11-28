import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel, QTextEdit, QPushButton, QFileDialog


from logic.return_file_logic import return_file_process_flow
from logic.send_file_logic import send_file_process_flow
from logic.summary import summary_analysis



class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_folder = None  # Initialize variable to store the selected folder path
        self.function_mapping = {
            'Prepare File For CYB': self.process_cyb,
            'Remap To SF': self.process_sf,
            'Analysis': self.summary
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
        self.combo.addItems(['', 'Prepare File For CYB', 'Remap To SF', 'Analysis'])  # Blank option at the top

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
        
        end_result = send_file_process_flow(folder_path)
        self.text_display.append(end_result)
        

    def process_sf(self, folder_path):
        # Processing logic for "Remap To SF"
        
        end_result2 = return_file_process_flow(folder_path)
        self.text_display.append(end_result2)

    def summary(self, folder_path):
        # Processing logic for "SUMMARY"
        
        end_result3 = summary_analysis(folder_path)
        self.text_display.append(end_result3)
        
        


