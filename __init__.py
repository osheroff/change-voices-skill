from mycroft import MycroftSkill, intent_file_handler


class ChangeVoices(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('voices.change.intent')
    def handle_voices_change(self, message):
        self.speak_dialog('voices.change')


def create_skill():
    return ChangeVoices()

