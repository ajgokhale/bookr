import csv

def csv_to_dict(reader):
    profiles = dict()
    tokenized = dict()

    for entry in reader:
        entry = list(entry)
        if len(entry) == 3:
            profiles[entry[0]] = (entry[1], entry[2])
            tokenized[entry[2]] = (entry[0])

    return profiles, tokenized
