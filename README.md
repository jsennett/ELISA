# ELISA
ELISA: EducationaL Instruction Set Architecture

The goal of this project is to build a custom instruction set simulator with a friendly user-interface that can be used to educate about the fundamentals of computer architecture and instruction set design. 

## Setup
`pip3 install -r requirements.txt`

## How to run

### Memory Demo
`python3 src/memory_demo.py`

### Graphical User Interface
`cd src/`
`python3 gui/gui.py`

### Simulator Demo
`python3 src/simulator_demo.py`

## How to build

### Rebuild the GUI
`pyuic5 src/gui/gui.ui -o src/gui/mainwindow.py`

## How to test
`pytest`
