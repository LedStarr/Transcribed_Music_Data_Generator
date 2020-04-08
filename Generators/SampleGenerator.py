# -*- coding: utf-8 -*-
"""
@author: Tobias Lint
@email: tobias@lint.at
"""
import random
from music21 import stream, tempo, note
from Util.Helpers import midi_to_wav


class SampleGenerator:
    """
    Class for Generating the Samples
    """

    def __init__(self, roots, signs, scales, octaves, pauseRatios,
                 tempi, noteLengths, possibleSynths, DEBUG=True):
        """
        Initializing SampleGenerator - Object

        Args:
            roots: List of Str - used for generating Note-Objects 
            signs: List of Str - used for generating Note-Objects 
            scales: List of Scale-Objects - used for generating Note-Objects
            octaves: List of int - used for generating Note-Objects
            pauseRatios: List of float - used for generating Note-Objects
            tempi: List of int - used for generating Note-Objects
            noteLengths: List of Str - used for generating Note-Objects
            possibleSynths: List of Modules - used for Synthesizing MIDI_To_WAV
            DEBUG: bool - Switch for Printing Debug-Statements into the console
        """
        self.scale = scales[random.randrange(len(scales))]
        root = roots[random.randrange(len(roots))]
        sign = signs[random.randrange(len(signs))]
        self.rootNote = note.Note(root + sign)
        self.possibleNotes = self.scale.calc_notes(self.rootNote)
        self.possibleOctaves = octaves
        self.pauseRatio = pauseRatios[random.randrange(len(pauseRatios))]
        self.tempo = tempi[random.randrange(len(tempi))]
        self.possibleNoteLengths = noteLengths

        self.DEBUG = DEBUG

    def __str__(self):
        return str.format("Sample Information: Octave: {0} Root: {1}  Scale {2}", min(self.possibleOctaves),
                          self.rootNote, self.scale)

    def generate(self, number_of_notes_per_sample, midi_file_path, wav_file_path):
        """
        Checks if self.midiFolderName and self.wavFolderName are already existent in destinationFolder and clears them if Files are already in them.
        If they do not exists then it will create them.
        
        Then it generates as much MIDI-Files as given by numberOfSamples. From these Files WAV-Files are synthesized and 
        the Paths to both MIDI and WAV-Files are stored in a CSV File which is also saved into destinationFolder.
        
        
        Args:
            number_of_notes_per_sample: int - Number of Notes generated for every Sample
            midi_file_path: str - Path where to save MIDI-Files into
            wav_file_path:  str - Path where to save WAV-Files into
        """
        # Initializing Stream
        s = stream.Measure()
        s.append(tempo.MetronomeMark(number=self.tempo))

        for i in range(0, number_of_notes_per_sample):
            # Initializing Note
            note_picker = self.possibleNotes[random.randrange(len(self.possibleNotes))]
            octave_picker = self.possibleOctaves[random.randrange(len(self.possibleOctaves))]
            note_length_picker = self.possibleNoteLengths[random.randrange(len(self.possibleNoteLengths))]
            note_string = note_picker.name + str(octave_picker)
            if random.uniform(0, 1) > self.pauseRatio:
                element = note.Note(note_string, type=note_length_picker)
            else:
                element = note.Rest(note_string, type=note_length_picker)
            # Adding Note to Stream
            s.append(element)

        # Write a MIDI-File from Stream
        if self.DEBUG:
            print("MIDI: " + midi_file_path)
            print("WAV: " + wav_file_path)
        s.write('midi', fp=midi_file_path)

        # Synthesize WAV-File from MIDI-File
        midi_to_wav(wav_file_path, midi_file_path)


