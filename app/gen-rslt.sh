#!/usr/bin/env bash

cwd=$(pwd)
exe="gen_time_bond.x"
dat_inp="time_bond.inp"
rslt_path="${cwd}/0_rslt"
nstep="$(sed -n "3p" "${dat_inp}")"

for ini in "${cwd}/"ini_*;
do
    for trj in "${ini}"/ini*;
    do
        if [[ -e "${trj}"/standard.out ]]; then
            last_line=$(tail -n 1 "${trj}/standard.out" | awk '{print $1}')
        else
            continue
        fi

        if [[ "${last_line}" == "${nstep}" && ! -e "${rslt_path}/rslt_${trj##*/}.dat" ]]; then

            "${exe}" "${dat_inp}" "${trj}"/trj.xyz "${rslt_path}/rslt_${trj##*/}.dat"
        fi
    done
done
