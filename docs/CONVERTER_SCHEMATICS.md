# Converter schematics (96 V prototype + Leaf-pack version)

Folders: `converter_96V/` and `converter_Leaf400V/` - each has the .kicad_sch, a minimal .kicad_pro, a netlist table and a BOM.
Regenerate both with `python3 tools/gen_schematics.py <output_dir>`.

## Architecture (same in both, only ratings/values differ)
Isolated full-bridge, centre-tapped secondary, synchronous rectification, 14 V / ~36 A / 500 W, 100 kHz.
- Primary: Q1-Q4 full bridge, Lr + blocking cap, T1.
- Secondary: Q5/Q6 sync rectifiers, L1 + output caps, 2 mohm shunt + current-sense amp.
- Controller (ESP32) on the 14 V side, drives the primary FETs through two isolated gate drivers; isolated 15 V bias (U6) feeds the primary side.
- Start-up needs 12 V on J2 (bench supply, or a vehicle 12 V battery via fused lead, mind the Leaf negative-post sensor rule); afterwards the output keeps the controller alive via D4.
- Default state is safe: drivers disabled by a pull-up on DRV_DIS, PWM/SR lines pulled low.

| | 96 V | Leaf pack |
|---|---|---|
| Input | 82-110 V | 288-403 V |
| Ratio | 4:1:1 | 16:1:1 |
| Primary FETs | 150 V, TO-220 | 650 V SiC/SJ, TO-247 |
| Bootstrap diode | 200 V fast | 600 V fast |
| Fuse / bleed / caps | 10 A, 100k, 47 uF 150 V | HV DC fuse, 2x100k, 4.7 uF 500 V film |

## What was checked and what was not
- Checked in Python: balanced s-expressions, every pin assigned a net, no single-pin nets, no duplicate refs (71 / 72 parts, 43 / 44 nets).
- NOT checked: KiCad was not available here, so neither file has been opened in KiCad, ERC'd or simulated. Expect to fix small things on first open. If KiCad complains about the .kicad_pro, delete it and open the .kicad_sch directly.
- Connectivity is by net label on a short wire at every pin; layout is a plain column grid, not a polished drawing.
- Symbols are generic boxes (`CarEngineGen:`). Pin numbers on the isolated driver, bias block, regulator and sense amp are placeholders: map them to the real datasheets and add footprints before PCB work.
- No PCB was made. HV creepage/clearance, isolation barrier layout and thermal design need a proper layout stage.

## Known open items
1. Hardware over-current latch into DRV_DIS (firmware-only protection is not enough).
2. Phase-shift/ZVS timing and Lr value need simulation (LTspice or similar) before power-up.
3. Sync-rectifier timing from the ESP32 is delicate: begin with SR1/SR2 held low (body diodes only, low power).
4. Pre-charge and contactors belong on the pack side; this board assumes a pre-charged, fused input.
5. Input OVP/UVLO and a secondary-side input-voltage monitor are not drawn.
