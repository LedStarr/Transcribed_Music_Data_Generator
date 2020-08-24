# Musicological Machine Learning Database Generator


This Script is intended to help Musicologists and everybody else to generate randomly generated *MIDI* and *WAV Files*. 

First it will generate a *MIDI File* and then synthesizes a *WAV File* from it. 
Theses Files will be stored inside a *CSV* or a Train and Test *CSV* afterwards and stores the relative paths 
to the newly generated Files with some extra information.

This Data is intended to help in cases where transcribed Music-Data is scars and or the human bias is something you 
want to cancel out of the equation.

By running main.py the Script will ask you some questions and generate all Files afterwards. Feel free to use the 
*batch_generate()* Method from the *DataBaseGenerator* Class for creating the Data-Sets on your own.

## Dependencies:
This script uses:
- [music21](https://github.com/cuthbertLab/music21) for creating the *MIDI Files*
- [mido](https://github.com/mido/mido) for reading the *MIDI Files* in a stream.
- [pyo](https://github.com/belangeo/pyo) as sound engine for synthesizing the *WAV Files*
- [pandas](https://github.com/pandas-dev/pandas) for creating the *CSV's*
- [numpy](https://github.com/numpy/numpy) for creating random numbers
- [tqdm](https://github.com/tqdm/tqdm) for displaying a progress bar


**Since pyo only supports Python 3.7 it is currently not possible to use this script with higher Versions of Python.**
