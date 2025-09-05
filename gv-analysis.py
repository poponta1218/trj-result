import tomllib
from pathlib import Path
from pprint import pprint

import numpy as np


class IRC:
    def __init__(self, system: str, config: dict):
        self.system: str = system
        self.config: dict = config
        self.log_path: Path = Path()
        self.irc_forward: list[dict] = []
        self.irc_backward: list[dict] = []
        self.irc: list[dict] = []
        self.reac: dict[str, tuple[float, float, float]] = {}
        self.prod: dict[str, tuple[float, float, float]] = {}
        self.ts: dict[str, tuple[float, float, float]] = {}

    def load_gvlog(self, gvlog: Path) -> tuple[list[dict], list[dict]]:
        # TODO(poponta): Fix the reverse-flagging position (it causes incorrect product identification)
        self.log_path = gvlog
        irc_forward, irc_backward = [], []
        reverse_flag = False
        with gvlog.open() as f:
            text = f.read()
            struc_blocks = text.split(sep="Input orientation:\n")[1:]
            for block in struc_blocks:
                lines = block.splitlines()
                coord = {}
                for line in lines:
                    if "Beginning calculation of the REVERSE path." in line:
                        reverse_flag = True
                    try:
                        if len(line.split()) == 6:
                            atom_label = line.split()[0]
                            atomic_symbol = atomnum2sym(int(line.split()[1]))
                            x, y, z = map(float, line.split()[3:])
                            coord[atomic_symbol + atom_label] = (x, y, z)

                    except (ValueError, TypeError):
                        continue
                if reverse_flag:
                    irc_backward.append(coord)
                else:
                    irc_forward.append(coord)
            irc_forward.append(irc_backward[0])
            irc_backward = irc_backward[1:]
        self.irc_forward = irc_forward
        self.irc_backward = irc_backward
        self.irc = irc_backward[::-1] + irc_forward
        self.ts = irc_forward[0]
        self.prod = irc_forward[-1]
        self.reac = irc_backward[-1]
        return irc_forward, irc_backward

    def calc_distance(self, coord: dict, atom1: str, atom2: str) -> float:
        try:
            x1, y1, z1 = coord[atom1]
            x2, y2, z2 = coord[atom2]
            return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)

        except KeyError:
            print(f"Atom {atom1} or {atom2} not found in coordinates.")
            return float("nan")

    def gen_distance_data(self, distance: list[tuple[float, ...]], header: list[str], filename: Path) -> None:
        with filename.open("w") as f:
            f.write(",".join(header) + "\n")
            for d in distance:
                f.write(f"{d[0]:.4f},{d[1]:.4f},{d[2]:.4f}\n")

    def gen_distance_position_data(self, coord: dict, header: list[str], filename: Path) -> None:
        with filename.open("w") as f:
            f.write(",".join(header) + "\n")
            r22 = distance(coord, *self.config["r1"])
            r42 = distance(coord, *self.config["r2"])
            r_im = distance(coord, *self.config["r3"])
            f.write(f"{r22:.4f},{r42:.4f},{r_im:.4f}\n")


def atomnum2sym(atomic_num: int) -> str:
    atomic_symbols = {
        1: "H",
        2: "He",
        3: "Li",
        4: "Be",
        5: "B",
        6: "C",
        7: "N",
        8: "O",
        9: "F",
        10: "Ne",
        11: "Na",
        12: "Mg",
        13: "Al",
        14: "Si",
        15: "P",
        16: "S",
        17: "Cl",
        18: "Ar",
        19: "K",
        20: "Ca",
        21: "Sc",
        22: "Ti",
        23: "V",
        24: "Cr",
        25: "Mn",
        26: "Fe",
        27: "Co",
        28: "Ni",
        29: "Cu",
        30: "Zn",
        31: "Ga",
        32: "Ge",
        33: "As",
        34: "Se",
        35: "Br",
        36: "Kr",
        37: "Rb",
        38: "Sr",
        39: "Y",
        40: "Zr",
        41: "Nb",
        42: "Mo",
        43: "Tc",
        44: "Ru",
        45: "Rh",
        46: "Pd",
        47: "Ag",
        48: "Cd",
        49: "In",
        50: "Sn",
        51: "Sb",
        52: "Te",
        53: "I",
        54: "Xe",
        55: "Cs",
        56: "Ba",
        57: "La",
        58: "Ce",
        59: "Pr",
        60: "Nd",
        61: "Pm",
        62: "Sm",
        63: "Eu",
        64: "Gd",
        65: "Tb",
        66: "Dy",
        67: "Ho",
        68: "Er",
        69: "Tm",
        70: "Yb",
        71: "Lu",
        72: "Hf",
        73: "Ta",
        74: "W",
        75: "Re",
        76: "Os",
        77: "Ir",
        78: "Pt",
        79: "Au",
        80: "Hg",
        81: "Tl",
        82: "Pb",
        83: "Bi",
        84: "Po",
        85: "At",
        86: "Rn",
        87: "Fr",
        88: "Ra",
        89: "Ac",
        90: "Th",
        91: "Pa",
        92: "U",
        93: "Np",
        94: "Pu",
        95: "Am",
        96: "Cm",
        97: "Bk",
        98: "Cf",
        99: "Es",
        100: "Fm",
        101: "Md",
        102: "No",
        103: "Lr",
        104: "Rf",
        105: "Db",
        106: "Sg",
        107: "Bh",
        108: "Hs",
        109: "Mt",
        110: "Ds",
        111: "Rg",
        112: "Cn",
        113: "Nh",
        114: "Fl",
        115: "Mc",
        116: "Lv",
        117: "Ts",
        118: "Og",
    }
    return atomic_symbols.get(atomic_num, "X")


def distance(coord: dict, atom1: str, atom2: str) -> float:
    x1, y1, z1 = coord[atom1]
    x2, y2, z2 = coord[atom2]
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)


def main():
    irc_dir = Path("data/irc").resolve()
    irc_toml = irc_dir.joinpath("irc.toml").resolve()
    with irc_toml.open("rb") as f:
        irc_conf = tomllib.load(f)
    gvlogs = [log for log in irc_dir.glob("*.log") if log.is_file()]
    for log in gvlogs:
        system = log.name.split("_")[0]
        irc = IRC(system, irc_conf[system])
        irc.load_gvlog(log)
        distance_data = []
        for coord in irc.irc:
            r1 = distance(coord, *irc_conf[system]["r1"])
            r2 = distance(coord, *irc_conf[system]["r2"])
            r3 = distance(coord, *irc_conf[system]["r3"])
            distance_data.append((r1, r2, r3))
        header = ["R_(2+2)", "R_(4+2)", "R_im"]
        irc.gen_distance_data(distance_data, header, log.with_suffix(".dist.dat"))
        irc.gen_distance_position_data(irc.ts, header, log.with_suffix(".ts-pos.dat"))
        irc.gen_distance_position_data(irc.prod, header, log.with_suffix(".prod-pos.dat"))
        irc.gen_distance_position_data(irc.reac, header, log.with_suffix(".reac-pos.dat"))

        for key, value in irc.ts.items():
            print(f"{key:>4}{value[0]:>12.6f}{value[1]:>12.6f}{value[2]:>12.6f}")
        print("-" * 60)
        for key, value in irc.prod.items():
            print(f"{key:>4}{value[0]:>12.6f}{value[1]:>12.6f}{value[2]:>12.6f}")
        print("-" * 60)
        for key, value in irc.reac.items():
            print(f"{key:>4}{value[0]:>12.6f}{value[1]:>12.6f}{value[2]:>12.6f}")


if __name__ == "__main__":
    main()
