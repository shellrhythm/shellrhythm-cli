
from src.termutil import term, print_at
from src.constants import Color
from src.scenes.game_objects.base_object import GameplayObject

class EditorTimeline():
    backcolor = Color("1d1d1d")
    topcolor = Color("505050")

    current_tab:int = 0

    async def draw(self, editor):
        # print_at(0,term.height-3, editor.reset_color+"-"*(term.width))
        for i in range(-(int(term.width/80)+1),int(term.width/8)-(int(term.width/80))+1):
            char = "'"
            if (4-(i%4))%4 == (int(editor.conduc.current_beat)%4):
                char = "|"
            slight_offset = int(editor.conduc.current_beat%1 * 8)
            real_draw_at = int((i*8)+(term.width*0.1)-slight_offset)
            draw_at = max(real_draw_at, 0)
            # maxAfterwards = int(min(7,term.width - (drawAt+1)))
            if i+editor.conduc.current_beat >= 0 or real_draw_at == draw_at:
                print_at(draw_at, term.height-5, char+(" "*7))
            else:
                print_at(draw_at, term.height-5, " "*8)
        print_at(0,term.height-4, self.backcolor.on_col+(" "*(term.width-1)))
        print_at(int(term.width*0.1), term.height-4, "@")
        beatpos_string = f"{int(editor.conduc.current_beat//4)}"\
            + f", {round(editor.conduc.current_beat%4, 5)}"
        print_at(0,term.height-6, self.topcolor.on_col
        + " " + editor.loc('editor.timelineInfos.bpm')+ ": " + str(editor.conduc.bpm) +
        "   " + editor.loc('editor.timelineInfos.snap')+ ": 1/" + str(editor.snap)+
        "   " + editor.loc('editor.timelineInfos.beatpos') + ": " + beatpos_string+
        "  " + editor.reset_color
        # +f"{editor.loc('editor.timelineInfos.bpm')}: {editor.conduc.bpm} | "
        # +f"{editor.loc('editor.timelineInfos.snap')}: 1/{editor.snap} | "
        # +f"{editor.loc('editor.timelineInfos.bar')}: {int(editor.conduc.current_beat//4)} | "
        # +f"{editor.loc('editor.timelineInfos.beat')}: {round(editor.conduc.current_beat%4, 5)} | "
        +term.clear_eol)
        for note in reversed(editor.notes):
            remaining_beats = note.beat_position - editor.conduc.current_beat

            #TIMELINE
            if remaining_beats*8+(term.width*0.1) >= 0:
                rendered_string = note.editor_timeline_icon(
                    editor.reset_color + self.backcolor.on_col, False
                )
                if note.editor_tab == self.current_tab:
                    print_at(
                        int(remaining_beats*8+(term.width*0.1)),
                        term.height-4,
                        rendered_string
                    )

        #Current note info
        if len(editor.notes) > editor.selected_note:
            selected_obj:GameplayObject = editor.notes[editor.selected_note]
            print_at(0, term.height-7, selected_obj.display_informations(
                editor.reset_color, editor.selected_note))

            #Render selected note on top in the timeline
            obj_remaining_beats = selected_obj.beat_position - editor.conduc.current_beat
            if obj_remaining_beats*8+(term.width*0.1) >= 0:
                rendered_string = selected_obj.editor_timeline_icon(
                    editor.reset_color + self.backcolor.on_col, True)
                print_at(
                    int(obj_remaining_beats*8+(term.width*0.1)),
                    term.height-4,
                    rendered_string
                )

    async def input(self, editor, val):

        if val.name in ("KEY_RIGHT", "KEY_SRIGHT"):
            multiplier = {"KEY_RIGHT": 1, "KEY_SRIGHT": 4}[val.name]
            editor.conduc.current_beat += (1/editor.snap)*4*multiplier
        if val.name in ("KEY_LEFT", "KEY_SLEFT"):
            multiplier = {"KEY_LEFT": 1, "KEY_SLEFT": 4}[val.name]
            editor.conduc.current_beat = max(
                editor.conduc.current_beat - (1/editor.snap)*4*multiplier,
                0
            )
        if val.name == "KEY_HOME":
            editor.conduc.current_beat = 0

        if len(editor.notes) > 0:
            if val.name in ("KEY_DOWN", "KEY_SDOWN"):
                multiplier = {"KEY_DOWN": 1, "KEY_SDOWN": 4}[val.name]
                editor.selected_note = min(editor.selected_note + (1*multiplier),
                                        len(editor.chart["notes"])-1)
                actual_note = editor.notes[editor.selected_note]
                editor.conduc.current_beat = actual_note.beat_position
            if val.name in ("KEY_UP", "KEY_SUP"):
                multiplier = {"KEY_UP": 1, "KEY_SUP": 4}[val.name]
                editor.selected_note = max(editor.selected_note - (1*multiplier), 0)
                actual_note = editor.notes[editor.selected_note]
                editor.conduc.current_beat = actual_note.beat_position

        if val in ["1", "2"]:
            self.current_tab = int(val)-1
