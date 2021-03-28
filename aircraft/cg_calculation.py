import numpy as np

from helpers import load_data


class CenterOfGravity:

    def __init__(self, file_name='data.csv', transport=True):
        """Computes the aircraft center of gravity at operational empty weight"""
        self.data = load_data(file_name)

        if transport:
            self.factors = {
                'wing': 12.2,  # w.r.t exposed area
                'fuselage': 6.8,  # w.r.t wetted area
                'horizontal_tail': 9.8,  # w.r.t exposed area
                'vertical_tail': 9.8,  # w.r.t exposed area
                'nose_gear': 0.009,  # w.r.t MTO
                'main_gear': 0.048,  # w.r.t MTO
                'power_plant': 1.4,  # w.r.t ME
                'systems': 0.1,  # w.r.t MTO
            }
        else:
            self.factors = {
                'wing': 49,  # w.r.t exposed area
                'fuselage': 24,  # w.r.t wetted area
                'horizontal_tail': 27,  # w.r.t exposed area
                'vertical_tail': 27,  # w.r.t exposed area
                'nose_gear': 0.006,  # w.r.t MTO
                'main_gear': 0.037,  # w.r.t MTO
                'power_plant': 1.3,  # w.r.t ME
                'systems': 0.17,  # w.r.t MTO
            }

        self.get_cr()

        self.wet_area = self.Swet()
        self.exposed_area = self.wet_area / 2 * (1 + 0.2 * self.data['t/c'])

        self.cgs = self.components_cg()
        self.mass = self.components_mass()

        # self.cg = self.aircraft_cg()

    def get_cr(self):
        """Computes the chord length at the rooot for wing, vertica tail and horizontal tail"""
        self.cr = 2 * self.data['S'] / ((self.data['taper'] + 1) * self.data['b'])
        self.cr_h = 2 * self.data['S_h'] / ((self.data['taper_h'] + 1) * self.data['b_h'])
        self.cr_v = 2 * self.data['S_v'] / ((self.data['taper_v'] + 1) * self.data['b_half_v'] * 2)

    def Swet(self):
        dfus = 3.56
        lfus = self.data['l_f']
        Swnet = self.data['S'] * 2 - 26.21 / 9 * 1.4 * dfus
        tc = self.data['t/c']
        kf = 0.2  # done
        cr = self.cr
        bcw = 26.21
        Sh = self.data['S_h']
        Sv = self.data['S_v']
        return np.pi / dfus * (lfus - 1.3 * dfus) + Swnet * (2 + 0.5 * tc) + kf * bcw * cr + 2 * (Sh + Sv)

    def components_mass(self):
        """Returns a dictionary with the mass of each a/c component"""
        factors = self.factors
        MTOW = self.data['MTOW']
        ME = 1  # TODO: Discover real value

        mass = {}

        mass['wing'] = factors['wing'] * self.exposed_area + factors['main_gear'] * MTOW + factors['power_plant'] * ME
        mass['fuselage'] = factors['fuselage'] * self.wet_area + factors['nose_gear'] * MTOW + factors['systems'] * MTOW
        mass['horizontal_tail'] = factors['horizontal_tail'] * MTOW
        mass['vertical_tail'] = factors['vertical_tail'] * MTOW

        return mass

    def convert_mac(self, mac, x_chord):
        cr = 2 * self.data['S'] / ((self.data['taper'] + 1) * self.data['b'])
        taper_ratio = self.data['taper']
        y = (mac / cr - 1) / -2 / (1 - taper_ratio) * self.data['b']
        sweep_LE = np.arctan(
            np.tan(self.data['quart_sweep'] - 4 / self.data['A'] * (-25 / 100 * (1 - taper_ratio) / (1 + taper_ratio))))
        a = y * np.sin(sweep_LE) / np.cos(sweep_LE) + x_chord
        return a

    def chord_at_pctg(self, root_pctg, surface='w'):
        """Returns the chord length at n% from the

        args:
            root_pctg (float): pctg of the root where the chord is wanted
            surface (str): 'w' for wing, 'v' for vertical tail, 'h' for horizontal tail
        """
        if surface == 'w':
            taper_ratio = self.data['taper']
            b = self.data['b']
            cr = self.cr
        elif surface == 'v':
            taper_ratio = self.data['taper_v']
            b = self.data['b_half_v'] * 2
            cr = self.cr_v
        elif surface == 'h':
            taper_ratio = self.data['taper_h']
            b = self.data['b_h']
            cr = self.cr
        else:
            return None

        y = root_pctg * b / 2
        return cr * (1 - 2 * (1 - taper_ratio) * y / b)

    def components_cg(self):
        """Returns a dictionary with the cg of each a/c component"""
        cgs = {}

        cgs['wing'] = self.convert_mac(0.38 * self.chord_at_pctg(0.4, surface='w'))
        cgs['fuselage'] = 0.42 * self.data['l_f']
        cgs['horizontal_tail'] = self.convert_mac(0.42 * self.chord_at_pctg(0.38, surface='h'))
        cgs['vertical_tail'] = self.convert_mac(0.42 * self.chord_at_pctg(0.55, surface='v'))

        return cgs

    def aircraft_cg(self):
        """Returns the aircraft cg wrt the three main groups: wing, fuselage and tail"""
        numerator = 0
        denominator = 0
        for mass, cg in zip(self.mass, self.cgs):
            numerator += mass * cg
            denominator += mass

        return numerator / denominator


def main():
    cg_oew = CenterOfGravity()


if __name__ == "__main__":
    main()
