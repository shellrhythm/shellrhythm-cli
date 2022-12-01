from index import print_at, print_column, print_cropped, print_lines_at, Conductor, load_charts, chartData
from blessed import Terminal

conduc = Conductor()

term = Terminal()
turnOff = False

hitCount = 0
maxHits = 16

hits = []
totalOffset = 0

def handle_input():
	val = ''
	val = term.inkey(timeout=1/60)
	if val:
		global totalOffset
		global hitCount
		offset = (conduc.currentBeat - int(conduc.currentBeat)) * (60/conduc.bpm)
		print_at(0,14, f"{term.center(str(round(offset, 3)))}")
		hits.append(offset)
		totalOffset += offset
		hitCount += 1
		if hitCount >= maxHits:
			global turnOff
			turnOff = True

def draw():
	text_beat = "○ ○ ○ ○"
	text_beat = text_beat[:int(conduc.currentBeat)%4 * 2] + "●" + text_beat[(int(conduc.currentBeat)%4 * 2) + 1:]

	print_at(0,10,f"{term.center('Hit on beat!')}")
	print_at(0,12,f"{term.center(text_beat)}")

def init():
	load_charts()
	conduc.loadsong(chartData[0])
	conduc.play()
	with term.fullscreen(), term.cbreak(), term.hidden_cursor():
		print(term.clear)
		while not turnOff:
			deltatime = conduc.update()
			draw()

			handle_input()

	print(round(totalOffset / hitCount, 3))
	return totalOffset / hitCount

if __name__ == "__main__":
	init()