"""Creates the aircraft's loading diagram"""
import matplotlib.pyplot as plt
import numpy as np

from helpers import load_data


class Loading:

    def __init__(self):
        self.data = load_data()
        self.xcg = [self.data['XcgOEW']]
        self.mass = [0]

    def get_new_xcg(self, xcg_old, mass_old, xcg_item, mass_item):
        xcg_old = xcg_old
        mass_old = mass_old

        mass_new = mass_item + mass_old
        xcg_new = (mass_old * xcg_old + mass_item * xcg_item) / mass_new

        self.xcg.append(xcg_new)
        self.mass.append(mass_new)

        return xcg_new, mass_new

    def load_cargo(self):
        xcg_old = self.xcg[-1]
        mass_old = self.mass[-1]

        xcg_cargo_f = 0.2  # TODO: get real data
        mass_cargo_f = 1000  # TODO: get real data

        xcg_cargo_aft = 0.6  # TODO: get real data
        mass_cargo_aft = 1500  # TODO: get real data

        xcg_f, mass_f = self.get_new_xcg(xcg_old, mass_old, xcg_cargo_f, mass_cargo_f)
        xcg_aft, mass_aft = self.get_new_xcg(xcg_old, mass_old, xcg_cargo_aft, mass_cargo_aft)
        xcg_end, mass_end = self.get_new_xcg(xcg_f, mass_f, xcg_cargo_aft, mass_cargo_aft)

        xcg_list_f = [xcg_old, xcg_f, xcg_end]
        mass_list_f = [mass_old, mass_f, mass_end]

        xcg_list_aft = [xcg_old, xcg_aft, xcg_end]
        mass_list_aft = [mass_old, mass_aft, mass_end]

        return xcg_list_f, mass_list_f, xcg_list_aft, mass_list_aft

    def load_seats(self, x_seats_f, x_seats_aft):
        n_seats = 20  # Number os seats in a single column  TODO: get real data

        # x_seats_f = 0.1  # TODO: get real data
        # x_seats_aft = 0.6  # TODO: get real data

        x_cg_f = np.linspace(x_seats_f, x_seats_aft, 20)
        x_cg_aft = np.linspace(x_seats_aft, x_seats_f, 20)

        mass_average_pax = 70 * 2  # Times two because passengers are loaded 2 by 2 TODO: get real data
        xcg_old = self.xcg[-1]
        mass_old = self.mass[-1]

        def load_passengers(x_cg_pax_list):
            xcg_list = [xcg_old]
            mass_list = [mass_old]

            for x_cg_pax in x_cg_pax_list:
                xcg, mass = self.get_new_xcg(xcg_list[-1], mass_list[-1], x_cg_pax, mass_average_pax)
                xcg_list.append(xcg)
                mass_list.append(mass)
            return xcg_list, mass_list

        xcg_list_f, mass_list_f = load_passengers(x_cg_f)
        xcg_list_aft, mass_list_aft = load_passengers(x_cg_aft)

        return xcg_list_f, mass_list_f, xcg_list_aft, mass_list_aft

    def load_fuel(self):
        xcg_old = self.xcg[-1]
        mass_old = self.mass[-1]

        xcg_fuel = 0.8  # TODO: get real data
        mass_fuel = 5000  # TODO: get real data

        xcg_end, mass_end = self.get_new_xcg(xcg_old, mass_old, xcg_fuel, mass_fuel)

        return [xcg_old, xcg_end], [mass_old, mass_end]

    def plot(self):
        """Plot the loaging diagram"""

        # Define styles
        cargo = {'c': 'blue', 'marker': 'o'}
        window = {'c': 'green', 'marker': '+'}
        aisle = {'c': 'pink', 'marker': '+'}
        middle = {'c': 'gray', 'marker': '+'}
        fuel = {'c': 'orange', 'marker': 's'}

        # Create plot
        fig, ax = plt.subplots()
        ax.plot(self.xcg, self.mass)

        # Get cargo xcg shift
        xcg_cargo_f, mass_cargo_f, xcg_cargo_aft, mass_cargo_aft = self.load_cargo()
        l1, = ax.plot(xcg_cargo_f, mass_cargo_f, **cargo)
        ax.plot(xcg_cargo_aft, mass_cargo_aft, **cargo)

        # Get window seats xcg shift
        xcg_window_f, mass_windows_f, xcg_window_aft, mass_windows_aft = self.load_seats(0.1, 0.6)
        l2, = ax.plot(xcg_window_f, mass_windows_f, **window)
        ax.plot(xcg_window_aft, mass_windows_aft, **window)

        # Get aisle seats xcg shift
        xcg_aisle_f, mass_aisle_f, xcg_aisle_aft, mass_aisle_aft = self.load_seats(0.1, 0.6)
        l3, = ax.plot(xcg_aisle_f, mass_aisle_f, **aisle)
        ax.plot(xcg_aisle_aft, mass_aisle_aft, **aisle)

        # Get middle seats xcg shift
        xcg_middle_f, mass_middle_f, xcg_middle_aft, mass_middle_aft = self.load_seats(0.1, 0.6)
        l4, = ax.plot(xcg_middle_f, mass_middle_f, **middle)
        ax.plot(xcg_middle_aft, mass_middle_aft, **middle)

        # Get fuel xcg shift
        xcg_fuel, mass_fuel = self.load_fuel()
        l5, = ax.plot(xcg_fuel, mass_fuel, **fuel)

        # Find and plot maximum xcg shift
        max_xcg, min_xcg = max(self.xcg), min(self.xcg)
        max_mass, min_mass= max(self.mass), min(self.mass)

        ax.plot([max_xcg, max_xcg], [min_mass, max_mass], '--k', alpha=0.55)
        ax.plot([min_xcg, min_xcg], [min_mass, max_mass], '--k', alpha=0.55)

        # Print results
        print('-' * 45)
        print(f"{'Results':^45}")
        print('-' * 45)
        print(f"{'Maximum Xcg_mac [-]':<25} {max_xcg:<20}")
        print(f"{'Minimum Xcg_mac [-]':<25} {min_xcg:<20}")
        print(f"{'Final mass [kg]':<25} {max_mass:<20} ")

        # Add plot labels, title, legend
        fig.suptitle("Loading diagram", fontsize=16)
        ax.set_xlabel(r'$X_{cg_{MAC}}$ [-]')
        ax.set_ylabel(f'Mass [kg]')
        ax.set_xlim(0, 1)
        plt.legend([l1, l2, l3, l4, l5], ['Cargo', 'Window seats', 'Aisle seats', 'Middle seats', 'Fuel'])
        plt.grid()
        plt.show()

def main():
    loading = Loading()
    loading.plot()


if __name__ == "__main__":
    main()
