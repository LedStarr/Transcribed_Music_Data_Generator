"""
Copyright (c) 2020 Tobias Lint <tobias@lint.at>. All rights reserved.
Licensed under the MIT License.
"""
import mido

DEBUG = False


class Note:
    """
    Helper Class for Extracting Notes from MidiFile
    """
    def __init__(self, pitch, velocity, channel):
        """
        Initializing Note - Object

        Args:
            pitch: str - Pitch from mido Midi Message
            velocity: str - Velocity from mido Midi Message
            channel: str - Channel from mido Midi Message
        """
        self.pitch = pitch
        self.velocity = velocity
        self.channel = channel
        self.startTime = -1
        self.duration = -1

    def set_start_time(self, current_time):
        """
        Sets the start time of current Note

        Args:
            current_time: float - Value for indicating current_time for calculating the Duration of current Note
        """
        if DEBUG:
            print("Note Started at: " + str(current_time))
        self.startTime = current_time

    def calc_duration(self, current_time):
        """
        Calculates the Duration of current Note

        Args:
            current_time: float - Value for indicating current_time for calculating the Duration of current Note
        """
        if DEBUG:
            print("Start: {0} - Current {1}".format(self.startTime, current_time))
        self.duration = (current_time - self.startTime)

    def __eq__(self, other):
        return self.pitch == other.pitch and self.channel == other.channel

    def __str__(self):
        return "Note - Pitch: {0}, Velocity: {1}, Duration: {2}, Channel: {3}, StartTime: {4}".format(self.pitch,
                                                                                                      self.velocity,
                                                                                                      self.duration,
                                                                                                      self.channel,
                                                                                                      self.startTime)


class NoteExtractor:
    """
    Helper Class for extracting all Midi Note specific Information for generating MIDI and WAV Files in a Midi File
    """
    def __init__(self):
        self.notPaired = []
        self.paired = []
        self.currentTime = 0.0

    def __add_note_for_paring(self, msg):
        # TODO:
        pitch = msg.note
        velocity = msg.velocity
        channel = msg.channel
        note = Note(pitch, velocity, channel)
        note.set_start_time(self.currentTime)

        self.notPaired.append(note)

    def __pair_note(self, msg):
        # TODO:
        pitch = msg.note
        velocity = msg.velocity
        channel = msg.channel
        note = Note(pitch, velocity, channel)
        if note in self.notPaired:
            pair_note = self.notPaired[self.notPaired.index(note)]
            pair_note.calc_duration(self.currentTime)
            self.paired.append(pair_note)
            self.notPaired.remove(pair_note)
        else:
            raise Exception("The note has not been found in not Paired List. " + str(note))

    def __reset(self):
        """
        Resets all Values used for calculation by the Note Extractor
        """
        self.currentTime = 0.0
        self.notPaired = []
        self.paired = []

    def get_notes(self, midi_file):
        """
        TODO: beschreibungen
        Returns all Midi Information as Note - Object

        Args:
            midi_file - mido.MidiFile
        """
        if type(midi_file) is not mido.MidiFile:
            raise Exception(
                "The Midi File given to this function get_notes is not of Type MidiFile from mido-Library! "
                "Data: '{0}'".format(midi_file))

        self.__reset()

        for msg in midi_file:
            delta_time = msg.time
            self.currentTime += delta_time
            if not msg.is_meta:
                if msg.type == "note_on":
                    self.__add_note_for_paring(msg)
                if msg.type == "note_off":
                    self.__pair_note(msg)
            else:
                if DEBUG: print('Meta: {0}'.format(msg))
        if DEBUG:
            print("Total Time Elapsed: " + str(self.currentTime))
            print("Time from file: " + str(midi_file.length))

        sorted(self.paired, key=lambda note: note.startTime)
        return self.paired

