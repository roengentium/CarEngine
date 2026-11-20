# Car Engine: documentation pack

Added alongside your existing KiCad files (nothing in the original schematics/PCBs was edited).

| File | What it is |
|---|---|
| LEAF_2022_INTERFACE.md | What a 2022 Nissan Leaf pack/12 V system actually provides, with sources |
| DESIGN_REVIEW.md | Issues spotted in the current project files |
| DESIGN_CALC.md | Sizing for 14 V out from the Leaf-pack range and from 96 V (generated) |
| BOM.csv | Candidate parts matching the sizing (verify before ordering) |
| DATASHEETS.md | Datasheet/reference links |
| TEST_PLAN.md | Staged bring-up plan, lowest voltage first |
| CONVERTER_SCHEMATICS.md | Notes on the two KiCad schematics + placed PCBs (`../converter_96V`, `../converter_Leaf400V`) |
| FIRMWARE_SPEC.md | Controller behaviour and safety sequence (spec only) |
| ../firmware/pins.h | Pin map matching the schematic |
| ../tools/dcdc_calc.py | Calculator that regenerates DESIGN_CALC.md; `gen_converter.py` + `fplib.py` rebuild both schematics, footprints and PCBs |

Project map: `CarEngine.*` is the main 96 V design (IR2101 half-bridges, six N-MOSFETs, ESP32, a 96V_TO_12V module).
`Cirkit Converter.*` / `circuit_image.png` is a transformer-based converter concept (UCC27524, IRLZ44N, 60CPQ150 rectifier, 9 V battery as stand-in source).
`3dprinter/` is an unrelated Pico + TMC2209 project and was left alone.
