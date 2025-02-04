from ravellib.lib.effects import EQSignal
class Equalize():
    """
        Please define Equalize
    """

    def __init__(self, main_trackout, other_trackouts, sr):
        # trackout to be processed
        self.main_trackout = main_trackout
        # other trackouts does not contain main_trackout
        self.other_trackouts = other_trackouts
        self.sr = sr

    def equalize(self):
        # List of EQSignals, which contain a mono signal npArray
        signals = list()
        if len(self.other_trackouts) == 0:
            self.other_trackouts.append(self.main_trackout)
        for loaded_np in self.other_trackouts:
            _eq = EQSignal(loaded_np, 1024, 1024, 1024, -12, "vocal", self.sr, 10, 3, -2)
            signals.append(_eq)

        '''
            @parameters
                1: numpy array
                3: more to be desired...
        '''
        eq = EQSignal(self.main_trackout, 1024, 1024,
                      1024, -12, "vocal", self.sr, 10, 3, -2)

        # equalize the trackout and return
        params = eq.eq_params(signals)
        equalized = eq.equalization(params, 2)
        print(f'returning eqwave of type {type(equalized)}: {equalized}')
        return equalized
