from itertools import combinations
from pysat.solvers import Glucose3
from pysat.card import *
import tkinter, time
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

Color_type = ['red', 'green', 'black']
Algorithms_type = ['AStar', 'Backtracking', 'Brute force', 'PySAT']
Delaytime = ['0.5', '0.75', '1.0', '1.25', '1.5']

FONT12 = 'Time 12'
FONT16 = 'Time 16'

def readMatrix(strinput):
    Matrix = list()
    f = open(strinput[:-1])
    for line in f:
        line = line.replace('.', '-1')
        temp = list()
        for num in line.split():
            temp.append(int(num))
        Matrix.append(temp)
    return Matrix

def getConstraint(matrix):
    i = 0
    for x in matrix:
        for y in x:
            if y >= 0:
                i += 1
    return i

class Color_puzzle(Frame):
    def __init__(self, master):
        
        self.init_algo()
        # GUI
        super().__init__(master)
        self.halt = False
        self.DelayBox = ttk.Combobox(self, width=25, height=2, values=Delaytime)
        self.Algorithm = ttk.Combobox(self, width=25, height=2, values=Algorithms_type)
        self.Address = Text(self, font=FONT12, height=1, width=19)
        self.stepheur = Text(self, font=FONT12, height=1, width=19)
        self.buttonBrowser = Button(self, text='Browse', font=FONT12, height=1, width=10, command=lambda:self.BrowseFiles())
        self.buttonUpdate = Button(self, text='Update', font=FONT12, height=1, width=10, command=lambda:self.start())
        #self.buttonStop = Button(self, text='Stop', font=FONT12, height=2, width=10, command=lambda:self.stopprocess())
        self.lbframe = LabelFrame(self, text='Algorithm', font=FONT16)
        self.LbinfoFrame = LabelFrame(self, bg='burlywood1')
        self.gridGUI()


    def init_algo(self):
        self.row = 0
        self.column = 0
        self.posCell = [[0, 0], [-1, -1], [-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1], [0, -1]]

        
        self.info = list(list())
        self.adj = list(list())
        self.color = list(list())
        self.clauses = list()
        self.stp = 0
        # A*
        self.invalid = list()
        self.heur = 0
        self.space = set()
        self.visited = list(list())
        self.check_AStar = list()

        self.cellNum = list()
        self.foundSolution = 0

    def gridGUI(self):
        self.Address.grid(row=0, column=0, padx=1, pady=2)
        self.DelayBox.grid(row=1, column=0, padx=1, pady=2)
        self.Algorithm.grid(row=2, column=0, padx=1, pady=2)
        self.stepheur.grid(row=3, column=0, padx=1, pady=2)
        self.buttonBrowser.grid(row=0, column=1, padx=1, pady=2)
        self.buttonUpdate.grid(row=1, column=1, rowspan=2, padx=1, pady=2)
        #self.buttonStop.grid(row=0, column=2, rowspan=3, padx=1)
        self.lbframe.grid(row=5, column=0, columnspan=10)
        self.LbinfoFrame.grid(row=4, columnspan=16)

    def BrowseFiles(self):
        filename = filedialog.askopenfilename(
            title="Select a File",
            filetypes=(("Text files","*.txt*"),("all files","*.*")))
        self.Address.delete('1.0', tkinter.END)
        self.Address.insert(tkinter.END, filename)
        InforMatrix = readMatrix(self.Address.get('1.0', tkinter.END))
        ColorMatrix = [[-1 for i in range(0, len(InforMatrix))]
                            for j in range(0, len(InforMatrix))]
        self.createBoard(InforMatrix, ColorMatrix)
        for x in self.LbinfoFrame.winfo_children():
            x.destroy()
        '''    
        Label(self.LbinfoFrame, text=f'SIZE: {len(InforMatrix)}x{len(InforMatrix)}', font=(
            'Helvetica bold', 12), bg='burlywood1').grid(row=0, column=0, padx=10)
        Label(self.LbinfoFrame, text=f'CONSTRAINTS: {getConstraint(InforMatrix)}', font=(
            'Helvetica bold', 12), bg='burlywood1').grid(row=0, column=1, padx=10)
        Label(self.LbinfoFrame, font=('Helvetica bold', 12),
              text='TIME LIMIT: 10 minutes', bg='burlywood1').grid(row=0, column=3)
        '''
    def createCell(self, infoMa, colorMa):
        if infoMa < 0:
            infoMa = " "
        lb = tkinter.Label(self.lbframe,text=infoMa,font=FONT12,bg=Color_type[colorMa],fg='white',height=2,width=4,relief=RIDGE)
        return lb

    def createBoard(self, infoMa, colorMa):
        for x in self.lbframe.winfo_children():
            x.destroy()

        for i in range(0, len(infoMa)):
            for j in range(0, len(infoMa)):
                self.createCell(infoMa[i][j], colorMa[i][j]).grid(column=j, row=i)

    def start(self):
        step = -1
        heur = -1
        InfoMatrix = readMatrix(self.Address.get('1.0', tkinter.END))
        ColorMatrix = [[-1 for i in range(0, len(InfoMatrix))]for j in range(0, len(InfoMatrix))]

        self.createBoard(InfoMatrix, ColorMatrix)
        self.lbframe['text'] = self.Algorithm.get()
        fAddr = self.Address.get('1.0', tkinter.END)[:-1]
        algor = self.Algorithm.get()
        if self.DelayBox.get():
            timedelay = float(self.DelayBox.get())
        else: timedelay = 0.5 # default

        if fAddr == '' or algor == '':
            # show messagebox
            messagebox.showinfo("ErrorMessage", "fill can not empty")
        else:
            time.sleep(timedelay)
            self.Run(fAddr, algor, timedelay)
            
    def Restart(self, step, heur, colorMa):
        self.update()
        self.UpdateColor(colorMa)
        # print lai step va heuristic
        #obj.stepHeur['text'] = f'step: {step} - heuristic: {heur}'
        self.stepheur.delete('1.0', tkinter.END)
        text = f'step: {step} - heuristic: {heur}'
        self.stepheur.insert(tkinter.END, text)
        if self.DelayBox.get() == '':
            time.sleep(0.1)
        else:
            time.sleep(float(self.DelayBox.get())-0.3)

    def getInfoStart(self):
        return (self.Address.get('1.0', tkinter.END), self.Algorithm.get())

    def UpdateColor(self, matrix):
        for i in range(0, len(matrix)):
            for j in range(0, len(matrix)):
                self.lbframe.grid_slaves(row=i, column=j)[0].config(bg=Color_type[matrix[i][j]])

    def readFileData (self, addrFile):
        self.init_algo()
        f = open(addrFile, "r")
    
        for line in f:
            # All position '.' will be replace to '-1' for progress
            line = line.replace('.', '-1')
            self.info.append(line.split())

        self.row = len(self.info)
        self.column = len(self.info[0])

        for i in range(self.row):
            self.color.append(list())
            self.adj.append(list())
            self.visited.append(list())

            for j in range(self.column):
                self.info[i][j] = int(self.info[i][j])
                # Pos have 9 cell around
                numAdj = 9
                if i == 0 or j == 0 or i == self.row - 1 or j == self.column - 1:
                    if i in (0, self.row - 1) and j in (0, self.column - 1):
                        # Pos vertex of the matrix has 4 cell around
                        numAdj = 4
                    else:
                        # Pos edge of the matrix has 6 cell around
                        numAdj = 6

                if self.info[i][j] != -1:
                    self.cellNum.append((i, j)) 

                self.adj[i].append(numAdj)
                self.color[i].append(0)
                self.visited[i].append(0)

        f.close()

    def makeCNF(self):
        for i in range(self.row):
            for j in range(self.column):
                if self.info[i][j] != -1:
                    # xC(n - x + 1)
                    negCons = combinations([0, 1, 2, 3, 4, 5, 6, 7, 8], self.adj[i][j] - self.info[i][j] + 1)
                    # xC(x + 1)
                    posCons = combinations([0, 1, 2, 3, 4, 5, 6, 7, 8], self.info[i][j] + 1)

                    if negCons:
                        for choosen in negCons:
                            clause = list()

                            for k in choosen:
                                X = i + self.posCell[k][0]
                                Y = j + self.posCell[k][1]
                                if (X not in range(self.row)) or (Y not in range(self.column)):
                                    break
                                clause.append(X * self.column + Y + 1)

                            if len(clause) == len(choosen) and clause not in self.clauses:
                                self.clauses.append(clause)
                                self.invalid.append(self.heur)
                                self.heur += 1

                    if posCons:
                        for choosen in posCons:
                            clause = list()

                            for k in choosen:
                                X = i + self.posCell[k][0]
                                Y = j + self.posCell[k][1]
                                if (X not in range(self.row)) or (Y not in range(self.column)):
                                    break
                                clause.append(-(X * self.column + Y + 1))

                            if len(clause) == len(choosen) and clause not in self.clauses:
                                self.clauses.append(clause)
                                self.invalid.append(self.heur)
                                self.heur += 1

    def pySat(self):
        self.makeCNF()
        g = Glucose3()

        for item in self.clauses:
            g.add_clause(item)

        if g.solve():
            self.foundSolution = 1
            model = g.get_model()

            for value in model:
                temp = abs(value) - 1
                X = temp // self.column
                Y = temp % self.column

                if value > 0:
                    self.color[X][Y] = 1
                else:
                    self.color[X][Y] = 0
        self.Restart(1, 0, self.color)
        
    def calcH (self, cell):
        #heur so clause
        #literal ID cell
        # Thoa cang nhieu rang buoc thi cang hop le => Heristic
        res = 0
        for i in self.invalid:
            if cell in self.clauses[i]:
                res += 1
        
        return self.heur - res

    def AStar(self, step, delayTime):
        if step not in self.check_AStar:
            self.Restart(step, self.heur, self.color)
            self.check_AStar.append(step)

        q = list()
        
        if str(self.invalid) in self.space: 
            return
        self.space.add(str(self.invalid))
        
        for cell in self.cellNum:
            for k in range(9):
                X = cell[0] + self.posCell[k][0]
                Y = cell[1] + self.posCell[k][1]

                if (X not in range(self.row)) or (Y not in range(self.column)):
                    continue

                if not self.visited[X][Y]:
                    id = X * self.column + Y + 1
                    temp = self.calcH(id)
                    if temp < self.heur:
                        H = temp
                        q.append((H, id, 1))

                    id = -(X * self.column + Y + 1)
                    temp = self.calcH(id)
                    if temp < self.heur:
                        H = temp
                        q.append((H, id, 0))
     
        q.sort(key=lambda x: x[0], reverse=True)

        #list cac o mau
        for choosen in q:
            
            changed = list()
            
            for i in self.invalid:
                if choosen[1] in self.clauses[i]:
                    changed.append(i)
            for i in changed:
                self.invalid.remove(i)

            preHeur = self.heur
            self.heur = choosen[0]
            temp = abs(choosen[1]) - 1
            self.color[temp // self.column][temp % self.column] = choosen[2]
            self.visited[temp // self.column][temp % self.column] = 1

            if self.SAT() or self.heur == 0:
                self.foundSolution = 1
                self.Restart(self.check_AStar[-1] + 1, 0, self.color)
                return
            
            self.AStar(step + 1, delayTime)
            
            if self.foundSolution:
                return

            self.color[temp // self.column][temp % self.column] = choosen[2]
            self.visited[temp // self.column][temp % self.column] = 0
            self.heur = preHeur

            for i in changed:
                self.invalid.append(i)

    def SAT(self):
        for cell in self.cellNum:
            temp = 0
            for i in range(9):
                X = cell[0] + self.posCell[i][0]
                Y = cell[1] + self.posCell[i][1]

                if (X not in range(self.row)) or (Y not in range(self.column)):
                    continue

                temp += self.color[X][Y]

            if temp != self.info[cell[0]][cell[1]]:
                return 0

        return 1

    def backTracking(self, start):
        self.Restart(self.stp, 0, self.color)
        self.stp += 1
        if (start == len(self.cellNum)):
            if self.SAT():
                self.foundSolution = 1
            return

        perm = combinations([0, 1, 2, 3, 4, 5, 6, 7, 8], self.info[self.cellNum[start][0]][self.cellNum[start][1]])

        for each in list(perm):
            changed = list()
            count = 0

            for i in range(9):
                X = self.cellNum[start][0] + self.posCell[i][0]
                Y = self.cellNum[start][1] + self.posCell[i][1]

                if (X not in range(self.row)) or (Y not in range(self.column)):
                    continue

                if i in each:
                    if not self.color[X][Y]:
                        self.color[X][Y] = 1
                        changed.append((X, Y))

                count += self.color[X][Y]

            if count != len(each):
                for i in changed:
                    self.color[i[0]][i[1]] = 0
                continue

            self.backTracking(start + 1)
            if self.foundSolution:
                return

            for i in changed:
                self.color[i[0]][i[1]] = 0
    
    def bruteForce(self, start):
        self.Restart(self.stp, 0, self.color)
        self.stp += 1
        if (start == (self.row - 1) * self.column + (self.column - 1)):
            if self.SAT():
                self.foundSolution = 1
            return

        X = start // self.column
        Y = start % self.column

        if Y == self.column - 1:
            start = (X + 1) * self.column
        else:
            start += 1

        self.bruteForce(start)
        if self.foundSolution:
            return

        self.color[X][Y] = 1

        self.bruteForce(start)
        if self.foundSolution:
            return

        self.color[X][Y] = 0

    def showSolution(self):
        for self.row in self.info:
            for item in self.row:
                if item == -1:
                    print(" . ", end="")
                else:
                    print("", item, "", end="")
            print()

        for i in range(len(self.info[0])):
            print("---", end="")

        if not self.foundSolution:
            print("NO SOLUTION")
            return
        print("\n")
        for self.row in self.color:
            for item in self.row:
                print("", item, "", end="")
            print()

    def  RunFinish (self):
        return self.foundSolution

    def color_(self):
        return self.color

    def info_(self):
        return self.info

    def RunPysat(self, fileAddr):

        self.readFileData(fileAddr)
        self.pySat()
        self.showSolution()
        messagebox.showinfo("CONGRATULATIONS", "SUCCESS!")

    def RunBacktracking(self, fileAddr):

        self.readFileData(fileAddr)
        self.backTracking(0)
        self.showSolution()
        messagebox.showinfo("CONGRATULATIONS", "SUCCESS!")

    def RunBruteForce(self, fileAddr):

        self.readFileData(fileAddr)
        self.bruteForce(0)
        self.showSolution()
        messagebox.showinfo("CONGRATULATIONS", "SUCCESS!")

    def RunAstar(self, fileAddr, delayTime):

        self.readFileData(fileAddr)
        self.makeCNF()
        self.AStar(0, delayTime)
        self.showSolution()
        messagebox.showinfo("CONGRATULATIONS", "SUCCESS!")

    def Run(self, fileAddr, algorithm, timeDelay): 

        if algorithm == "PySAT": 
            self.RunPysat(fileAddr)
        
        if algorithm == "AStar":
            self.RunAstar(fileAddr, timeDelay)
            
        
        if algorithm == "Backtracking":
            self.RunBacktracking(fileAddr)
        
        if algorithm == "Brute force":
            self.RunBruteForce(fileAddr)

# GUI
window = Tk()
window.title("Color Puzzle")
main = Color_puzzle(window)
main.pack()
main.mainloop()