# Printer controller (Pico + 4x TMC2209) - notes
Files: PrinterController.kicad_sch, PrinterController_routed.kicad_pcb (140x90 mm, 2 layers)
Parts: U1 Pico, U2-U5 TMC2209 (X,Y,Z,E), J3-J6 motors, C1-C4 100uF/35V, J1 24V in (AFTER an inline 5-10A fuse), J2 24V out to MOSFET module,
J7 -> MOSFET module IN1 (HEAT), IN2 (FAN), GND; J8 thermistor, J9-J11 endstops, R1 1k (UART TX), R2 4.7k + C5 100nF (thermistor).
Driver addresses (MS1/MS2): X=0, Y=1, Z=2, E=3. UART: TX via 1k and RX both on PDN_UART bus.
## You must do
1. GND is NOT routed: in KiCad add a filled zone on B.Cu (and F.Cu if you like), net GND, over the board, press B to fill. Then run DRC.
2. Check your TMC2209 module's pin order against the symbol (EN,MS1,MS2,PDN,CLK,PDIAG,STEP,DIR / VMOT,GND,2B,2A,1A,1B,VIO,GND). Modules differ.
3. Power traces are 0.6 mm (24V) - fine for logic and drivers (~1.5A each) but heater current goes through the MOSFET module wiring, not this board.
4. Do NOT connect Pico VSYS/VBUS; power the Pico from the Pi USB. Footprints are KiCad-library names: run Update PCB from Schematic if you want them linked.
5. Not opened in KiCad here: schematic/PCB are hand-generated text, expect small fixes.
