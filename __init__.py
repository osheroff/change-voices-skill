import random
import time
import subprocess

from dataclasses import dataclass

from mycroft import MycroftSkill, intent_file_handler
from mycroft.configuration import Configuration


def get_config(config, path, default=None):
    value = config
    for p in path:
        if not p in value or not isinstance(value, dict):
            return default
        value = value.get(p)
    return value


@dataclass
class Mimic3Voice:
    voice: str
    speaker: str

    def __repr__(self):
        return self.name

    @property
    def name(self):
        return f"{self.voice}#{self.speaker}"

    @classmethod
    def from_config(clazz):
        config = Configuration.get()
        voice = get_config(
            config, ["tts", "mimic3_tts_plug", "voice"], "en_US/cmu-arctic_low"
        )
        speaker = get_config(config, ["tts", "mimic3_tts_plug", "speaker"], "fem")
        return clazz(voice, speaker)


VOICES = []
for speaker in [
    "aup",
    "awb",
    "axb",
    "eey",
    "fem",
    "jmk",
    "ksp",
    "ljm",
    "rxr",
    "slp",
    "slt",
]:
    VOICES.append(Mimic3Voice("en_US/cmu-arctic_low", speaker))

VOICES.append(Mimic3Voice("en_UK/apope_low", "pope"))


class ChangeVoices(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.config = Configuration.get()
        self.voice = Mimic3Voice.from_config()
        self.voice_index = 0

        for (index, v) in enumerate(VOICES):
            if v == self.voice:
                self.voice_index = index
        self.log.info(f"my voice: {self.voice}")
        self.log.info(f"set voice_index to {self.voice_index}")

    def reset_voice(self):
        voiced = self.get_voiced("cancelled", self.voice)
        self.speak(voiced)

    def check_compat(self):
        tts_module = get_config(self.config, ["tts", "module"], "mimic")
        if tts_module != "mimic3_tts_plug":
            self.speak_dialog("incompatible")
            return False
        return True

    def get_voiced(self, key, voice):
        dialog = self.dialog_renderer.render(key, None)
        voiced_dialog = f"""
            <speak><voice name="{voice.name}">{dialog}</voice></speak>
        """
        return voiced_dialog

    @intent_file_handler("voices.change.intent")
    def handle_voices_change(self, message):
        if not self.check_compat():
            return

        first_confirm = False
        while True:
            self.voice_index += 1
            if self.voice_index > len(VOICES) - 1:
                self.voice_index = 0

            new_voice = VOICES[self.voice_index]
            self.log.info(f"setting voice to {new_voice.name}")

            if not first_confirm:
                dialog = "voices.confirm.first"
                first_confirm = True
            else:
                dialog = "voices.confirm.next"

            voiced = self.get_voiced(dialog, new_voice)
            resp = self.ask_yesno(voiced)
            if resp == "no":
                continue
            elif resp == "yes" or resp == "okay":
                self.speak("okay")
                self.voice = VOICES[self.voice_index]
                self.configure_voice()
                return
            else:
                self.reset_voice()
                return

    def configure_voice(self):
        subprocess.call(
            ["mycroft-config", "set", "tts.mimic3_tts_plug.speaker", self.voice.speaker]
        )
        subprocess.call(
            ["mycroft-config", "set", "tts.mimic3_tts_plug.voice", self.voice.voice]
        )


def create_skill():
    return ChangeVoices()
