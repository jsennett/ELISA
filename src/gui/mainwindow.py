# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/gui/gui.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_mainwindow(object):
    def setupUi(self, mainwindow):
        mainwindow.setObjectName("mainwindow")
        mainwindow.resize(1384, 870)
        self.stepButton = QtWidgets.QPushButton(mainwindow)
        self.stepButton.setGeometry(QtCore.QRect(900, 560, 111, 32))
        self.stepButton.setObjectName("stepButton")
        self.tabs = QtWidgets.QTabWidget(mainwindow)
        self.tabs.setGeometry(QtCore.QRect(530, 90, 811, 401))
        self.tabs.setTabsClosable(False)
        self.tabs.setObjectName("tabs")
        self.codeTab = QtWidgets.QWidget()
        self.codeTab.setObjectName("codeTab")
        self.codeEditor = CodeEditor(self.codeTab)
        self.codeEditor.setGeometry(QtCore.QRect(0, 0, 811, 371))
        self.codeEditor.setObjectName("codeEditor")
        self.tabs.addTab(self.codeTab, "")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.instructionTable = QtWidgets.QTableWidget(self.tab)
        self.instructionTable.setGeometry(QtCore.QRect(0, 0, 811, 371))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.instructionTable.sizePolicy().hasHeightForWidth())
        self.instructionTable.setSizePolicy(sizePolicy)
        self.instructionTable.setSizeIncrement(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setFamily("Courier")
        font.setPointSize(11)
        self.instructionTable.setFont(font)
        self.instructionTable.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.instructionTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.instructionTable.setAlternatingRowColors(True)
        self.instructionTable.setRowCount(0)
        self.instructionTable.setObjectName("instructionTable")
        self.instructionTable.setColumnCount(4)
        item = QtWidgets.QTableWidgetItem()
        self.instructionTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.instructionTable.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.instructionTable.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.instructionTable.setHorizontalHeaderItem(3, item)
        self.instructionTable.horizontalHeader().setCascadingSectionResizes(True)
        self.instructionTable.horizontalHeader().setDefaultSectionSize(190)
        self.instructionTable.horizontalHeader().setSortIndicatorShown(False)
        self.instructionTable.horizontalHeader().setStretchLastSection(True)
        self.instructionTable.verticalHeader().setVisible(False)
        self.instructionTable.verticalHeader().setDefaultSectionSize(22)
        self.instructionTable.verticalHeader().setHighlightSections(True)
        self.instructionTable.verticalHeader().setSortIndicatorShown(False)
        self.instructionTable.verticalHeader().setStretchLastSection(False)
        self.tabs.addTab(self.tab, "")
        self.animationTab = QtWidgets.QWidget()
        self.animationTab.setObjectName("animationTab")
        self.pipelineTable = QtWidgets.QTableWidget(self.animationTab)
        self.pipelineTable.setGeometry(QtCore.QRect(0, 0, 811, 401))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.pipelineTable.setFont(font)
        self.pipelineTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.pipelineTable.setObjectName("pipelineTable")
        self.pipelineTable.setColumnCount(1)
        self.pipelineTable.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.pipelineTable.setHorizontalHeaderItem(0, item)
        self.pipelineTable.horizontalHeader().setVisible(False)
        self.pipelineTable.horizontalHeader().setCascadingSectionResizes(False)
        self.pipelineTable.horizontalHeader().setDefaultSectionSize(400)
        self.pipelineTable.horizontalHeader().setStretchLastSection(True)
        self.pipelineTable.verticalHeader().setCascadingSectionResizes(True)
        self.pipelineTable.verticalHeader().setDefaultSectionSize(30)
        self.tabs.addTab(self.animationTab, "")
        self.stepBreakpointButton = QtWidgets.QPushButton(mainwindow)
        self.stepBreakpointButton.setGeometry(QtCore.QRect(1120, 560, 191, 32))
        self.stepBreakpointButton.setObjectName("stepBreakpointButton")
        self.line_2 = QtWidgets.QFrame(mainwindow)
        self.line_2.setGeometry(QtCore.QRect(530, 630, 801, 20))
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.title = QtWidgets.QLabel(mainwindow)
        self.title.setGeometry(QtCore.QRect(440, -10, 561, 111))
        self.title.setObjectName("title")
        self.line_1 = QtWidgets.QFrame(mainwindow)
        self.line_1.setGeometry(QtCore.QRect(540, 530, 801, 20))
        self.line_1.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_1.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_1.setObjectName("line_1")
        self.importButton = QtWidgets.QPushButton(mainwindow)
        self.importButton.setGeometry(QtCore.QRect(1102, 60, 131, 32))
        self.importButton.setObjectName("importButton")
        self.exportButton = QtWidgets.QPushButton(mainwindow)
        self.exportButton.setGeometry(QtCore.QRect(1230, 60, 113, 32))
        self.exportButton.setObjectName("exportButton")
        self.addBreakpointButton = QtWidgets.QPushButton(mainwindow)
        self.addBreakpointButton.setGeometry(QtCore.QRect(1000, 504, 141, 32))
        self.addBreakpointButton.setObjectName("addBreakpointButton")
        self.stepNCyclesButton = QtWidgets.QPushButton(mainwindow)
        self.stepNCyclesButton.setGeometry(QtCore.QRect(900, 590, 121, 32))
        self.stepNCyclesButton.setObjectName("stepNCyclesButton")
        self.resetButton = QtWidgets.QPushButton(mainwindow)
        self.resetButton.setGeometry(QtCore.QRect(682, 504, 151, 32))
        self.resetButton.setObjectName("resetButton")
        self.currentCycleLabel = QtWidgets.QLabel(mainwindow)
        self.currentCycleLabel.setGeometry(QtCore.QRect(560, 560, 101, 21))
        self.currentCycleLabel.setObjectName("currentCycleLabel")
        self.stepCompletionButton = QtWidgets.QPushButton(mainwindow)
        self.stepCompletionButton.setGeometry(QtCore.QRect(1120, 590, 191, 32))
        self.stepCompletionButton.setObjectName("stepCompletionButton")
        self.line = QtWidgets.QFrame(mainwindow)
        self.line.setGeometry(QtCore.QRect(830, 550, 31, 81))
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.dataTabs = QtWidgets.QTabWidget(mainwindow)
        self.dataTabs.setGeometry(QtCore.QRect(10, 80, 501, 771))
        self.dataTabs.setObjectName("dataTabs")
        self.registerTab = QtWidgets.QWidget()
        self.registerTab.setObjectName("registerTab")
        self.registerTable = QtWidgets.QTableWidget(self.registerTab)
        self.registerTable.setEnabled(True)
        self.registerTable.setGeometry(QtCore.QRect(0, 0, 491, 741))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.registerTable.sizePolicy().hasHeightForWidth())
        self.registerTable.setSizePolicy(sizePolicy)
        self.registerTable.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setFamily("Courier")
        font.setPointSize(11)
        font.setBold(False)
        font.setWeight(50)
        self.registerTable.setFont(font)
        self.registerTable.setAutoFillBackground(False)
        self.registerTable.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.registerTable.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.registerTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.registerTable.setAlternatingRowColors(True)
        self.registerTable.setShowGrid(True)
        self.registerTable.setWordWrap(True)
        self.registerTable.setRowCount(0)
        self.registerTable.setObjectName("registerTable")
        self.registerTable.setColumnCount(2)
        item = QtWidgets.QTableWidgetItem()
        self.registerTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.registerTable.setHorizontalHeaderItem(1, item)
        self.registerTable.horizontalHeader().setVisible(False)
        self.registerTable.horizontalHeader().setCascadingSectionResizes(False)
        self.registerTable.horizontalHeader().setDefaultSectionSize(222)
        self.registerTable.horizontalHeader().setStretchLastSection(True)
        self.registerTable.verticalHeader().setVisible(False)
        self.registerTable.verticalHeader().setDefaultSectionSize(22)
        self.dataTabs.addTab(self.registerTab, "")
        self.memoryTab = QtWidgets.QWidget()
        self.memoryTab.setObjectName("memoryTab")
        self.memoryTable = QtWidgets.QTableWidget(self.memoryTab)
        self.memoryTable.setEnabled(True)
        self.memoryTable.setGeometry(QtCore.QRect(0, 0, 491, 741))
        self.memoryTable.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setFamily("Courier")
        font.setPointSize(11)
        self.memoryTable.setFont(font)
        self.memoryTable.setAutoFillBackground(False)
        self.memoryTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.memoryTable.setAlternatingRowColors(True)
        self.memoryTable.setRowCount(0)
        self.memoryTable.setObjectName("memoryTable")
        self.memoryTable.setColumnCount(2)
        item = QtWidgets.QTableWidgetItem()
        self.memoryTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.memoryTable.setHorizontalHeaderItem(1, item)
        self.memoryTable.horizontalHeader().setDefaultSectionSize(222)
        self.memoryTable.horizontalHeader().setStretchLastSection(True)
        self.memoryTable.verticalHeader().setVisible(False)
        self.memoryTable.verticalHeader().setDefaultSectionSize(22)
        self.dataTabs.addTab(self.memoryTab, "")
        self.cacheTab = QtWidgets.QWidget()
        self.cacheTab.setObjectName("cacheTab")
        self.cacheTable = QtWidgets.QTableWidget(self.cacheTab)
        self.cacheTable.setGeometry(QtCore.QRect(0, 0, 491, 741))
        font = QtGui.QFont()
        font.setFamily("Courier")
        font.setPointSize(11)
        self.cacheTable.setFont(font)
        self.cacheTable.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.cacheTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.cacheTable.setAlternatingRowColors(True)
        self.cacheTable.setRowCount(0)
        self.cacheTable.setObjectName("cacheTable")
        self.cacheTable.setColumnCount(8)
        item = QtWidgets.QTableWidgetItem()
        self.cacheTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.cacheTable.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.cacheTable.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.cacheTable.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.cacheTable.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.cacheTable.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.cacheTable.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.cacheTable.setHorizontalHeaderItem(7, item)
        self.cacheTable.horizontalHeader().setCascadingSectionResizes(True)
        self.cacheTable.horizontalHeader().setDefaultSectionSize(50)
        self.cacheTable.horizontalHeader().setSortIndicatorShown(False)
        self.cacheTable.horizontalHeader().setStretchLastSection(True)
        self.cacheTable.verticalHeader().setVisible(False)
        self.cacheTable.verticalHeader().setDefaultSectionSize(22)
        self.cacheTable.verticalHeader().setHighlightSections(True)
        self.cacheTable.verticalHeader().setSortIndicatorShown(False)
        self.cacheTable.verticalHeader().setStretchLastSection(False)
        self.dataTabs.addTab(self.cacheTab, "")
        self.removeBreakpointButton = QtWidgets.QPushButton(mainwindow)
        self.removeBreakpointButton.setGeometry(QtCore.QRect(1200, 504, 141, 32))
        self.removeBreakpointButton.setObjectName("removeBreakpointButton")
        self.groupBox = QtWidgets.QGroupBox(mainwindow)
        self.groupBox.setGeometry(QtCore.QRect(510, 620, 861, 221))
        self.groupBox.setAutoFillBackground(True)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.setConfigurationButton = QtWidgets.QPushButton(self.groupBox)
        self.setConfigurationButton.setGeometry(QtCore.QRect(300, 190, 201, 32))
        self.setConfigurationButton.setObjectName("setConfigurationButton")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.groupBox)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 30, 204, 155))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.L1 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.L1.setContentsMargins(0, 0, 0, 0)
        self.L1.setObjectName("L1")
        self.L1Enabled = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.L1Enabled.setChecked(True)
        self.L1Enabled.setObjectName("L1Enabled")
        self.L1.addWidget(self.L1Enabled)
        self.L1AssociativityLayout = QtWidgets.QHBoxLayout()
        self.L1AssociativityLayout.setObjectName("L1AssociativityLayout")
        self.L1AssociativityLabel = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.L1AssociativityLabel.setObjectName("L1AssociativityLabel")
        self.L1AssociativityLayout.addWidget(self.L1AssociativityLabel)
        self.L1Associativity = QtWidgets.QComboBox(self.verticalLayoutWidget)
        self.L1Associativity.setObjectName("L1Associativity")
        self.L1Associativity.addItem("")
        self.L1Associativity.addItem("")
        self.L1Associativity.addItem("")
        self.L1Associativity.addItem("")
        self.L1Associativity.addItem("")
        self.L1Associativity.addItem("")
        self.L1Associativity.addItem("")
        self.L1AssociativityLayout.addWidget(self.L1Associativity)
        self.L1.addLayout(self.L1AssociativityLayout)
        self.L1LinesLayout = QtWidgets.QHBoxLayout()
        self.L1LinesLayout.setObjectName("L1LinesLayout")
        self.L1LinesLabel = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.L1LinesLabel.setObjectName("L1LinesLabel")
        self.L1LinesLayout.addWidget(self.L1LinesLabel)
        self.L1Lines = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.L1Lines.setObjectName("L1Lines")
        self.L1LinesLayout.addWidget(self.L1Lines)
        self.L1.addLayout(self.L1LinesLayout)
        self.L1WordsPerLineLayout = QtWidgets.QHBoxLayout()
        self.L1WordsPerLineLayout.setObjectName("L1WordsPerLineLayout")
        self.L1WordsPerLineLabel = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.L1WordsPerLineLabel.setObjectName("L1WordsPerLineLabel")
        self.L1WordsPerLineLayout.addWidget(self.L1WordsPerLineLabel)
        self.L1WordsPerLine = QtWidgets.QComboBox(self.verticalLayoutWidget)
        self.L1WordsPerLine.setObjectName("L1WordsPerLine")
        self.L1WordsPerLine.addItem("")
        self.L1WordsPerLine.addItem("")
        self.L1WordsPerLine.addItem("")
        self.L1WordsPerLine.addItem("")
        self.L1WordsPerLine.addItem("")
        self.L1WordsPerLine.addItem("")
        self.L1WordsPerLine.addItem("")
        self.L1WordsPerLine.setItemText(6, "")
        self.L1WordsPerLineLayout.addWidget(self.L1WordsPerLine)
        self.L1.addLayout(self.L1WordsPerLineLayout)
        self.L1CyclesLayout = QtWidgets.QHBoxLayout()
        self.L1CyclesLayout.setObjectName("L1CyclesLayout")
        self.L1CyclesLabel = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.L1CyclesLabel.setObjectName("L1CyclesLabel")
        self.L1CyclesLayout.addWidget(self.L1CyclesLabel)
        self.L1Cycles = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.L1Cycles.setObjectName("L1Cycles")
        self.L1CyclesLayout.addWidget(self.L1Cycles)
        self.L1.addLayout(self.L1CyclesLayout)
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.groupBox)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(210, 30, 204, 155))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.L2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.L2.setContentsMargins(0, 0, 0, 0)
        self.L2.setObjectName("L2")
        self.L2Enabled = QtWidgets.QCheckBox(self.verticalLayoutWidget_2)
        self.L2Enabled.setChecked(True)
        self.L2Enabled.setObjectName("L2Enabled")
        self.L2.addWidget(self.L2Enabled)
        self.L2AssociativityLayout = QtWidgets.QHBoxLayout()
        self.L2AssociativityLayout.setObjectName("L2AssociativityLayout")
        self.L2AssociativityLabel = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.L2AssociativityLabel.setText("Assoc.")
        self.L2AssociativityLabel.setObjectName("L2AssociativityLabel")
        self.L2AssociativityLayout.addWidget(self.L2AssociativityLabel)
        self.L2Associativity = QtWidgets.QComboBox(self.verticalLayoutWidget_2)
        self.L2Associativity.setObjectName("L2Associativity")
        self.L2Associativity.addItem("")
        self.L2Associativity.addItem("")
        self.L2Associativity.addItem("")
        self.L2Associativity.addItem("")
        self.L2Associativity.addItem("")
        self.L2Associativity.addItem("")
        self.L2Associativity.addItem("")
        self.L2AssociativityLayout.addWidget(self.L2Associativity)
        self.L2.addLayout(self.L2AssociativityLayout)
        self.L2LinesLayout = QtWidgets.QHBoxLayout()
        self.L2LinesLayout.setObjectName("L2LinesLayout")
        self.L2LinesLabel = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.L2LinesLabel.setObjectName("L2LinesLabel")
        self.L2LinesLayout.addWidget(self.L2LinesLabel)
        self.L2Lines = QtWidgets.QLineEdit(self.verticalLayoutWidget_2)
        self.L2Lines.setObjectName("L2Lines")
        self.L2LinesLayout.addWidget(self.L2Lines)
        self.L2.addLayout(self.L2LinesLayout)
        self.L2WordsPerLineLayout = QtWidgets.QHBoxLayout()
        self.L2WordsPerLineLayout.setObjectName("L2WordsPerLineLayout")
        self.L2WordsPerLineLabel = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.L2WordsPerLineLabel.setObjectName("L2WordsPerLineLabel")
        self.L2WordsPerLineLayout.addWidget(self.L2WordsPerLineLabel)
        self.L2WordsPerLine = QtWidgets.QComboBox(self.verticalLayoutWidget_2)
        self.L2WordsPerLine.setObjectName("L2WordsPerLine")
        self.L2WordsPerLine.addItem("")
        self.L2WordsPerLine.addItem("")
        self.L2WordsPerLine.addItem("")
        self.L2WordsPerLine.addItem("")
        self.L2WordsPerLine.addItem("")
        self.L2WordsPerLine.addItem("")
        self.L2WordsPerLine.addItem("")
        self.L2WordsPerLine.setItemText(6, "")
        self.L2WordsPerLineLayout.addWidget(self.L2WordsPerLine)
        self.L2.addLayout(self.L2WordsPerLineLayout)
        self.L2CyclesLayout = QtWidgets.QHBoxLayout()
        self.L2CyclesLayout.setObjectName("L2CyclesLayout")
        self.L2CyclesLabel = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.L2CyclesLabel.setObjectName("L2CyclesLabel")
        self.L2CyclesLayout.addWidget(self.L2CyclesLabel)
        self.L2Cycles = QtWidgets.QLineEdit(self.verticalLayoutWidget_2)
        self.L2Cycles.setObjectName("L2Cycles")
        self.L2CyclesLayout.addWidget(self.L2Cycles)
        self.L2.addLayout(self.L2CyclesLayout)
        self.line_4 = QtWidgets.QFrame(self.groupBox)
        self.line_4.setGeometry(QtCore.QRect(580, 30, 61, 151))
        self.line_4.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.verticalLayoutWidget_3 = QtWidgets.QWidget(self.groupBox)
        self.verticalLayoutWidget_3.setGeometry(QtCore.QRect(410, 30, 204, 155))
        self.verticalLayoutWidget_3.setObjectName("verticalLayoutWidget_3")
        self.L3 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_3)
        self.L3.setContentsMargins(0, 0, 0, 0)
        self.L3.setObjectName("L3")
        self.L3Enabled = QtWidgets.QCheckBox(self.verticalLayoutWidget_3)
        self.L3Enabled.setObjectName("L3Enabled")
        self.L3.addWidget(self.L3Enabled)
        self.L3AssociativityLayout = QtWidgets.QHBoxLayout()
        self.L3AssociativityLayout.setObjectName("L3AssociativityLayout")
        self.L3AssociativityLabel = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        self.L3AssociativityLabel.setObjectName("L3AssociativityLabel")
        self.L3AssociativityLayout.addWidget(self.L3AssociativityLabel)
        self.L3Associativity = QtWidgets.QComboBox(self.verticalLayoutWidget_3)
        self.L3Associativity.setObjectName("L3Associativity")
        self.L3Associativity.addItem("")
        self.L3Associativity.addItem("")
        self.L3Associativity.addItem("")
        self.L3Associativity.addItem("")
        self.L3Associativity.addItem("")
        self.L3Associativity.addItem("")
        self.L3Associativity.addItem("")
        self.L3AssociativityLayout.addWidget(self.L3Associativity)
        self.L3.addLayout(self.L3AssociativityLayout)
        self.L3LinesLayout = QtWidgets.QHBoxLayout()
        self.L3LinesLayout.setObjectName("L3LinesLayout")
        self.L3LinesLabel = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        self.L3LinesLabel.setObjectName("L3LinesLabel")
        self.L3LinesLayout.addWidget(self.L3LinesLabel)
        self.L3Lines = QtWidgets.QLineEdit(self.verticalLayoutWidget_3)
        self.L3Lines.setObjectName("L3Lines")
        self.L3LinesLayout.addWidget(self.L3Lines)
        self.L3.addLayout(self.L3LinesLayout)
        self.L3WordsPerLineLayout = QtWidgets.QHBoxLayout()
        self.L3WordsPerLineLayout.setObjectName("L3WordsPerLineLayout")
        self.L3WordsPerLineLabel = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        self.L3WordsPerLineLabel.setObjectName("L3WordsPerLineLabel")
        self.L3WordsPerLineLayout.addWidget(self.L3WordsPerLineLabel)
        self.L3WordsPerLine = QtWidgets.QComboBox(self.verticalLayoutWidget_3)
        self.L3WordsPerLine.setObjectName("L3WordsPerLine")
        self.L3WordsPerLine.addItem("")
        self.L3WordsPerLine.addItem("")
        self.L3WordsPerLine.addItem("")
        self.L3WordsPerLine.addItem("")
        self.L3WordsPerLine.addItem("")
        self.L3WordsPerLine.addItem("")
        self.L3WordsPerLine.addItem("")
        self.L3WordsPerLine.setItemText(6, "")
        self.L3WordsPerLineLayout.addWidget(self.L3WordsPerLine)
        self.L3.addLayout(self.L3WordsPerLineLayout)
        self.L3CyclesLayout = QtWidgets.QHBoxLayout()
        self.L3CyclesLayout.setObjectName("L3CyclesLayout")
        self.L3CyclesLabel = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        self.L3CyclesLabel.setObjectName("L3CyclesLabel")
        self.L3CyclesLayout.addWidget(self.L3CyclesLabel)
        self.L3Cycles = QtWidgets.QLineEdit(self.verticalLayoutWidget_3)
        self.L3Cycles.setText("")
        self.L3Cycles.setObjectName("L3Cycles")
        self.L3CyclesLayout.addWidget(self.L3Cycles)
        self.L3.addLayout(self.L3CyclesLayout)
        self.verticalLayoutWidget_4 = QtWidgets.QWidget(self.groupBox)
        self.verticalLayoutWidget_4.setGeometry(QtCore.QRect(630, 100, 231, 61))
        self.verticalLayoutWidget_4.setObjectName("verticalLayoutWidget_4")
        self.memory = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_4)
        self.memory.setContentsMargins(0, 0, 0, 0)
        self.memory.setObjectName("memory")
        self.memoryLinesLayout = QtWidgets.QHBoxLayout()
        self.memoryLinesLayout.setObjectName("memoryLinesLayout")
        self.memoryLinesLabel = QtWidgets.QLabel(self.verticalLayoutWidget_4)
        self.memoryLinesLabel.setObjectName("memoryLinesLabel")
        self.memoryLinesLayout.addWidget(self.memoryLinesLabel)
        self.memoryLines = QtWidgets.QLineEdit(self.verticalLayoutWidget_4)
        self.memoryLines.setAlignment(QtCore.Qt.AlignCenter)
        self.memoryLines.setObjectName("memoryLines")
        self.memoryLinesLayout.addWidget(self.memoryLines)
        self.memory.addLayout(self.memoryLinesLayout)
        self.memoryCyclesLayout = QtWidgets.QHBoxLayout()
        self.memoryCyclesLayout.setObjectName("memoryCyclesLayout")
        self.memoryCyclesLabel = QtWidgets.QLabel(self.verticalLayoutWidget_4)
        self.memoryCyclesLabel.setObjectName("memoryCyclesLabel")
        self.memoryCyclesLayout.addWidget(self.memoryCyclesLabel)
        self.memoryCycles = QtWidgets.QLineEdit(self.verticalLayoutWidget_4)
        self.memoryCycles.setAlignment(QtCore.Qt.AlignCenter)
        self.memoryCycles.setObjectName("memoryCycles")
        self.memoryCyclesLayout.addWidget(self.memoryCycles)
        self.memory.addLayout(self.memoryCyclesLayout)
        self.pipelineEnabledButton = QtWidgets.QCheckBox(self.groupBox)
        self.pipelineEnabledButton.setGeometry(QtCore.QRect(660, 60, 141, 20))
        self.pipelineEnabledButton.setChecked(True)
        self.pipelineEnabledButton.setObjectName("pipelineEnabledButton")
        self.NCyclesLabel = QtWidgets.QLabel(mainwindow)
        self.NCyclesLabel.setGeometry(QtCore.QRect(1025, 594, 16, 21))
        self.NCyclesLabel.setObjectName("NCyclesLabel")
        self.stepSize = QtWidgets.QLineEdit(mainwindow)
        self.stepSize.setGeometry(QtCore.QRect(1040, 594, 51, 21))
        self.stepSize.setAlignment(QtCore.Qt.AlignCenter)
        self.stepSize.setObjectName("stepSize")
        self.breakpoint = QtWidgets.QLineEdit(mainwindow)
        self.breakpoint.setGeometry(QtCore.QRect(1140, 508, 61, 21))
        self.breakpoint.setText("")
        self.breakpoint.setAlignment(QtCore.Qt.AlignCenter)
        self.breakpoint.setObjectName("breakpoint")
        self.currentCycle = QtWidgets.QLineEdit(mainwindow)
        self.currentCycle.setGeometry(QtCore.QRect(670, 550, 141, 31))
        self.currentCycle.setText("")
        self.currentCycle.setAlignment(QtCore.Qt.AlignCenter)
        self.currentCycle.setReadOnly(True)
        self.currentCycle.setObjectName("currentCycle")
        self.loadButton = QtWidgets.QPushButton(mainwindow)
        self.loadButton.setGeometry(QtCore.QRect(530, 504, 151, 32))
        self.loadButton.setObjectName("loadButton")
        self.programCounterLabel = QtWidgets.QLabel(mainwindow)
        self.programCounterLabel.setGeometry(QtCore.QRect(540, 600, 131, 21))
        self.programCounterLabel.setObjectName("programCounterLabel")
        self.programCounter = QtWidgets.QLineEdit(mainwindow)
        self.programCounter.setGeometry(QtCore.QRect(670, 590, 141, 31))
        self.programCounter.setText("")
        self.programCounter.setAlignment(QtCore.Qt.AlignCenter)
        self.programCounter.setReadOnly(True)
        self.programCounter.setObjectName("programCounter")
        self.saveButton = QtWidgets.QPushButton(mainwindow)
        self.saveButton.setGeometry(QtCore.QRect(1230, 30, 113, 32))
        self.saveButton.setObjectName("saveButton")
        self.restoreButton = QtWidgets.QPushButton(mainwindow)
        self.restoreButton.setGeometry(QtCore.QRect(1102, 30, 131, 32))
        self.restoreButton.setObjectName("restoreButton")
        self.memoryDisplayBox = QtWidgets.QComboBox(mainwindow)
        self.memoryDisplayBox.setGeometry(QtCore.QRect(160, 40, 132, 26))
        self.memoryDisplayBox.setObjectName("memoryDisplayBox")
        self.memoryDisplayBox.addItem("")
        self.memoryDisplayBox.addItem("")
        self.memoryDisplayBox.addItem("")
        self.memoryDisplayBox.addItem("")
        self.memoryDisplayLabel = QtWidgets.QLabel(mainwindow)
        self.memoryDisplayLabel.setGeometry(QtCore.QRect(46, 42, 109, 20))
        self.memoryDisplayLabel.setObjectName("memoryDisplayLabel")

        self.retranslateUi(mainwindow)
        self.tabs.setCurrentIndex(1)
        self.dataTabs.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(mainwindow)

    def retranslateUi(self, mainwindow):
        _translate = QtCore.QCoreApplication.translate
        mainwindow.setWindowTitle(_translate("mainwindow", "Dialog"))
        self.stepButton.setText(_translate("mainwindow", "Step 1 cycle"))
        self.tabs.setTabText(self.tabs.indexOf(self.codeTab), _translate("mainwindow", "Code"))
        item = self.instructionTable.horizontalHeaderItem(0)
        item.setText(_translate("mainwindow", "Memory Address"))
        item = self.instructionTable.horizontalHeaderItem(1)
        item.setText(_translate("mainwindow", "Text Instruction"))
        item = self.instructionTable.horizontalHeaderItem(2)
        item.setText(_translate("mainwindow", "Hex Instruction"))
        item = self.instructionTable.horizontalHeaderItem(3)
        item.setText(_translate("mainwindow", "BP"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab), _translate("mainwindow", "Instructions"))
        item = self.pipelineTable.horizontalHeaderItem(0)
        item.setText(_translate("mainwindow", "Value"))
        self.tabs.setTabText(self.tabs.indexOf(self.animationTab), _translate("mainwindow", "Pipeline"))
        self.stepBreakpointButton.setText(_translate("mainwindow", "Step until next breakpoint"))
        self.title.setText(_translate("mainwindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:24pt; font-weight:600;\">ELISA: EducationaL Instruction Set Architecture</span></p><p align=\"center\"><span style=\" font-size:18pt;\">Josh Sennett &amp; Yash Adhikari -- CMPSCI 535: Computer Architecture</span></p></body></html>"))
        self.importButton.setText(_translate("mainwindow", "Import Code"))
        self.exportButton.setText(_translate("mainwindow", "Export Code"))
        self.addBreakpointButton.setText(_translate("mainwindow", "Add Breakpoint"))
        self.stepNCyclesButton.setText(_translate("mainwindow", "Step N cycles"))
        self.resetButton.setText(_translate("mainwindow", "Clear Instructions"))
        self.currentCycleLabel.setText(_translate("mainwindow", "<html><head/><body><p><span style=\" font-size:14pt; font-weight:600;\">Current Cycle:</span></p></body></html>"))
        self.stepCompletionButton.setText(_translate("mainwindow", "Step until completion"))
        self.registerTable.setSortingEnabled(False)
        item = self.registerTable.horizontalHeaderItem(0)
        item.setText(_translate("mainwindow", "$R - Integer Registers"))
        item = self.registerTable.horizontalHeaderItem(1)
        item.setText(_translate("mainwindow", "$F - Floating Point Registers"))
        self.dataTabs.setTabText(self.dataTabs.indexOf(self.registerTab), _translate("mainwindow", "Registers"))
        item = self.memoryTable.horizontalHeaderItem(0)
        item.setText(_translate("mainwindow", "Address"))
        item = self.memoryTable.horizontalHeaderItem(1)
        item.setText(_translate("mainwindow", "Value"))
        self.dataTabs.setTabText(self.dataTabs.indexOf(self.memoryTab), _translate("mainwindow", "Memory"))
        item = self.cacheTable.horizontalHeaderItem(0)
        item.setText(_translate("mainwindow", "Level"))
        item = self.cacheTable.horizontalHeaderItem(1)
        item.setText(_translate("mainwindow", "Tag"))
        item = self.cacheTable.horizontalHeaderItem(2)
        item.setText(_translate("mainwindow", "Index"))
        item = self.cacheTable.horizontalHeaderItem(3)
        item.setText(_translate("mainwindow", "Valid"))
        item = self.cacheTable.horizontalHeaderItem(4)
        item.setText(_translate("mainwindow", "Word 1"))
        item = self.cacheTable.horizontalHeaderItem(5)
        item.setText(_translate("mainwindow", "Word 2"))
        item = self.cacheTable.horizontalHeaderItem(6)
        item.setText(_translate("mainwindow", "Word 3"))
        item = self.cacheTable.horizontalHeaderItem(7)
        item.setText(_translate("mainwindow", "Word 4"))
        self.dataTabs.setTabText(self.dataTabs.indexOf(self.cacheTab), _translate("mainwindow", "Cache"))
        self.removeBreakpointButton.setText(_translate("mainwindow", "Remove Breakpoint"))
        self.setConfigurationButton.setText(_translate("mainwindow", "Set Configuration"))
        self.L1Enabled.setText(_translate("mainwindow", "L1 Cache Enabled"))
        self.L1AssociativityLabel.setText(_translate("mainwindow", "Assoc."))
        self.L1Associativity.setItemText(0, _translate("mainwindow", "Direct-Mapped"))
        self.L1Associativity.setItemText(1, _translate("mainwindow", "2-Way"))
        self.L1Associativity.setItemText(2, _translate("mainwindow", "4-Way"))
        self.L1Associativity.setItemText(3, _translate("mainwindow", "8-Way"))
        self.L1Associativity.setItemText(4, _translate("mainwindow", "16-Way"))
        self.L1Associativity.setItemText(5, _translate("mainwindow", "32-Way"))
        self.L1Associativity.setItemText(6, _translate("mainwindow", "N-Way"))
        self.L1LinesLabel.setText(_translate("mainwindow", "# Lines: 2^"))
        self.L1Lines.setText(_translate("mainwindow", "7"))
        self.L1WordsPerLineLabel.setText(_translate("mainwindow", "Words/Line"))
        self.L1WordsPerLine.setCurrentText(_translate("mainwindow", "1"))
        self.L1WordsPerLine.setItemText(0, _translate("mainwindow", "1"))
        self.L1WordsPerLine.setItemText(1, _translate("mainwindow", "2"))
        self.L1WordsPerLine.setItemText(2, _translate("mainwindow", "4"))
        self.L1WordsPerLine.setItemText(3, _translate("mainwindow", "8"))
        self.L1WordsPerLine.setItemText(4, _translate("mainwindow", "16"))
        self.L1WordsPerLine.setItemText(5, _translate("mainwindow", "32"))
        self.L1CyclesLabel.setText(_translate("mainwindow", "Delay"))
        self.L1Cycles.setText(_translate("mainwindow", "0"))
        self.L2Enabled.setText(_translate("mainwindow", "L2 Cache Enabled"))
        self.L2Associativity.setItemText(0, _translate("mainwindow", "Direct-Mapped"))
        self.L2Associativity.setItemText(1, _translate("mainwindow", "2-Way"))
        self.L2Associativity.setItemText(2, _translate("mainwindow", "4-Way"))
        self.L2Associativity.setItemText(3, _translate("mainwindow", "8-Way"))
        self.L2Associativity.setItemText(4, _translate("mainwindow", "16-Way"))
        self.L2Associativity.setItemText(5, _translate("mainwindow", "32-Way"))
        self.L2Associativity.setItemText(6, _translate("mainwindow", "N-Way"))
        self.L2LinesLabel.setText(_translate("mainwindow", "# Lines: 2^"))
        self.L2Lines.setText(_translate("mainwindow", "8"))
        self.L2WordsPerLineLabel.setText(_translate("mainwindow", "Words/Line"))
        self.L2WordsPerLine.setCurrentText(_translate("mainwindow", "1"))
        self.L2WordsPerLine.setItemText(0, _translate("mainwindow", "1"))
        self.L2WordsPerLine.setItemText(1, _translate("mainwindow", "2"))
        self.L2WordsPerLine.setItemText(2, _translate("mainwindow", "4"))
        self.L2WordsPerLine.setItemText(3, _translate("mainwindow", "8"))
        self.L2WordsPerLine.setItemText(4, _translate("mainwindow", "16"))
        self.L2WordsPerLine.setItemText(5, _translate("mainwindow", "32"))
        self.L2CyclesLabel.setText(_translate("mainwindow", "Delay"))
        self.L2Cycles.setText(_translate("mainwindow", "3"))
        self.L3Enabled.setText(_translate("mainwindow", "L3 Cache Enabled"))
        self.L3AssociativityLabel.setText(_translate("mainwindow", "Assoc."))
        self.L3Associativity.setItemText(0, _translate("mainwindow", "Direct-Mapped"))
        self.L3Associativity.setItemText(1, _translate("mainwindow", "2-Way"))
        self.L3Associativity.setItemText(2, _translate("mainwindow", "4-Way"))
        self.L3Associativity.setItemText(3, _translate("mainwindow", "8-Way"))
        self.L3Associativity.setItemText(4, _translate("mainwindow", "16-Way"))
        self.L3Associativity.setItemText(5, _translate("mainwindow", "32-Way"))
        self.L3Associativity.setItemText(6, _translate("mainwindow", "N-Way"))
        self.L3LinesLabel.setText(_translate("mainwindow", "# Lines: 2^"))
        self.L3Lines.setText(_translate("mainwindow", "9"))
        self.L3WordsPerLineLabel.setText(_translate("mainwindow", "Words/Line"))
        self.L3WordsPerLine.setCurrentText(_translate("mainwindow", "1"))
        self.L3WordsPerLine.setItemText(0, _translate("mainwindow", "1"))
        self.L3WordsPerLine.setItemText(1, _translate("mainwindow", "2"))
        self.L3WordsPerLine.setItemText(2, _translate("mainwindow", "4"))
        self.L3WordsPerLine.setItemText(3, _translate("mainwindow", "8"))
        self.L3WordsPerLine.setItemText(4, _translate("mainwindow", "16"))
        self.L3WordsPerLine.setItemText(5, _translate("mainwindow", "32"))
        self.L3CyclesLabel.setText(_translate("mainwindow", "Delay"))
        self.memoryLinesLabel.setText(_translate("mainwindow", "Memory Address Space: 2^"))
        self.memoryLines.setText(_translate("mainwindow", "12"))
        self.memoryCyclesLabel.setText(_translate("mainwindow", "Delay to Access Memory"))
        self.memoryCycles.setText(_translate("mainwindow", "100"))
        self.pipelineEnabledButton.setText(_translate("mainwindow", "Pipelining Enabled"))
        self.NCyclesLabel.setText(_translate("mainwindow", "N:"))
        self.stepSize.setText(_translate("mainwindow", "1"))
        self.loadButton.setText(_translate("mainwindow", "Load Instructions"))
        self.programCounterLabel.setText(_translate("mainwindow", "<html><head/><body><p><span style=\" font-size:14pt; font-weight:600;\">Program Counter:</span></p></body></html>"))
        self.saveButton.setText(_translate("mainwindow", "Save Program"))
        self.restoreButton.setText(_translate("mainwindow", "Restore Program"))
        self.memoryDisplayBox.setCurrentText(_translate("mainwindow", "Binary"))
        self.memoryDisplayBox.setItemText(0, _translate("mainwindow", "Binary"))
        self.memoryDisplayBox.setItemText(1, _translate("mainwindow", "Hexadecimal"))
        self.memoryDisplayBox.setItemText(2, _translate("mainwindow", "Decimal"))
        self.memoryDisplayBox.setItemText(3, _translate("mainwindow", "Human-Readable"))
        self.memoryDisplayLabel.setText(_translate("mainwindow", "<html><head/><body><p><span style=\" font-size:14pt; font-weight:600;\">Display Format:</span></p></body></html>"))

from codeeditor import CodeEditor
