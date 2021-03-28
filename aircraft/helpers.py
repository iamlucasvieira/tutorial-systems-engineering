import csv


def load_data(file_name):
    """Returns csv data"""
    data = {}
    with open(file_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            if len(row) == 2:
                variable, value = row
                data[variable] = float(value)
    return data


def main():
    data = load_data()
    print(data)


if __name__ == "__main__":
    main()
