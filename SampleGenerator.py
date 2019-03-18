# -*- coding: utf-8 -*-
"""
@author: Tobias Lint
@email: tobias@lint.at
"""
import os
import shutil
import pandas as pd
import numpy as np
import random

from music21 import stream, tempo, note

from Helpers import Scale, MIDI_to_WAV
import pysynth, pysynth_b, pysynth_c, pysynth_d, pysynth_e, pysynth_s


class DataBaseGenerator:
    """
    Class for Generating the Sample Data Base
    """

    def __init__(self, numberOfNotesPerSample=20, FolderPath = "", nameOfCSV="DB_WAVs_and_MIDIs.csv"):
        """
        Initializing DataBaseGenerator - Object

        Args:
            numberOfNotesPerSample: int - Number of Samples to be generated and saved into DB
            FolderPath: str - Folder to save all Files into
            nameOfCSV: str - Name of Database File
        """
        self.DEBUG = False
        self.FolderPath = FolderPath
        self.nameOfCSV = nameOfCSV
        self.possibleSynthesizer = [pysynth, pysynth_b, pysynth_c, pysynth_d, pysynth_e, pysynth_s]
        self.midiFolderName = "MIDI-Files\\"
        self.wavFolderName = "WAV-Files\\"
        self.possibleOctaves = [3, 4, 5, 6]
        self.possibleRoots = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        self.possibleSigns = ["-", "", "#"]
        self.possibleNoteLengths = ['16th', 'eighth', 'quarter', 'half', 'whole']
        self.possiblePauseRatios = np.linspace(0, 0.40, 10, endpoint=True)
        self.possibleTempi = np.linspace(40, 240, 50, endpoint=True, dtype=int)
        self.possibleScales = self.initScales()
        self.numberOfNotesPerSample = numberOfNotesPerSample

    def initScales(self):
        """
        Returns a list of Scale-Objects which hold all Intervals needed to describe a scale
        """
        dorian = Scale("Dorian", 2, 1, 2, 2, 2, 1, 2)
        phrygian = Scale("Phrygian", 1, 2, 2, 2, 1, 2, 2)
        lydian = Scale("Lydian", 2, 2, 2, 1, 2, 2, 1)
        mixolydian = Scale("Mixolydian", 2, 2, 1, 2, 2, 1, 2)
        aeolian = Scale("Äolian", 2, 1, 2, 2, 1, 2, 2)
        locrian = Scale("Locrian", 1, 2, 2, 1, 2, 2, 2)
        major = Scale("Major", 2, 2, 1, 2, 2, 2, 1)  # auch Ionisch
        minor = Scale("Minor", 2, 1, 2, 2, 1, 2, 2)  # Äolisch und Moll
        chromatic = Scale("Chromatic", 1, 1, 1, 1, 1, 1, 1)
        chipsyminor = Scale("Chipsyminor", 2, 1, 3, 1, 1, 3, 1)
        chipsymajor = Scale("Chipsymajor", 1, 3, 1, 2, 1, 3, 1)
        pentatonicMajor = Scale("Pentatonik major", 2, 2, 3, 2)
        pentatonicMinor = Scale("Pentatonik minor", 1, 2, 4, 1)

        scales = [dorian, phrygian, lydian, mixolydian, aeolian, locrian, major, minor, chromatic, chipsyminor,
                  chipsymajor, pentatonicMajor, pentatonicMinor]

        return scales

    def generate(self, numberOfSamples, destinationFolder=""):
        """
        Checks if self.midiFolderName and self.wavFolderName are already existent in destinationFolder and clears them if Files are already in them.
        If they do not exists then it will create them.
        
        Then it generates as much MIDI-Files as given by numberOfSamples. From these Files WAV-Files are synthesized and 
        the Paths to both MIDI and WAV-Files are stored in a CSV File wich is also saved into destinationFolder.
        
        
        Args:
            numberOfSamples: int - Number of Samples to generate
            destinationFolder: str - Path where to save Files into
        """

        # Checks Paths
        self.FolderPath = destinationFolder
        if os.path.exists(destinationFolder + self.midiFolderName):
            shutil.rmtree(destinationFolder + self.midiFolderName, ignore_errors=True)
            os.makedirs(destinationFolder + self.midiFolderName)
        else:
            os.makedirs(destinationFolder + self.midiFolderName)

        if os.path.exists(destinationFolder + self.wavFolderName):
            shutil.rmtree(destinationFolder + self.wavFolderName, ignore_errors=True)
            os.makedirs(destinationFolder + self.wavFolderName)
        else:
            os.makedirs(destinationFolder + self.wavFolderName)

        # Init Lists
        IDs = []
        waveFilePaths = []
        midiFilePaths = []

        for i in range(0, numberOfSamples):
            print("Generate Sample Nr. " + str(i))
            # Init Sample
            sG = SampleGenerator(self.possibleRoots, self.possibleSigns, self.possibleScales, self.possibleOctaves,
                                 self.possiblePauseRatios, self.possibleTempi, self.possibleNoteLengths,
                                 self.possibleSynthesizer)
            midiFileName = str.format("MIDI_{0}-Scale({1})_Root({2})_BPM({3})_Synth({4}).mid", i, sG.scale,
                                      sG.rootNote.nameWithOctave,
                                      sG.tempo, str(sG.synth.__name__))
            wavFileName = str.format("Sample_{0}-Scale({1})_Root({2})_BPM({3})_Synth({4}).wav", i, sG.scale,
                                     sG.rootNote.nameWithOctave, sG.tempo, str(sG.synth.__name__))
            midiFilePath = destinationFolder + self.midiFolderName + midiFileName
            wavFilePath = destinationFolder + self.wavFolderName + wavFileName

            # Generate Sample
            sG.generate(self.numberOfNotesPerSample, midiFilePath, wavFilePath)

            # Add to Lists
            IDs.append("ID_" + str(i))
            midiFilePaths.append(midiFilePath)
            waveFilePaths.append(wavFilePath)

        # Create CSV-File from Lists
        data = {'Sample-ID': IDs, 'WAV-File': waveFilePaths, 'MIDI-File': midiFilePaths}
        df = pd.DataFrame(data=data)
        df.to_csv(self.nameOfCSV, sep=';', encoding='utf-8')


class SampleGenerator:
    """
    Class for Generating the Samples
    """

    def __init__(self, roots, signs, scales, octaves, pauseRatios,
                 tempi, noteLengths, possibleSynths, DEBUG=False):
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
        self.possibleNotes = self.scale.calcNotes(self.rootNote)
        self.possibleOctaves = octaves
        self.pauseRatio = pauseRatios[random.randrange(len(pauseRatios))]
        self.tempo = tempi[random.randrange(len(tempi))]
        self.possibleNoteLengths = noteLengths
        self.synth = possibleSynths[random.randrange(len(possibleSynths))]
        self.DEBUG = DEBUG

    def __str__(self):
        return str.format("Sample Information: Octave: {0} Root: {1}  Scale {2}", min(self.possibleOctaves),
                          self.rootNote, self.scale)

    def generate(self, numberOfNotesPerSample, midiFilePath, wavFilePath):
        """
        Checks if self.midiFolderName and self.wavFolderName are already existent in destinationFolder and clears them if Files are already in them.
        If they do not exists then it will create them.
        
        Then it generates as much MIDI-Files as given by numberOfSamples. From these Files WAV-Files are synthesized and 
        the Paths to both MIDI and WAV-Files are stored in a CSV File which is also saved into destinationFolder.
        
        
        Args:
            numberOfNotesPerSample: int - Number of Notes generated for every Sample
            midiFilePath: str - Path where to save MIDI-Files into
            wavFilePath:  str - Path where to save WAV-Files into
        """
        # Initializing Stream
        s = stream.Measure()
        s.append(tempo.MetronomeMark(number=self.tempo))

        for i in range(0, numberOfNotesPerSample):
            # Initializing Note
            notePicker = self.possibleNotes[random.randrange(len(self.possibleNotes))]
            octavePicker = self.possibleOctaves[random.randrange(len(self.possibleOctaves))]
            noteLengthPicker = self.possibleNoteLengths[random.randrange(len(self.possibleNoteLengths))]
            note_string = notePicker.name + str(octavePicker)
            if random.uniform(0, 1) > self.pauseRatio:
                element = note.Note(note_string, type=noteLengthPicker)
            else:
                element = note.Rest(note_string, type=noteLengthPicker)
            # Adding Note to Stream
            s.append(element)

        ##Write a MIDI-File from Stream
        if self.DEBUG:
            print("MIDI: " + midiFilePath)
            print("WAV: " + wavFilePath)
        s.write('midi', fp=midiFilePath)
        # Synthesize WAV-File from MIDI-File
        MIDI_to_WAV(self.synth, midiFilePath, wavFilePath, )


if __name__ == "__main__":
    numberOfSamples = int(input('How many Samples do you want? \n'))

    print("############## Starting to Generate Sample Database ##############")
    generator = DataBaseGenerator()
    generator.generate(numberOfSamples)
    print("############################ Finished ############################")
