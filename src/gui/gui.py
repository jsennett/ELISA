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

Next steps:

    implement breakpoints
    implement step until breakpoint
    implement step until completion
    correctly export/restore program
    catch exceptions rather than crashing
    split display format into two options for data display and address/tag/idx display

"""
from PyQt5.QtCore import QCoreApplication
from PyQt5 import QtWidgets, QtGui
from mainwindow import Ui_mainwindow
from simulator import Simulator
from memory import Memory, Cache
import assembler
import sys

import logging
# logging.basicConfig(level=logging.DEBUG)


class ApplicationWindow(QtWidgets.QMainWindow):


    def __init__(self):
        super(ApplicationWindow, self).__init__()

        # Set up UI
        self.ui = Ui_mainwindow()
        self.ui.setupUi(self)
        self.setWindowTitle('ELISA')

        # Error dialog box
        self.error_dialog = QtWidgets.QErrorMessage()
        logging.info("GUI: UI is setup.")

        # Connect a simulator
        self.simulator = Simulator()

        # Update data tables, pulling info from simulator
        self.update_data()

        # Add button functionality
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
        self.ui.L1Lines.setValidator(QtGui.QIntValidator(1, 32))
        self.ui.L1Cycles.setValidator(QtGui.QIntValidator(0, 300))
        self.ui.L2Lines.setValidator(QtGui.QIntValidator(1, 32))
        self.ui.L2Cycles.setValidator(QtGui.QIntValidator(0, 300))
        self.ui.L3Lines.setValidator(QtGui.QIntValidator(1, 32))
        self.ui.L3Cycles.setValidator(QtGui.QIntValidator(0, 300))
        self.ui.memoryCycles.setValidator(QtGui.QIntValidator(0, 1000))
        self.ui.memoryLines.setValidator(QtGui.QIntValidator(1, 32))
        self.ui.breakpoint.setValidator(QtGui.QIntValidator(1, 10000))

        # Qt Designer is buggy, and a few settings are not being preserved.
        # Overwrite these settings to ensure they are carried over.
        # TODO: See if gui.ui is corrected, and if so, remove this.
        # TODO: Change register table vertical header to be 0-indexed.
        self.ui.registerTable.verticalHeader().setVisible(True)
        self.ui.registerTable.horizontalHeader().setVisible(True)
        self.ui.instructionTable.verticalHeader().setVisible(True)
        self.ui.instructionTable.horizontalHeader().setVisible(True)
        self.ui.memoryTable.horizontalHeader().setVisible(True)
        self.ui.memoryTable.verticalHeader().setVisible(False)
        self.ui.cacheTable.horizontalHeader().setVisible(True)
        self.ui.cacheTable.verticalHeader().setVisible(False)

        # Set lines per
        self.ui.L1WordsPerLine.setCurrentIndex(2)
        self.ui.L2WordsPerLine.setCurrentIndex(2)
        self.ui.L3WordsPerLine.setCurrentIndex(2)

        # Switch to default initial tabs
        self.ui.tabs.setCurrentIndex(0)
        self.ui.dataTabs.setCurrentIndex(0)
        self.statusBar().showMessage("Welcome!")

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
            "memoryLines": self.ui.memoryLines.text(),
            "memoryCycles": self.ui.memoryCycles.text(),
            "pipelineEnabledButton": self.ui.pipelineEnabledButton.isChecked()
        }
        logging.info('GUI: Configuration:\n\t' + '\n\t'.join(["{}-{}".format(k, v) for (k, v) in configuration.items()]))

        # With a new configuration of the cache, the simulator is reset.
        self.simulator = Simulator()
        memory_heirarchy = []
        try:

            # Validate memory size
            memory_size = int(configuration['memoryLines'])
            if memory_size > 32 or memory_size <= 0:
                raise ValueError("Invalid memory size: {}".format(memory_size))
            lines = 2**memory_size

            # Validate delay
            memory_cycles = int(configuration["memoryCycles"])
            if memory_cycles < 0 or memory_cycles > 300:
                raise ValueError("Unreasonable memory delay specified: {}".format(memory_cycles))

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

                    # Calculate number of lines
                    cache_size = int(configuration[level + 'Lines'])
                    if cache_size > 32 or cache_size <= 0:
                        raise ValueError("Invalid cache size: {}".format(cache_size))
                    lines = 2**cache_size

                    # Parse associativity options
                    if configuration[level + "Associativity"] == "Direct-Mapped":
                        associativity = 1
                    elif configuration[level + "Associativity"] == "N-way":
                        associativity = lines
                    else:
                        associativity = int(''.join(
                            x for x in configuration[level + "Associativity"]
                            if x.isdigit()))

                    # Associativity shouldn't be greater than # lines
                    if associativity > lines:
                        raise ValueError('Cannot set cache associativity higher than # lines')

                    # Cycles should be reasonable
                    cache_cycles = int(configuration[level + "Cycles"])
                    if cache_cycles < 0 or cache_cycles > 300:
                        raise ValueError("Unreasonable cache delay specified: {}".format(cache_cycles))

                    # Create Cache Objects
                    cache = Cache(
                        lines=lines,
                        words_per_line=int(configuration[level + "WordsPerLine"]),
                        delay=int(cache_cycles),
                        associativity=associativity,
                        next_level=memory_heirarchy[0],
                        noisy=False,
                        name=level)

                    # Insert into memory heirarchy
                    memory_heirarchy.insert(0, cache)
                    logging.info("GUI: {} cache added.".format(level))

        except ValueError as e:
            self.error_dialog.showMessage(str(e))
            return

        # Once validated, use configuration to create simulator memory_heirarchy
        self.simulator.memory_heirarchy = memory_heirarchy
        logging.info(str(self.simulator.memory_heirarchy))
        for level in self.simulator.memory_heirarchy:
            logging.info(level)

        # Enable or disable pipeline depending on user choice
        self.simulator.pipeline_enabled = configuration['pipelineEnabledButton']

        # Last, clear and update the cache and memory tables, and load instructions (if any)
        self.update_data()
        self.load()
        self.statusBar().showMessage("Memory configured.")


    def step(self):
        logging.info("GUI: step()")

        if self.simulator.end_of_program:
            self.statusBar().showMessage("End of program.")
            return

        try:
            self.simulator.step()  # update simulator
            self.update_data()     # update UI
            self.statusBar().showMessage("Step taken.")
        except AttributeError as e:
            msg = str(e) + "... Perhaps you haven't loaded any instructions yet?"
            self.error_dialog.showMessage(msg)
            return


    def step_n(self):
        # TODO: Implement this method
        logging.info("GUI: step_n()")

        try:
            n = int(self.ui.stepSize.text())
        except ValueError as e:
            self.error_dialog.showMessage(str(e))
            return

        # Step n times, or until end of program.
        for _ in range(n):

            # If end of program before end of n steps
            if self.simulator.end_of_program:
                self.update_data()
                self.statusBar().showMessage("End of program.")
                return

            self.simulator.step()

        self.update_data()
        self.statusBar().showMessage("{} steps taken.".format(n))

    def step_breakpoint(self):
        # TODO: Implement this method
        logging.info("GUI: step_breakpoint()")

        # Step at least once; break out of loop once we hit a breakpoint,
        # or once our program ends
        while True:
            self.simulator.step()

            # Initial memory location of text; hardcoded 0 for now
            text_offset = 0x0

            # Instruction num; PC + text offset, plus 1 since 1-indexed
            instruction_num = (self.simulator.PC + text_offset) // 4

            # If we're at the end of the program, stop stepping
            if self.simulator.end_of_program:
                self.statusBar().showMessage("End of program.")
                break

            # Current breakpoint?
            logging.warning("Getting BP value from cell ({}, {})".format(instruction_num, 3))
            bp_cell = self.ui.instructionTable.item(instruction_num, 3)
            if bp_cell is not None and bp_cell.text() == 'X':
                # Note: breakpoints are 1-indexed while cells are 0 indexed
                # So, the breakpoint is instruction_num + 1
                self.statusBar().showMessage("Stepped until breakpoint {}".format(instruction_num + 1))
                break

        self.update_data()

    def step_completion(self):
        # TODO: Implement this method
        logging.info("GUI: step_completion()")

        while not self.simulator.end_of_program:
            self.simulator.step()

    def import_file(self):
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
        self.statusBar().showMessage("Code imported.")

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
        self.statusBar().showMessage("Code exported.")

    def load(self):
        """Load assembly instructions into the instruction table"""
        logging.info("GUI: load()")

        code = self.ui.codeEditor.toPlainText()
        logging.info("Current editor contents: \n\t {}".format(code))

        try:
            # Parse text into assembly instructions
            text_instructions = assembler.assemble_to_text(code)

            # Convert assembly into machine code
            numerical_instructions = assembler.assemble_to_numerical(code)
        except:
            self.error_dialog.showMessage("Unable to assemble instructions." +
                                          "\nPleases check your syntax.")
            return


        # Reset before setting the new instructions
        self.simulator.reset()
        self.simulator.set_instructions(numerical_instructions)

        # Update the instructions table
        self.ui.instructionTable.setRowCount(len(text_instructions))
        for idx in range(len(text_instructions)):
            self.ui.instructionTable.setItem(idx, 0, QtWidgets.QTableWidgetItem(hex(4 * idx)))
            self.ui.instructionTable.setItem(idx, 1, QtWidgets.QTableWidgetItem(text_instructions[idx]))
            self.ui.instructionTable.setItem(idx, 2, QtWidgets.QTableWidgetItem("{:08X}".format(numerical_instructions[idx])[2:]))

        self.ui.tabs.setCurrentIndex(1)
        self.statusBar().showMessage("Instructions loaded.")

        # Update data; since instructions are in memory, we need to update.
        self.update_data()


    def reset(self):
        logging.info("GUI: reset()")

        # Reset the simulator
        self.simulator.reset()
        self.update_data()

        # Reset the instruction table
        self.ui.instructionTable.setRowCount(0)
        self.statusBar().showMessage("Instructions reset.")


    def add_breakpoint(self):
        logging.info("GUI: add_breakpoint()")

        # Validate breakpoint
        try:
            n = int(self.ui.breakpoint.text())
            if n < 1:
                raise ValueError("Breakpoint must be at least 1")
        except ValueError as e:
            self.error_dialog.showMessage(str(e))
            return

        # Update the instruction table with the breakpoint
        self.ui.instructionTable.setItem(n - 1, 3, QtWidgets.QTableWidgetItem("X"))

        # Switch to the instructions table to show the change
        self.ui.tabs.setCurrentIndex(1)
        self.statusBar().showMessage("Breakpont added at instruction #{}".format(n))

    def remove_breakpoint(self):
        # TODO: Implement this method
        logging.info("GUI: remove_breakpoint()")
        try:
            n = int(self.ui.breakpoint.text())
        except ValueError as e:
            self.error_dialog.showMessage(str(e))
            return

        # Update the instruction table to remove the breakpoint
        self.ui.instructionTable.setItem(n - 1, 3, QtWidgets.QTableWidgetItem(""))

        # Switch to the instructions table to show the change
        self.ui.tabs.setCurrentIndex(1)
        self.statusBar().showMessage("Breakpont removed at instruction #: {}".format(n))

    def update_data(self):
        logging.info("GUI: update_data()")

        # Update the program counter and cycle count
        self.ui.currentCycle.setText(str(self.simulator.cycle))
        self.ui.programCounter.setText(self.display(self.simulator.PC))

        # Determine table dimensions
        register_rows, register_columns = 32 + 1, 2

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
            # Set R0-R31 and F0-F31
            self.ui.registerTable.setItem(idx, 0, QtWidgets.QTableWidgetItem(self.display(self.simulator.R[idx])))
            self.ui.registerTable.setItem(idx, 1, QtWidgets.QTableWidgetItem(self.display(self.simulator.F[idx])))

        # Set LO / HI
        self.ui.registerTable.setItem(32, 0, QtWidgets.QTableWidgetItem(self.display(self.simulator.LO)))
        self.ui.registerTable.setItem(32, 1, QtWidgets.QTableWidgetItem(self.display(self.simulator.HI)))

        # 0-indexed vertical header for registers $R0-$R32, $F0-$F32
        self.ui.registerTable.setVerticalHeaderLabels([str(n) for n in range(32)]
                                                      + ["L/H"])

        # Memory table
        for idx, value in enumerate(self.simulator.memory_heirarchy[-1].data):
            self.ui.memoryTable.setItem(idx,0, QtWidgets.QTableWidgetItem(hex(4 * idx)))
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
                self.ui.cacheTable.setItem(cache_table_idx, 1, QtWidgets.QTableWidgetItem(bin(self.simulator.memory_heirarchy[level].data[idx][0])[2:]))
                self.ui.cacheTable.setItem(cache_table_idx, 2, QtWidgets.QTableWidgetItem(bin(idx)[2:]))
                self.ui.cacheTable.setItem(cache_table_idx, 3, QtWidgets.QTableWidgetItem(bin(self.simulator.memory_heirarchy[level].data[idx][-1])[2:]))

                for offset in range(self.simulator.memory_heirarchy[level].words_per_line):
                    self.ui.cacheTable.setItem(cache_table_idx, 4 + offset, QtWidgets.QTableWidgetItem(self.display(self.simulator.memory_heirarchy[level].data[idx][1 + offset])))

        # Pipeline table: 4 buffer rows, Cycle, PC, status, dependencies and # memory levels
        pipeline_rows = 4 + 5 + len(self.simulator.memory_heirarchy)
        self.ui.pipelineTable.setRowCount(pipeline_rows)

        # Status Row
        self.ui.pipelineTable.setItem(0, 0, QtWidgets.QTableWidgetItem(str(self.simulator.status)))

        # Dependencies
        self.ui.pipelineTable.setItem(1, 0, QtWidgets.QTableWidgetItem(str(['$r'+str(n) for n in self.simulator.R_dependences])))
        self.ui.pipelineTable.setItem(2, 0, QtWidgets.QTableWidgetItem(str(['$f'+str(n) for n in self.simulator.F_dependences])))

        # Buffer rows
        for idx in range(4):
            self.ui.pipelineTable.setItem(idx + 3, 0, QtWidgets.QTableWidgetItem(str(self.simulator.buffer[idx])))

        # Cycle, PC
        self.ui.pipelineTable.setItem(7, 0, QtWidgets.QTableWidgetItem(str(self.simulator.cycle)))
        self.ui.pipelineTable.setItem(8, 0, QtWidgets.QTableWidgetItem(str(self.simulator.PC)))

        # Memory and Cache levels
        for idx, level in enumerate(self.simulator.memory_heirarchy):
            self.ui.pipelineTable.setItem(idx + 9, 0, QtWidgets.QTableWidgetItem(str(level)))

        # Pipelining enabled
        self.ui.pipelineTable.setItem(9 + len(self.simulator.memory_heirarchy),
             0, QtWidgets.QTableWidgetItem(self.simulator.pipeline_enabled))

        # Set pipline table row labels
        pipelineHeaders = (
            ['Status', '$R Dependencies', '$F Dependencies'] +
            ['IF -> ID', 'ID -> EX', 'EX -> MEM', 'MEM-> WB', 'Cycle', 'PC'] +
            [level.name for level in self.simulator.memory_heirarchy] +
            ['Pipeline Enabled'] )
        self.ui.pipelineTable.setVerticalHeaderLabels(pipelineHeaders)


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
        # TODO: Allow for different delays for data tables, program counter
        # TODO: Fix display of negative numbers; use twos complement or fix cutoff.
        display_format = self.ui.memoryDisplayBox.currentText()
        if display_format == "Binary":
            if n >= 0:
                return bin(n)[2:]
            else:
                return '-' + bin(n)[3:]
        elif display_format == "Hexadecimal":
            return hex(n)
        else:
            return str(n)

    def save(self):
        """Save a program's state, including all information needed to
        restore the program from its current state.

        This includes:
            All of the simulator, including registers, cache, memory, PC, etc
            All of the data in the instructionTable
        """
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog # this prevents OSX warning message
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", "","All Files (*);;DAT Files (*.dat)", options=options)
        if filename:
            logging.info("GUI: saving program to " + filename)
        else:
            return

        # Write the contents of the editor to file
        # filename is the var to use
        import pickle

        instruction_rows = self.ui.instructionTable.rowCount()
        instruction_cols = self.ui.instructionTable.columnCount()
        instruction_contents = [ [None] * instruction_cols
                                for row in range(instruction_rows)]
        for i in range(instruction_rows):
            for j in range(instruction_cols):
                cell =  self.ui.instructionTable.item(i, j)
                if cell is not None:
                    instruction_contents[i][j] = cell.text()

        with open(filename, 'wb') as f:
            pickle.dump([self.simulator, instruction_contents], f)

    def restore(self):
        # Get the filename
        options = QtWidgets.QFileDialog.Options()

        # Prevent OSX warning message
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open File", "", "All Files (*);;DAT Files (*.dat)",
            options=options)

        # If a file was selected
        if filename:
            logging.info("GUI: restoring program " + filename)
        # Else, if dialog escaped, return without importing
        else:
            return

        import pickle

        with open(filename, 'rb') as f:
            self.simulator, instruction_contents = pickle.load(f)

        # Restore the instruction table
        self.ui.instructionTable.setRowCount(len(instruction_contents))
        if len(instruction_contents) > 0:
            for i in range(len(instruction_contents)):
                for j in range(len(instruction_contents[0])):
                    cell_contents = instruction_contents[i][j]
                    if cell_contents is not None:
                        self.ui.instructionTable.setItem(i, j, QtWidgets.QTableWidgetItem(cell_contents))

        self.update_data()

def main():
    app = QtWidgets.QApplication(sys.argv)

    app.setWindowIcon(QtGui.QIcon('gui/ELISA.png'))
    QCoreApplication.setOrganizationName("ELISA")
    QCoreApplication.setOrganizationDomain("github.com/jsennett/ELISA.git")
    QCoreApplication.setApplicationName("ELISA")

    application = ApplicationWindow()
    application.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
