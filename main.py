import shutil
from pathlib import Path

import numpy as np
import polars as pl
from matplotlib import pyplot as plt


class IRC:
    def __init__(self) -> None:
        self.path: Path = Path()
        self.data: pl.DataFrame = pl.DataFrame()
        self.ts: tuple[float, ...] = ()
        self.product: tuple[float, ...] = ()
        self.reactant: tuple[float, ...] = ()

    def load_data(self, path: Path) -> pl.DataFrame:
        self.path = path
        self.data = pl.read_csv(path)
        return self.data

    def set_point(self, path: Path, point_name: str) -> None:
        if point_name == "ts":
            self.ts = pl.read_csv(path).row(0)

        if point_name == "product":
            self.product = pl.read_csv(path).row(0)

        if point_name == "reactant":
            self.reactant = pl.read_csv(path).row(0)


class Trajectory:
    def __init__(self):
        self.path: Path = Path()
        self.data: pl.DataFrame = pl.DataFrame()
        self.product: str = ""
        self.reaction_time: float = -1.0

    def load_data(self, path: Path) -> pl.DataFrame:
        self.path = path
        self.data = pl.from_numpy(np.loadtxt(path, skiprows=1), schema=["time", "r1", "r2", "r3"])
        return self.data

    def judge_product(self, judge_conf: dict[str, tuple[float, float]]) -> str | None:
        r1_min = judge_conf["r1"][0]
        r1_max = judge_conf["r1"][1]
        r2_min = judge_conf["r2"][0]
        r2_max = judge_conf["r2"][1]
        r3_min = judge_conf["r3"][0]
        r3_max = judge_conf["r3"][1]

        for row in self.data.iter_rows(named=True):
            if row["r3"] >= r3_max and row["r1"] >= r1_max and row["r2"] >= r2_max:
                self.product = "reactant"
                self.reaction_time = row["time"]
                break
            if row["r3"] <= r3_min:
                if row["r1"] <= r1_min and row["r2"] >= r2_max:
                    self.product = "prod_1"
                    self.reaction_time = row["time"]
                    break
                if row["r1"] >= r1_max and row["r2"] <= r2_min:
                    self.product = "prod_2"
                    self.reaction_time = row["time"]
                    break
            else:
                continue
        if self.product == "":
            self.product = "failed"

        return self.product


def print_stats(system: Path) -> None:
    prod_1 = len(list(system.joinpath("prod_1").glob("*.dat")))
    prod_2 = len(list(system.joinpath("prod_2").glob("*.dat")))
    reactant = len(list(system.joinpath("reactant").glob("*.dat")))
    failed = len(list(system.joinpath("failed").glob("*.dat")))

    prod_1_ratio = prod_1 / (prod_1 + prod_2) if (prod_1 + prod_2) > 0 else 0
    prod_2_ratio = prod_2 / (prod_1 + prod_2) if (prod_1 + prod_2) > 0 else 0
    print(f"Statistics for {system.name}:")
    print(f"    prod_1: {prod_1:>4} ({prod_1_ratio * 100:.1f}%)")
    print(f"    prod_2: {prod_2:>4} ({prod_2_ratio * 100:.1f}%)")
    print(f"  reactant: {reactant:>4}")
    print(f"    failed: {failed:>4}")


def main():
    data_dir = Path("data/judge").resolve()
    systems = [sys for sys in data_dir.glob("*") if sys.is_dir()]

    img_dir = Path("data/img").resolve()
    img_dir.mkdir(parents=True, exist_ok=True)

    irc_dir = Path("data/irc").resolve()

    judge_conf = {
        "r1": (1.7, 2.8),
        "r2": (1.7, 3.4),
        "r3": (1.7, 2.8),
    }
    plot_conf = {
        "prod_1": {"color": "red", "label": "(2+2) product", "zorder": 2},
        "prod_2": {"color": "blue", "label": "(4+2) product", "zorder": 3},
        "reactant": {"color": "green", "label": "Reactant", "zorder": 1},
    }
    for sys in systems:
        judge_dirs = [sys.joinpath(d) for d in ["prod_1", "prod_2", "reactant", "failed"]]
        if not all(d.exists() for d in judge_dirs):
            for d in judge_dirs:
                d.mkdir(parents=True, exist_ok=True)

        fig1, axes1 = plt.subplots(nrows=3, figsize=(5, 17))
        fig1.tight_layout()
        fig1.suptitle(f"{sys.name}", fontsize=20)
        for ax in axes1:
            ax.set_box_aspect(1)
            ax.minorticks_on()
            ax.tick_params(
                axis="both",
                which="major",
                direction="in",
                bottom=True,
                top=True,
                left=True,
                right=True,
                labelsize=16,
                size=10,
            )
            ax.tick_params(
                axis="both",
                which="minor",
                direction="in",
                bottom=True,
                top=True,
                left=True,
                right=True,
                labelsize=10,
                length=5,
            )
        axes1[0].set_xlabel("Time (fs)", fontsize=18)
        axes1[0].set_ylabel(r"$R_{\text{2+2}}$ ($\mathrm{\AA}$)", fontsize=18)
        axes1[0].set_xlim(0, 300)
        axes1[0].set_ylim(1, 6)
        axes1[1].set_xlabel("Time (fs)", fontsize=18)
        axes1[1].set_ylabel(r"$R_{\text{4+2}}$ ($\mathrm{\AA}$)", fontsize=18)
        axes1[1].set_xlim(0, 300)
        axes1[1].set_ylim(1, 6)
        axes1[2].set_xlabel("Time (fs)", fontsize=18)
        axes1[2].set_ylabel(r"$R_{\text{im}}$ ($\mathrm{\AA}$)", fontsize=18)
        axes1[2].set_xlim(0, 300)
        axes1[2].set_ylim(1, 6)

        fig2, axes2 = plt.subplots(ncols=1, figsize=(5, 6))
        fig2.tight_layout()
        axes2.set_title(f"{sys.name}", fontsize=20)
        axes2.set_box_aspect(1)
        axes2.minorticks_on()
        axes2.tick_params(
            axis="both",
            which="major",
            direction="in",
            bottom=True,
            top=True,
            left=True,
            right=True,
            labelsize=16,
            size=10,
        )
        axes2.tick_params(
            axis="both",
            which="minor",
            direction="in",
            bottom=True,
            top=True,
            left=True,
            right=True,
            labelsize=10,
            length=5,
        )
        axes2.set_ylabel(r"$R_{2}$ ($\mathrm{\AA}$)", fontsize=18)
        axes2.set_ylim(1, 6)
        axes2.set_xlabel(r"$R_{1}$ ($\mathrm{\AA}$)", fontsize=18)
        axes2.set_xlim(1, 6)

        for dat in sys.glob("*.dat"):
            trj = Trajectory()
            trj.load_data(dat)
            trj.judge_product(judge_conf)
            shutil.copy2(dat, sys.joinpath(trj.product, dat.name))

            axes1[0].plot(
                trj.data["time"],
                trj.data["r1"],
                lw=0.5,
                color=plot_conf[trj.product]["color"],
                zorder=plot_conf[trj.product]["zorder"],
            )
            axes1[1].plot(
                trj.data["time"],
                trj.data["r2"],
                lw=0.5,
                color=plot_conf[trj.product]["color"],
                zorder=plot_conf[trj.product]["zorder"],
            )
            axes1[2].plot(
                trj.data["time"],
                trj.data["r3"],
                lw=0.5,
                color=plot_conf[trj.product]["color"],
                zorder=plot_conf[trj.product]["zorder"],
            )
            axes2.plot(
                trj.data["r1"],
                trj.data["r2"],
                lw=0.5,
                color=plot_conf[trj.product]["color"],
                zorder=plot_conf[trj.product]["zorder"],
            )
        for dat in irc_dir.glob(f"{sys.name}_ts*.dist.dat"):
            irc = IRC()
            irc.load_data(dat)
            axes2.plot(irc.data["R_(2+2)"], irc.data["R_(4+2)"], lw=3, color="black", zorder=10)
            ts_path = dat.parent.joinpath(dat.name.replace("dist", "ts-pos"))
            prod_path = dat.parent.joinpath(dat.name.replace("dist", "prod-pos"))
            reac_path = dat.parent.joinpath(dat.name.replace("dist", "reac-pos"))
            irc.set_point(ts_path, "ts")
            irc.set_point(prod_path, "product")
            irc.set_point(reac_path, "reactant")
            axes2.scatter(irc.ts[0], irc.ts[1], s=100, marker="o", edgecolor="black", facecolor="white", zorder=20)
            axes2.scatter(
                irc.product[0],
                irc.product[1],
                s=100,
                marker="o",
                edgecolor="black",
                facecolor="white",
                zorder=20,
            )
            axes2.scatter(
                irc.reactant[0],
                irc.reactant[1],
                s=100,
                marker="o",
                edgecolor="black",
                facecolor="white",
                zorder=20,
            )
        fig1.savefig(f"{img_dir}/{sys.name}-distances.png", dpi=400, bbox_inches="tight")
        fig2.savefig(f"{img_dir}/{sys.name}-2d.png", dpi=400, bbox_inches="tight")

        print_stats(sys)


if __name__ == "__main__":
    main()
