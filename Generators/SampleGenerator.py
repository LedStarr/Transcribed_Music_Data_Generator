#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Tobias Lint
@email: tobias@lint.at
"""
import random
from music21 import stream, tempo, note, chord


class SampleGenerator:
    """
    Class for Generating the Samples
    """

    def __init__(self, roots, signs, scales, octaves, pauseRatios,
                 chordRatios, tempos, noteLengths, debug=False):
        """
        Initializing SampleGenerator - Object

        Args:
            roots: List of Str - used for generating Note-Objects 
            signs: List of Str - used for generating Note-Objects 
            scales: List of Scale-Objects - used for generating Note-Objects
            octaves: List of int - used for generating Note-Objects
            pauseRatios: List of float - used for generating Note-Objects
            chordRatios: List of float - used for generating Note-Objects
            tempos: List of int - used for generating Note-Objects
            noteLengths: List of Str - used for generating Note-Objects
            DEBUG: bool - Switch for Printing Debug-Statements into the console
        """
        self.scale = scales[random.randrange(len(scales))]
        root = roots[random.randrange(len(roots))]
        sign = signs[random.randrange(len(signs))]
        self.rootNote = note.Note(root + sign)
        self.possibleNotes = self.scale.calc_notes(self.rootNote)
        self.possibleOctaves = octaves
        self.pauseRatio = pauseRatios[random.randrange(len(pauseRatios))]
        self.chordRatio = chordRatios[random.randrange(len(chordRatios))]
        self.tempo = tempos[random.randrange(len(tempos))]
        self.possibleNoteLengths = noteLengths
        self.debug = debug

    def __str__(self):
        return str.format("Sample Information: Octave: {0} Root: {1}  Scale {2}", min(self.possibleOctaves),
                          self.rootNote, self.scale)

    def __get_note_params(self):
        """
        Returns randomly picked Note Parameters from which Music21 Note,Rest or Chrod Objects can be made.
        """
        note_picker = self.possibleNotes[random.randrange(len(self.possibleNotes))]
        octave_picker = self.possibleOctaves[random.randrange(len(self.possibleOctaves))]
        note_length_picker = self.possibleNoteLengths[random.randrange(len(self.possibleNoteLengths))]
        return note_picker.name + str(octave_picker), note_length_picker

    def generate(self, number_of_notes_per_sample, midi_file_path, wav_file_path):
        """
        Generates as much MIDI-Files as given by numberOfSamples. From these Files WAV-Files are synthesized and
        the Paths to both MIDI and WAV-Files are stored in a CSV File which is also saved into destinationFolder.
        
        
        Args:
            number_of_notes_per_sample: int - Number of Notes generated for every Sample
            midi_file_path: str - Path where to save MIDI-Files into
            wav_file_path: str - Path where to save WAV-Files into
        """
        # Initializing Stream
        s = stream.Measure()
        s.append(tempo.MetronomeMark(number=self.tempo))

        for i in range(0, number_of_notes_per_sample):
            if random.uniform(0, 1) > self.pauseRatio:
                if random.uniform(0, 1) > self.chordRatio:
                    # Add Chord
                    notes = []
                    # Creates a chord with either 2, 3 or 4 Notes
                    while len(notes) < random.randrange(2, 4, 1):
                        note_string, note_length = self.__get_note_params();
                        new_note = note.Note(note_string, type=note_length)
                        if new_note not in notes:
                            notes.append(new_note)
                    s.append(chord.Chord(notes))
                else:
                    # Add single Note
                    note_string, note_length = self.__get_note_params();
                    s.append(note.Note(note_string, type=note_length))
            else:
                # Add Pause
                note_string, note_length = self.__get_note_params();
                s.append(note.Rest(note_string, type=note_length))

        # Write a MIDI-File from Stream
        if self.debug:
            print("MIDI: " + midi_file_path)
            print("WAV: " + wav_file_path)
        s.write('midi', fp=midi_file_path)
