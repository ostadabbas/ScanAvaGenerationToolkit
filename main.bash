#!/bin/bash

bldLs=(
#'shuangjun_180522_1602_niket.blend'
#'shuangjun_180522_1628_jacket_good.blend'
#'shuangjun_180521_1516.blend'
#'shuangjun_180521_1531.blend'
#'shuangjun_180521_1548.blend'
#'shuangjun_180521_1600.blend'
#'shuangjun_180521_1658_grayt.blend'
#'shuangjun_180522_1542.blend'
#'shuangjun_whiteHood_180502_1536.blend'
#'shuangjun_diskShirt_180403_1748.blend'
'shuangjun_rainCoat_180403_1734.blend'
#'amir_18_3_29.blend'
#'behnaz_scan.blend'
#'naveen_180403_1612.blend'
#'naveen_180403_1635.blend'
#'sarah_171201_1045.blend'
#'sarah_180423_1211.blend'
#'sarah_180423_1220.blend'
#'sarah_180423_1317.blend'
#'shuangjun_180403_1734.blend'
#'shuangjun_180403_1748.blend'
#'shuangjun_180502_1536.blend'
#'william_180502_1449.blend'
#'william_180502_1509.blend'
#'william_180503_1704.blend'
#'yu_170723_1000.blend'
)

for bldNm in "${bldLs[@]}"
do
echo working on ${bldNm}
sbatch execute.bash $bldNm
echo work finished on ${bldNm}
done
echo job done!

