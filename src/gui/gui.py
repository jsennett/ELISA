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
from PyQt5 import QtWidgets, QtGui
from mainwindow import Ui_mainwindow
from simulator import Simulator
from memory import Memory, Cache
import sys

import logging
logging.basicConfig(level=logging.INFO)


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()

        # Set up UI
        self.ui = Ui_mainwindow()
        self.ui.setupUi(self)

        # Error dialog box
        self.ui.error_dialog = QtWidgets.QErrorMessage()
        logging.info("GUI: UI is setup.")

        # Connect a simulator
        self.simulator = Simulator()

        # Add button functionality
        #     DONE:
        # add breakpoint
        # remove breakpoint
        # set configuration
        # import
        # export
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
        self.ui.addBreakpointButton.clicked.connect(self.add_breakpoint)
        self.ui.removeBreakpointButton.clicked.connect(self.remove_breakpoint)

        # Add input validators
        self.ui.L1Lines.setValidator(QtGui.QIntValidator(1, 2**26))
        self.ui.L1Cycles.setValidator(QtGui.QIntValidator(0, 1000))
        self.ui.L2Lines.setValidator(QtGui.QIntValidator(1, 2**26))
        self.ui.L2Cycles.setValidator(QtGui.QIntValidator(0, 1000))
        self.ui.L3Lines.setValidator(QtGui.QIntValidator(1, 2**26))
        self.ui.L3Cycles.setValidator(QtGui.QIntValidator(0, 1000))
        self.ui.memoryCycles.setValidator(QtGui.QIntValidator(0, 1000))
        self.ui.memoryLines.setValidator(QtGui.QIntValidator(1, 32))
        self.ui.addBreakpoint.setValidator(QtGui.QIntValidator(1, 10000))
        self.ui.removeBreakpoint.setValidator(QtGui.QIntValidator(1, 10000))

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

        # Read the file
        with open(filename) as f:
            file_contents = f.read()

        # Copy contents into the code editor
        self.ui.codeEditor.setPlainText(file_contents)

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
    
    def reset(self):
        # TODO: Implement this method
        logging.info("GUI: reset()")
        pass

    def add_breakpoint(self):
        # TODO: Implement this method
        logging.info("GUI: add_breakpoint()")
        try:
            n = int(self.ui.addBreakpoint.text())
            if n < 1:
                raise ValueError("Breakpoint must be at least 1")
        except ValueError as e:
            self.ui.error_dialog.showMessage(str(e))
            return

        # Get the set of current breakpoints
        current_breakpoints = set(self.ui.currentBreakpoints.toPlainText().split(', '))

        # Add new breakpoint, and discard empty string caused by split()
        current_breakpoints.add(self.ui.addBreakpoint.text())
        current_breakpoints.discard('') 

        # current_breakpoints is a sets of strings
        # sort by integer value, then concatenate results with comma delimeter.
        # update the field with the new result
        self.ui.currentBreakpoints.setText(', '.join(list(sorted(current_breakpoints, key=lambda x: int(x)))))
        logging.info("new breakpoints" + self.ui.currentBreakpoints.toPlainText())

    def remove_breakpoint(self):
        # TODO: Implement this method
        logging.info("GUI: remove_breakpoint()")
        try:
            n = int(self.ui.removeBreakpoint.text())
        except ValueError as e:
            self.ui.error_dialog.showMessage(str(e))
            return

        # Get the set of current breakpoints
        current_breakpoints = set(self.ui.currentBreakpoints.toPlainText().split(', '))

        # Discard specified breakpoint, and discard empty string caused by split()
        current_breakpoints.discard(self.ui.removeBreakpoint.text())
        current_breakpoints.discard('')

        # current_breakpoints is a sets of strings
        # sort by integer value, then concatenate results with comma delimeter.
        # update the field with the new result
        self.ui.currentBreakpoints.setText(', '.join(list(sorted(current_breakpoints, key=lambda x: int(x)))))
        logging.info("new breakpoints" + self.ui.currentBreakpoints.toPlainText())

    def update_data(self):
        # TODO: Implement this method
        logging.info("GUI: update_data()")

        # Populate memory table from simulator memory
        # Populate cache table from simulator caches
        # Populate register table from simulator registers

        # TODO: remove default values from GUI tables.        
        pass


def main():
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()
    application.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()