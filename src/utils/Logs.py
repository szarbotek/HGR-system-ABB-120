class Logs:

    stream_text = ""

    @classmethod
    def print(cls, *args):
        print(args)
        cls.stream_text += str(args) + "\n"