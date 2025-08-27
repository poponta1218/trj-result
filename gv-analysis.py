from pathlib import Path
from pprint import pprint

import numpy as np


def gv2irc(gvlog: Path) -> tuple[list[dict], list[dict]]:
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
    return irc_forward, irc_backward


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
    }
    return atomic_symbols.get(atomic_num, "X")


def main():
    irc_dir = Path("data/irc").resolve()
    gvlogs = [log for log in irc_dir.glob("*.log") if log.is_file()]
    for log in gvlogs:
        if log.name == "C=CC_ts1_42-gv.log":
            irc_forward, irc_backward = gv2irc(log)
            ts1 = irc_forward[0]
            prod1 = irc_forward[-1]
            reac = irc_backward[-1]
            for key in ts1.keys():
                print(f"{key:>4} {ts1[key][0]:>12.6f} {ts1[key][1]:>12.6f} {ts1[key][2]:>12.6f}")
            print("-" * 40)
            for key in reac.keys():
                print(f"{key:>4} {reac[key][0]:>12.6f} {reac[key][1]:>12.6f} {reac[key][2]:>12.6f}")
            print("-" * 40)
            for key in prod1.keys():
                print(f"{key:>4} {prod1[key][0]:>12.6f} {prod1[key][1]:>12.6f} {prod1[key][2]:>12.6f}")


if __name__ == "__main__":
    main()
