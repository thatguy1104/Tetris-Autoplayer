from board import Direction, Rotation
import board
import random
import itertools
from board import Board
from time import sleep
import statistics

# f = open("demofile2.txt", "w")
# f.write(str(allmoves))
# f.close()

class Player:
    def choose_action(self, board):
        raise NotImplementedError

def heights(trialboard):
    height = 24
    heights = []
    avg_heights = []
    for x in range(trialboard.width):
        min_y_seen = 24
        for y in range(trialboard.height):
            if (x, y) in trialboard:
                if y < min_y_seen:
                    min_y_seen = y
        heights.append((height - min_y_seen))
        # print((x, height - min_y_seen))
    return sum(heights)

def avg_heights(trialboard):
    all_heigts = heights(trialboard)
    num = len(all_heigts)
    return (sum(h[1] for h in all_heigts) / num)

def moves():
    allmoves = []
    movesDir = [Direction.Left,
                Direction.Right,
                Rotation.Clockwise,
                Rotation.Anticlockwise]

    for create_moves in itertools.combinations_with_replacement(movesDir, 9): # from https://docs.python.org/3/library/itertools.html
        subset_list = list(create_moves)
        subset_list.reverse()
        subset_list.append(Direction.Drop)
        allmoves.append(subset_list)

    return allmoves

def mainaction(board):
    score = []
    movescore = [1]
    allmoves = moves()
    
    for lists in allmoves:      
        sandbox = board.clone()
        oldscore = sandbox.score
        hole = 0
        height = 24
        allheights, diff_in_height, var, num_of_blocks, allholes = [], [], [], [], []
 
        for move in lists:
            if sandbox.falling is None: continue
            elif isinstance(move, Rotation):
                sandbox.rotate(move)
            elif isinstance(move, Direction):
                sandbox.move(move)
            else:
                continue        

        holes = 0
        for x in range(sandbox.width):
            min_y_seen = 24
            temp = 0
            for y in range(sandbox.height):
                if (x, y) in sandbox:
                    if y <= min_y_seen:

                        # OVERALL HEIGHT
                        min_y_seen = y
                        allheights.append((height - min_y_seen))

                        # HEIGHT DIFFERENCES
                        ma = max(y for (x, y) in sandbox.cells)
                        mi = min(y for (x, y) in sandbox.cells)
                        differences = (ma-mi)
                        diff_in_height.append(differences)

                        mean = (height - min_y_seen) / 10
                        difsq = (y - mean)*(y - mean)
                        var.append(difsq)

                        num_of_blocks.append(len(sandbox.cells))
                        
                if(x, y) in sandbox.cells:
                    temp = temp + 1
                if (x, y) not in sandbox.cells and temp > 0:
                    holes = holes + 1
                    allholes.append(holes)

                    # # HOLES IN THE BOARD
                    # if y >= min_y_seen:
                    #     if (x, y) in sandbox.cells and (x, y + 1) not in sandbox.cells and (x, y + 2) in sandbox.cells:
                    #         hole = hole + 10
                    #         allholes.append(hole)
                    #     else:
                    #         allholes.append(0)
            # VARIANCE
            act_var = sum(var) / 10

        # STANDARD DIVIATION
        sd = []
        sd.append(statistics.stdev(allheights))

        # BUMPINESS
        bump = []
        for i in range(len(allheights)-1):
            l = abs(allheights[i+1] - allheights[i])
            bump.append(l)

        # GAME
        if sandbox.score - oldscore > 99:
            movescore.append(10)
        elif sandbox.score - oldscore > 199:
            movescore.append(5)
        else:
            movescore.append(0)

        
        # movescore = [float(i)/max(movescore) for i in movescore]
        sumofscores = sum(movescore)
        sumofheights = sum(allheights)
        sumofdifferences = sum(diff_in_height)
        sumofbump = sum(bump)
        sumofsd = sum(sd)
        sumofvar = sum(var) / 1000
        sumofblocks = sum(num_of_blocks) / 10
        sumofholes = sum(allholes)

        ok = [-0.5, 0.25, 0.29, 0.05, 0.35, 0, 0, 0.35]
        # Normalise the values of individual weights: sums up to 1
        s = [float(i)/sum(ok) for i in ok] # from https://stackoverflow.com/questions/26785354/normalizing-a-list-of-numbers-in-python

        heuristics = (s[0]*sumofheights, s[1]*sumofdifferences, s[2]*sumofscores, s[3]*sumofbump,
                           s[4]*sumofsd, s[5]*sumofvar, s[6]*sumofblocks, s[7]*sumofholes)
        sum_of_heuro = sum(heuristics)

        # 2, 16, 1, 8 tuple move - score: 4440
        # 2, 0, 0, 8 tuples move - score: 5376
        # 10, 1, 1, 8 tuple move - score: 6874
        # 10, 1, 1, 10 tuple move - score:  8805
        # 10, 1, 10, 10 tuple move - score: 9699
        # 10, 1, 10, 1, 10 tuple move score: 10404 (with four heuristics)
        # 10, 1, 10, 1, 1, 0, 0, 0, 10 tuple move score: 17632 (left, right, left, right, clock, anti-clock)
        # 1.5, 0.5, 0.5, 0.1, 0, 0, 0,

        score.append(sum_of_heuro)
    lowestscoore = score.index(min(score))
    return allmoves[lowestscoore]

class RandomPlayer(Player):
    # def __init__(self, seed=None):
    #     self.random = Random(seed)

    def choose_action(self, board):
        return mainaction(board)


SelectedPlayer = RandomPlayer
