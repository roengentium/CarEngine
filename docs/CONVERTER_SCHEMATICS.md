# Converter schematics + PCBs (rev B)

Folders `converter_96V/` and `converter_Leaf400V/` each contain: `.kicad_sch`, `.kicad_pcb`, `.kicad_pro`, `fp-lib-table`, `CarEngineGen.pretty/` (footprints), netlist, BOM, and `*_placement.png`.
Open the `.kicad_pcb` or `.kicad_sch` from inside its own folder so `${KIPRJMOD}` finds the footprint library.
Regenerate: copy your `CarEngine.kicad_pcb` next to the script (used as the KiCad-10 file header) and run `python3 tools/gen_converter.py <output_dir>`.

## What changed since rev A
- Hardware over-current protection: LM393 comparator (U8) trips at ~1.8 V on ISENSE (~45 A); the fault pulls EN_G low through D5, Q8 turns off, DRV_DIS goes high and the drivers shut down. The MCU can also read OCP_N.
- Real UCC21520DW pinout (checked against TI SLUSCJ9): both VCCI pins, DT pin with RDT/CDT dead-time network, DIS bypass, bootstrap diode + series resistor.
- Real INA180A1 pinout, RECOM R-78E3.3-0.5 style 3.3 V regulator, ESP32 DevKitC header pin numbers.
- Input TVS (D6), sync-rect and bridge gate pull-downs, 6 PWM/SR pull-downs.
- Every symbol now has a real footprint (project-local library), and the PCB references the same symbols by UUID.

## PCB status (honest)
- Placed, not routed. 88/89 footprints on the board with nets assigned, outline, 4 mounting holes, barrier marking, and region outlines on Dwgs.User. Placement check: no courtyard overlaps, everything inside the board.
- Board size: 96 V 170x126 mm, Leaf 200x140 mm, 2 layers. Primary left, secondary right, barrier in the middle; T1, U2/U3 (UCC21520), U6 (bias module), CY1 (Y-cap) straddle it by design.
- To do in KiCad: draw B.Cu zones (PGND on the primary half, SGND on the secondary half), set net classes (wide tracks for VBUS, SW*, SEC*, VOUT*; clearance rules for the HV nets), route, run DRC. 36 A nets (SEC_CT, VOUT_RAW, VOUT, SGND) need heavy copper or bus bars, not normal traces.
- Primary<->secondary spacing: bare regions are 4 mm (96 V) / 10 mm (Leaf) apart. Package-limited crossings: UCC21520DW pads 7.3 mm apart (package creepage spec is 8 mm: verify), bias module and Y-cap as listed in the check output. The Leaf board needs a proper creepage/clearance review for your applicable standard before any HV test.
- Placement is a functional first pass (gate drive near drivers, sync-rect near T1); tighten the switching loops during layout.

## Placeholders you must resolve
- T1 (custom transformer), L1, Lr, film caps, F1: footprints are generic pad patterns.
- U6 isolated bias module: pad order is a placeholder; match the module you pick.
- ESP32 footprint assumes a 38-pin DevKitC-style board with 25.4 mm row spacing; check yours.
- NC_CMP2 (second comparator output) is intentionally unconnected: expect an ERC note.
- Nothing here has been opened in KiCad, ERC'd, DRC'd or simulated. The `.kicad_pro` is minimal: if it misbehaves, delete it and let KiCad create one.
