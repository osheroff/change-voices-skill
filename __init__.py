import random
import time
from mycroft import MycroftSkill, intent_file_handler
from mycroft.audio import wait_while_speaking
from mycroft.configuration import Configuration
from mycroft.messagebus.message import Message

class ChangeVoices(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.config = Configuration.get()
        self.accents = [ 'aew', 'ahw', 'aup', 'awb', 'axb', 'eey', 'fem', 'jmk', 'ksp', 'ljm', 'rms', 'rxr', 'slp', 'slt' ]
        self.accent_index = random.choice(range(len(self.accents)))

    @intent_file_handler('voices.change.intent')
    def handle_voices_change(self, message):
        self.accent_index += 1
        if self.accent_index > len(self.accents) - 1:
            self.accent_index = 0  

        new_voice = self.accents[self.accent_index]
        self.log.info(f"setting voice to {new_voice}")
        new_conf = {'config': {'tts': {'mimic3_tts_plug': { 'speaker': new_voice } }}}

        def _rest(something):
            self.log.info("enter message callback")
            time.sleep(2.0)
            self.log.info("done sleeping")
            self.speak_dialog('voices.change', wait=True)
            resp = self.ask_yesno('voices.confirm')
            if resp == 'no':
                return self.handle_voices_change(message) 
            elif resp == 'stop':
                return 
            elif resp == 'yes':
                self.speak("ok")

        self.bus.once('voice.change.finish', _rest)
        self.bus.emit(Message('configuration.patch', new_conf))
        self.bus.emit(Message('voice.change.finish'))
        self.log.info(f"emitted events")


def create_skill():
    return ChangeVoices()

