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


    def wing_mass(self):
        factor = self.factors['wing']

        #


def main():
    cg_oew = CenterOfGravity()


if __name__ == "__main__":
    main()
