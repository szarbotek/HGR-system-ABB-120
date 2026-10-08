class SignalUnit:
    FLAG_emit_SIGNAL_A008: bool = None
    DATA_emit_SIGNAL_A008: tuple[str] | None
    FLAG_emit_SIGNAL_A009: bool
    DATA_emit_SIGNAL_A009: bool

    # FLAG_emit_SIGNAL_A011: bool
    # DATA_emit_SIGNAL_A011: T_TagCommand

    @classmethod
    def refresh_signal(cls):
        # restowanie sygnałó↓w ustawonych na drodze strerowania systemem HGR
        """
            Reset  flag po każdym użyciu
        :return:
        """
        cls.FLAG_emit_SIGNAL_A008 = False
        cls.DATA_emit_SIGNAL_A008 = None
        cls.FLAG_emit_SIGNAL_A009 = False
        cls.DATA_emit_SIGNAL_A009 = False
        ###cls.FLAG_emit_SIGNAL_A011: bool = False
        ##self.DATA_emit_SIGNAL_A011: T_TagCommand = CommunicationTags.NONTAG