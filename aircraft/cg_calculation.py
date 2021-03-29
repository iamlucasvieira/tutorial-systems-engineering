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

        self.areas = self.get_areas()

        self.cgs = self.components_cg()
        self.mass = self.components_mass()

        self.cg = self.aircraft_cg()

    def get_cr(self):
        """Computes the chord length at the rooot for wing, vertica tail and horizontal tail"""
        self.cr = 2 * self.data['S'] / ((self.data['taper'] + 1) * self.data['b'])
        self.cr_h = 2 * self.data['S_h'] / ((self.data['taper_h'] + 1) * self.data['b_h'])
        self.cr_v = 2 * self.data['S_v'] / ((self.data['taper_v'] + 1) * self.data['b_half_v'] * 2)

    @staticmethod
    def wet_to_exposed(mass):
        return mass / 2 * (1 + 0.2 * self.data['t/c'])

    def get_areas(self):
        """Returns the areas of each group to estimate their mass"""
        areas = {}

        # Wing exposed area
        S = self.data['S']
        d_fus = self.data['l_h']
        b = self.data['b']
        chord_fuselage, _ = self.chord_at_pctg(d_fus / b, surface='w')

        area_w = S - d_fus * chord_fuselage
        areas['wing'] = area_w

        # Vertical tail area
        area_v = self.data['S_v']
        areas['vertical_tail'] = area_v

        # Horizontal tail area
        area_h = self.data['S_h']
        areas['horizontal_tail'] = area_h

        # Fuselage area
        l_fus = self.data['l_f']
        d_fus = self.data['l_h']
        area_f = np.pi * d_fus * l_fus
        areas['fuselage'] = area_f

        # Power plant "area" (for power plant the mass estimation is based on engine mass)
        areas['power_plant'] = self.data['ME']

        # Systems "area" (For systems the MTOW is used for mass estimation)
        areas['systems'] = self.data['MTOW']

        return areas

    def components_mass(self):
        """Returns a dictionary with the mass of each a/c component"""
        factors = self.factors
        areas = self.areas
        MTOW = self.data['MTOW']
        ME = self.data['ME']  # We got from wikipedia  ALF502R-3
        area_w = areas['wing']
        area_f = areas['fuselage']
        area_v = areas['vertical_tail']
        area_h = areas['horizontal_tail']

        mass = {}

        mass['wing'] = factors['wing'] * area_w + factors['main_gear'] * MTOW + factors['power_plant'] * ME
        mass['fuselage'] = factors['fuselage'] * area_f + factors['nose_gear'] * MTOW + factors['systems'] * MTOW
        mass['horizontal_tail'] = factors['horizontal_tail'] * area_h
        mass['vertical_tail'] = factors['vertical_tail'] * area_v

        return mass

    def cg_distance_from_nose(self, x_loc, y, surface='w'):
        """Returns the cg distance of the wing, vertical tail, and horizontal tail"""

        if surface == 'w':
            tr = self.data['taper']
            quarter_sweep = self.data['quart_sweep']
            A = self.data['A']
            distance_to_root = self.data['nose_distance_w']
        elif surface == 'v':
            tr = self.data['taper_v']
            quarter_sweep = self.data['quart_sweep_v']
            A = self.data['A_v']
            distance_to_root = self.data['nose_distance_v']
        elif surface == 'h':
            tr = self.data['taper_h']
            quarter_sweep = self.data['quart_sweep_h']
            A = self.data['A_h']
            distance_to_root = self.data['nose_distance_h']
        else:
            return None

        sweep_le = np.arctan(np.tan(np.radians(quarter_sweep)) - 4 / A * (-0.25 * (1 - tr) / (1 + tr)))
        self.sweep_le = sweep_le

        # The c.g. is given as the distance to the leading edge of the root + the distance of the leading edge of the root to the a/c nose
        cg_distance = x_loc + y * np.tan(sweep_le) + distance_to_root

        return cg_distance

    def chord_at_pctg(self, span_pctg, surface='w'):
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
            cr = self.cr_h
        else:
            return None

        y = span_pctg * b / 2
        return cr * (1 - 2 * (1 - taper_ratio) * y / b), y

    def components_cg(self):
        """Returns a dictionary with the cg of each a/c component"""
        cgs = {}

        # To compute the c.g. position: first the it is found as a distance in the chord. Then it is transformed into distance to nose

        chord_cg_w, dist_le_w = self.chord_at_pctg(0.4, surface='w')
        cgs['wing'] = self.cg_distance_from_nose(chord_cg_w * 0.38, dist_le_w, surface='w')

        chord_cg_h, dist_le_h = self.chord_at_pctg(0.38, surface='h')
        cgs['horizontal_tail'] = self.cg_distance_from_nose(chord_cg_h * 0.42, dist_le_h, surface='h')

        chord_cg_v, dist_le_v = self.chord_at_pctg(0.38, surface='v')
        cgs['vertical_tail'] = self.cg_distance_from_nose(chord_cg_v * 0.43, dist_le_v, surface='v')

        cgs['fuselage'] = 0.42 * self.data['l_f']

        return cgs

    def aircraft_cg(self):
        """Returns the aircraft cg wrt the three main groups: wing, fuselage and tail"""
        numerator, denominator = 0, 0

        for group in ['wing', 'horizontal_tail', 'vertical_tail', 'fuselage']:
            numerator += self.mass[group] * self.cgs[group]
            denominator += self.mass[group]

        XLEMAC = self.data['XLEMAC']
        mac = self.data['mac']

        aircraft_cg = (numerator / denominator - XLEMAC) / mac
        return aircraft_cg

    def wrt_mac(self, value):
        return (value-self.data['XLEMAC'])/self.data['mac']

    def print(self):
        print('-' * 60)
        print(f"{'c.g. calculation':^60}")
        print('-' * 60)

        print(f"{'Aircraft c.g.':<30} {self.cg:<30}")

        print(f"{'Wing c.g.':<30} {self.wrt_mac(self.cgs['wing']):<30}")
        print(f"{'H. tail c.g.':<30} {self.wrt_mac(self.cgs['horizontal_tail']):<30}")
        print(f"{'V. tail c.g.':<30} {self.wrt_mac(self.cgs['vertical_tail']):<30}")
        print(f"{'Fuselage c.g.':<30} {self.wrt_mac(self.cgs['fuselage']):<30}")


def main():
    cg_oew = CenterOfGravity()
    cg_oew.print()


if __name__ == "__main__":
    main()
