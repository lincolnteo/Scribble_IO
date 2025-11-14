# Inspired by PyQt5 Creating Paint Application In 40 Minutes
#  https://www.youtube.com/watch?v=qEgyGyVA1ZQ

# NB If the menus do not work then click on another application and then click back
# and they will work https://python-forum.io/Thread-Tkinter-macOS-Catalina-and-Python-menu-issue

# PyQt documentation links are prefixed with the word 'documentation' in the code below and can be accessed automatically
#  in PyCharm using the following technique https://www.jetbrains.com/help/pycharm/inline-documentation.html

from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QFileDialog, QDockWidget, QPushButton, QVBoxLayout, \
    QLabel, QSizePolicy, QHBoxLayout, QRadioButton, QLineEdit
from PyQt6.QtGui import QIcon, QPainter, QPen, QPixmap
import sys
import csv, random
from PyQt6.QtCore import Qt, QPoint


class PictionaryGame(QMainWindow):  # documentation https://doc.qt.io/qt-6/qwidget.html
    '''
    Painting Application class
    '''

    def __init__(self):
        super().__init__()

        # set window title
        self.setWindowTitle("Pictionary Game - A2 Template")

        # set the windows dimensions
        top = 400
        left = 400
        width = 800
        height = 600
        self.setGeometry(top, left, width, height)

        # set the icon
        self.setWindowIcon(QIcon("./icons/paint-brush.png"))

        # canvas image
        self.image = QPixmap("./icons/canvas.png")

        mainWidget = QWidget()
        self.setCentralWidget(mainWidget)
        # Ensure the central widget expands to fill available space so docks
        # will be at the window edges
        mainWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # draw settings (default)
        self.drawing = False
        self.brushSize = 3
        self.brushColor = Qt.GlobalColor.black

        # reference to last point recorded by mouse
        self.lastPoint = QPoint()

        # players and scores
        self.players = ["Player 1", "Player 2"]
        self.playerNum = 0  # current drawer index
        self.currentPlayerNum = self.playerNum  # shown in "Current Turn"
        self.scores = [0 for _ in self.players]

        # mode and words
        self.mode = 'easy'
        self.wordList = []
        self.currentWord = ""

        # guessing state
        self.isGuessPhase = False
        self.attemptsLeft = 0
        self.guessOver = False

        # Left dock (player info + guessing)
        self.leftDock = QDockWidget()
        self.leftDock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.leftDock.setFeatures(QDockWidget.DockWidgetFeature(0))
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.leftDock)

        # widget inside the left Dock
        playerInfo = QWidget()
        self.leftLayout = QVBoxLayout()
        playerInfo.setLayout(self.leftLayout)
        playerInfo.setMaximumSize(200, self.height())

        # Current turn
        self.currentTurnLabel = QLabel("Current Turn:")
        self.currentPlayerLabel = QLabel(f"{self.players[self.currentPlayerNum]}")
        self.leftLayout.addWidget(self.currentTurnLabel)
        self.leftLayout.addWidget(self.currentPlayerLabel)
        self.leftLayout.addSpacing(10)

        # Scores
        self.leftLayout.addWidget(QLabel("Scores:"))
        self.scoreLabels = [QLabel(f"{self.players[0]}: {self.scores[0]}"),
                            QLabel(f"{self.players[1]}: {self.scores[1]}")]
        self.leftLayout.addWidget(self.scoreLabels[0])
        self.leftLayout.addWidget(self.scoreLabels[1])
        self.leftLayout.addSpacing(8)

        # Play mode
        self.leftLayout.addWidget(QLabel("Play Mode:"))
        self.radioEasy = QRadioButton("Easy")
        self.radioHard = QRadioButton("Hard")
        self.radioEasy.setChecked(True)
        self.leftLayout.addWidget(self.radioEasy)
        self.leftLayout.addWidget(self.radioHard)
        self.radioEasy.toggled.connect(lambda checked: self.set_mode('easy') if checked else None)
        self.radioHard.toggled.connect(lambda checked: self.set_mode('hard') if checked else None)
        self.leftLayout.addSpacing(10)

        # Current word (visible)
        self.leftLayout.addWidget(QLabel("Current Word:"))
        self.wordLabel = QLabel("----------")
        self.leftLayout.addWidget(self.wordLabel)
        self.leftLayout.addSpacing(8)

        # Guessing UI (always visible)
        self.guessInput = QLineEdit()
        self.guessInput.setPlaceholderText("Enter your guess here")
        self.guessButton = QPushButton("Guess")
        self.guessButton.clicked.connect(self.handle_guess)
        self.attemptsLabel = QLabel("")
        guessLayout = QVBoxLayout()
        guessLayout.addWidget(self.guessInput)
        guessLayout.addWidget(self.guessButton)
        guessLayout.addWidget(self.attemptsLabel)
        self.leftLayout.addLayout(guessLayout)

        # Next Turn button
        self.nextTurnButton = QPushButton("Next Turn")
        self.nextTurnButton.clicked.connect(self.next_turn)
        self.leftLayout.addWidget(self.nextTurnButton)

        # style left dock
        playerInfo.setAutoFillBackground(True)
        p = playerInfo.palette()
        p.setColor(playerInfo.backgroundRole(), Qt.GlobalColor.lightGray)
        playerInfo.setPalette(p)
        self.leftDock.setWidget(playerInfo)

        # Right dock (tools)
        self.rightDock = QDockWidget()
        self.rightDock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.rightDock.setFeatures(QDockWidget.DockWidgetFeature(0))
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.rightDock)

        # widget inside the right Dock
        colorPalette = QWidget()
        self.rightLayout = QVBoxLayout()
        colorPalette.setLayout(self.rightLayout)
        colorPalette.setMaximumSize(200, self.height())

        # Color palette controls
        self.rightLayout.addWidget(QLabel("Color Palette:"))
        self.rightLayout.addSpacing(6)

        self.btn_black = QPushButton("Black")
        self.btn_black.setStyleSheet("background-color: #000000; color: #ffffff;")
        self.btn_black.clicked.connect(self.black)
        self.rightLayout.addWidget(self.btn_black)

        self.btn_red = QPushButton("Red")
        self.btn_red.setStyleSheet("background-color: #cc0000; color: #ffffff;")
        self.btn_red.clicked.connect(self.red)
        self.rightLayout.addWidget(self.btn_red)

        self.btn_green = QPushButton("Green")
        self.btn_green.setStyleSheet("background-color: #008800; color: #ffffff;")
        self.btn_green.clicked.connect(self.green)
        self.rightLayout.addWidget(self.btn_green)

        self.btn_yellow = QPushButton("Yellow")
        self.btn_yellow.setStyleSheet("background-color: #ffdd00; color: #000000;")
        self.btn_yellow.clicked.connect(self.yellow)
        self.rightLayout.addWidget(self.btn_yellow)
        self.rightLayout.addStretch(1)

        # Visual status and brush sizes
        self.rightLayout.addWidget(QLabel("Current:"))
        swatchLayout = QHBoxLayout()
        self.colorIndicator = QLabel()
        self.colorIndicator.setFixedSize(20, 20)
        self.colorIndicator.setStyleSheet("background-color: #000000; border: 1px solid #000000;")
        swatchLayout.addWidget(self.colorIndicator)
        self.colorNameLabel = QLabel("Black")
        swatchLayout.addWidget(self.colorNameLabel)
        self.sizeLabel = QLabel(f"{self.brushSize} px")
        swatchLayout.addWidget(self.sizeLabel)
        swatchLayout.addStretch(1)
        self.rightLayout.addLayout(swatchLayout)
        self.rightLayout.addSpacing(6)

        # Brush size buttons
        self.rightLayout.addWidget(QLabel("Brush Sizes:"))
        self.threePxButton = QPushButton("3 px")
        self.threePxButton.clicked.connect(self.threepx)
        self.rightLayout.addWidget(self.threePxButton)

        self.fivePxButton = QPushButton("5 px")
        self.fivePxButton.clicked.connect(self.fivepx)
        self.rightLayout.addWidget(self.fivePxButton)

        self.sevenPxButton = QPushButton("7 px")
        self.sevenPxButton.clicked.connect(self.sevenpx)
        self.rightLayout.addWidget(self.sevenPxButton)

        self.ninePxButton = QPushButton("9 px")
        self.ninePxButton.clicked.connect(self.ninepx)
        self.rightLayout.addWidget(self.ninePxButton)

        self.rightLayout.addStretch(1)

        # Clear and Save buttons
        self.clearButton = QPushButton("Clear Canvas")
        self.clearButton.clicked.connect(self.clear)
        self.rightLayout.addWidget(self.clearButton)

        self.saveButton = QPushButton("Save Canvas")
        self.saveButton.clicked.connect(self.save)
        self.rightLayout.addWidget(self.saveButton)

        # right dock appearance
        colorPalette.setAutoFillBackground(True)
        p = colorPalette.palette()
        p.setColor(colorPalette.backgroundRole(), Qt.GlobalColor.lightGray)
        colorPalette.setPalette(p)
        self.rightDock.setWidget(colorPalette)

        # Load initial words and pick one
        self.getList(self.mode)
        self.currentWord = self.getWord()
        self.wordLabel.setText(self.currentWord)

    # event handlers
    def mousePressEvent(self,
                        event):  # when the mouse is pressed, documentation: https://doc.qt.io/qt-6/qwidget.html#mousePressEvent
        if event.button() == Qt.MouseButton.LeftButton:  # if the pressed button is the left button
            self.drawing = True  # enter drawing mode
            self.lastPoint = event.pos()  # save the location of the mouse press as the lastPoint
            print(self.lastPoint)  # print the lastPoint for debugging purposes

    def mouseMoveEvent(self,
                       event):  # when the mouse is moved, documenation: documentation: https://doc.qt.io/qt-6/qwidget.html#mouseMoveEvent
        if self.drawing:
            painter = QPainter(self.image)  # object which allows drawing to take place on an image
            # allows the selection of brush colour, brish size, line type, cap type, join type. Images available here http://doc.qt.io/qt-6/qpen.html
            painter.setPen(QPen(self.brushColor, self.brushSize, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                                Qt.PenJoinStyle.RoundJoin))
            painter.drawLine(self.lastPoint,
                             event.pos())  # draw a line from the point of the orginal press to the point to where the mouse was dragged to
            self.lastPoint = event.pos()  # set the last point to refer to the point we have just moved to, this helps when drawing the next line segment
            self.update()  # call the update method of the widget which calls the paintEvent of this class

    def mouseReleaseEvent(self,
                          event):  # when the mouse is released, documentation: https://doc.qt.io/qt-6/qwidget.html#mouseReleaseEvent
        if event.button() == Qt.MouseButton.LeftButton:  # if the released button is the left button, documentation: https://doc.qt.io/qt-6/qt.html#MouseButton-enum ,
            self.drawing = False  # exit drawing mode

    # paint events
    def paintEvent(self, event):
        # you should only create and use the QPainter object in this method, it should be a local variable
        canvasPainter = QPainter(
            self)  # create a new QPainter object, documentation: https://doc.qt.io/qt-6/qpainter.html
        canvasPainter.drawPixmap(QPoint(),
                                 self.image)  # draw the image , documentation: https://doc.qt.io/qt-6/qpainter.html#drawImage-1

    # resize event - this function is called
    def resizeEvent(self, event):
        self.image = self.image.scaled(self.width(), self.height())

    # slots
    def save(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
                                                  "PNG(*.png);;JPG(*.jpg *.jpeg);;All Files (*.*)")
        if filePath == "":  # if the file path is empty
            return  # do nothing and return
        self.image.save(filePath)  # save file image to the file path

    def clear(self):
        # reset canvas to the provided canvas image
        self.image = QPixmap("./icons/canvas.png")
        self.update()

    def threepx(self):
        self.brushSize = 3
        self.sizeLabel.setText("3 px")

    def fivepx(self):
        self.brushSize = 5
        self.sizeLabel.setText("5 px")

    def sevenpx(self):
        self.brushSize = 7
        self.sizeLabel.setText("7 px")

    def ninepx(self):
        self.brushSize = 9
        self.sizeLabel.setText("9 px")

    def black(self):
        self.brushColor = Qt.GlobalColor.black
        self.colorIndicator.setStyleSheet("background-color: #000000; border: 1px solid #000000;")
        self.colorNameLabel.setText("Black")

    def red(self):
        self.brushColor = Qt.GlobalColor.red
        self.colorIndicator.setStyleSheet("background-color: #cc0000; border: 1px solid #000000;")
        self.colorNameLabel.setText("Red")

    def green(self):
        self.brushColor = Qt.GlobalColor.green
        self.colorIndicator.setStyleSheet("background-color: #008800; border: 1px solid #000000;")
        self.colorNameLabel.setText("Green")

    def yellow(self):
        self.brushColor = Qt.GlobalColor.yellow
        self.colorIndicator.setStyleSheet("background-color: #ffdd00; border: 1px solid #000000;")
        self.colorNameLabel.setText("Yellow")

    # Guess handling
    def handle_guess(self):
        # only accept guesses during guess phase
        if not self.isGuessPhase:
            return
        guess = self.guessInput.text().strip()
        if not guess:
            return
        # compare case-insensitive
        if guess.lower() == self.currentWord.lower():
            # correct
            self.scores[self.currentPlayerNum] += 1
            self.scoreLabels[self.currentPlayerNum].setText(
                f"{self.players[self.currentPlayerNum]}: {self.scores[self.currentPlayerNum]}")
            self.attemptsLabel.setText("Correct! Word: " + self.currentWord)
            self.wordLabel.setText(self.currentWord)
            self.isGuessPhase = False
            self.guessOver = True
        else:
            # wrong guess
            self.attemptsLeft -= 1
            if self.attemptsLeft <= 0:
                self.attemptsLabel.setText("No attempts left. Word: " + self.currentWord)
                self.wordLabel.setText(self.currentWord)
                self.isGuessPhase = False
                self.guessOver = True
            else:
                self.attemptsLabel.setText(f"Wrong. Attempts left: {self.attemptsLeft}")
        self.guessInput.clear()

    def start_guess_phase(self):
        # Enter guessing phase: the player after the drawer will be the guesser
        self.isGuessPhase = True
        self.guessOver = False
        self.attemptsLeft = 3
        guesser = (self.playerNum + 1) % len(self.players)
        self.currentPlayerNum = guesser
        self.currentPlayerLabel.setText(f"{self.players[self.currentPlayerNum]}")
        # hide the word from the guesser (show placeholder)
        self.wordLabel.setText("----------")
        self.attemptsLabel.setText(f"Attempts left: {self.attemptsLeft}")

    def end_guess_phase_and_start_next_drawer(self):
        # Move drawer forward and prepare new word for the next drawer
        self.playerNum = (self.playerNum + 1) % len(self.players)
        self.currentPlayerNum = self.playerNum
        self.currentPlayerLabel.setText(f"{self.players[self.currentPlayerNum]}")
        # new word for the new drawer
        self.getList(self.mode)
        self.currentWord = self.getWord()
        self.wordLabel.setText(self.currentWord)
        self.isGuessPhase = False
        self.guessOver = False
        self.attemptsLabel.setText("")

    # Get a random word from the list read from file
    def getWord(self):
        if not self.wordList:
            return ""
        return random.choice(self.wordList)

    # read word list from file
    def getList(self, mode):
        # Read either comma-separated or one-word-per-line files and build a flat list
        words = []
        try:
            with open(mode + 'mode.txt', encoding='utf-8') as csv_file:
                csv_reader = csv.reader(csv_file)
                for row in csv_reader:
                    # row may be a list of values; extend the words list
                    for token in row:
                        token = token.strip()
                        if token:
                            words.append(token)
        except FileNotFoundError:
            words = []
        self.wordList = words

        # open a file
        # open a file

    def open(self):
        '''
        This is an additional function which is not part of the tutorial. It will allow you to:
         - open a file dialog box,
         - filter the list of files according to file extension
         - set the QImage of your application (self.image) to a scaled version of the file)
         - update the widget
        '''
        filePath, _ = QFileDialog.getOpenFileName(self, "Open Image", "",
                                                  "PNG(*.png);;JPG(*.jpg *.jpeg);;All Files (*.*)")
        if filePath == "":  # if not file is selected exit
            return
        with open(filePath, 'rb') as f:  # open the file in binary mode for reading
            content = f.read()  # read the file
        self.image.loadFromData(content)  # load the data into the file
        width = self.width()  # get the width of the current QImage in your application
        height = self.height()  # get the height of the current QImage in your application
        self.image = self.image.scaled(width, height)  # scale the image from file and put it in your QImage
        self.update()  # call the update method of the widget which calls the paintEvent of this class

    # change mode between easy and hard
    def set_mode(self, mode: str):
        self.mode = mode
        self.getList(mode)
        self.currentWord = self.getWord()
        if not self.isGuessPhase:
            self.wordLabel.setText(self.currentWord)

    def next_turn(self):
        if not self.isGuessPhase and not self.guessOver:
            self.start_guess_phase()
        else:
            self.end_guess_phase_and_start_next_drawer()


# this code will be executed if it is the main module but not if the module is imported
#  https://stackoverflow.com/questions/419163/what-does-if-name-main-do
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PictionaryGame()
    window.show()
    app.exec()  # start the event loop running
