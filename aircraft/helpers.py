import csv


def load_data():
    """Returns csv data"""
    data = {}
    with open('data.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            variable, value = row
            data[variable] = float(value)
    return data


def main():
    data = load_data()
    print(data)


if __name__ == "__main__":
    main()
