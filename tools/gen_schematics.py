#!/usr/bin/env python3
"""Generates KiCad 9 schematics + netlist/BOM/ERC-lite for the 14 V isolated DC-DC (96 V bench and Leaf-pack variants).
Connectivity is by net label on a wire stub at every pin."""
import uuid, math, csv, sys, os, json
def U(): return str(uuid.uuid4())
G = 2.54

# ---------- generic symbol library: name -> (left pins, right pins, hw, description, ref prefix) ----------
def two(desc, pre): return ([("1","1")],[("2","2")],2*G,desc,pre)
SYMS = {
 "R":    two("Resistor","R"), "C": two("Capacitor","C"), "L": two("Inductor","L"),
 "D":    ([("A","1")],[("K","2")],2*G,"Diode","D"),
 "FUSE": two("Fuse","F"),
 "TB2":  ([("1","1")],[("2","2")],3*G,"2-pin terminal","J"),
 "NMOS": ([("G","1")],[("D","2"),("S","3")],3*G,"N-channel MOSFET","Q"),
 "XFMR_CT": ([("P1","1"),("P2","2")],[("S1","3"),("CT","4"),("S2","5")],4*G,"Transformer, centre-tapped secondary","T"),
 "ISO_DRV_DUAL": ([("INA","1"),("INB","2"),("VCCI","3"),("GNDI","4"),("DIS","5")],
                  [("VDDA","6"),("OUTA","7"),("VSSA","8"),("VDDB","9"),("OUTB","10"),("VSSB","11")],5*G,
                  "Isolated dual-channel gate driver (UCC21520 class). PIN NUMBERS ARE PLACEHOLDERS - map to datasheet","U"),
 "UCC27524": ([("ENA","1"),("INA","2"),("GND","3"),("INB","4")],[("ENB","8"),("OUTA","7"),("VDD","6"),("OUTB","5")],4*G,"Dual low-side driver","U"),
 "ESP32": ([("3V3","1"),("GND","2"),("IO25_PWM_AH","3"),("IO26_PWM_AL","4"),("IO27_PWM_BH","5"),("IO14_PWM_BL","6")],
           [("IO32_SR1","7"),("IO33_SR2","8"),("IO34_VSENSE","9"),("IO35_ISENSE","10"),("IO36_TSENSE","11"),("IO13_DRV_DIS","12")],5*G,"ESP32 dev module (functional pins)","U"),
 "BUCK": ([("VIN","1"),("GND","2")],[("VOUT","3")],4*G,"Buck regulator block (e.g. AP63203 class)","U"),
 "ISO_DCDC": ([("VIN","1"),("GND_IN","2")],[("VO+","3"),("VO-","4")],4*G,"Isolated DC-DC bias block","U"),
 "INA180": ([("IN+","1"),("IN-","2"),("GND","3")],[("OUT","4"),("VS","5")],4*G,"Current-sense amp block (INA180A1 class)","U"),
}
EO = '(effects (font (size 1.27 1.27)))'
def lib_symbol(name):
    L,R,hw,desc,pre = SYMS[name]
    h = max(len(L),len(R))
    s = f'\t\t(symbol "CarEngineGen:{name}"\n\t\t\t(exclude_from_sim no)\n\t\t\t(in_bom yes)\n\t\t\t(on_board yes)\n'
    s += f'\t\t\t(property "Reference" "{pre}" (at 0 {G*h+2.54:.2f} 0) {EO})\n'
    s += f'\t\t\t(property "Value" "{name}" (at 0 -5.08 0) {EO})\n'
    s += f'\t\t\t(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
    s += f'\t\t\t(property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
    s += f'\t\t\t(property "Description" "{desc}" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
    s += f'\t\t\t(symbol "{name}_0_1"\n\t\t\t\t(rectangle (start {-hw:.2f} {-G:.2f}) (end {hw:.2f} {G*h:.2f}) (stroke (width 0.254) (type default)) (fill (type background)))\n\t\t\t)\n'
    s += f'\t\t\t(symbol "{name}_1_1"\n'
    for i,(pn,num) in enumerate(L):
        s += f'\t\t\t\t(pin passive line (at {-(hw+G):.2f} {G*(h-1-i):.2f} 0) (length 2.54) (name "{pn}" (effects (font (size 1.0 1.0)))) (number "{num}" (effects (font (size 1.0 1.0)))))\n'
    for i,(pn,num) in enumerate(R):
        s += f'\t\t\t\t(pin passive line (at {(hw+G):.2f} {G*(h-1-i):.2f} 180) (length 2.54) (name "{pn}" (effects (font (size 1.0 1.0)))) (number "{num}" (effects (font (size 1.0 1.0)))))\n'
    s += '\t\t\t)\n\t\t\t(embedded_fonts no)\n\t\t)\n'
    return s

def build(cfg):
    comps = []   # dict(ref,sym,value,fp,col,nets{pinname:net})
    def add(ref,sym,value,col,nets,fp="",note=""):
        comps.append(dict(ref=ref,sym=sym,value=value,col=col,nets=nets,fp=fp,note=note))
    R0805,C0805="Resistor_SMD:R_0805_2012Metric","Capacitor_SMD:C_0805_2012Metric"
    # ---- col 0 input
    add("J1","TB2","VIN "+cfg["vin_txt"],0,{"1":"VBUS_RAW","2":"PGND"},"TerminalBlock:TerminalBlock_bornier-2_P5.08mm")
    add("F1","FUSE",cfg["fuse"],0,{"1":"VBUS_RAW","2":"VBUS"})
    add("C1","C",cfg["cin"],0,{"1":"VBUS","2":"PGND"}); add("C2","C",cfg["cin"],0,{"1":"VBUS","2":"PGND"})
    if cfg["hv"]:
        add("RBL1","R",cfg["rbleed"],0,{"1":"VBUS","2":"BLEED_MID"}); add("RBL2","R",cfg["rbleed"],0,{"1":"BLEED_MID","2":"PGND"})
    else:
        add("RBL1","R",cfg["rbleed"],0,{"1":"VBUS","2":"PGND"})
    add("CY1","C","2.2nF Y1 safety cap (PGND-SGND)",0,{"1":"PGND","2":"SGND"})
    # ---- col 1 bridge
    for q,(g,d,s) in {"Q1":("GA_H","VBUS","SWA"),"Q2":("GA_L","SWA","PGND"),"Q3":("GB_H","VBUS","SWB"),"Q4":("GB_L","SWB","PGND")}.items():
        add(q,"NMOS",cfg["qpri"],1,{"G":g,"D":d,"S":s},cfg["qfp"])
    for i,(drv,gate,src) in enumerate([("HO_A","GA_H","SWA"),("LO_A","GA_L","PGND"),("HO_B","GB_H","SWB"),("LO_B","GB_L","PGND")],1):
        add(f"RG{i}","R","4.7R",1,{"1":drv,"2":gate},R0805)
        add(f"RGS{i}","R","10k",1,{"1":gate,"2":src},R0805)
    # ---- col 2 drivers
    for leg,(ina,inb) in {"A":("PWM_AH","PWM_AL"),"B":("PWM_BH","PWM_BL")}.items():
        sw="SW"+leg; u="U2" if leg=="A" else "U3"
        add(u,"ISO_DRV_DUAL",cfg["drv"],2,{"INA":ina,"INB":inb,"VCCI":"V3V3","GNDI":"SGND","DIS":"DRV_DIS",
            "VDDA":"VBOOT_"+leg,"OUTA":"HO_"+leg,"VSSA":sw,"VDDB":"VPRI_15V","OUTB":"LO_"+leg,"VSSB":"PGND"},"Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm")
        add("DB"+("1" if leg=="A" else "2"),"D",cfg["dboot"],2,{"A":"VPRI_15V","K":"VBOOT_"+leg})
        add("CB"+("1" if leg=="A" else "2"),"C","1uF",2,{"1":"VBOOT_"+leg,"2":sw},C0805)
        add("CD"+("1" if leg=="A" else "2"),"C","1uF",2,{"1":"VPRI_15V","2":"PGND"},C0805)
        add("CV"+("1" if leg=="A" else "2"),"C","100nF",2,{"1":"V3V3","2":"SGND"},C0805)
    # ---- col 3 resonant + transformer + sync rect
    add("LR1","L",cfg["lr"],3,{"1":"SWA","2":"PRI_L"})
    add("CBLK1","C",cfg["cblk"],3,{"1":"PRI_L","2":"PRI_A"})
    add("T1","XFMR_CT",cfg["xfmr"],3,{"P1":"PRI_A","P2":"SWB","S1":"SEC1","CT":"SEC_CT","S2":"SEC2"})
    for i,(sec,gate) in enumerate([("SEC1","GSR1"),("SEC2","GSR2")],5):
        add(f"Q{i}","NMOS",cfg["qsec"],3,{"G":gate,"D":sec,"S":"SGND"},"Package_TO_SOT_THT:TO-220-3_Vertical")
    for i,sec in enumerate(["SEC1","SEC2"],1):
        add(f"RSN{i}","R","10R 1W",3,{"1":sec,"2":f"SNUB{i}"}); add(f"CSN{i}","C","1nF 100V",3,{"1":f"SNUB{i}","2":"SGND"})
    # ---- col 4 output
    add("L1","L",cfg["lo"],4,{"1":"SEC_CT","2":"VOUT_RAW"})
    for i in range(1,4): add(f"COUT{i}","C","100uF 25V polymer",4,{"1":"VOUT_RAW","2":"SGND"})
    add("RSH1","R","2mR 3W shunt",4,{"1":"VOUT_RAW","2":"VOUT"})
    add("COUT4","C","100uF 25V polymer",4,{"1":"VOUT","2":"SGND"})
    add("U7","INA180","INA180A1 (20 V/V)",4,{"IN+":"VOUT_RAW","IN-":"VOUT","GND":"SGND","OUT":"ISENSE","VS":"V3V3"})
    add("CIS1","C","100nF",4,{"1":"V3V3","2":"SGND"},C0805)
    add("RG5","R","4.7R",4,{"1":"OUT_SR1","2":"GSR1"},R0805); add("RG6","R","4.7R",4,{"1":"OUT_SR2","2":"GSR2"},R0805)
    add("J3","TB2","VOUT 14 V / 36 A (heavy-gauge)",4,{"1":"VOUT","2":"SGND"})
    # ---- col 5 controller
    add("U1","ESP32","ESP32 dev module (bench controller)",5,{"3V3":"V3V3","GND":"SGND","IO25_PWM_AH":"PWM_AH","IO26_PWM_AL":"PWM_AL",
        "IO27_PWM_BH":"PWM_BH","IO14_PWM_BL":"PWM_BL","IO32_SR1":"SR1","IO33_SR2":"SR2","IO34_VSENSE":"VSENSE","IO35_ISENSE":"ISENSE",
        "IO36_TSENSE":"TSENSE","IO13_DRV_DIS":"DRV_DIS"})
    for i,n in enumerate(["PWM_AH","PWM_AL","PWM_BH","PWM_BL","SR1","SR2"],1):
        add(f"RPD{i}","R","10k pulldown",5,{"1":n,"2":"SGND"},R0805)
    add("RDIS1","R","10k pullup (default = drivers disabled)",5,{"1":"V3V3","2":"DRV_DIS"},R0805)
    add("RFB1","R","47k",5,{"1":"VOUT","2":"VSENSE"},R0805); add("RFB2","R","10k",5,{"1":"VSENSE","2":"SGND"},R0805)
    add("CFB1","C","100nF",5,{"1":"VSENSE","2":"SGND"},C0805)
    add("RNTC1","R","10k NTC (on heatsink)",5,{"1":"V3V3","2":"TSENSE"}); add("RT2","R","10k",5,{"1":"TSENSE","2":"SGND"},R0805)
    # ---- col 6 aux/bias/SR driver
    add("J2","TB2","AUX 12 V in (start-up/bench)",6,{"1":"VAUX","2":"SGND"},"TerminalBlock:TerminalBlock_bornier-2_P5.08mm")
    add("D3","D","Schottky 40V 3A (aux OR-ing)",6,{"A":"VAUX","K":"VCTRL"}); add("D4","D","Schottky 40V 3A (output OR-ing)",6,{"A":"VOUT","K":"VCTRL"})
    add("U4","UCC27524","UCC27524",6,{"ENA":"VCTRL","INA":"SR1","GND":"SGND","INB":"SR2","ENB":"VCTRL","OUTA":"OUT_SR1","VDD":"VCTRL","OUTB":"OUT_SR2"},"Package_SO:SOIC-8_3.9x4.9mm_P1.27mm")
    add("CVC1","C","1uF",6,{"1":"VCTRL","2":"SGND"},C0805); add("CVC2","C","10uF 25V",6,{"1":"VCTRL","2":"SGND"},C0805)
    add("U5","BUCK","14V->3.3V buck (e.g. AP63203)",6,{"VIN":"VCTRL","GND":"SGND","VOUT":"V3V3"})
    add("CIN5","C","10uF 25V",6,{"1":"VCTRL","2":"SGND"},C0805); add("COUT5","C","22uF 10V",6,{"1":"V3V3","2":"SGND"},C0805)
    add("U6","ISO_DCDC","Isolated 14V->15V, >=1W, "+cfg["iso"],6,{"VIN":"VCTRL","GND_IN":"SGND","VO+":"VPRI_15V","VO-":"PGND"})
    return comps

CFG96 = dict(name="CarEngine_96V_14V", title="96 V to 14 V isolated DC-DC (bench/prototype profile)", hv=False, vin_txt="82-110 V DC",
  fuse="10 A DC fuse", cin="47uF 150V", rbleed="100k 2W", qpri="150V N-FET, <=15 mohm", qfp="Package_TO_SOT_THT:TO-220-3_Vertical",
  drv="UCC21520-class, >=1.5kV iso", dboot="ES1D 200V fast", lr="~1-2 uH (tune by sim)", cblk="1uF 250V film", xfmr="Np:Ns:Ns = 4:1:1, 600 W / 100 kHz",
  qsec="100V N-FET, <=5 mohm", lo="~3 uH, Isat >= 46 A", iso="1.5 kV", dc="2024")
CFGHV = dict(name="CarEngine_Leaf400V_14V", title="Leaf-pack (96S, 288-403 V) to 14 V isolated DC-DC", hv=True, vin_txt="288-403 V DC (96S pack)",
  fuse="HV DC-rated fuse, ~5 A", cin="4.7uF 500V film", rbleed="100k 3W (>=400V rated) x2 in series", qpri="650V SiC/SJ N-FET, <=60 mohm", qfp="Package_TO_SOT_THT:TO-247-3_Vertical",
  drv="UCC21520-class, reinforced iso", dboot="ES1J 600V fast", lr="~10 uH (tune by sim)", cblk="1uF 630V film", xfmr="Np:Ns:Ns = 16:1:1, 600 W / 100 kHz, reinforced isolation",
  qsec="100V N-FET, <=5 mohm", lo="~3 uH, Isat >= 46 A", iso="reinforced, >=3 kV", dc="2024")

def emit(cfg, outdir):
    comps = build(cfg)
    NAME=cfg["name"]; ROOT=U()
    # layout
    COLX=[40+ i*78 for i in range(7)]; ytop=45
    ycur=[ytop]*7
    for c in comps:
        L,R,hw,desc,pre = SYMS[c["sym"]]; h=max(len(L),len(R))
        c["h"]=h; c["hw"]=hw; col=c["col"]
        c["x"]=round(COLX[col]/G)*G
        # reserve space: ref above body (h*G) , value below
        y = ycur[col] + G*h + 4*G
        c["y"]=round(y/G)*G
        ycur[col] = c["y"] + G + 4*G
    out=[f'(kicad_sch\n\t(version 20250114)\n\t(generator "eeschema")\n\t(generator_version "9.0")\n\t(uuid "{ROOT}")\n\t(paper "A1")\n',
         f'\t(title_block (title "{cfg["title"]}") (date "2026-11-18") (rev "A") (comment 1 "Generated netlist-by-label schematic. NOT ERC/DRC-checked in KiCad.") (comment 2 "Symbols are generic; pin numbers on IC blocks are placeholders."))\n',
         '\t(lib_symbols\n']
    for s in SYMS: out.append(lib_symbol(s))
    out.append('\t)\n')
    nets={}
    body=[]
    for c in comps:
        L,R,hw,desc,pre = SYMS[c["sym"]]; h=c["h"]; X,Y=c["x"],c["y"]
        fp = c["fp"]
        body.append(f'\t(symbol\n\t\t(lib_id "CarEngineGen:{c["sym"]}")\n\t\t(at {X:.2f} {Y:.2f} 0)\n\t\t(unit 1)\n\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp no)\n\t\t(uuid "{U()}")\n'
          f'\t\t(property "Reference" "{c["ref"]}" (at {X:.2f} {Y-G*h-1.27:.2f} 0) {EO})\n'
          f'\t\t(property "Value" "{c["value"]}" (at {X:.2f} {Y+G+1.27:.2f} 0) {EO})\n'
          f'\t\t(property "Footprint" "{fp}" (at {X:.2f} {Y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
          f'\t\t(property "Datasheet" "" (at {X:.2f} {Y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
          f'\t\t(property "Description" "{desc}" (at {X:.2f} {Y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))\n')
        allp=[(n,num,"L",i) for i,(n,num) in enumerate(L)]+[(n,num,"R",i) for i,(n,num) in enumerate(R)]
        for pn,num,side,i in allp:
            body.append(f'\t\t(pin "{num}" (uuid "{U()}"))\n')
            net=c["nets"].get(pn)
            assert net, (c["ref"],pn)
            py=Y-G*(h-1-i)
            if side=="L": ex=X-(hw+G); lx=ex-G; ang=180; just="right bottom"
            else:         ex=X+(hw+G); lx=ex+G; ang=0;   just="left bottom"
            body.append(None)  # placeholder to keep order
            body.pop()
            c.setdefault("_wires",[]).append((ex,py,lx,ang,just,net))
            nets.setdefault(net,[]).append((c["ref"],pn,num))
        body.append(f'\t\t(instances (project "{NAME}" (path "/{ROOT}" (reference "{c["ref"]}") (unit 1))))\n\t)\n')
    for c in comps:
        for ex,py,lx,ang,just,net in c["_wires"]:
            body.append(f'\t(wire (pts (xy {ex:.2f} {py:.2f}) (xy {lx:.2f} {py:.2f})) (stroke (width 0) (type default)) (uuid "{U()}"))\n')
            body.append(f'\t(label "{net}" (at {lx:.2f} {py:.2f} {ang}) (effects (font (size 1.27 1.27)) (justify {just})) (uuid "{U()}"))\n')
    heads=["1. INPUT / BULK","2. FULL-BRIDGE + GATE R","3. ISOLATED DRIVERS","4. RESONANT, XFMR, SYNC RECT","5. OUTPUT FILTER + SENSE","6. CONTROLLER (secondary side)","7. AUX, BIAS, SR DRIVER"]
    for i,hd in enumerate(heads):
        body.append(f'\t(text "{hd}" (exclude_from_sim no) (at {COLX[i]-12:.2f} 25 0) (effects (font (size 2.54 2.54) bold) (justify left)) (uuid "{U()}"))\n')
    warn = ("HV WARNING: 288-403 V DC is lethal. Bench-test only on a current-limited supply behind an isolation transformer. "
            "Do not defeat Leaf contactors/interlocks/BMS." if cfg["hv"] else
            "Prototype profile: 82-110 V DC. Keep first tests <=60 V, current-limited. Same architecture as the Leaf (HV) version.")
    notes=[warn,
      "Controller lives on the 14 V (secondary) side; primary FETs driven through isolated drivers; bias for primary side from isolated DC-DC U6.",
      "Start-up: needs 12 V on J2 (bench supply or vehicle 12 V battery) to boot the ESP32; U6/U4/U5 then run from VCTRL, D4 takes over from the output.",
      "Open items: hardware over-current latch to DRV_DIS, phase-shift/ZVS tuning (LR1), sync-rect timing, HV creepage/clearance, thermal. Generic symbols: map pins to datasheets."]
    for i,n in enumerate(notes):
        body.append(f'\t(text "{n}" (exclude_from_sim no) (at 40 {10+i*4} 0) (effects (font (size 1.8 1.8)) (justify left)) (uuid "{U()}"))\n')
    out += body
    out.append('\t(sheet_instances (path "/" (page "1")))\n\t(embedded_fonts no)\n)\n')
    os.makedirs(outdir,exist_ok=True)
    open(f"{outdir}/{NAME}.kicad_sch","w").write("".join(out))
    json.dump({"meta":{"filename":NAME+".kicad_pro","version":1}},open(f"{outdir}/{NAME}.kicad_pro","w"),indent=2)
    # netlist md, BOM, ERC-lite
    with open(f"{outdir}/{NAME}_netlist.md","w") as f:
        f.write(f"# Netlist: {cfg['title']}\n\n| Net | Pins |\n|---|---|\n")
        for n in sorted(nets): f.write(f"| {n} | {', '.join(f'{r}.{p}' for r,p,_ in nets[n])} |\n")
    with open(f"{outdir}/{NAME}_BOM.csv","w",newline="") as f:
        w=csv.writer(f); w.writerow(["Ref","Symbol","Value","Footprint"])
        for c in sorted(comps,key=lambda c:(c["ref"][0],int("".join(ch for ch in c["ref"] if ch.isdigit()) or 0))): w.writerow([c["ref"],c["sym"],c["value"],c["fp"]])
    issues=[]
    for n,p in nets.items():
        if len(p)<2: issues.append(f"single-pin net: {n} {p}")
    refs=[c["ref"] for c in comps]
    if len(refs)!=len(set(refs)): issues.append("duplicate refs")
    # every pin of every comp assigned
    return comps,nets,issues

if __name__=="__main__":
    base=sys.argv[1]
    for cfg,d in [(CFG96,"converter_96V"),(CFGHV,"converter_Leaf400V")]:
        comps,nets,issues=emit(cfg,f"{base}/{d}")
        print(cfg["name"],len(comps),"parts",len(nets),"nets","ISSUES:",issues or "none")
