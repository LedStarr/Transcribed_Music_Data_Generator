"""
Copyright (c) 2020 Tobias Lint <tobias@lint.at>. All rights reserved.
Licensed under the MIT License.
"""
from Generators.DataBaseGenerator import DataBaseGenerator
import os
import shutil

FOLDER_NAME = "MIDI and Wave Data"


def __ask_int(message):
    """
    Asks User for an Integer Value

    Args:
        message = str - Input from Console
    """
    value = ''
    while not isinstance(value, int):
        value = input(message)
        try:
            value = int(value)
            return value
        except:
            print("The Value you Provided is not a Integer. Input: '{0}'".format(value))


def __ask_bool(message):
    """
    Asks User for an 'y' or 'n' Char, which corresponds to a boolean.

    Args:
        message = str - Input from Console
    """
    value = ''
    while value != 'y' and value != 'n':
        value = input(message)

    return value == 'y'


def __ask_delete_when_not_empty(directory_path):
    """
    Asks User if he wants to remove all files in the given Directory and removes them if true.
    It also creates the Directory if it does not exist.

    Args:
        directory_path = str - Input from Console
    """
    if os.path.exists(directory_path):
        if len(os.listdir(directory_path)) != 0:
            do_delete = __ask_bool("The provided path is not empty. Should I empty it? (y/n)")
            if do_delete:
                try:
                    # Remove folder (if exists) with all files
                    if os.path.isdir(directory_path):
                        shutil.rmtree(directory_path, ignore_errors=True)
                    # Create new folder
                    os.mkdir(directory_path)
                except IOError:
                    raise IOError("Error upon either deleting or creating the directory or files. "
                                  "Please provide an empty Directory.")
    else:
        os.makedirs(directory_path)


# MAIN FUNCTION
if __name__ == "__main__":

    # SPLIT
    split = __ask_bool('Do you want to split the Samples into a training and test set? (y/n)')

    # NUMBER OF SAMPLES
    if split:
        number_of_samples_train = ''
        number_of_samples_test = ''

        number_of_samples_train = __ask_int('How many Samples do you want for training? \n')
        number_of_samples_test = __ask_int('How many Samples do you want for testing? \n')
    else:
        number_of_samples = __ask_int('How many Samples do you want? \n')

    # POLYPHONIC
    use_polyphonic = __ask_bool('Do you want to have polyphonic Samples in the Samples? (y/n)')

    # NOTES PER SAMPLE
    notes_per_sample = __ask_int('How many Notes, Pauses and/or Chords should be in one Sample? (y/n)')

    # MULTIPLE SYNTH MODULES
    use_synth_modules = __ask_bool('Do you want to use multiple synth modules? '
                                   'This will make the Samples get synthesized with different sound colors.(y/n)')

    # DIRECTORY
    setDirectory = __ask_bool('Do you want to provide your own Path? '
                              'Otherwise the Samples will be stored in the Directory '
                              'from where you have started this script. (y/n)')

    if setDirectory:
        path = ''
        while not os.path.isdir(path):
            path = input('Please provide a path:')
            path = path.replace('"', '')
            path = path.replace("'", '')
            if not os.path.isdir(path):
                print("The path you provided is not a directory. Input: '{0}'".format(path))
            else:
                path = os.path.join(path, FOLDER_NAME)
                __ask_delete_when_not_empty(path)

    else:
        path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(path, FOLDER_NAME)
        __ask_delete_when_not_empty(path)
    print("Storing Files in Directory: '{0}'".format(path))

    # GENERATE
    print("\n############## Starting to Generate Sample Database ##############\n")
    print("\n")

    try:
        generator = DataBaseGenerator(number_of_notes_per_sample=notes_per_sample, use_synth_modules=use_synth_modules)
        if split:
            generator.batch_generate_with_split(destination_directory=path,
                                                number_of_samples_train=number_of_samples_train,
                                                number_of_samples_test=number_of_samples_test,
                                                use_polyphonic=use_polyphonic)
        else:
            generator.batch_generate(destination_folder=path,
                                     number_of_samples=number_of_samples,
                                     use_polyphonic=use_polyphonic)
    except PermissionError:
        print("Access to path was denied")

    print("############################ Finished ############################\n")
