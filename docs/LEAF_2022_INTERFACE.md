# 2022 Nissan Leaf: what you are actually connecting to

## The headline problem
The project is labelled 96 V. A 2022 Leaf pack is **not 96 V**. The 96 is the number of cells in series (96s):
- 40 kWh pack: 96s2p, 350 V nominal (ev-database.org; Nissan Leaf Wiki).
- 62 kWh (e+) pack: 96s3p (Nissan Leaf Wiki).
- Reported working range is roughly 360-400 V (industrialmonitordirect.com); a 96 x 3.0-4.2 V envelope is 288-403 V, which is what DESIGN_CALC.md uses.

A 96 V design wired to this pack would be overstressed by about 4x. Parts rated for 96 V (including the IRLZ44N, 55 V) would fail violently.

## The car already makes 14 V
- The onboard DC-DC steps ~360-400 V down to a regulated ~13.5 V float, ~14.5 V while bulk charging the 12 V battery.
- Reported rating ~1.7 kW / ~135 A, only active in READY mode (third-party source; confirm in the service manual).
- Wiring rule from the same source: do not hang external loads on the 12 V battery's negative post; the car measures current there with a Hall sensor and can set a fault.

So the easy way to get 14 V "from a Leaf" is to take it from the car's 12 V system, not to build a second converter.

## If you still want your own HV-to-14 V converter
- Treat the pack as a ~400 V lethal source. Leaf HV is behind sealed contactors; do not defeat interlocks or the BMS (LBC) to get at it.
- Realistic paths: (1) a bench supply (current-limited, <= 60 V) for all early testing; (2) a bench HV supply with an isolation transformer once the low-voltage version works; (3) a pack only on a proper HV bench, with someone trained, fusing, pre-charge and an E-stop.
- Use the 288-403 V profile in DESIGN_CALC.md for the real converter and the 82-110 V profile only for a scaled-down prototype.

## Sources
- https://industrialmonitordirect.com/blogs/knowledgebase/nissan-leaf-12v-recharge-dc-dc-specs-max-amperage-and-wiring
- https://ev-database.org/imp/car/1656/Nissan-Leaf
- https://nissanleaf.carhackingwiki.com/index.php/Lithium_Ion_Battery
- Nissan Leaf Owner's/Service Manual (ZE1): get the official copy for pack, DC-DC and HV interlock details; not pulled here (no network from the sandbox).
