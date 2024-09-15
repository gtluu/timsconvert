import os
import re
from timsconvert.data_input import dot_d_detection
from timsconvert.timestamp import get_timestamp
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale, QMetaObject, QObject, QPoint, QRect, QSize,
                            QTime, QUrl, Qt, QTimer, QProcess)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QGradient, QIcon, QImage,
                           QKeySequence, QLinearGradient, QPainter, QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QLabel, QLineEdit, QListView, QMainWindow, QPushButton,
                               QRadioButton, QSizePolicy, QSpinBox, QWidget, QFileDialog, QProgressBar, QDialog,
                               QDialogButtonBox, QVBoxLayout, QMessageBox, QTableWidgetItem)
from timsconvert.timsconvert_gui_template import Ui_TimsconvertGuiWindow


class TimsconvertGuiWindow(QMainWindow, Ui_TimsconvertGuiWindow):
    """
    Class containing all attributes and methods to parse and process GUI parameters for the TIMSCONVERT GUI. UI elements
    are inherited from Ui_TimsconvertGuiWindow.
    """
    def __init__(self):
        super(TimsconvertGuiWindow, self).__init__()

        self.input = {}
        self.args = {'input': [],  # QLineEdit + QPushButton (select directory dialogue button)
                     'outdir': '',  # QLineEdit + QPushButton (select directory dialogue button)
                     'mode': 'centroid',  # QRadioButton
                     'compression': 'zlib',  # QCheckbox
                     'ms2_only': False,  # QCheckbox
                     'use_raw_calibration': False,  # QCheckbox
                     'pressure_compensation_strategy': 'none',  # QRadioButton
                     'exclude_mobility': False,  # QCheckbox
                     'mz_encoding': 64,  # QRadioButton
                     'intensity_encoding': 64,  # QRadioButton
                     'mobility_encoding': 64,  # QRadioButton
                     'barebones_metadata': False,  # QCheckbox
                     'profile_bins': 0,  # QLineEdit
                     'maldi_output_file': 'combined',  # QRadioButton
                     'maldi_plate_map': '',  # QLineEdit + QPushButton (select file dialogue button)
                     'imzml_mode': 'processed',  # QRadioButton
                     'verbose': False}  # QCheckbox

        self.selected_row_from_queue = ''
        self.errors = None

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

        # Initialize Process
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)

        # Run
        self.RunButton.clicked.connect(self.run)

    def show_hide_binning(self):
        """
        Set the visibility of the m/z binning parameters GUI elements based on whether or not Profile mode conversion
        is selected.
        """
        if self.ModeProfileRadio.isChecked():
            self.NumBinsLabel.setVisible(True)
            self.BinSpectraCheckbox.setVisible(True)
            self.NumBinsSpinBox.setVisible(True)
        else:
            self.NumBinsLabel.setVisible(False)
            self.BinSpectraCheckbox.setVisible(False)
            self.NumBinsSpinBox.setVisible(False)

    def browse_input(self):
        """
        Open a QFileDialog to get the path of a directory. The directory can either be a Bruker .d directory for a
        single file or a directory containing one or more Bruker .d directories, which will result in all .d directories
        in all subdirectories being loaded.
        """
        input_path = QFileDialog().getExistingDirectory(self, 'Select Directory...', '')
        if os.path.isdir(input_path):
            if not input_path.endswith('.d'):
                new_input = dot_d_detection(input_path)
            elif input_path.endswith('.d'):
                new_input = [input_path]
            new_input = [i.replace('/', '\\') for i in new_input]
            old_row_count = self.InputList.rowCount()
            self.InputList.setRowCount(self.InputList.rowCount() + len(new_input))
            for row, input_filename in enumerate(new_input, start=old_row_count):
                new_key = os.path.split(input_filename)[-1]
                if new_key in self.input.keys():
                    copy_count = len([i for i in self.input.keys() if i.startswith(new_key)])
                    new_key += f'({str(copy_count)})'
                self.input[new_key] = input_filename
                text_item = QTableWidgetItem(new_key)
                self.InputList.setItem(row, 0, text_item)

    def select_output_directory(self):
        """
        Open a QFileDialog to get the path of the directory in which the converted output files will be saved to.
        """
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
        """
        Select rows from the InputList QTableWidget object and save their indices to the selected_row_from_queue
        attribute.
        """
        self.selected_row_from_queue = self.InputList.selectionModel().selectedIndexes()

    def remove_from_queue(self):
        """
        Remove one or more selected rows from the InputList QTableWidget object.
        """
        for row in sorted([i.row() for i in self.selected_row_from_queue], reverse=True):
            del self.input[self.InputList.item(row, 0).text()]
            self.InputList.removeRow(row)

    def run(self):
        """
        Parse all arguments from GUI elements and run the TIMSCONVERT conversion workflow.
        """
        # Gray out and disable ability to click all buttons.
        self.AddInputDialogueButton.setEnabled(False)
        self.RemoveFromQueueButton.setEnabled(False)
        self.OutputDirectoryBrowseButton.setEnabled(False)
        self.MaldiPlateMapBrowseButton.setEnabled(False)
        self.RunButton.setEnabled(False)

        # Collect arguments from GUI.
        self.args['input'] = list(self.input.values())
        self.args['outdir'] = str(self.OutputDirectoryLine.text())
        if (self.ModeProfileRadio.isChecked() and
                not self.ModeCentroidRadio.isChecked() and
                not self.ModeRawRadio.isChecked()):
            self.args['mode'] = 'profile'
        elif (not self.ModeProfileRadio.isChecked() and
              self.ModeCentroidRadio.isChecked() and
              not self.ModeRawRadio.isChecked()):
            self.args['mode'] = 'centroid'
        elif (not self.ModeProfileRadio.isChecked() and
              not self.ModeCentroidRadio.isChecked() and
              self.ModeRawRadio.isChecked()):
            self.args['mode'] = 'raw'
        if self.CompressionCheckbox.isChecked():
            self.args['compression'] = 'zlib'
        else:
            self.args['compression'] = 'none'
        if self.Ms2OnlyCheckbox.isChecked():
            self.args['ms2_only'] = True
        else:
            self.args['ms2_only'] = False
        if self.RecalibratedDataCheckbox.isChecked():
            self.args['use_raw_calibration'] = False
        else:
            self.args['use_raw_calibration'] = True
        if (self.MobilityCompensationNoneRadio.isChecked() and
                not self.MobilityCompensationGlobalRadio.isChecked() and
                not self.MobilityCompensationFrameRadio.isChecked()):
            self.args['pressure_compensation_strategy'] = 'none'
        elif (not self.MobilityCompensationNoneRadio.isChecked() and
              self.MobilityCompensationGlobalRadio.isChecked() and
              not self.MobilityCompensationFrameRadio.isChecked()):
            self.args['pressure_compensation_strategy'] = 'global'
        elif (not self.MobilityCompensationNoneRadio.isChecked() and
              not self.MobilityCompensationGlobalRadio.isChecked() and
              self.MobilityCompensationFrameRadio.isChecked()):
            self.args['pressure_compensation_strategy'] = 'frame'
        if self.ExcludeMobilityCheckbox.isChecked():
            self.args['exclude_mobility'] = True
        else:
            self.args['exclude_mobility'] = False
        if self.MZEncoding64Radio.isChecked() and not self.MZEncoding32Radio.isChecked():
            self.args['mz_encoding'] = 64
        elif not self.MZEncoding64Radio.isChecked() and self.MZEncoding32Radio.ischecked():
            self.args['mz_encoding'] = 32
        if self.IntensityEncoding64Radio.isChecked() and not self.IntensityEncoding32Radio.isChecked():
            self.args['intensity_encoding'] = 64
        elif not self.IntensityEncoding64Radio.isChecked() and self.IntensityEncoding32Radio.isChecked():
            self.args['intensity_encoding'] = 32
        if self.MobilityEncoding64Radio.isChecked() and not self.MobilityEncoding32Radio.isChecked():
            self.args['mobility_encoding'] = 64
        elif not self.MobilityEncoding64Radio.isChecked() and self.MobilityEncoding32Radio.isChecked():
            self.args['mobility_encoding'] = 32
        if self.BarebonesMetadataCheckbox.isChecked():
            self.args['barebones_metadata'] = True
        else:
            self.args['barebones_metadata'] = False
        if self.BinSpectraCheckbox.isChecked():
            self.args['profile_bins'] = int(self.NumBinsSpinBox.text())
        else:
            self.args['profile_bins'] = 0
        if (self.MaldiOutputFileCombinedRadio.isChecked() and
                not self.MaldiOutputFileIndividualRadio.isChecked() and
                not self.MaldiOutputFileSampleRadio.isChecked()):
            self.args['maldi_output_file'] = 'combined'
        elif (not self.MaldiOutputFileCombinedRadio.isChecked() and
              self.MaldiOutputFileIndividualRadio.isChecked() and
              not self.MaldiOutputFileSampleRadio.isChecked()):
            self.args['maldi_output_file'] = 'individual'
        elif (not self.MaldiOutputFileCombinedRadio.isChecked() and
              not self.MaldiOutputFileIndividualRadio.isChecked() and
              self.MaldiOutputFileSampleRadio.isChecked()):
            self.args['maldi_output_file'] = 'sample'
        self.args['maldi_plate_map'] = str(self.MaldiPlateMapLine.text())
        if self.MaldiImzmlModeProcessedRadio.isChecked() and not self.MaldiImzmlModeContinuousRadio.isChecked():
            self.args['imzml_mode'] = 'processed'
        elif not self.MaldiImzmlModeProcessedRadio.isChecked() and self.MaldiImzmlModeContinuousRadio.isChecked():
            self.args['imzml_mode'] = 'continuous'

        # Convert Data
        if len(self.args['input']) > 0:
            # Build and run command in QProcess.
            process_args = ['TIMSCONVERT_CMD.py']
            for key, value in self.args.items():
                if key == 'input':
                    process_args.append(f'--input')
                    process_args = process_args + self.args['input']
                elif key not in ['ms2_only', 'use_raw_calibration', 'exclude_mobility', 'barebones_metadata', 'verbose']:
                    process_args.append(f'--{key}')
                    process_args.append(str(value))
                elif self.args[key]:
                    process_args.append(f'--{key}')
            self.process.start('python', process_args)

            # Replace queue list with progress bars.
            for row in range(self.InputList.rowCount()):
                progress_bar = QProgressBar()
                progress_bar.setValue(0)
                progress_bar.setFormat(f"{self.InputList.item(row, 0).text()}")
                progress_bar.setObjectName(f"{self.InputList.item(row, 0).text()}")
                progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.InputList.setCellWidget(row, 0, progress_bar)
        else:
            # Show error message if no files are found in the queue.
            error = QMessageBox(self)
            error.setWindowTitle('Error')
            error.setText('No input files found in the queue.')
            error_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'errors')
            if not os.path.isdir(error_dir):
                os.mkdir(error_dir)
            with open(f'{error_dir}\\{get_timestamp()}_error.log', 'w') as error_log:
                error_log.write('stderr')
            error.exec()

    def handle_stdout(self):
        """
        Use the stdout stream text to update the percentage values in the progress bars found in each row of the input
        list queue.
        """
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode('utf8')
        percentage = re.search(r'(\d+)%', stdout)
        dot_d_file = re.search(r'([^:/]+\.d)', stdout)
        if percentage and dot_d_file:
            percentage = int(percentage.group(1))
            dot_d_file = dot_d_file.group(1).split('\\')[-1]
            self.InputList.findChild(QProgressBar, dot_d_file).setValue(percentage)

    def handle_stderr(self):
        """
        Use the stderr stream text to output any errors to an error log and an error message box.
        """
        data = self.process.readAllStandardError()
        stderr = bytes(data).decode('utf8')
        error = QMessageBox(self)
        error.setWindowTitle('Error')
        error_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'errors')
        error.setText(stderr + '\n' + 'Errors have been written to ' + error_dir)
        if not os.path.isdir(error_dir):
            os.mkdir(error_dir)
        with open(f'{error_dir}\\{get_timestamp()}_error.log', 'w') as error_log:
            error_log.write(stderr)
        error.exec()

    def process_finished(self):
        """
        Show a QMessageBox on completion to show that TIMSCONVERT has finished converting data from the current queue.
        """
        finished = QMessageBox(self)
        finished.setWindowTitle('TIMSCONVERT')
        finished.setText('TIMSCONVERT has finished running.')
        finished_button = finished.exec()

        if finished_button == QMessageBox.StandardButton.Ok:
            self.input = {}
            self.args['input'] = []
            self.InputList.setRowCount(0)
            self.AddInputDialogueButton.setEnabled(True)
            self.RemoveFromQueueButton.setEnabled(True)
            self.OutputDirectoryBrowseButton.setEnabled(True)
            self.MaldiPlateMapBrowseButton.setEnabled(True)
            self.RunButton.setEnabled(True)


def main():
    app = QApplication([])

    window = TimsconvertGuiWindow()
    window.show()

    app.exec()


if __name__ == '__main__':
    main()
