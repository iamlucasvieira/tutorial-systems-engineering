"""Creates the aircraft's loading diagram"""
import matplotlib.pyplot as plt
import numpy as np

from aircraft.cg_calculation import CenterOfGravity
from helpers import load_data


class Loading:

    # def __init__(self, file_name='NewData.csv'):
    def __init__(self, file_name='data.csv'):
        self.data = load_data(file_name)

        # Get cg at oew:
        CG = CenterOfGravity()
        xcg_oew = CG.cg
        self.xcg = [xcg_oew]  # assumed to be 0.25c we can update this later in more detail if we find another way
        self.mass = [self.data['OEW']]

    def get_new_xcg(self, xcg_old, mass_old, xcg_item, mass_item):
        """Returns the new mass and c.g. after an item is added"""
        xcg_old = xcg_old
        mass_old = mass_old

        mass_new = mass_item + mass_old
        xcg_new = (mass_old * xcg_old + mass_item * xcg_item) / mass_new

        self.xcg.append(xcg_new)
        self.mass.append(mass_new)

        return xcg_new, mass_new

    def load_cargo(self):
        """Shift the c.g. by loading the two cargo compartments"""
        xcg_old = self.xcg[-1]
        mass_old = self.mass[-1]

        XLEMAC = self.data['XLEMAC']
        mac = self.data['mac']

        xcg_cargo_f = (8.44 - XLEMAC) / mac
        mass_cargo_f = self.data['front_cargo_w']

        xcg_cargo_aft = (16.88 - XLEMAC) / mac
        mass_cargo_aft = self.data['aft_cargo_w']

        xcg_f, mass_f = self.get_new_xcg(xcg_old, mass_old, xcg_cargo_f, mass_cargo_f)
        xcg_aft, mass_aft = self.get_new_xcg(xcg_old, mass_old, xcg_cargo_aft, mass_cargo_aft)
        xcg_end, mass_end = self.get_new_xcg(xcg_f, mass_f, xcg_cargo_aft, mass_cargo_aft)

        xcg_list_f = [xcg_old, xcg_f, xcg_end]
        mass_list_f = [mass_old, mass_f, mass_end]

        xcg_list_aft = [xcg_old, xcg_aft, xcg_end]
        mass_list_aft = [mass_old, mass_aft, mass_end]

        return xcg_list_f, mass_list_f, xcg_list_aft, mass_list_aft

    def load_seats(self, gap=0):
        """Shift the c.g. by loading the passengers

        args
            gap (int): Number of seats that are skipped in a single column
        """

        XLEMAC = self.data['XLEMAC']
        mac = self.data['mac']
        dist_seats = self.data['dist_seats']

        n_seats = 17  # Number os seats in a single column

        x_seats_f = (2.4 / 11.3 * 26.50)  # Initial seat c.g.
        x_seats_aft = x_seats_f + dist_seats * n_seats  # Final seat c.g.

        x_cg_f = (np.linspace(x_seats_f, x_seats_aft, n_seats) - XLEMAC) / mac
        x_cg_aft = (np.linspace(x_seats_aft, x_seats_f, n_seats) - XLEMAC) / mac

        mass_average_pax = 92
        xcg_old = self.xcg[-1]
        mass_old = self.mass[-1]

        def load_passengers(x_cg_pax_list):
            """Add passengers and shift the c.g."""
            xcg_list = [xcg_old]
            mass_list = [mass_old]

            for x_cg_pax in x_cg_pax_list:
                if x_cg_pax > gap_xcg:  # When one of the columns have a gap
                    xcg, mass = self.get_new_xcg(xcg_list[-1], mass_list[-1], x_cg_pax, mass_average_pax)
                else:
                    # Load first and second passenger at same xcg
                    _, _ = self.get_new_xcg(xcg_list[-1], mass_list[-1], x_cg_pax, mass_average_pax)
                    xcg, mass = self.get_new_xcg(xcg_list[-1], mass_list[-1], x_cg_pax, mass_average_pax)

                xcg_list.append(xcg)
                mass_list.append(mass)

            return xcg_list, mass_list

        gap_xcg = x_cg_f[n_seats - gap - 1]  # Used to determine the c.g. position where a column with a gap stops

        xcg_list_f, mass_list_f = load_passengers(x_cg_f)
        xcg_list_aft, mass_list_aft = load_passengers(x_cg_aft, )

        return xcg_list_f, mass_list_f, xcg_list_aft, mass_list_aft

    def load_fuel(self):
        """Shift the c.g. by loading the fuel tanks"""
        xcg_old = self.xcg[-1]
        mass_old = self.mass[-1]

        xcg_fuel = 0.8  # cg fuel is equal to cg fuel tank TODO: get real data
        mass_fuel = self.data['fuel_max']  # TODO: get real data (done)

        xcg_end, mass_end = self.get_new_xcg(xcg_old, mass_old, xcg_fuel, mass_fuel)

        return [xcg_old, xcg_end], [mass_old, mass_end]

    def plot(self):
        """Plot the loading diagram"""

        # Define styles
        cargo = {'c': '#003f5c', 'marker': 'o'}
        window = {'c': '#58508d', 'marker': '+'}
        aisle = {'c': '#bc5090', 'marker': '+'}
        middle = {'c': '#ff6361', 'marker': '+'}
        fuel = {'c': '#ffa600', 'marker': 's'}

        # Create plot
        fig, ax = plt.subplots()
        ax.plot(self.xcg, self.mass)

        # Get cargo xcg shift
        xcg_cargo_f, mass_cargo_f, xcg_cargo_aft, mass_cargo_aft = self.load_cargo()
        l1, = ax.plot(xcg_cargo_f, mass_cargo_f, **cargo)
        ax.plot(xcg_cargo_aft, mass_cargo_aft, **cargo)

        # Get window seats xcg shift
        xcg_window_f, mass_windows_f, xcg_window_aft, mass_windows_aft = self.load_seats()
        l2, = ax.plot(xcg_window_f, mass_windows_f, **window)
        ax.plot(xcg_window_aft, mass_windows_aft, **window)

        # Get aisle seats xcg shift
        xcg_aisle_f, mass_aisle_f, xcg_aisle_aft, mass_aisle_aft = self.load_seats(gap=2)
        l3, = ax.plot(xcg_aisle_f, mass_aisle_f, **aisle)
        ax.plot(xcg_aisle_aft, mass_aisle_aft, **aisle)

        # Get middle seats xcg shift
        xcg_middle_f, mass_middle_f, xcg_middle_aft, mass_middle_aft = self.load_seats()
        l4, = ax.plot(xcg_middle_f, mass_middle_f, **middle)
        ax.plot(xcg_middle_aft, mass_middle_aft, **middle)

        # Get fuel xcg shift
        xcg_fuel, mass_fuel = self.load_fuel()
        l5, = ax.plot(xcg_fuel, mass_fuel, **fuel)

        # Find and plot maximum xcg shift
        margin = 0.02
        max_xcg, min_xcg = max(self.xcg) * (1 + margin), min(self.xcg) * (1 - margin)
        max_mass, min_mass = max(self.mass), min(self.mass)

        ax.plot([max_xcg, max_xcg], [min_mass, max_mass], '--k', alpha=0.55)
        ax.plot([min_xcg, min_xcg], [min_mass, max_mass], '--k', alpha=0.55)

        # Print results
        print('-' * 40)
        print(f"{'Results':^40}")
        print('-' * 40)
        print(f"{'Maximum Xcg_mac':<25} {max_xcg:<8} {'[-]':<7}")
        print(f"{'Minimum Xcg_mac':<25} {min_xcg:<8} {'[-]':<7}")
        print(f"{'MZFW':<25} {mass_middle_f[-1]:<8} {'[kg]':<7}")
        print(f"{'MTOW':<25} {max_mass:<8} {'[kg]':<7}")

        # Add plot labels, title, legend
        fig.suptitle("Loading diagram", fontsize=16)
        ax.set_xlabel(r'$X_{cg_{MAC}}$ [-]')
        ax.set_ylabel(f'Mass [kg]')
        ax.set_xlim(min_xcg * 0.8, max_xcg * 1.1)
        plt.legend([l1, l2, l3, l4, l5], ['Cargo', 'Window seats', 'Aisle seats', 'Middle seats', 'Fuel'])
        plt.grid()
        plt.show()

    # def get_xcg_ac(self):
    #
    #     xcg, mass = self.get_xcg_wing()
    #     xcg, mass = self.get_xcg_tail()
    #
    #     return value


def main():
    loading = Loading()
    loading.plot()


if __name__ == "__main__":
    main()
