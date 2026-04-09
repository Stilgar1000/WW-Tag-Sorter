import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel

class TagSorterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Tag Sorter GUI')
        layout = QVBoxLayout()

        self.label = QLabel('Select an input database file and output location.')
        layout.addWidget(self.label)

        self.btn_input = QPushButton('Select Input Database')
        self.btn_input.clicked.connect(self.select_input)
        layout.addWidget(self.btn_input)

        self.btn_output = QPushButton('Select Output Location')
        self.btn_output.clicked.connect(self.select_output)
        layout.addWidget(self.btn_output)

        self.setLayout(layout)

    def select_input(self):
        options = QFileDialog.Options()
        self.input_file, _ = QFileDialog.getOpenFileName(self, 'Select Input Database File', os.getcwd(), 'All Files (*)', options=options)
        if self.input_file:
            self.label.setText(f'Selected Input: {self.input_file}')

    def select_output(self):
        options = QFileDialog.Options()
        self.output_directory = QFileDialog.getExistingDirectory(self, 'Select Output Location', os.getcwd(), options=options)
        if self.output_directory:
            self.label.setText(f'Selected Output Directory: {self.output_directory}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TagSorterApp()
    ex.show()
    sys.exit(app.exec_())