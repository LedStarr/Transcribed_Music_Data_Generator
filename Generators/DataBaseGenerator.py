import os
import shutil
import pandas as pd
import numpy as np

from Util.Helpers import Scale
from Generators.SampleGenerator import SampleGenerator


class DataBaseGenerator:
    """
    Class for Generating the Sample Data Base
    """

    def __init__(self, number_of_notes_per_sample=20, folder_path="", name_of_csv="DB_WAVs_and_MIDIs.csv"):
        """
        Initializing DataBaseGenerator - Object

        Args:
            number_of_notes_per_sample: int - Number of Samples to be generated and saved into DB
            folder_path: str - Folder to save all Files into
            name_of_csv: str - Name of Database File
        """
        self.DEBUG = False
        self.folderPath = folder_path
        self.nameOfCSV = name_of_csv
        self.possibleSynthesizer = []
        self.midiFolderName = "MIDI-Files"
        self.wavFolderName = "WAV-Files"
        self.possibleOctaves = [3, 4, 5, 6]
        self.possibleRoots = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        self.possibleSigns = ["-", "", "#"]
        self.possibleNoteLengths = ['16th', 'eighth', 'quarter', 'half', 'whole']
        self.possiblePauseRatios = np.linspace(0, 0.40, 10, endpoint=True)
        self.possibleTempi = np.linspace(40, 240, 50, endpoint=True, dtype=int)
        self.possibleScales = self._init_scales()
        self.numberOfNotesPerSample = number_of_notes_per_sample

    @staticmethod
    def _init_scales():
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

    def _handle_folders(self, destination_folder):
        # Checks Paths
        if destination_folder == "":
            self.folderPath = os.path.join(os.path.expanduser("~"), "Desktop", "ML_DB")
        else:
            if os.path.exists(destination_folder) and os.path.isdir(destination_folder):
                if len(os.listdir(destination_folder)) == 0:
                    self.folderPath = destination_folder
                else:
                    raise Exception("The given Directory: '{0}' is not empty!".format(destination_folder))

            else:
                raise Exception("The given Directory: '{0}' is not a valid Directory!".format(destination_folder))

        # Empty Folders
        midi_folder_path = os.path.join(self.folderPath, self.midiFolderName)
        if os.path.exists(midi_folder_path):
            shutil.rmtree(midi_folder_path, ignore_errors=True)
            os.makedirs(midi_folder_path)
        else:
            os.makedirs(midi_folder_path)
        wave_folder_path = os.path.join(self.folderPath, self.wavFolderName)
        if os.path.exists(wave_folder_path):
            shutil.rmtree(wave_folder_path, ignore_errors=True)
            os.makedirs(wave_folder_path)
        else:
            os.makedirs(wave_folder_path)

    def generate(self, number_of_samples, destination_folder = ""):
        """
        Checks if self.midiFolderName and self.wavFolderName are already existent in destinationFolder and clears them if Files are already in them.
        If they do not exists then it will create them.

        Then it generates as much MIDI-Files as given by numberOfSamples. From these Files WAV-Files are synthesized and
        the Paths to both MIDI and WAV-Files are stored in a CSV File wich is also saved into destinationFolder.


        Args:
            number_of_samples: int - Number of Samples to generate
            destination_folder: str - Path where to save Files into
        """
        self._handle_folders(destination_folder)

        # Init Lists
        ids = []
        wave_file_paths = []
        midi_file_paths = []

        for i in range(0, number_of_samples):
            print("Generate Sample Nr. " + str(i))
            # Init Sample
            sample_gen = SampleGenerator(self.possibleRoots, self.possibleSigns, self.possibleScales,
                                         self.possibleOctaves, self.possiblePauseRatios, self.possibleTempi,
                                         self.possibleNoteLengths, self.possibleSynthesizer)
            midi_file_name = str.format("MIDI_{0}-Scale({1})_Root({2})_BPM({3}).mid", i, sample_gen.scale,
                                        sample_gen.rootNote.nameWithOctave,
                                        sample_gen.tempo)
            wav_file_name = str.format("Sample_{0}-Scale({1})_Root({2})_BPM({3}).wav", i, sample_gen.scale,
                                       sample_gen.rootNote.nameWithOctave,
                                       sample_gen.tempo)

            midi_file_path = os.path.join(self.folderPath, self.midiFolderName, midi_file_name)
            wav_file_path = os.path.join(self.folderPath, self.wavFolderName, wav_file_name)

            # Generate Sample
            sample_gen.generate(self.numberOfNotesPerSample, midi_file_path, wav_file_path)

            # Add to Lists
            ids.append("ID_" + str(i))
            midi_file_paths.append(midi_file_path)
            wave_file_paths.append(wav_file_path)

        # Create and save CSV-File from Lists
        data = {'Sample-ID': ids, 'WAV-File': wave_file_paths, 'MIDI-File': midi_file_paths}
        df = pd.DataFrame(data=data)
        path_to_csv = os.path.join(self.folderPath, self.nameOfCSV)
        df.to_csv(path_to_csv, sep=';', encoding='utf-8')
