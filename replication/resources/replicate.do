* ERW, the natural resource map (/map?tab=resources), layer "Tight oil and shale gas plays": its five headline figures,
* rebuilt from the publisher's own file.

* Method: docs/methods/resources.md, "Tight oil and shale gas plays" and "Replication and cross-check (session 8603)".
* Session 8603, chain 504, 19 November 2026.

* Before this file: download https://www.eia.gov/maps/map_data/TightOil_ShaleGas_Plays_Lower48_EIA.zip (U.S. Energy
* Information Administration, public domain; 323,424 bytes, sha256 c09b3bd2982754cfb63d12bbbfde6c6c5e8c02eee73e54d231a7c7de73f0541e)
* and unzip it into this folder. Run this file from this folder.

* This do-file has not been run: Stata is not installed on the machine that wrote it. "python replicate.py --zip <the zip>"
* reads the same table and reproduces the same figures (556 of 556 figures of the layer on 19 November 2026).

* Expected values, on EIA's file of December 2021:

*   1. plays: 50

*   2. smallest area, square miles: 184.825557581

*   3. mean area, square miles: 10,280.334960034

*   4. largest area, square miles: 59,054.2252868

*   5. the Marcellus (ID MARP01), square miles: 58,326.4 to one decimal

clear all

* The shapefile's table of attributes: one row a play, the area in the field Area_sq_mi.
import dbase using "ShalePlays_US_EIA_Dec2021.dbf", clear

count
display "1. plays: " r(N)

summarize Area_sq_mi, format
display "2. smallest area, square miles: " %15.9f r(min)
display "3. mean area, square miles: " %15.9f r(mean)
display "4. largest area, square miles: " %15.7f r(max)

list Shale_play Basin Area_sq_mi if ID == "MARP01", noobs
display "5. the Marcellus, square miles: see the line above"
