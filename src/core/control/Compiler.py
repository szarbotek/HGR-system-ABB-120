from src.numeric.CircularBuffer import CircularBuffer
from src.core.control.QueueSystem import QueueSystem
from src.core.control.SignalUnit import SignalUnit

from src.utils.Logs import Logs


from typing import Sequence, Any, List

class Compiler:
    _queue: CircularBuffer

    @classmethod
    def compile(cls, queue: CircularBuffer):
        """
           Kompile opoowiada za analize polecen wpisywanych poprzez ruchy rą na podstawie wpisanej przez nie koleji
           wykonywane zostaje akcje odpytań oraz akce DO
        """
        _queue = queue

        try:
            cls._LOG("\n\n@compile START ====================================", cls._queue)
            code: List[str] = cls._queue.get_reverse_buffer()

            if not( set(code).intersection(QueueSystem.QUESTION) ):
                ## jesłi kolejka nie zaweira zapytania nie mogą być wstawiane komendy i opcje
                cls._TRASH(QueueSystem.COMMAND.DO)
            # elif WordCoder.QUESTION.CONTROL_PROMPT in code:
            #     # index = code.index(WordCoder.QUESTION.CONTROL_PROMPT)
            #     pass
            #
            elif QueueSystem.COMMAND.BREAK in code:
                cls.BREAK( code )
            elif QueueSystem.COMMAND.END in code:
                cls.END()
            elif QueueSystem.QUESTION.NEW in code:
                ## inicjajca parametrów zapytania
                index = code.index( QueueSystem.QUESTION.NEW )
                ## inicjajca parametrów zapytania
                new_question = code[index + 1:]
                cls.NEW(new_question)
            elif QueueSystem.QUESTION.MOV in code:
                cls.MOV( code )
            elif QueueSystem.QUESTION.INTERACT in code:
                cls.INTERACT( code )
            elif QueueSystem.QUESTION.CONNECT in code:
                cls.CONNECT( code )
            elif QueueSystem.QUESTION.RUNSYS in code:
                cls.RUNSYS( code )

            cls._LOG("@compile END =========================================", _queue)
        except:
            Logs.print(f"<ERR:WordCoder> Compiler Error")

    ACTIVATE_LOG: bool = False

    print( SignalUnit.FLAG_emit_SIGNAL_A008, "<\n<\n<\n<\n<\n<<<<<<<")
    # FLAG_emit_SIGNAL_A008: bool
    # DATA_emit_SIGNAL_A008: tuple[str]|None
    # FLAG_emit_SIGNAL_A009: bool
    # DATA_emit_SIGNAL_A009: bool
    # #FLAG_emit_SIGNAL_A011: bool
    # #DATA_emit_SIGNAL_A011: T_TagCommand
    #
    # @classmethod
    # def refresh_signal_2_basic_status(cls):
    #     """
    #         Reset  flag po każdym użyciu
    #     :return:
    #     """
    #     cls.FLAG_emit_SIGNAL_A008 = False
    #     cls.DATA_emit_SIGNAL_A008 = None
    #
    #     cls.FLAG_emit_SIGNAL_A009 = False
    #     cls.DATA_emit_SIGNAL_A009 = False
    #
    #     ###cls.FLAG_emit_SIGNAL_A011: bool = False
    #     ##self.DATA_emit_SIGNAL_A011: T_TagCommand = CommunicationTags.NONTAG


    ## === build ===
    @classmethod
    def _LOG(cls, *_):
        if cls.ACTIVATE_LOG:
            Logs.print("@", *_)

    @classmethod
    def _half_path_in_tree(cls, tree, items, path2elem=None):
        """
            Funkcja odszukuje pierwszą ścieżkę elementów. Ścieżka nie musi byc pełna
        """
        if path2elem is None:  path2elem = []

        for itm in items:
            if itm in tree or itm.__class__ in tree:
                if isinstance(tree.get(itm), dict):
                    path2elem.append(itm)
                    p2e = path2elem.copy()
                    path2elem = cls._half_path_in_tree(tree[itm], items, path2elem)
                    if path2elem == None:
                        return p2e
                    break
                elif isinstance(tree.get(itm.__class__), dict):
                    path2elem.append(itm)
                    p2e = path2elem.copy()
                    path2elem = cls._half_path_in_tree(tree.get(itm.__class__), items, path2elem)
                    if path2elem == None:
                        return p2e
                    break
                else:
                    path2elem.append(itm)
                    break
        else:
            return None
        return path2elem

    @staticmethod
    def _get_by_path(tree, path2elem):
        node = tree
        for key in path2elem:
            if key in node:
                node = node.get(key)
            elif key.__class__ in node:
                node = node.get(key.__class__)
        return node

    ## === base ===

    @classmethod
    def _GET_CODE(cls):
        """
            Zwrócenie aktualnego statusu kolejki
        """
        return cls._queue.get_reverse_buffer()

    @classmethod
    def _PUT(cls, *commands):
        """
            _PUT: word;
            ? funkcja wstawia element na poczatek kolejki
        """
        cls._LOG(">>_PUT", commands)
        for cmd in commands:
            cls._queue.put(cmd)

    @classmethod
    def _TRASH(cls, command):
        """
            TRASH:;
            ? usuwa wszystkie elementy z kolejki
        """
        cls._LOG(">>TRASH", command)

        ## oczekiwanie na DO które aktywuje proces
        if command == QueueSystem.COMMAND.DO:
            ## usuwanie wszysykich elementów
            cls._queue.clear()

    @classmethod
    def _CLC(cls):
        """
            _CLC:;
            ? ususwa i elemnt z kolejki domyślnie pierwszy
        """
        cls._LOG(">>_CLC proc", cls._GET_CODE())

        CODE = cls._GET_CODE() #save last state
        cls._TRASH(QueueSystem.COMMAND.DO) # empty question
        cls._PUT(*CODE[:-1])  #remove last

        cls._LOG(">>_CLC end", cls._GET_CODE())

    ## === action ===
    @classmethod
    def NEW(cls, new_question: str|Sequence[str]):
        """
            NEW: new_question;

            operator new przenosi wszystko znajduje się w kolejce po konstruktorze
            tworzy nowe zapytanie

        """
        cls._LOG(">>NEW", new_question)

        ## wyczyszenie obecnej koleji
        cls._TRASH(QueueSystem.COMMAND.DO)

        ## ustawiene nowego zapytania
        if isinstance(new_question, str): # single label
            cls._PUT(new_question)
        elif isinstance(new_question, Sequence): # multile label
            cls._PUT(*new_question)

    @classmethod
    def END(cls,*non):
        """
            END: ;

            Kończy prace odpytania czyści kolejke
        """

        cls._LOG(">>END")

        ## czyszczenie kolejki
        cls._TRASH(QueueSystem.COMMAND.DO)

    @classmethod
    def BREAK(cls, ask: Sequence[str]):
        """
            BREAK: question;

            Otrzymuje stan kolejki i wywołuje zamknięcie przedniego zapytania oraz konstruktor nowego zapytania


        """
        assert isinstance(ask, Sequence), TypeError

        index_BREAK = ask.index(QueueSystem.COMMAND.BREAK)
        ask: List[str] = list(ask)

        ## przepisanie kolejki z instrukcją zakończenia
        ask_before_break: List[str] = ask[:index_BREAK] + [QueueSystem.COMMAND.FINISH]
        ## przygotowanie nowego konstruktora
        ask_after_break: List[str] = ask[index_BREAK + 1:]

        cls._LOG(">>BREAK:", ask_before_break, "{X}", ask_after_break)
        # IN BREAK
        # wywołania zakończenia zapytania
        if QueueSystem.QUESTION.MOV in ask_before_break:
            cls.MOV(ask_before_break)
        elif QueueSystem.QUESTION.INTERACT in ask_before_break:
            cls.INTERACT(ask_before_break)
        elif QueueSystem.QUESTION.CONNECT in ask_before_break:
            cls.CONNECT(ask_before_break)
        elif QueueSystem.QUESTION.RUNSYS in ask_before_break:
            cls.RUNSYS(ask_before_break)
        elif QueueSystem.QUESTION.MOVSYS in ask_before_break:
            cls.MOVSYS(ask_before_break)

        ## aktualizacja stanu kolejki bez instrukcji wywoływanych przez BREAK
        cls.NEW(ask_after_break)
        cls.compile(cls._queue)

    ## === HGR system===
    @classmethod
    def MOV(cls, commands): pass

    @classmethod
    def INTERACT(cls, commands): pass

    @classmethod
    def CONNECT(cls, commands): pass

    @classmethod
    def RUNSYS(cls, commands): pass

    @classmethod
    def MOVSYS(cls, commands): pass

    @classmethod
    def __PATERN(cls, *non):
        """
            _PATERN: non:

            <?> ...

            BREAK: -> active
        """
        cls._LOG(">>_PATERN:", *non)

        ## drzewo odpowiadające za poprane zbudowanie zapytania
        tree = {
            "1": {
                "1.1": {
                    "1.1.1": 1,
                    "1.1.2": 2,
                    "1.1.3": 3,
                },
                "1.2": {
                    "1.2.1": 1,
                    "1.2.2": 2,
                    "1.2.3": 3,
                },
                "1.3": {
                    "1.3.1": 1,
                    "1.3.2": 2,
                    "1.3.3": 3,
                },
            },
            "2": {
                "2.1": {
                    "2.1.1": 1,
                    "2.1.2": 2,
                    "2.1.3": 3,
                },
                "2.2": {
                    "2.2.1": 1,
                    "2.2.2": 2,
                    "2.2.3": 3,
                },
                "2.3": {
                    "2.3.1": 1,
                    "2.3.2": 2,
                    "2.3.3": 3,
                },
            },
            "3": {
                "3.1": {
                    "3.1.1": 1,
                    "3.1.2": 2,
                    "3.1.3": 3,
                },
                "3.2": {
                    "3.2.1": 1,
                    "3.2.2": 2,
                    "3.2.3": 3,
                },
                "3.3": {
                    "3.3.1": 1,
                    "3.3.2": 2,
                    "3.3.3": 3,
                },
            },
        }

        ## jest to inicjator zapytania odpowiadający gestowi, który go wstawia
        new_ask = [..., ...]

        ## === PRZYGOTOWANIE =======================================================================================
        """
            Akcja ma na celu zbudowanie poprawnej kolejki odpytania
        """
        commands: List

        if not (QueueSystem.COMMAND.FINISH in commands):
            new_cmds = cls._half_path_in_tree(tree, non)
            new_ask.extend(new_cmds)
            cls.NEW(new_ask)

            some_dict = {}
            ## przeszukiwanie w celu znalezienia ostatniego wystapienia
            active_object = None
            for cmd in commands:
                if cmd in some_dict:
                    active_object = cmd

            ## ... 1 slowo
            if active_object is not None:

                new_ask.append(active_object)

                ## przeszukiwanie w celu znalezienia ostatniego wystapienia
                active_action = None
                for cmd in commands:
                    if cmd in some_dict:
                        active_action = cmd

                ## ... 2 slowo
                if active_action is not None:
                    new_ask.append(active_action)

                    ## ... 3 slowo
                    if QueueSystem.COMMAND.DO in commands:
                        new_ask.append(QueueSystem.COMMAND.DO)

                ## uruchomienie konstruktora kolejki, skasowanie obecnego stanu i dodanie nowego z przygotowanymi polecaniami
                cls.NEW(new_ask)
        else:
            ## inicjacja FINISH, załoadowanie konstruktora z komend w przypadku finish
            new_ask.extend(commands)