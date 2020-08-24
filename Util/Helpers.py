"""
Copyright (c) 2020 Tobias Lint <tobias@lint.at>. All rights reserved.
Licensed under the MIT License.
"""
from pyo import *
from mido import MidiFile
from Util.NoteExtractor import NoteExtractor
import os


class Scale:
    """
    Class for storing Information about a Musical-Scale
    TODO: use Scale-Objects from music21 Library
    """

    def __init__(self, name, first_interval, second_interval, third_interval, fourth_interval, fifth_interval=None,
                 sixth_interval=None, seventh_interval=None, debug=False):
        """
        Initializing Scale - Object
        
        If only 4 intervals are defined make it a Scale with 5 Notes

        Args:
            first_interval: int - Describes how many musical half steps are between the root Note and the 2nd Note of Scale
            second_interval: int - Describes how many musical half steps are between the 2nd Note and the 3rd Note of Scale
            third_interval: int - Describes how many musical half steps are between the 3rd Note and the 4th Note of Scale
            fourth_interval: int - Describes how many musical half steps are between the 4th Note and the 5th Note of Scale
            fifth_interval: int - Describes how many musical half steps are between the 5th Note and the 6th Note of Scale
            sixth_interval: int - Describes how many musical half steps are between the 6th Note and the 7th Note of Scale
            seventh_interval: int - Describes how many musical half steps are between the 7th Note and the 8th Note of Scale
            debug: bool - Switch for Printing Debug-Statements into the console
        """
        self.name = name
        if fifth_interval is not None:

            self.intervals = [first_interval, second_interval, third_interval, fourth_interval, fifth_interval,
                              sixth_interval, seventh_interval]
        else:
            self.intervals = [first_interval, second_interval, third_interval, fourth_interval]

        if debug:
            print(self.name + " - Scale created")

    def __str__(self):
        return self.name

    def calc_notes(self, root_note):
        """
        Calculates all notes in Scale 
        
        Args:
            root_note: Note Object - Base for calculating all notes in Scale
        Return:
            notes: List of Note Objects
        """
        tmp = root_note
        notes = [tmp]
        for interval in self.intervals:
            tmp = tmp.transpose(interval)
            notes.append(tmp)

        return notes


class Synthesizer:
    """
    Class for generating WAV-File from a MIDI FIle.
    TODO: Implement Synthesizer as an Interface for multiple Synthesizers with different stiles
    """
    def __init__(self):
        # Initialize the Server in offline mode.
        self.server = Server(duplex=0, audio="offline")
        # only show Errors
        self.server.setVerbosity(1)

    def midi_to_wav(self, filename, midi_file_path):
        """
        Synthesizes a WAV-File from a MIDI-File

        Args:
            filename: str - Filename of generated WAV-File
            midi_file_path: str - Path to MIDI File for generating WAV-File
        """
        if not os.path.isfile(midi_file_path) or not midi_file_path.endswith('.mid'):
            raise Exception(
                "The path given '{0}' to the Function midi_to_wav is not a MIDI-File.".format(midi_file_path))

        # Opening the MIDI file...
        midi_file_path = MidiFile(midi_file_path)

        # Extract all NoteInformation
        extractor = NoteExtractor()
        all_notes = extractor.get_notes(midi_file_path)

        # Boot the Server.
        self.server.boot()
        # Set recording parameters.
        self.server.recordOptions(dur=midi_file_path.length + .1,
                                  filename=filename,
                                  fileformat=0,
                                  sampletype=0)

        pyo_objects = []
        for midiNote in all_notes:
            note_freq = midiToHz(midiNote.pitch)
            dur = midiNote.duration
            delay = midiNote.startTime

            # synthesize object for every tone
            lfo = Sine(.1).range(0, .18)
            obj_l = SineLoop(freq=note_freq, feedback=lfo, mul=0.3).out(chnl=0, dur=dur, delay=delay)
            obj_r = SineLoop(freq=note_freq, feedback=lfo, mul=0.3).out(chnl=1, dur=dur, delay=delay)

            # add to List so it stays in memory
            pyo_objects.append(obj_l)
            pyo_objects.append(obj_r)

        # Start with rendering.
        self.server.start()
        # Cleanup for the next pass.
        self.server.shutdown()
