"""

Josh Sennett
Yash Adhikari
CS 535

User Interface

# Requirements:

GUI:
enables the user to observe the state of the architecture as a program executes. Thus,
somewhat like a debugger, it will allow single stepping, execution to a breakpoint, and/or
for a specified number of cycles. It will need commands for loading and saving
programs (or the entire state), and resetting the state.

The user interface will need to be extended to
support running to completion, breakpoints, viewing memory in different formats
(instruction, decimal, hex, etc.), and managing the configurations of the simulator. 

Display clock cycles

For the demonstration, you just need to have enough instructions working to show that
all of the major operation types (load, store, ALU, branch) are working. The simulator
should be able to load a binary program, and then single-step execute it. The program
must at least demonstrate loading and storing values between memory and registers,
register-to-register arithmetic, and a conditional branch. A good demonstration is the
equivalent of a for loop that reads a series of pairs of values from memory, adds them,
stores the results back to memory, and exits when the loop control counter reaches the
termination condition.

The simulator should keep and display a count of the execution cycles, and it should be
possible to run both with and without a cache, and in a mode where the pipeline is
disabled (each instruction goes all the way through before the next one starts).
The user interface at this stage should support viewing the registers (including PC,
status, etc.) and memory (main and cache) in hexadecimal, loading a program from a
file, and stepping through it to see how the state changes. At this point, you will have all
of the major components of the simulator working.
"""
from PyQt5.QtCore import QFileInfo, QSettings, QCoreApplication
from PyQt5 import QtWidgets, QtGui
from mainwindow import Ui_mainwindow
from simulator import Simulator
from memory import Memory, Cache
import assembler
import sys

import logging
logging.basicConfig(level=logging.INFO)


class ApplicationWindow(QtWidgets.QMainWindow):


    def __init__(self):
        super(ApplicationWindow, self).__init__()

        settings = QSettings("gui.ini", QSettings.IniFormat)


        # Set up UI
        self.ui = Ui_mainwindow()
        self.ui.setupUi(self)

        # Error dialog box
        self.ui.error_dialog = QtWidgets.QErrorMessage()
        logging.info("GUI: UI is setup.")

        # Connect a simulator
        self.simulator = Simulator()

        # TODO: Add animation pane, if enough time.

        # Update data tables, pulling info from simulator
        self.update_data()

        # Add button functionality
        # 
        #     IN PROGRESS:
        # step 1 cycle
        # step n cycles
        # step until breakpoint
        # step until completion        
        # 
        #     TODO:
        # reset
        self.ui.setConfigurationButton.clicked.connect(self.configure_cache)
        self.ui.stepButton.clicked.connect(self.step)
        self.ui.stepNCyclesButton.clicked.connect(self.step_n)
        self.ui.stepBreakpointButton.clicked.connect(self.step_breakpoint)
        self.ui.stepCompletionButton.clicked.connect(self.step_completion)
        self.ui.importButton.clicked.connect(self.import_file)
        self.ui.exportButton.clicked.connect(self.export_file)
        self.ui.resetButton.clicked.connect(self.reset)
        self.ui.loadButton.clicked.connect(self.load)
        self.ui.saveButton.clicked.connect(self.save)
        self.ui.restoreButton.clicked.connect(self.restore)
        self.ui.addBreakpointButton.clicked.connect(self.add_breakpoint)
        self.ui.removeBreakpointButton.clicked.connect(self.remove_breakpoint)
        self.ui.memoryDisplayBox.activated.connect(self.update_data)

        # Add input validators
        self.ui.L1Lines.setValidator(QtGui.QIntValidator(1, 2**26))
        self.ui.L1Cycles.setValidator(QtGui.QIntValidator(0, 1000))
        self.ui.L2Lines.setValidator(QtGui.QIntValidator(1, 2**26))
        self.ui.L2Cycles.setValidator(QtGui.QIntValidator(0, 1000))
        self.ui.L3Lines.setValidator(QtGui.QIntValidator(1, 2**26))
        self.ui.L3Cycles.setValidator(QtGui.QIntValidator(0, 1000))
        self.ui.memoryCycles.setValidator(QtGui.QIntValidator(0, 1000))
        self.ui.memoryLines.setValidator(QtGui.QIntValidator(1, 32))
        self.ui.breakpoint.setValidator(QtGui.QIntValidator(1, 10000))

        # Qt Designer is buggy, and a few settings are not being preserved.
        # Overwrite these settings to ensure they are carried over.
        # TODO: See if gui.ui is corrected, and if so, remove this.
        self.ui.registerTable.verticalHeader().setVisible(True)
        self.ui.registerTable.horizontalHeader().setVisible(True)
        self.ui.instructionTable.verticalHeader().setVisible(True)
        self.ui.instructionTable.horizontalHeader().setVisible(True)
        self.ui.memoryTable.horizontalHeader().setVisible(True)
        self.ui.memoryTable.verticalHeader().setVisible(False)
        self.ui.cacheTable.horizontalHeader().setVisible(True)
        self.ui.cacheTable.verticalHeader().setVisible(False)

        # Switch to default initial tabs
        self.ui.tabs.setCurrentIndex(0)
        self.ui.dataTabs.setCurrentIndex(0)


    def configure_cache(self):
        logging.info("GUI: configure_cache()")

        # Get configuration from user input
        configuration = {
            # L1
            "L1Enabled": self.ui.L1Enabled.isChecked(),
            "L1Associativity": self.ui.L1Associativity.currentText(),              
            "L1Lines": self.ui.L1Lines.text(),
            "L1WordsPerLine": self.ui.L1WordsPerLine.currentText(),
            "L1Cycles": self.ui.L1Cycles.text(),

            # L2
            "L2Enabled": self.ui.L2Enabled.isChecked(),
            "L2Associativity": self.ui.L2Associativity.currentText(),              
            "L2Lines": self.ui.L2Lines.text(),
            "L2WordsPerLine": self.ui.L2WordsPerLine.currentText(),
            "L2Cycles": self.ui.L2Cycles.text(),

            # L3
            "L3Enabled": self.ui.L3Enabled.isChecked(),
            "L3Associativity": self.ui.L3Associativity.currentText(),              
            "L3Lines": self.ui.L3Lines.text(),
            "L3WordsPerLine": self.ui.L3WordsPerLine.currentText(),
            "L3Cycles": self.ui.L3Cycles.text(),

            # Final column
            "writePolicyBox": self.ui.writePolicyBox.currentText(),
            "evictionPolicyBox": self.ui.evictionPolicyBox.currentText(),
            "memoryLines": self.ui.memoryLines.text(),
            "memoryCycles": self.ui.memoryCycles.text(),
            "pipelineEnabledButton": self.ui.pipelineEnabledButton.isChecked()
        }
        logging.info('GUI: Configuration:\n\t' + '\n\t'.join(["{}-{}".format(k, v) for (k, v) in configuration.items()]))

        # TODO: Implement write and eviction policy settings + pipeline 
        # enabled, and use these configurations to set the policies.

        memory_heirarchy = []
        try:

            # Create Memory Objects
            DRAM = Memory(
                lines=2**int(configuration["memoryLines"]),
                delay=int(configuration["memoryCycles"]),
                noisy=False,
                name="DRAM")

            # Insert into memory heirarchy
            memory_heirarchy.insert(0, DRAM)
            logging.info("GUI: DRAM added.")

            # Build the levels of the cache
            for level in ["L3", "L2", "L1"]:

                if configuration[level + "Enabled"]:

                    # Parse associativity options
                    if configuration[level + "Associativity"] == "Direct-Mapped":
                        associativity = 1
                    elif configuration[level + "Associativity"] == "N-way":
                        associativity = configuration[level + "Lines"]
                    else:
                        associativity = int(''.join(x for x in configuration[level + "Associativity"] if x.isdigit()))

                    # Associativity shouldn't be greater than # lines
                    if associativity > int(configuration[level + "Lines"]):
                        raise ValueError('Cannot set cache associativity higher than # lines')

                    # Create Cache Objects
                    cache = Cache(
                        lines=int(configuration[level + "Lines"]),
                        words_per_line=int(configuration[level + "WordsPerLine"]),
                        delay=int(configuration[level + "Cycles"]),
                        associativity=associativity,
                        next_level=memory_heirarchy[0],
                        noisy=False,
                        name=level)

                    # Insert into memory heirarchy
                    memory_heirarchy.insert(0, cache)
                    logging.info("GUI: {} cache added.".format(level))

        except ValueError as e:
            self.ui.error_dialog.showMessage(str(e))
            return

        # Once validated, use configuration to create simulator memory_heirarchy
        self.simulator.memory_heirarchy = memory_heirarchy
        logging.info(str(self.simulator.memory_heirarchy))
        for level in self.simulator.memory_heirarchy:
            logging.info(level)

        # Last, clear and update the cache and memory tables
        self.update_data()



    def step(self):
        logging.info("GUI: step()")

        self.simulator.step() # update simulator
        self.update_data()    # update UI
        pass

    def step_n(self):
        # TODO: Implement this method
        logging.info("GUI: step_n()")

        try:
            n = int(self.ui.stepSize.text())
        except ValueError as e:
            self.ui.error_dialog.showMessage(str(e))
            return

        for _ in range(n):
            self.simulator.step()
        self.update_data()

    def step_breakpoint(self):
        # TODO: Implement this method
        logging.info("GUI: step_breakpoint()")
        pass

    def step_completion(self):
        # TODO: Implement this method
        logging.info("GUI: step_completion()")
        pass

    def import_file(self):
        # TODO:
        # A next step would be to import a program in progress -- including 
        # all data, configurations, and current state of the program.
        # This requires serialize/deserializing all parts of the program.
        # So, do this part last.
        logging.info("GUI: import_file()")

        # Get the filename
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog # this prevents OSX warning message
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", "","All Files (*);;Assembly Files (*.asm)", options=options)
        if filename:
            logging.info("GUI: reading " + filename)
        else:
            # If escaped, return without importing.
            return

        # Read the file
        with open(filename) as f:
            file_contents = f.read()

        # Copy contents into the code editor
        self.ui.codeEditor.setPlainText(file_contents)

        # Switch to the code editor tab
        self.ui.tabs.setCurrentIndex(0)

    def export_file(self):
        # TODO:
        # A next step would be to export a program in progress -- including 
        # all data, configurations, and current state of the program.
        # This requires serialize/deserializing all parts of the program.
        # So, do this part last.
        logging.info("GUI: export_file()")

        # Get the filename
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog # this prevents OSX warning message
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", "","All Files (*);;Assembly Files (*.asm)", options=options)
        if filename:
            logging.info("GUI: writing to " + filename)

        # Write the contents of the editor to file
        with open(filename, 'w') as f:
            f.write(self.ui.codeEditor.toPlainText())

    def load(self):
        """Load assembly instructions into the instruction table"""
        logging.info("GUI: reset()")

        code = self.ui.codeEditor.toPlainText()
        logging.info("Current editor contents: \n\t {}".format(code))

        # Parse text into assembly instructions
        text_instructions = assembler.parse_text(code)

        # Convert assembly into machine code
        numerical_instructions = [assembler.assemble_instruction(line) for line in text_instructions]

        # Update the instructions table
        self.ui.instructionTable.setRowCount(len(text_instructions))
        for idx in range(len(text_instructions)):
            self.ui.instructionTable.setItem(idx, 0, QtWidgets.QTableWidgetItem(text_instructions[idx]))
            self.ui.instructionTable.setItem(idx, 1, QtWidgets.QTableWidgetItem(self.display(numerical_instructions[idx])))
            self.ui.instructionTable.setItem(idx, 2, QtWidgets.QTableWidgetItem("Waiting..."))
   
        self.ui.tabs.setCurrentIndex(1)


    def reset(self):
        # TODO: Implement this method
        logging.info("GUI: reset()")
        pass

    def add_breakpoint(self):
        logging.info("GUI: add_breakpoint()")
        try:
            n = int(self.ui.breakpoint.text())
            if n < 1:
                raise ValueError("Breakpoint must be at least 1")
        except ValueError as e:
            self.ui.error_dialog.showMessage(str(e))
            return

        # Update the instruction table with the breakpoint
        self.ui.instructionTable.setItem(n - 1, 3, QtWidgets.QTableWidgetItem("X"))

        # Switch to the instructions table to show the change
        self.ui.tabs.setCurrentIndex(1)

    def remove_breakpoint(self):
        # TODO: Implement this method
        logging.info("GUI: remove_breakpoint()")
        try:
            n = int(self.ui.breakpoint.text())
        except ValueError as e:
            self.ui.error_dialog.showMessage(str(e))
            return

        # Update the instruction table to remove the breakpoint
        self.ui.instructionTable.setItem(n - 1, 3, QtWidgets.QTableWidgetItem(""))

        # Switch to the instructions table to show the change
        self.ui.tabs.setCurrentIndex(1)

    def update_data(self):
        # TODO: 
        #   currently, we are rewriting the entire memory contents each time we update
        #   which is once per step-1/step-N. This is currently quite fast (no noticable lag)
        #   but if it slows down performance, we can change this to update only parts that change.
        #   For example, one method updates for a new configuration (heavy update)
        #   and another updates if only a few values change (light update)
        logging.info("GUI: update_data()")

        # Update the program counter and cycle count
        self.ui.currentCycle.setText(str(self.simulator.cycle))
        self.ui.programCounter.setText(self.display(self.simulator.PC))


        # Determine table dimensions
        register_rows, register_columns = 32, 2 
        memory_rows, memory_columns = self.simulator.memory_heirarchy[-1].lines, 2
        if len(self.simulator.memory_heirarchy) == 1:
            # If there is no cache, just have a placeholder table.
            cache_rows, cache_columns = 32, (4 + 1) 
            self.ui.cacheTable.setHorizontalHeaderLabels(["Level", "Tag", "Index", "Valid", "Word 1"])

        else:
            # If there is a cache, determine table size from the levels of the simulator's memory heirarchy

            # The rows are the lines in each of the cache levels
            cache_rows = sum([self.simulator.memory_heirarchy[level].lines
                for level in range(len(self.simulator.memory_heirarchy) - 1)])

            # The columns are Level, Tag, Index, Valid, and [Words]; so, 4 + words per line)
            max_num_words_per_line = max([self.simulator.memory_heirarchy[level].words_per_line
                for level in range(len(self.simulator.memory_heirarchy) - 1)])
            cache_columns = 4 + max_num_words_per_line
            self.ui.cacheTable.setHorizontalHeaderLabels(["Level", "Tag", "Index", "Valid"] + ["Word " + str(i + 1) for i in range(max_num_words_per_line)])

        logging.info("register size: " + str((register_rows, register_columns)))
        logging.info("memory size: " + str((memory_rows, memory_columns)))
        logging.info("cache size: " + str((cache_rows, cache_columns)))

        # Update table dimensions
        self.ui.registerTable.setRowCount(register_rows)
        self.ui.registerTable.setColumnCount(register_columns)
        self.ui.memoryTable.setRowCount(memory_rows)
        self.ui.memoryTable.setColumnCount(memory_columns)
        self.ui.cacheTable.setRowCount(cache_rows)
        self.ui.cacheTable.setColumnCount(cache_columns)

        # Update table contents
        # Register table
        for idx in range(32):
            # TODO: see if there is a more efficient way than replacing cell by cell
            # TODO: use display format to adjust string representation. Use instead of str()
            self.ui.registerTable.setItem(idx, 0, QtWidgets.QTableWidgetItem(self.display(self.simulator.R[idx])))
            self.ui.registerTable.setItem(idx, 1, QtWidgets.QTableWidgetItem(self.display(self.simulator.F[idx])))

        # Memory table
        for idx, value in enumerate(self.simulator.memory_heirarchy[-1].data):
            self.ui.memoryTable.setItem(idx,0, QtWidgets.QTableWidgetItem(self.display(idx)))
            self.ui.memoryTable.setItem(idx,1, QtWidgets.QTableWidgetItem(self.display(value)))
            
        # Cache table
        for level in range(len(self.simulator.memory_heirarchy) - 1):
            for idx, row in enumerate(self.simulator.memory_heirarchy[level].data):

                # Index within the cache table
                # Since cache levels are squashed into a single table, 
                # L2 lines should appear after L1.
                cache_table_idx = self.idx_to_cache_table_idx(idx, level)

                # Level Name, Tag, Index, Valid
                self.ui.cacheTable.setItem(cache_table_idx, 0, QtWidgets.QTableWidgetItem(self.simulator.memory_heirarchy[level].name))
                self.ui.cacheTable.setItem(cache_table_idx, 1, QtWidgets.QTableWidgetItem(self.display(self.simulator.memory_heirarchy[level].data[idx][0])))
                self.ui.cacheTable.setItem(cache_table_idx, 2, QtWidgets.QTableWidgetItem(self.display(idx)))
                self.ui.cacheTable.setItem(cache_table_idx, 3, QtWidgets.QTableWidgetItem(self.display(self.simulator.memory_heirarchy[level].data[idx][-1])))

                for offset in range(self.simulator.memory_heirarchy[level].words_per_line):
                    self.ui.cacheTable.setItem(cache_table_idx, 4 + offset, QtWidgets.QTableWidgetItem(self.display(self.simulator.memory_heirarchy[level].data[idx][1 + offset])))

    def idx_to_cache_table_idx(self, idx, level):
        """Since cache contents are appended to a single cache table, this function
        converts a cache index for a level into a whole table index."""
        displacement = 0
        for prior_level in range(level):
            displacement += self.simulator.memory_heirarchy[prior_level].lines
        return idx + displacement


    def display(self, n, min_bits=1):
        """Display an int n according to the set display format"""
        # TODO: If we want leading zeros, implement the min_bits argument to specify extent of left-padding.
        # For now, ignore leading zeros; I think this will look better.
        # TODO: Set alignment of tables; data should be right justified.
        display_format = self.ui.memoryDisplayBox.currentText()
        if display_format == "Binary":
            return bin(n)[2:] 
        elif display_format == "Hexadecimal":
            return hex(n)
        else:
            return str(n)

    def save(self):
        # TODO: Restore is buggy; it does not restore labels and table contents.
        # We may have to manually iterate over settings to save the right things to the INI.
        # Get the filename
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog # this prevents OSX warning message
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", "","All Files (*);;INI Files (*.ini)", options=options)
        if filename:
            logging.info("GUI: saving program to " + filename)
        else:
            return

        # Write the contents of the editor to file
        settings = QSettings(filename, QSettings.IniFormat)
        
        for w in QtWidgets.qApp.allWidgets():
            mo = w.metaObject()
            if w.objectName() != "":
                for i in range(mo.propertyCount()):
                    name = mo.property(i).name()
                    settings.setValue("{}/{}".format(w.objectName(), name), w.property(name))

    def restore(self):
        # TODO: Restore is buggy; it does not restore labels and table contents.
        # We may have to manually iterate over settings to save the right things to the INI.
        # Get the filename
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog # this prevents OSX warning message
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", "","All Files (*);;INI Files (*.ini)", options=options)
        if filename:
            logging.info("GUI: restoring program " + filename)
        else:
            # If escaped, return without importing.
            return

        settings = QSettings(filename, QSettings.IniFormat)
        file_info = QFileInfo(settings.fileName())

        if file_info.exists() and file_info.isFile():
            for w in QtWidgets.qApp.allWidgets():
                mo = w.metaObject()
                if w.objectName() != "":
                    for i in range(mo.propertyCount()):
                        name = mo.property(i).name()
                        val = settings.value("{}/{}".format(w.objectName(), name), w.property(name))
                        w.setProperty(name, val)
        else:
            logging.info("GUI: failed to restore " + filename)


def main():
    app = QtWidgets.QApplication(sys.argv)
    QCoreApplication.setOrganizationName("ELISA")
    QCoreApplication.setOrganizationDomain("github.com/jsennett/ELISA.git")
    QCoreApplication.setApplicationName("ELISA")    
    application = ApplicationWindow()
    application.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()