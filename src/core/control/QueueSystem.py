from enum import Enum
from typing import List, Dict, Tuple, Sequence, Any
from src.Config import NONE_LABEL


class QueueSystem:

    class HOTKEY_PROGRAM(str, Enum):
        HOTKEY_RUN_1 = "HGR_1"
        HOTKEY_RUN_2 = "HGR_2"
        HOTKEY_RUN_3 = "HGR_3"

    class LABEL(str, Enum):
        """
            KLasa reprezentuje etykiery kodowania, zgodne z etykietami gestów. Klasa ma również 2 dodatkowe elementy
            star reprezentująca dowolny gest,oraz non reprezentująca brak gestu.
        """
        call = "call"
        dislike = "dislike"
        fist = "fist"
        grip = "grip"
        like = "like"
        little_finger = "little_finger"
        one = "one"
        peace = "peace"
        rock = "rock"
        stop = "stop"
        three = "three"
        three3 = "three3"
        thumb_index = "thumb_index"
        non = NONE_LABEL
        star = "*"

    class INFO(str, Enum):
        GUI = "GUI"
        ROBOT_SERVER = "ROBOT-SERVER"

    class QUESTION(str, Enum):
        NEW = "NEW"
        ##
        MOV = "MOV"
        INTERACT = "INTERACT"
        ##
        CONNECT = "CONNECT"
        ##
        RUNSYS = "RUNSYS"
        ##
        MOVSYS = "MOVSYS"

        CONTROL_PROMPT = ">>"

    class COMMAND(str, Enum):
        DO = "DO"
        CLC = "CLC"
        END = "END" ## ma za zadanie zakończyć prace obecnego odpytania i wyczyści kolejkę
        BREAK = "BREAK" ## przerywa obecne odpytanie, ale pozostawia nowy stan odpytania
        FINISH = "FINISH" ## dodany do kolejki odpowiada za przerwanie w zapytania

    class OPTION(str, Enum):
        ## opcje MOV
        SITE_RL = "SITE_RL"
        SITE_UD = "SITE_UD"
        SITE_IO = "SITE_IO"
        LEFT = "LEFT"
        RIGHT = "RIGHT"
        UP = "UP"
        DOWN = "DOWN"
        IN = "IN"
        OUT = "OUT"
        ## ITERACT
        SELECT = "SELECT"
        PUSH_BUTTON = "PUSH_BUTTON"
        SLIDER = "PUSH_BUTTON"
        ACTIVATE_OBJECT = "ACTIVATE_OBJECT"
        DEACTIVATE_OBJECT = "DEACTIVATE_OBJECT"
        END_INTERACT = "END_INTERACT"
        ## CONNECT
        ENABLE = "ENABLE"
        DISABLE = "DISABLE"
        # SELECT = ...
        INCREMENT = "INCREMENT"
        DECREMENT = "DECREMENT"
        PICK = "PICK"
        NEXT = "NEXT"
        PREV = "PREV"
        RUN = "RUN"
        STOP = "STOP"
        RESUME = "RESUME"
        ## MOVSYS
        X_PLUS = "X_PLUS"
        X_MINUS = "X_MINUS"
        Y_PLUS = "Y_PLUS"
        Y_MINUS = "Y_MINUS"
        Z_PLUS = "Z_PLUS"
        Z_MINUS = "Z_MINUS"

    class DYNAMIC:
        class SelfStr_NUMERATOR(type):
            def __str__(cls) -> str: return str(cls.value)

        class NUMERATOR(metaclass=SelfStr_NUMERATOR):
            def __init__(self, value:int=0, range_:int=5):
                self.value = value
                self.range = range_

            def setup(self, value:int, range_:int):
                self.value = value
                self.range = range_

            def increment(self):
                self.value += 1
                if self.value >= self.range:
                    self.value = 0

            def decrement(self):
                self.value -= 1
                if self.value < 0:
                    self.value = self.range

            def __str__(self):
                return str(self.value)

        class SelfStr_LITERAL_LIST(type):
            def __str__(cls) -> str: return str(cls.objects_list[cls.index])

        class LITERAL_LIST(metaclass=SelfStr_LITERAL_LIST):
            def __init__(self, index=0, object_list = None):
                self.objects_list: Sequence[Any] = object_list
                self.index = index
                self.range = len(self.objects_list)

            def setup(self, index:int, object_list:Sequence[Any] ):
                self.objects_list = object_list
                self.index = index
                self.range = len(self.objects_list)

            def next(self):
                self.index += 1
                if self.index >= self.range:
                    self.index = 0

            def prev(self):
                self.index -= 1
                if self.index < 0:
                    self.index = self.range - 1

            def __str__(self):
                return str(self.objects_list[self.index])

    numerator_connect: DYNAMIC.NUMERATOR =  DYNAMIC.NUMERATOR(0, 3)
    literal_programs: DYNAMIC.LITERAL_LIST = DYNAMIC.LITERAL_LIST(0, ["None1", "None2", "None3"])

    main_hand = {  ## Aby aktywować zasobnik command_hand na końcu powinno być przypisane odpowiednie przekierowanie
        LABEL.stop + LABEL.rock: [QUESTION.NEW, INFO.GUI, QUESTION.MOV],
        LABEL.rock + LABEL.star: [COMMAND.END],
        LABEL.stop + LABEL.one: [QUESTION.NEW, INFO.GUI, QUESTION.INTERACT],
        LABEL.one + LABEL.star: [COMMAND.BREAK],
        LABEL.stop + LABEL.call: [QUESTION.NEW, INFO.ROBOT_SERVER, QUESTION.CONNECT],
        LABEL.call + LABEL.star: [COMMAND.END],
        LABEL.stop + LABEL.grip: [QUESTION.NEW, INFO.ROBOT_SERVER, QUESTION.RUNSYS],
        LABEL.grip + LABEL.star: [COMMAND.END],
        LABEL.stop + LABEL.thumb_index: [QUESTION.NEW, INFO.ROBOT_SERVER, QUESTION.MOVSYS],
        LABEL.thumb_index + LABEL.star: [COMMAND.END],

        # LABEL.star + LABEL.call: QUESTION.CONTROL_PROMPT,
    }
    command_hand = {
        QUESTION.MOV: {
            LABEL.star + LABEL.like: [OPTION.SITE_RL, OPTION.RIGHT, COMMAND.DO],
            LABEL.star + LABEL.thumb_index: [OPTION.SITE_RL, OPTION.LEFT, COMMAND.DO],
            LABEL.star + LABEL.rock: OPTION.SITE_UD,
            LABEL.rock + LABEL.three3: [OPTION.UP, COMMAND.DO],
            LABEL.rock + LABEL.little_finger: [OPTION.DOWN, COMMAND.DO],
            LABEL.fist + LABEL.stop: OPTION.SITE_IO,
            LABEL.stop + LABEL.one: [OPTION.IN, COMMAND.DO],
            LABEL.stop + LABEL.peace: [OPTION.OUT, COMMAND.DO],
            LABEL.call + LABEL.like: [COMMAND.DO],
            LABEL.call + LABEL.dislike: [COMMAND.CLC],
        },
        QUESTION.INTERACT: {
            LABEL.star + LABEL.thumb_index: [COMMAND.BREAK, QUESTION.NEW, INFO.GUI, QUESTION.INTERACT, OPTION.SELECT],
            LABEL.thumb_index + LABEL.one: OPTION.PUSH_BUTTON,
            LABEL.stop + LABEL.fist: [OPTION.ACTIVATE_OBJECT, COMMAND.DO],
            LABEL.fist + LABEL.stop: [OPTION.DEACTIVATE_OBJECT, COMMAND.DO],
            LABEL.thumb_index + LABEL.peace: OPTION.SLIDER,
        },
        QUESTION.CONNECT: {
            LABEL.thumb_index + LABEL.like: [OPTION.ENABLE, COMMAND.DO],
            LABEL.thumb_index + LABEL.dislike: [OPTION.DISABLE, COMMAND.DO],
            LABEL.fist + LABEL.rock: [OPTION.SELECT, numerator_connect],
            LABEL.rock + LABEL.one: [OPTION.INCREMENT, COMMAND.DO],
            LABEL.rock + LABEL.little_finger: [OPTION.DECREMENT, COMMAND.DO],
            LABEL.rock + LABEL.stop: [OPTION.PICK, COMMAND.DO]
        },
        QUESTION.RUNSYS: {
            LABEL.call + LABEL.one: [HOTKEY_PROGRAM.HOTKEY_RUN_1, OPTION.RUN, COMMAND.DO],  ## hot call
            LABEL.call + LABEL.peace: [HOTKEY_PROGRAM.HOTKEY_RUN_2, OPTION.RUN, COMMAND.DO],
            LABEL.call + LABEL.three: [HOTKEY_PROGRAM.HOTKEY_RUN_3, OPTION.RUN, COMMAND.DO],
            LABEL.fist + LABEL.rock: [OPTION.SELECT, literal_programs],
            LABEL.rock + LABEL.one: [OPTION.NEXT, COMMAND.DO],
            LABEL.rock + LABEL.little_finger: [OPTION.PREV, COMMAND.DO],
            LABEL.rock + LABEL.stop: [OPTION.RUN, COMMAND.DO],      ## run select program
            LABEL.grip + LABEL.like: [OPTION.RESUME, COMMAND.DO],   ## resume
            LABEL.grip + LABEL.dislike: [OPTION.STOP, COMMAND.DO],  ## stop
        },
        QUESTION.MOVSYS: {
            LABEL.grip + LABEL.like: [OPTION.Z_MINUS, COMMAND.DO],
            LABEL.grip + LABEL.dislike: [OPTION.Z_PLUS, COMMAND.DO],
            LABEL.grip + LABEL.thumb_index: [OPTION.X_PLUS, COMMAND.DO],
            LABEL.grip + LABEL.call: [OPTION.X_MINUS, COMMAND.DO],
            LABEL.grip + LABEL.little_finger: [OPTION.Y_PLUS, COMMAND.DO],
            LABEL.grip + LABEL.one: [OPTION.Y_MINUS, COMMAND.DO],
        },
    }