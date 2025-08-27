from pathlib import Path

import numpy as np
import polars as pl
from matplotlib import pyplot as plt


class IRC:
    pass


class Trajectory:
    pass


def main():
    data_dir = Path("data/judge").resolve()
    systems = [sys for sys in data_dir.glob("*") if sys.is_dir()]
    img_dir = Path("data/img")
    img_dir.mkdir(parents=True, exist_ok=True)
    for sys in systems:
        fig, axes = plt.subplots(ncols=4, figsize=(16, 5))
        fig.tight_layout()
        for ax in axes:
            ax.set_box_aspect(1)
        for dist in sys.glob("*.dat"):
            df = pl.from_numpy(np.loadtxt(dist, skiprows=1), schema=["time", "r1", "r2", "r3"])
            axes[0].plot(df["time"], df["r1"], lw=0.5)
            axes[0].set_xlabel("Time (fs)", fontsize=18)
            axes[0].set_ylabel(r"$R_{\text{2+2}}$ ($\mathrm{\AA}$)", fontsize=18)
            axes[0].set_xlim(0, 300)
            axes[0].set_ylim(1, 6)
            axes[1].plot(df["time"], df["r2"], lw=0.5)
            axes[1].set_xlabel("Time (fs)", fontsize=18)
            axes[1].set_ylabel(r"$R_{\text{4+2}}$ ($\mathrm{\AA}$)", fontsize=18)
            axes[1].set_xlim(0, 300)
            axes[1].set_ylim(1, 6)
            axes[2].plot(df["time"], df["r3"], lw=0.5)
            axes[2].set_xlabel("Time (fs)", fontsize=18)
            axes[2].set_ylabel(r"$R_{\text{im}}$ ($\mathrm{\AA}$)", fontsize=18)
            axes[2].set_xlim(0, 300)
            axes[2].set_ylim(1, 6)
            axes[3].plot(df["r1"], df["r2"], lw=0.5)
            axes[3].set_xlabel(r"$R_{\text{2+2}}$ ($\mathrm{\AA}$)", fontsize=18)
            axes[3].set_ylabel(r"$R_{\text{4+2}}$ ($\mathrm{\AA}$)", fontsize=18)
            axes[3].set_xlim(1, 6)
            axes[3].set_ylim(1, 6)
        fig.savefig(f"{img_dir}/{sys.name}-distances.png", dpi=400)


if __name__ == "__main__":
    main()
