#!/bin/bash
# Session 10222: the burn restatement for each grid, one at a time
PY=/c/Users/lossa/Documents/erw/.venv/Scripts/python.exe
W=C:/Users/lossa/Documents/erw/warehouse/raw/eia930_emissions/20261004T021545Z
D=/c/Users/lossa/Documents/erw-c710-c/runs/c10222
export ERW_SPEND_CAP_USD=0
$PY $D/burn.py nyiso NYIS America/New_York 0.05 $W/20261004T021728.227265Z_00010_NYIS.xlsx $D/burn_nyiso.csv
$PY $D/burn.py ercot ERCO America/Chicago 0.05 $W/20261004T021615.318504Z_00004_ERCO.xlsx $D/burn_ercot.csv
$PY $D/burn.py isone ISNE America/New_York 0.05 $W/20261004T021636.602873Z_00006_ISNE.xlsx $D/burn_isone.csv
$PY $D/burn.py spp SWPP America/Chicago 0.05 $W/20261004T021821.443138Z_00014_SWPP.xlsx $D/burn_spp.csv
$PY $D/burn.py miso MISO America/Chicago 0.05 $W/20261004T021704.171793Z_00008_MISO.xlsx $D/burn_miso.csv
$PY $D/burn.py pjm PJM America/New_York 0.15 $W/20261004T021753.302176Z_00012_PJM.xlsx $D/burn_pjm.csv
$PY $D/burn.py caiso CISO America/Los_Angeles 0.05 $W/20261004T021550.248664Z_00002_CISO.xlsx $D/burn_caiso.csv
echo done
