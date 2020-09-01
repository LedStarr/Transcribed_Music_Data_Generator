"""
Copyright (c) 2020 Tobias Lint <tobias@lint.at>. All rights reserved.
Licensed under the MIT License.
"""
import random
from music21 import stream, tempo, note, chord
from Util.Helpers import WavGenerator


class SampleGenerator:
    """
    Class for Generating the Samples
    """

    def __init__(self, roots, signs, scales, octaves, pause_ratios,
                 chord_ratios, tempos, note_lengths, synth_modules, debug=False):
        """
        Initializing SampleGenerator - Object

        Args:
            roots: List of Str - used for generating Note-Objects 
            signs: List of Str - used for generating Note-Objects 
            scales: List of Scale Objects - used for generating Note-Objects
            octaves: List of int - used for generating Note-Objects
            pause_ratios: List of float - used for generating Note-Objects
            chord_ratios: List of float - used for generating Note-Objects
            tempos: List of int - used for generating Note-Objects
            note_lengths: List of Str - used for generating Note-Objects
            synth_modules: List of SynthModule Objects - user for creating a WAV File from the generated MIDI FIle
            debug: bool - Switch for Printing Debug-Statements into the console
        """
        self.scale = scales[random.randrange(len(scales))]
        root = roots[random.randrange(len(roots))]
        sign = signs[random.randrange(len(signs))]
        self.rootNote = note.Note(root + sign)
        self.possibleNotes = self.scale.calc_notes(self.rootNote)
        self.possibleOctaves = octaves
        self.pauseRatio = pause_ratios[random.randrange(len(pause_ratios))]
        self.chordRatio = chord_ratios[random.randrange(len(chord_ratios))]
        self.tempo = tempos[random.randrange(len(tempos))]
        self.possibleNoteLengths = note_lengths
        self.wav_generator = WavGenerator(synth_modules[random.randrange((len(synth_modules)))])
        self.debug = debug

    def __str__(self):
        return str.format("Sample Information: Octave: {0} Root: {1}  Scale {2}", min(self.possibleOctaves),
                          self.rootNote, self.scale)

    def __get_note_params(self):
        """
        Returns randomly picked Note Parameters from which Music21 Note,Rest or Chord Objects can be made.
        """
        note_picker = self.possibleNotes[random.randrange(len(self.possibleNotes))]
        octave_picker = self.possibleOctaves[random.randrange(len(self.possibleOctaves))]
        note_length_picker = self.possibleNoteLengths[random.randrange(len(self.possibleNoteLengths))]
        return note_picker.name + str(octave_picker), note_length_picker

    def generate(self, number_of_notes_per_sample, midi_file_path, wav_file_path, use_polyphonic):
        """
        Generates as much MIDI-Files as given by numberOfSamples. From these Files WAV-Files are synthesized and
        the Paths to both MIDI and WAV-Files are stored in a CSV File which is also saved into destinationFolder.
        
        
        Args:
            number_of_notes_per_sample: int - Number of Notes generated for every Sample
            midi_file_path: str - Path where to save MIDI-Files into
            wav_file_path: str - Path where to save WAV-Files into
            use_polyphonic: bool - Switch for Polyphonic Samples or Monophonic
        """
        # Initializing Stream
        s = stream.Measure()
        s.append(tempo.MetronomeMark(number=self.tempo))

        for i in range(0, number_of_notes_per_sample):
            if random.uniform(0, 1) > self.pauseRatio:
                if use_polyphonic and random.uniform(0, 1) > self.chordRatio:
                    # Add Chord
                    notes = []
                    # Creates a chord with either 2, 3 or 4 Notes
                    while len(notes) < random.randrange(2, 4, 1):
                        note_string, note_length = self.__get_note_params()
                        new_note = note.Note(note_string, type=note_length)
                        if new_note not in notes:
                            notes.append(new_note)
                    s.append(chord.Chord(notes))
                else:
                    # Add single Note
                    note_string, note_length = self.__get_note_params()
                    s.append(note.Note(note_string, type=note_length))
            else:
                # Add Pause
                note_string, note_length = self.__get_note_params()
                s.append(note.Rest(note_string, type=note_length))

        # Write a MIDI-File from Stream
        if self.debug:
            print("MIDI: " + midi_file_path)
            print("WAV: " + wav_file_path)
        s.write('midi', fp=midi_file_path)

        # Synthesize WAV-File from MIDI-File
        self.wav_generator.midi_to_wav(wav_file_path, midi_file_path)

