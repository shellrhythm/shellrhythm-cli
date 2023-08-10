import json
import datetime
from src.termutil import print_at, print_lines_at, term, reset_color, print_box
from src.constants import RANKS, INPUT_FREQUENCY



def getRank(score):
    for i in range(len(RANKS)):
        rank = RANKS[i]
        if score >= rank[1]:
            return [rank[0], i, rank[2]]
    return ["X", -1, term.darkred]

class Grid:
    x = 0
    y = 0
    width = 0
    height = 0
    pointsToPlot = []
    colors = []
    symbolLookup = [
        [" ", "⠁", "⠂", "⠄", "⡀"], 
        ["⠈", "⠉", "⠊", "⠌", "⡈"],
        ["⠐", "⠑", "⠒", "⠔", "⡐"],
        ["⠠", "⠡", "⠢", "⠤", "⡠"],
        ["⢀", "⢁", "⢂", "⢄", "⣀"]
    ]
    gridrange = [-0.4,0.4]
    offset = 2

    def processPoints(self, point1, point2):
        if point1//4 == point2//4:
            return [self.symbolLookup[int(point1)%4+1][int(point2)%4+1]]
        else:
            if point2 != 2**32:
                return [
                    self.symbolLookup[int(point1)%4+1][0],
                    self.symbolLookup[0][int(point1)%4+1]
                ]
            else:
                return [
                    self.symbolLookup[int(point1)%4+1][0]
                ]

    def draw(self, cursorPos = 0):
        for i in range(
            max(0, (cursorPos*2)-len(self.pointsToPlot)), 
            min(len(self.pointsToPlot), (cursorPos + self.width)*2),
            2
        ):
            point1 = min(max(self.pointsToPlot[i],   self.gridrange[0]), self.gridrange[1])
            firstpos = (
                (point1 / (self.gridrange[1] - self.gridrange[0])) - self.gridrange[0]
                ) * self.height*4 + self.offset
            if i+1 < len(self.pointsToPlot):
                point2 = min(max(self.pointsToPlot[i+1], self.gridrange[0]), self.gridrange[1])
                secpos   = (
                    (point2 / (self.gridrange[1] - self.gridrange[0])) - self.gridrange[0]
                ) * self.height*4 + self.offset
            else:
                secpos = -2**32
            points = self.processPoints(firstpos, secpos)
            for j in range(len(points)):
                atpos = ((self.pointsToPlot[i+j] / (self.gridrange[1] - self.gridrange[0])) - self.gridrange[0]) * self.height + (self.offset/4)
                print_at(self.x + (i//2), self.y + int(atpos), self.colors[i+j] + points[j])

    def __init__(self, x, y, width, height) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height


def scoreCalc(maxScore, judgements, accuracy, missesCount, chart):
    filteredJudgementCount = 0
    totalNotes = 0
    for i in judgements:
        if i != {}:
            filteredJudgementCount += 1
    for i in chart["notes"]:
        if i["type"] == "hit_object":
            totalNotes += 1
    
    #TO ANYONE CHECKING THIS OUT: Here are the following ways score is calculated

    #Current score version: 1.1

    #1: Acc/100 * 80% of max score + 1/(misses+1) * 20% of max score
    #1.1: Acc/100 * 80% of max score + notes hit / (notes hit + misses) * 20% of max score

    if filteredJudgementCount != 0:
        accuracy_score = (accuracy/100) * (maxScore*0.8)
        miss_weight_on_score = filteredJudgementCount/(filteredJudgementCount+missesCount)
        combo_score = miss_weight_on_score * (maxScore*0.2)
        position_in_song = filteredJudgementCount/totalNotes

        result = (accuracy_score + combo_score) * position_in_song
        return result
    else:
        return -1

class ResultsScreen:
    resultsData = {}
    judgementCount = [0,0,0,0,0,0]
    rankIMGFile = []
    rankIMGImages = []
    isEnabled = False
    gameTurnOff = False
    offsets = []
    hitWindows = [None] #I did in fact change it later
    oneRowIsThisMS = 0.05 #so max 18 rows to write everything
    centerRow = 24
    debug = False
    grid = Grid(0,0,10,10)
    auto = False

    def setup(self):
        self.judgementCount = [0,0,0,0,0,0]
        self.grid.x = 5
        self.grid.y = self.centerRow - 8
        self.grid.height = 20
        self.offsets.clear()
        for i in range(len(self.resultsData["judgements"])):
            if self.resultsData["judgements"][i] != {}:
                self.judgementCount[self.resultsData["judgements"][i]["judgement"]] += 1
                self.offsets.append(self.resultsData["judgements"][i]["offset"])
                self.grid.pointsToPlot.append(-self.resultsData["judgements"][i]["offset"])
                self.grid.colors.append(RANKS[self.resultsData["judgements"][i]["judgement"]][3])
        self.render_accuracy_view()

    def draw_debug_info(self):
        print_at(60, 4, "Scored at date: " + datetime.datetime.fromtimestamp(self.resultsData["time"]).strftime('%d %b %y, %H:%M:%S'))
        print_at(60, 5, "Chart SHA256: " + term.underline + self.resultsData["checksum"][:6] + reset_color + self.resultsData["checksum"][6:])

    def render_accuracy_view(self, cursorPos = 0):
        for i in range(5):
            print_at(5, self.centerRow+(i*2)+2, RANKS[i+1][3]+" "*(term.width-9)+ reset_color)
            print_at(5, self.centerRow+(i*2)+1, RANKS[i+1][3]+" "*(term.width-9)+ reset_color)
            print_at(5, self.centerRow-(i*2)-1, RANKS[i+1][3]+" "*(term.width-9)+ reset_color)
            print_at(5, self.centerRow-(i*2)-2, RANKS[i+1][3]+" "*(term.width-9)+ reset_color)
        if self.resultsData != {}:
            print_at(3, self.centerRow, f"{RANKS[0][2]+RANKS[0][3]}0" + " "*(term.width-8)+ reset_color)
            print_at(3, self.centerRow-10, "+")
            print_at(3, self.centerRow+10, "-")
            self.grid.draw(cursorPos)


    def draw(self):
        if self.resultsData != {}:
            print_box(4, 2, term.width-7, term.height-4, reset_color, 0)
            rank = getRank(self.resultsData["score"])
            print_lines_at(5,3, self.rankIMGImages[rank[1]], color=rank[2])
            print_at(16, 4, f"{rank[2]}SCORE{reset_color}: {int(self.resultsData['score'])}")
            print_at(16, 6, f"{rank[2]}ACCURACY{reset_color}: {int(self.resultsData['accuracy'])}%")
            print_at(31, 4, f"{RANKS[0][2]}Marvelous: {RANKS[0][4]}{self.judgementCount[0]}{reset_color}")
            print_at(31, 5, f"{RANKS[1][2]}Perfect:   {RANKS[1][4]}{self.judgementCount[1]}{reset_color}")
            print_at(31, 6, f"{RANKS[2][2]}Epic:      {RANKS[2][4]}{self.judgementCount[2]}{reset_color}")
            print_at(31, 7, f"{RANKS[3][2]}Good:      {RANKS[3][4]}{self.judgementCount[3]}{reset_color}")
            print_at(31, 8, f"{RANKS[4][2]}Eh:        {RANKS[4][4]}{self.judgementCount[4]}{reset_color}")
            print_at(31, 9, f"{RANKS[5][2]}Misses:    {RANKS[5][4]}{self.judgementCount[5]}{reset_color}")
            if self.auto:
                print_at(16, 8, f"{term.reverse}[AUTO ENABLED]{reset_color}")
            if self.debug:
                self.draw_debug_info()
            self.render_accuracy_view()

    def handle_input(self):
        val = ''
        val = term.inkey(timeout=1/INPUT_FREQUENCY, esc_delay=0)

        if val.name == "KEY_ESCAPE":
            print(term.clear)
            self.gameTurnOff = True
        
    def __init__(self) -> None:
        f = open("./assets/ranks.txt")
        self.rankIMGFile = f.readlines()
        f.close()
        for lineIndex in range(0, len(self.rankIMGFile), 10):
            self.rankIMGImages.append("".join(self.rankIMGFile[lineIndex:lineIndex+10]))
        pass

if __name__ == "__main__":
    import sys
    results = ResultsScreen()
    f = open("./scores/" + sys.argv[1])
    results.resultsData = json.load(f)
    f.close()

    print(len(results.offsets))
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        print(term.clear)
        results.setup()

        while not results.gameTurnOff:
            results.draw()
            results.handle_input()

