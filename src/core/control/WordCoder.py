
from src.numeric.TaskBuffer import TaskBuffer, TimeCell
from src.numeric.CircularBuffer import CircularBuffer

from src.core.control.Compiler import Compiler
from src.core.control.QueueSystem import QueueSystem

from typing import Any, Sequence

class WordCoder:

    max_word_in_queue: int = 10

    def __init__(self, max_sample_amount, min_sample_time_ms):

        self.queue: CircularBuffer[Any] = CircularBuffer(WordCoder.max_word_in_queue)

        self.task_main_hand: TaskBuffer = TaskBuffer(
            data=[],
            max_cells= max_sample_amount,
            base_time_ms= min_sample_time_ms
        )
        self.task_command_hand: TaskBuffer = TaskBuffer(
            data=[],
            max_cells= max_sample_amount,
            base_time_ms= min_sample_time_ms
        )

        self.youngest_2_main: CircularBuffer[str]    = CircularBuffer(2)
        self.youngest_2_command: CircularBuffer[str] = CircularBuffer(2)

        self.check_swap_main: bool = False
        self.check_swap_command: bool = False

        self.active_mode_question: str | None = None

    def check_if_swap_gestures(self):
        if len(self.task_main_hand) == 0 and len(self.task_command_hand) == 0: return

        new_main_tc: TimeCell = self.task_main_hand.get_first()
        new_command_tc: TimeCell = self.task_command_hand.get_first()

        new_main: str = new_main_tc.value
        new_command: str = new_command_tc.value

        if new_main != self.youngest_2_main[0]:
            self.check_swap_main = True
            self.youngest_2_main.put(new_main)
            # print("JUMP MAIN", new_main, self.youngest_2_main)

        if new_command != self.youngest_2_command[0]:
            self.check_swap_command = True
            self.youngest_2_command.put(new_command)
            # print("JUMP COMMAND", new_command, self.youngest_2_command)

    def update_status(self):
        # check if occurs swaps between gestures
        self.check_if_swap_gestures()

        # update main hand word question
        if self.check_swap_main:
            self.check_swap_main = False
            # print("MAIN")
            g_new: str
            g_prev:str

            g_prev, g_new = self.youngest_2_main.get_list()

            question_const2const:str = QueueSystem.main_hand.get(g_new + g_prev)
            question_const2star:str  = QueueSystem.main_hand.get(g_new + QueueSystem.LABEL.star)
            question_star2const:str  = QueueSystem.main_hand.get(QueueSystem.LABEL.star + g_prev)
            question_star2star:str   = QueueSystem.main_hand.get(g_new + g_prev)

            if question_const2const is not None:
                self.new_question(question_const2const)
            elif question_const2star is not  None:
                self.new_question(question_const2star)
            elif question_star2const is not  None:
                self.new_question(question_star2const)
            elif question_star2star is not  None:
                self.new_question(question_star2star)

        # update command hand word question
        if self.check_swap_command:
            self.check_swap_command = False
            # print("COMMAND")
            g_prev, g_new = self.youngest_2_command.get_list()

            command_const2const:str = QueueSystem.command_hand.get(g_new + g_prev)
            command_const2star:str  = QueueSystem.command_hand.get(g_new + QueueSystem.LABEL.star)
            command_star2const:str  = QueueSystem.command_hand.get(QueueSystem.LABEL.star + g_prev)
            command_star2star:str   = QueueSystem.command_hand.get(QueueSystem.LABEL.star + QueueSystem.LABEL.star)

            if command_const2const is not None:
                self.new_command(command_const2const)
            elif command_const2star is not None:
                self.new_command(command_const2star)
            elif command_star2const is not None:
                self.new_command(command_star2const)
            elif command_star2star is not None:
                self.new_command(command_star2star)

    def put_task_main_command(self, main: str, command: str):
        if len(self.youngest_2_main)==0 :
            self.youngest_2_main.put(main)
            self.youngest_2_main.put(main)
        if len(self.youngest_2_command)==0:
            self.youngest_2_command.put(command)
            self.youngest_2_command.put(command)

        self.task_main_hand.push(main)
        self.task_command_hand.push(command)

    def new_question(self, question):
        ## utworzenie nowego zapytania
        if isinstance(question, list):
            for q in question:
                self.queue.put(q)
                self.active_mode_question = q
        else:
            self.queue.put(question)
            self.active_mode_question = question
        ## rekcja sterego zapytania na nowe
        Compiler.compile(self.queue)

    def new_command(self, commands):
        ## wstawienie komend
        if isinstance(commands, list):
            for cmd in commands:
                self.queue.put(cmd)
        else:
            self.queue.put(commands)
        ## wykonanie kompilacji
        Compiler.compile(self.queue)

    def get(self)->Sequence[Any]:
        return self.queue.get_buffer()