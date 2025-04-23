def standard_to_lineman_name(standard_name):
    words = standard_name.split("_")
    labels = []
    acronyms = ["TOA", "IR", "UV", "SST"]

    for word in words:
        if word.upper() in acronyms:
            labels.append(word.upper())
        else:
            labels.append(word.capitalize())

    return " ".join(labels)
