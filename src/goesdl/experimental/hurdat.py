from typing import TextIO


def str_to_float(value_strings):
    return [float(value) for value in value_strings]


def get_track_data(lines: list[str]):
    clines = []
    for line in lines:
        cline = []
        for i, word in enumerate(line.split(",")):
            if i in {0, 1, 4, 5}:
                cline.append(word.strip())
        line = []
        for i in range(len(cline)):
            if i == 0:
                cline[i] = f"{cline[i][:4]}-{cline[i][4:6]}-{cline[i][6:8]}"
            if i == 1:
                cline[i] = f"{int(cline[i]):0>4}"
                cline[i] = f"T{cline[i][:2]}:{cline[i][2:]}Z"
            if i == 2:
                cline[i] = (
                    f"+{cline[i][:-1]}"
                    if cline[i][-1] == "N"
                    else f"-{cline[i][:-1]}"
                )
            if i == 3:
                cline[i] = (
                    f"+{cline[i][:-1]}"
                    if cline[i][-1] == "E"
                    else f"-{cline[i][:-1]}"
                )
        line = [cline[0] + cline[1], cline[2], cline[3]]
        clines.append(line)

    iso_dates, latitudes, longitudes = zip(*clines)

    return (
        iso_to_timestamp(iso_dates),
        str_to_float(latitudes),
        str_to_float(longitudes),
    )


def parse_header(line: list[str]):
    parts = line.strip().split(",")

    identifier = parts[0].strip()
    sector = identifier[:2]
    number = int(identifier[2:4])
    year = int(identifier[4:8])

    name = parts[1].strip()
    nlines = int(parts[2].strip())

    return year, name, nlines, sector, number


def read_lines(file: TextIO, nlines: int):
    data_lines = []
    for _ in range(nlines):
        try:
            data_lines.append(next(file))
        except StopIteration:
            break
    return data_lines


def skip_lines(file: TextIO, nlines: int):
    for _ in range(nlines):
        try:
            next(file)
        except StopIteration:
            break


def parse_file(file: TextIO, target_name: str, target_year: str):
    while True:
        try:
            line = next(file)
            try:
                year, name, nlines, sector, number = parse_header(line)
                if year == target_year and name == target_name:
                    return read_lines(file, nlines)
                else:
                    skip_lines(file, nlines)
            except ValueError:
                continue
            except IndexError:
                continue
        except StopIteration:
            break
    return []


def parse_hurdat(
    file_path: str, target_name: str, target_year: str
) -> list[str]:
    target_name = target_name.upper()
    try:
        with open(file_path, "r") as file:
            lines = parse_file(file, target_name, target_year)
            if lines:
                return lines
        return []
    except FileNotFoundError:
        print(f"Error: El archivo no se encontró en la ruta: {file_path}")
        return []
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        return []
