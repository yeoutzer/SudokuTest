import pygame, sys
import requests
from bs4 import BeautifulSoup
from settings import *
from buttons import *

class App:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        self.running = True
        self.selected = None
        self.mousePos = None
        self.state = "playing"
        self.playingButtons = []
        self.font = pygame.font.SysFont("arial", cellSize // 2)
        self.lockedCells = []
        self.cellChanged = False
        self.wrongCells = []
        self.finished = False
        #self.grid = board3
        #self.load()
        self.grid = []
        self.getPuzzle("1")

    def run(self):
        while self.running:
            if self.state == "playing":
                self.playing_events()
                self.playing_update()
                self.playing_draw()
        pygame.quit()
        sys.exit()

#PLAYING STATE

    def playing_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            #User Click
            if event.type == pygame.MOUSEBUTTONDOWN:
                selected = self.mouseInGrid()
                if selected:
                    self.selected = selected
                else:
                    self.selected = None
                    for button in self.playingButtons:
                        if button.highlighted:
                            button.click()

            #User Type
            if event.type == pygame.KEYDOWN:
                if self.selected != None and list(self.selected) not in self.lockedCells:
                    if self.isInt(event.unicode):
                        #Cell changed
                        self.grid[self.selected[1]][self.selected[0]] = int(event.unicode)
                        self.cellChanged = True

    def playing_update(self):
        self.mousePos = pygame.mouse.get_pos()
        for button in self.playingButtons:
            button.update(self.mousePos)

        if self.cellChanged:
            self.wrongCells = []
            self.checkAllCells()
            if self.allCellsDone() and len(self.wrongCells) == 0:
                print("Solved")
                self.finished = True

    def playing_draw(self):
        self.window.fill(WHITE)
        
        for button in self.playingButtons:
            button.draw(self.window)

        if self.selected:
            self.drawSelection(self.window, self.selected)

        self.shadeLockedCells(self.window, self.lockedCells)
        self.shadeWrongCells(self.window, self.wrongCells)
        
        self.drawNumbers(self.window)
        self.drawGrid(self.window)
        pygame.display.update()
        self.cellChanged = False

#Check Board

    def allCellsDone(self):
        for row in self.grid:
            for num in row:
                if num == 0:
                    return False
        return True

    def clickedCheck(self):
        self.wrongCells = []
        self.checkZero()
        self.checkAllCells()

    def checkAllCells(self):
        self.checkRows()
        self.checkCols()
        self.checkGrids()

    def checkZero(self):
        for ri, row in enumerate(self.grid):
            for i in range(9):
                if self.grid[ri][i] == 0:
                    self.wrongCells.append([i, ri])

    def checkRows(self):
        for ri, row in enumerate(self.grid):
            check = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            for i in range(9):
                check[self.grid[ri][i]] += 1
            for i in range(9):
                if (check[self.grid[ri][i]] > 1
                and [i, ri] not in self.lockedCells
                and [i, ri] not in self.wrongCells
                and self.grid[ri][i] != 0):
                    self.wrongCells.append([i, ri])

    def checkCols(self):
        for i in range(9):
            check = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            for ri, row in enumerate(self.grid):
                check[self.grid[ri][i]] += 1
            for ri, row in enumerate(self.grid):
                if (check[self.grid[ri][i]] > 1
                and [i, ri] not in self.lockedCells
                and [i, ri] not in self.wrongCells
                and self.grid[ri][i] != 0):
                    self.wrongCells.append([i, ri])

    def checkGrids(self):
        for x in range(3):
            for y in range(3):
                check = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                for i in range(3):
                    for j in range(3):
                        ci = x * 3 + i
                        ri = y * 3 + j
                        check[self.grid[ri][ci]] += 1
                for i in range(3):
                    for j in range(3):
                        ci = x * 3 + i
                        ri = y * 3 + j
                        if (check[self.grid[ri][ci]] > 1
                        and [ci, ri] not in self.lockedCells
                        and [ci, ri] not in self.wrongCells
                        and self.grid[ri][ci] != 0):
                            self.wrongCells.append([ci, ri])
                


#Helper Functions

    def shadeWrongCells(self, window, wrong):
            for cell in wrong:
                pygame.draw.rect(window, WRONGCOLOR, (cell[0] * cellSize + gridPos[0], cell[1] * cellSize + gridPos[1], cellSize, cellSize))


    def shadeLockedCells(self, window, locked):
        for cell in locked:
            pygame.draw.rect(window, LOCKEDCOLOR, (cell[0] * cellSize + gridPos[0], cell[1] * cellSize + gridPos[1], cellSize, cellSize))

    def drawSelection(self, window, pos):
        pygame.draw.rect(window, LIGHTBLUE, (pos[0] * cellSize + gridPos[0], pos[1] * cellSize + gridPos[1], cellSize, cellSize))

    def drawGrid(self, window):
        pygame.draw.rect(window, BLACK, (gridPos[0], gridPos[1], WIDTH - 150, HEIGHT - 150), 2)
        for x in range(9):
            if x % 3 == 0:
                thick = 2
            else:
                thick = 1
            pygame.draw.line(window, BLACK, (gridPos[0] + (x * cellSize), gridPos[1]), (gridPos[0] + (x * cellSize), gridPos[1]  + 450), thick)
            pygame.draw.line(window, BLACK, (gridPos[0], gridPos[1] + (x * cellSize)), (gridPos[0] + 450, gridPos[1] + (x * cellSize)), thick)

    def drawNumbers(self, window):
        for ri, row in enumerate(self.grid):
            for ci, num in enumerate(row):
                if num != 0:
                    pos = [ci * cellSize + gridPos[0], ri * cellSize + gridPos[1]]
                    self.textToScreen(window, str(num), pos)

    def mouseInGrid(self):
        if (gridPos[0] < self.mousePos[0] < gridPos[0] + gridSize) and (gridPos[1] < self.mousePos[1] < gridPos[1] + gridSize):
            return ((self.mousePos[0] - gridPos[0]) // cellSize, (self.mousePos[1] - gridPos[1]) // cellSize)
        else:
            return False

    def loadButtons(self):
        self.playingButtons.append(Button(20, 40, WIDTH // 7, 40,
                                          function=self.clickedCheck,
                                          colour=(27, 142, 207),
                                          t="Check"))
        self.playingButtons.append(Button(140, 40, WIDTH // 7, 40,
                                          function=self.getPuzzle,
                                          colour=(117, 172, 112),
                                          params="1",
                                          t="Easy"))
        self.playingButtons.append(Button(WIDTH // 2 - (WIDTH // 7) // 2, 40, WIDTH // 7, 40,
                                          function=self.getPuzzle,
                                          colour=(204, 197, 110),
                                          params="2",
                                          t="Medium"))
        self.playingButtons.append(Button(380, 40, WIDTH // 7, 40,
                                          function=self.getPuzzle,
                                          colour=(99, 129, 48),
                                          params="3",
                                          t="Hard"))
        self.playingButtons.append(Button(500, 40, WIDTH // 7, 40,
                                          function=self.getPuzzle,
                                          colour=(207, 68, 68),
                                          params="4",
                                          t="Evil"))

    def textToScreen(self, window, text, pos):
        font = self.font.render(text, False, BLACK)
        fontWidth = font.get_width()
        fontHeight = font.get_height()
        pos[0] += (cellSize - fontWidth) // 2
        pos[1] += (cellSize - fontHeight) // 2
        window.blit(font, pos)

    def load(self):
        self.playingButtons = []
        self.loadButtons()
        self.lockedCells = []
        self.wrongCells = []
        self.finished = False

        for ri, row in enumerate(self.grid):
            for ci, num in enumerate(row):
                if num != 0:
                    self.lockedCells.append([ci, ri])

    def isInt(self, string):
        return string.isdigit()

    def getPuzzle(self, difficulty):
        html_doc = requests.get("https://nine.websudoku.com/?level={}".format(difficulty)).content
        soup = BeautifulSoup(html_doc, 'html.parser')
        ids = ['f00', 'f01', 'f02', 'f03', 'f04', 'f05', 'f06', 'f07', 'f08', 'f10', 'f11',
        'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f20', 'f21', 'f22', 'f23',
        'f24', 'f25', 'f26', 'f27', 'f28', 'f30', 'f31', 'f32', 'f33', 'f34', 'f35',
        'f36', 'f37', 'f38', 'f40', 'f41', 'f42', 'f43', 'f44', 'f45', 'f46', 'f47',
        'f48', 'f50', 'f51', 'f52', 'f53', 'f54', 'f55', 'f56', 'f57', 'f58', 'f60',
        'f61', 'f62', 'f63', 'f64', 'f65', 'f66', 'f67', 'f68', 'f70', 'f71', 'f72',
        'f73', 'f74', 'f75', 'f76', 'f77', 'f78', 'f80', 'f81', 'f82', 'f83', 'f84',
        'f85', 'f86', 'f87', 'f88']
        data = []

        for i in ids:
            data.append(soup.find('input', id=i))

        board = [[0 for x in range(9)] for x in range(9)]

        for i, cell in enumerate(data):
            try:
                board[i // 9][i % 9] = int(cell['value'])
            except:
                pass

        self.grid = board
        self.load()