import os
from timsconvert.data_input import dot_d_detection
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale, QMetaObject, QObject, QPoint, QRect, QSize,
                            QTime, QUrl, Qt, QTimer)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QGradient, QIcon, QImage,
                           QKeySequence, QLinearGradient, QPainter, QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QLabel, QLineEdit, QListView, QMainWindow, QPushButton,
                               QRadioButton, QSizePolicy, QSpinBox, QWidget, QFileDialog, QProgressBar)
from timsconvert_gui_template import Ui_TimsconvertGuiWindow


class TimsconvertGuiWindow(QMainWindow, Ui_TimsconvertGuiWindow):
    def __init__(self):
        super(TimsconvertGuiWindow, self).__init__()

        self.args = {'input': None,  # QLineEdit + QPushButton (select directory dialogue button)
                     'outdir': None,  # QLineEdit + QPushButton (select directory dialogue button)
                     'outfile': None,  # QLineEdit (only if .d file detected and not other directory)
                     'mode': None,  # QRadioButton
                     'compression': None,  # QCheckbox
                     'ms2_only': None,  # QCheckbox
                     'exclude_mobility': None,  # QCheckbox
                     'encoding': None,  # QRadioButton
                     'barebones_metadata': None,  # QCheckbox
                     'profile_bins': None,  # QLineEdit
                     'maldi_output_file': None,  # QRadioButton
                     'maldi_plate_map': None,  # QLineEdit + QPushButton (select file dialogue button)
                     'imzml_mode': None,  # QRadioButton
                     'chunk_size': None,  # QSpinBox
                     'verbose': None}  # QCheckbox

        self.selected_row_from_queue = ''

        self.setupUi(self)

        # Show/Hide Binning Settings if Profile Mode
        self.ModeProfileRadio.clicked.connect(self.show_hide_binning)
        self.ModeCentroidRadio.clicked.connect(self.show_hide_binning)
        self.ModeRawRadio.clicked.connect(self.show_hide_binning)

        # File browser dialogues
        # Add Input
        self.AddInputDialogueButton.clicked.connect(self.browse_input)
        # Select Output Directory
        self.OutputDirectoryBrowseButton.clicked.connect(self.select_output_directory)
        # Select MALDI Plate Map
        self.MaldiPlateMapBrowseButton.clicked.connect(self.select_maldi_plate_map)

        # Queue
        # Select Input
        self.InputList.selectionModel().selectionChanged.connect(self.select_from_queue)
        # Remove Input
        self.RemoveFromQueueButton.clicked.connect(self.remove_from_queue)

        # Run
        self.RunButton.clicked.connect(self.run)

    def show_hide_binning(self):
        if self.ModeProfileRadio.isChecked():
            self.NumBinsLabel.setVisible(True)
            self.BinSpectraCheckbox.setVisible(True)
            self.NumBinsSpinBox.setVisible(True)
        else:
            self.NumBinsLabel.setVisible(False)
            self.BinSpectraCheckbox.setVisible(False)
            self.NumBinsSpinBox.setVisible(False)

    def browse_input(self):
        input_path = QFileDialog().getExistingDirectory(self, 'Select Directory...', '')
        if os.path.isdir(input_path):
            if not input_path.endswith('.d'):
                self.args['input'] = dot_d_detection(input_path)
            elif input_path.endswith('.d'):
                self.args['input'] = [input_path]
            if self.args['input'] is not None:
                self.args['input'] = [i.replace('/', '\\') for i in self.args['input']]
                self.populate_table(self.args['input'])

    def select_output_directory(self):
        self.args['outdir'] = QFileDialog().getExistingDirectory(self, 'Select Directory...', '').replace('/', '\\')
        self.OutputDirectoryLine.setText(self.args['outdir'])

    def select_maldi_plate_map(self):
        self.args['maldi_plate_map'] = QFileDialog().getOpenFileName(self,
                                                                     'Select MALDI Plate Map...',
                                                                     '',
                                                                     filter='Comma Separated Values (*.csv)')
        self.args['maldi_plate_map'] = self.args['maldi_plate_map'][0].replace('/', '\\')
        self.MaldiPlateMapLine.setText(self.args['maldi_plate_map'])

    def select_from_queue(self):
        self.selected_row_from_queue = self.InputList.selectionModel().selectedIndexes()

    def remove_from_queue(self):
        for row in sorted([i.row() for i in self.selected_row_from_queue], reverse=True):
            self.InputList.removeRow(row)

    def run(self):
        # for now just replaces row with progress bar
        for row in range(self.InputList.rowCount()):
            progress_bar = QProgressBar()
            progress_bar.setValue(0)
            progress_bar.setFormat(f"{self.InputList.item(row, 0).text()}")
            progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.InputList.setCellWidget(row, 0, progress_bar)
        # Set up a timer to simulate real-time updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(1000)  # Update every 1000 milliseconds (1 second)


if __name__ == '__main__':
    app = QApplication([])

    window = TimsconvertGuiWindow()
    window.show()

    app.exec()
