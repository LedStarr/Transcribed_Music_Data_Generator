# -*- coding: utf-8 -*-
"""
@author: Tobias Lint
@email: tobias@lint.at
"""

from readmidi import MidiFile, getdur

import pyaudio
import wave


class Scale:
    """
    Class for storing Information about a Musical-Scale
    
    TODO: use Scale-Objects from music21 Library
    """

    def __init__(self, name, firstInterval, secondInterval, thirdInterval, fourthInterval, fithInterval=None,
                 sixthInterval=None, seventhInterval=None, DEBUG=False):
        """
        Initializing Scale - Object
        
        If only 4 intervals are defined make it a Scale with 5 Notes

        Args:
            firstInterval: int - Describes how many musical half steps are between the root Note and the 2nd Note of Scale
            secondInterval: int - Describes how many musical half steps are between the 2nd Note and the 3rd Note of Scale
            thirdInterval: int - Describes how many musical half steps are between the 3rd Note and the 4th Note of Scale
            fourthInterval: int - Describes how many musical half steps are between the 4th Note and the 5th Note of Scale
            fithInterval: int - Describes how many musical half steps are between the 5th Note and the 6th Note of Scale
            sixthInterval: int - Describes how many musical half steps are between the 6th Note and the 7th Note of Scale
            seventhInterval: int - Describes how many musical half steps are between the 7th Note and the 8th Note of Scale
            DEBUG: bool - Switch for Printing Debug-Statements into the console
        """
        self.name = name
        if fithInterval != None:

            self.intervals = [firstInterval, secondInterval, thirdInterval, fourthInterval, fithInterval,
                              sixthInterval, seventhInterval]
        else:
            self.intervals = [firstInterval, secondInterval, thirdInterval, fourthInterval]

        if DEBUG:
            print(self.name + " - Scale created")

    def __str__(self):
        return self.name

    def calcNotes(self, rootNote):
        """
        Calculates all notes in Scale 
        
        Args:
            rootNote: Note Object - Base for calculating all notes in Scale
        Return:
            notes: List of Note Objects
        """
        tmp = rootNote
        notes = [tmp]
        for interval in self.intervals:
            tmp = tmp.transpose(interval)
            notes.append(tmp)

        return notes


def MIDI_to_WAV(synth, midiFile, fileName, DEBUG=False):
    """
    This function is basically the Main-Function of readmidi.py wich was partially changed to make it callable from code.
    
    Args:
        synth: Module - used for Synthesizing the WAV-File
        midiFile: str - Path to MIDI-File from which to synthesise
        fileName: str - Name of WAV-File
        DEBUG: bool - Switch for Printing Debug-Statements into the console
    """

    def getnote(q):
        for x in q.keys():
            if q[x] >= 0:
                return x
        return None

    def gettotal():
        t = 0
        for x, y in song:
            t += 4 / y
        return t

    song = []
    notes = {}
    m = MidiFile(midiFile)

    if DEBUG:
        for t, n in enumerate(m.tracks):
            if len(n) > 0:
                print(t, n[0], len(n))

    for n in m.tracks[0]:
        if DEBUG: print(n)

        nn = str(n).split()
        start, stop = float(nn[2]), float(nn[3])
        if start != stop:  # note ends because of NOTE OFF event
            if start - gettotal() > 0:
                song.append(('r', getdur(gettotal(), start)))
                if DEBUG: print("r1")
            song.append((nn[0].lower(), getdur(start, stop)))
        elif float(nn[1]) == 0 and notes.get(nn[0].lower(), -1) >= 0:  # note ends because of NOTE ON with velocity = 0
            if notes[nn[0].lower()] - gettotal() > 0:
                song.append(('r', getdur(gettotal(), notes[nn[0].lower()])))
                if DEBUG: print("r2")
            song.append((nn[0].lower(), getdur(notes[nn[0].lower()], start)))
            notes[nn[0].lower()] = -1
        elif float(nn[1]) > 0 and notes.get(nn[0].lower(), -1) == -1:  # note ends because of new note
            old = getnote(notes)
            if old != None:
                if notes[old] != start:
                    song.append((old, getdur(notes[old], start)))
                notes[old] = -1
            elif start - gettotal() > 0:
                song.append(('r', getdur(gettotal(), start)))
                if DEBUG: print("r3")
            notes[nn[0].lower()] = start

    synth.make_wav(song, fn=fileName, bpm=m.tempo, silent=True)





def write_wav_file(filename, frames, rate=44100, channels=2):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    RECORD_SECONDS = 5

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=CHUNK)
    """
    print("* recording")

    frames = []

    for i in range(0, int(rate / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")
    """
    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()


write_wav_file("test.wav")
