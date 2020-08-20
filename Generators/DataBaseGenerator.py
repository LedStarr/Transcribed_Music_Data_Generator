"""
@author: Tobias Lint
@email: tobias@lint.at
"""
import os
import shutil
import pandas as pd
import numpy as np

from tqdm import tqdm
from Generators.SampleGenerator import SampleGenerator
from Util.Helpers import Synthesizer, Scale


class DataBaseGenerator:
    """
    Class for Generating the Sample Data Base
    """

    def __init__(self, number_of_notes_per_sample=20, folder_path=""):
        """
        Initializing DataBaseGenerator - Object

        Args:
            number_of_notes_per_sample: int - Number of Notes generated for every Sample
            folder_path: str - Folder to save all Files into
        """
        self.DEBUG = False
        self.folderPath = folder_path
        self.possibleChordRatios = []
        self.midiFolderName = "MIDI-Files"
        self.wavFolderName = "WAV-Files"
        self.possibleOctaves = [3, 4, 5, 6]
        self.possibleRoots = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        self.possibleSigns = ["-", "", "#"]
        self.possibleNoteLengths = ['16th', 'eighth', 'quarter', 'half', 'whole']
        self.possiblePauseRatios = np.linspace(0, 0.40, 10, endpoint=True)
        self.possibleChordRatios = np.linspace(0, 0.40, 10, endpoint=True)
        self.possibleTempos = np.linspace(40, 240, 50, endpoint=True, dtype=int)
        self.possibleScales = self.__init_scales()
        self.numberOfNotesPerSample = number_of_notes_per_sample
        self.synth = Synthesizer()

    @staticmethod
    def __init_scales():
        """
        Returns a list of Scale-Objects which hold all Intervals needed to describe a scale
        """
        dorian = Scale("Dorian", 2, 1, 2, 2, 2, 1, 2)
        phrygian = Scale("Phrygian", 1, 2, 2, 2, 1, 2, 2)
        lydian = Scale("Lydian", 2, 2, 2, 1, 2, 2, 1)
        mixolydian = Scale("Mixolydian", 2, 2, 1, 2, 2, 1, 2)
        aeolian = Scale("Aeolian", 2, 1, 2, 2, 1, 2, 2)
        locrian = Scale("Locrian", 1, 2, 2, 1, 2, 2, 2)
        major = Scale("Major", 2, 2, 1, 2, 2, 2, 1)
        minor = Scale("Minor", 2, 1, 2, 2, 1, 2, 2)
        chromatic = Scale("Chromatic", 1, 1, 1, 1, 1, 1, 1)
        gypsy_minor = Scale("GypsyMinor", 2, 1, 3, 1, 1, 3, 1)
        gypsy_major = Scale("GypsyMajor", 1, 3, 1, 2, 1, 3, 1)
        pentatonic_major = Scale("PentatonicMajor", 2, 2, 3, 2)
        pentatonic_minor = Scale("PentatonicMinor", 1, 2, 4, 1)

        scales = [dorian, phrygian, lydian, mixolydian, aeolian, locrian, major, minor, chromatic, gypsy_minor,
                  gypsy_major, pentatonic_major, pentatonic_minor]

        return scales

    @staticmethod
    def __create_save_file_name(prefix, postfix, current_id, sample_generator):
        """
        Creates a save filename for the MIDI and WAV Files from the Parameters used for generating them.

        Args:
            prefix = str - Holds the string that is placed in front of the generated string.
            postfix = str - Holds the string that is placed after the generated string.
            id = int - Holds the current ID of the generated MIDI and WAV Files.
            sample_generator - SampleGenerator - Holds all Parameters
        """
        # Create save FileName
        scale = str(sample_generator.scale)
        scale = scale.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
        root_note = str(sample_generator.rootNote.nameWithOctave)
        root_note = root_note.lower().replace("#", "_sharp").replace("-", "_flat")
        tempo = str(sample_generator.tempo)

        file_name = str.format("{0}_{1}_Scale({2})_Root({3})_BPM({4}).{5}",
                               prefix,
                               current_id,
                               scale,
                               root_note,
                               tempo,
                               postfix)

        file_name = file_name.replace(" ", "")
        return file_name

    def __handle_folders(self, destination_directory):
        """
        Checks the destination Directory for errors and possible files inside.
        Empties MIDI and WAV Folders or creates new ones if not exi
        """

        # Checks Paths
        if os.path.exists(destination_directory) and os.path.isdir(destination_directory):
            if len(os.listdir(destination_directory)) == 0:
                self.folderPath = destination_directory
            else:
                raise Exception("The given Directory: '{0}' is not empty!".format(destination_directory))

        else:
            raise Exception("The given Directory: '{0}' is not a valid Directory!".format(destination_directory))

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

    def batch_generate_with_split(self, destination_folder, number_of_samples_train,
                                  number_of_samples_test, polyphonic):
        # TODO:
        # Train
        print("############## Generating Train Files...###########################\n")
        train_folder = os.path.join(destination_folder, "Train")
        if not os.path.exists(train_folder):
            os.makedirs(train_folder)
        self.batch_generate(destination_folder=train_folder,
                            number_of_samples=number_of_samples_train,
                            name_of_csv="train.csv",
                            polyphonic=polyphonic)
        print("############## Finished generating Train Files####################\n")
        # Test
        print("############## Generating Test Files...###########################\n")
        test_folder = os.path.join(destination_folder, "Test")
        if not os.path.exists(test_folder):
            os.makedirs(test_folder)
        self.batch_generate(destination_folder=test_folder,
                            number_of_samples=number_of_samples_test,
                            name_of_csv="test.csv",
                            polyphonic=polyphonic)
        print("############## Finished generating Test Files#####################\n")

    def batch_generate(self, destination_folder, number_of_samples, name_of_csv="DB_WAVs_and_MIDIs.csv", polyphonic=True):
        """
        Checks if self.midiFolderName and self.wavFolderName are already existent in destinationFolder and clears them if Files are already in them.
        If they do not exists then it will create them.

        Then it generates as much MIDI-Files as given by numberOfSamples. From these Files WAV-Files are synthesized and
        the Paths to both MIDI and WAV-Files are stored in a CSV File wich is also saved into destinationFolder.


        Args:
            number_of_samples: int - Number of Samples to generate
            destination_folder: str - Path where to save Files into
            name_of_csv: str - Name of CSV
            polyphonic: bool - Switch for creating polyphonic Samples or Monophonic
        """
        self.__handle_folders(destination_folder)
        print("Generating Data into: '{0}'\n".format(self.folderPath))
        # Init Lists
        ids = []
        midi_file_paths = []
        wave_file_paths = []
        tempos = []
        scales = []
        root_notes = []

        inputs = tqdm(range(0, number_of_samples))

        for i in inputs:
            result = self.__generate(i, polyphonic)
            ids.append(result[0])
            midi_file_paths.append(result[1])
            wave_file_paths.append(result[2])
            tempos.append(result[3])
            scales.append(result[4])
            root_notes.append(result[5])

        # Create and save CSV-File from Lists
        data = {'WAV-File': wave_file_paths,
                'MIDI-File': midi_file_paths,
                "BPM": tempos,
                "Scale": scales,
                "RootNote": root_notes}

        df = pd.DataFrame(data=data)
        path_to_csv = os.path.join(self.folderPath, name_of_csv)
        df.to_csv(path_to_csv, sep=',', index=False, encoding='utf-8')

        print("\nGenerated {0} MIDI- and Wave-File(s) and a CSV-File storing "
              "both references in the Directory: '{1}'.".format(number_of_samples, self.folderPath))



    def __generate(self, i, polyphonic):
        #TODO:
        # print("Generate Sample Nr. " + str(i))
        # Init Sample
        sample_gen = SampleGenerator(self.possibleRoots, self.possibleSigns, self.possibleScales,
                                     self.possibleOctaves, self.possiblePauseRatios, self.possibleChordRatios,
                                     self.possibleTempos, self.possibleNoteLengths)

        # Create save FileName
        midi_file_name = self.__create_save_file_name("MIDI", "mid", i, sample_gen)
        wav_file_name = self.__create_save_file_name("WAV", "wav", i, sample_gen)

        midi_file_path = os.path.join(self.folderPath, self.midiFolderName, midi_file_name)
        wav_file_path = os.path.join(self.folderPath, self.wavFolderName, wav_file_name)
        rel_midi_file_path = os.path.join(self.midiFolderName, midi_file_name)
        rel_wav_file_path = os.path.join(self.wavFolderName, wav_file_name)

        # Generate Sample
        sample_gen.generate(self.numberOfNotesPerSample, midi_file_path, wav_file_path, polyphonic)
        # Synthesize WAV-File from MIDI-File
        self.synth.midi_to_wav(wav_file_path, midi_file_path)

        # Returns ID, relative path to Midi File, relative path to Wave File, Tempo, Scale, Key
        return [str(i), rel_midi_file_path, rel_wav_file_path, sample_gen.tempo, sample_gen.scale,
                sample_gen.rootNote.nameWithOctave]
