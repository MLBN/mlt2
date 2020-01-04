# some runtime goodies.

class Matrix():
    # one dimensional array with basic spreadsheet function.
    def __init__(self,cols=1):
        self.cols=cols
        self.data=list()
        self.frozen=False

    def __call__(self,i,j):
        # i=zeile, j=spalte
        return self.data[ (i-1)*self.cols+ j-1]

    def reset(self,cols=1):
        self.data.clear()
        self.cols=cols

    def freeze(self):
        self.frozen=True

    def unfreeze(self):
        self.frozen=False

    def append(self,x):
        if not self.frozen:
            self.data.append(x)


    def set(self,i,j,x):
        self.data[ (i-1)*self.cols+j-1] = x

    def csum(self,j):
        # Spaltensumme
        tot = 0
        curser = j-1
        maxindex=len(self.data)-1
        while curser <= maxindex:
            tot += self.data[ curser ]
            curser += self.cols
        return tot

M = Matrix(2)
M.data=[1,2,3,4,5,6]


