# Processing takes in a request and applies to correct audio processing to it.
# This is a wrapper around the Ravel API Library to expose it to a web server
# in a more usable and meaningful way.
# import librosa
import numpy as np
from io import BytesIO
import pickle
import sys
import scipy.io as sio
# PWD = "/Users/storj/dev/ravellabs/ravel/"
# sys.path.append(PWD)
from ravel.ravellib.lib.effects import EQSignal, CompressSignal, ReverbSignal,\
                                    DeEsserSignal, SignalAggregator
from ravel.ravellib.lib.preprocessing import crest_factor, compute_lfe

class Processor():
    def __init__(self, wavfile, listOfWavfiles, trackouts_binaries):
        self.wavfile = wavfile
        self.all_trackout_binaries = trackouts_binaries
        self.listOfWavfiles = listOfWavfiles
        self.trackouts = []
        self.signal_aggregator = []
        self.compression_params = []
        self.processed_tracks = []
        self.num_signals = 1

        # NB: This may not always be 44100 but we can deal with that later
        self.sample_rate = 44100
        self.signal_aggregator = SignalAggregator(
            self.sample_rate, self.num_signals)

    def create_npa_from_wav(self, wav_file):
        load_bytes = BytesIO(wav_file.file_binary)
        load_bytes.seek(0)
        picked_obj = pickle.dumps(load_bytes)
        loaded_np = np.frombuffer(picked_obj)
        return loaded_np

    def equalize(self):
        eq = Equalize(self.wavfile, self.listOfWavfiles)
        processed = eq.equalize()
        print(f"Successful equalization: \n\t {type(processed)}")
        return processed

    def compress(self):
        co = Compress(self.wavfile, self.signal_aggregator, self.all_trackout_binaries)
        processed = co.compress()
        print(f"Successful compression of type {type(processed)}: \n\t{processed}")
        return processed

    def deesser(self):
        de = Deesser(self.wavfile)
        processed = de.deess()
        print(f"Successful deesser of type {type(processed)}: \n\t{processed}")
        return processed

    def limit(self):
        print("Processor limiter")
        pass


class Equalize():
    """
        Please define Equalize
    """

    def __init__(self, main_trackout, other_trackouts):
        # trackout to be processed
        self.main_trackout = main_trackout
        # other trackouts does not contain main_trackout
        self.other_trackouts = other_trackouts

    def equalize(self):
        # List of EQSignals, which contain a mono signal npArray
        signals = list()
        if len(self.other_trackouts) == 0:
            print("This will break things?")
        for loaded_np in self.other_trackouts:
            _eq = EQSignal(loaded_np, 1024, 1024, 1024, -12, "vocal", 10, 3, -2)
            signals.append(_eq)

        '''
            @parameters
                1: numpy array
                3: more to be desired...
        '''
        eq = EQSignal(self.main_trackout, 1024, 1024,
                      1024, -12, "vocal", 10, 3, -2)

        # equalize the trackout and return
        params = eq.eq_params(signals)
        equalized = eq.equalization(params, 2)
        print(f'returning eqwave of type {type(equalized)}: {equalized}')
        return equalized


class Compress():
    """
    Creates a new Compressor channel
    """

    def __init__(self, wavfile, signal_aggregator, all_trackout_binaries):
        self.wavfile = wavfile
        self.all_trackout_binaries = all_trackout_binaries
        self.signal_aggregator = signal_aggregator


    def compress(self):
        """
        compression deals with Compressor and SignalAggregator classes.
        the signal aggregator class calculates stats that are relative
        to each other and themselves.
        Compressor needs to know about all the attributes from each of
        the trackouts in the track to make an accurate guess.
        """

        trackouts = self.all_trackout_binaries
        comp_signals = [] # All the other trackouts in a track np array of signals
        comp_lfe = [] # Convenience methods
        comp_crest = [] # 
        processed_signals = []

        # turn waveile into numpy array
        numpy_array = []

        # get params for compression
        # audio_type is the track type, e.g. vocals, drums, guitar, etc...
        audio_type = "vocal"

        # do this for each track out in a track
        for np_arr_track in trackouts:
            # Convert wav binary to np_array
            cp = CompressSignal(
                np_arr_track, 1024, 1024, 123,
                200, audio_type, 0.2, 1, 1000,
                2, 0.08, 1.0)

            cp_crest_factor = cp.crest_factor
            cp_lfe = cp.lfe
            comp_crest.append(cp_crest_factor)
            comp_lfe.append(cp_lfe)
            cfa = self.signal_aggregator.cfa(comp_crest)
            lfa = self.signal_aggregator.lfa(comp_lfe)
            comp_params = cp.comp_params(cfa=cfa, lfa=lfa)
            # push lfe and crest factor for each track into comp_lfe and
            # comp_crest in order?

        num_signals = len(trackouts)

        # we want to use 44100 sample rate as much as possible.
        # we can get this from librosa
        sample_rate = 44100
        agg = SignalAggregator(sample_rate, num_signals)
        lfa = agg.lfa(comp_lfe)
        cfa = agg.cfa(comp_crest)

        for i in range(len(comp_signals)):
            cp = comp_signals[i].comp_params(cfa, lfa)
            compressed = comp_signals[i].compression(cp)
            processed_signals.append(compressed)
        print(f"WOOT {processed_signals}")
        return processed_signals


class Reverb():
    def __init__(self):
        print("Creating a new Reverber: ", self)
        pass

    def reverb(self):
        numpy_array = []

        # audio type is the instrument on the track
        audio_type = "vocal"

        # tweakable
        amount = 95
        room_scale = 10
        rev = ReverbSignal(
            "", numpy_array, 1024, 1024, 1024, -12, audio_type,
            amount, 0.0, room_scale, 0.0, 0.4, 600, 6000, 2, 70, 12
        )
        processed = rev.reverb()
        return processed


class Deesser():
    def __init__(self, wavfile):
        self.wavfile = wavfile
        print("creating new DeEsser: ", self)
        pass

    def create_npa_from_wav(self, wav_file):
        load_bytes = BytesIO(wav_file)
        byte_buffer = load_bytes.getvalue()
        load_bytes.seek(0)
        picked_obj = pickle.dumps(load_bytes)
        loaded_np = np.frombuffer(byte_buffer)#, dtype=np.int32)
        print(f"what is the type return {type(loaded_np)}")
        return loaded_np

    def deess(self):
        # critical bands are the frequencies at which the deesser looks at to
        # calculate sharpness
        critical_bands = [
            100, 200, 300, 400, 510, 630, 770, 920, 1080, 1270,
            1480, 1720, 2000, 2320, 2700, 3150, 3700, 4400,
            5300, 6400, 7700, 9500, 12000, 15500
        ]
        c = 0.08

        # get numpy array from wavefile
        numpy_array = self.create_npa_from_wav(self.wavfile)

        # audio type is the track type
        audio_type = "vocal"
        sig = DeEsserSignal(numpy_array, 256, 256, 256, -12, audio_type,
                            critical_bands, c, 1.2, 0.65)

        sharpness = sig.compute_sharpness()
        gr = sig.gain_reduction(sharpness)
        processed = sig.deesser(gr)

        return processed


class Handler():
    """
    The Handler is responsible for queueing and building the effects for each
    track.
    """

    def __init__(self):
        """
        creates a new builder
        """
        self._builder = None
        self._builder = Processor(None, None, None)
        print("assigned builder: ", self._builder)
        pass

    def Builder(self):
        """
        The Handler works with the builder instance to create the processing
        stack for each request.
        """
        return self._builder

    def SignalAggregator(self):
        """
        This gets the SignalAggregator for a given track
        """
        pass

    def GetTrackouts(self, track_id):
        """
        GetTrackouts returns all the trackouts for a given `track_id`
        """
        pass


if __name__ == "__main__":
    """
    Allows the script to be run from the command line for proof of concept
    """

    handler = Handler()
    print("handler created: ", handler)

    builder = handler.Builder()
    print("builder from handler: ", builder)

    processor = Processor()

    print("processor created: ", processor)
    processor.equalize()
    processor.compress()
    processor.limit()

    # e.g. apply some processing
    # handler.default_processing()
    # e.g. apply all processing
    # handler.all()
