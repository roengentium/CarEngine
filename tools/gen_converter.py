#!/usr/bin/env python3
"""v2: schematic (KiCad) + footprint library + placed PCB (KiCad 10 syntax) for the 14 V isolated DC-DC, two variants."""
import uuid, os, sys, csv, json, re, math, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fplib
def U(): return str(uuid.uuid4())
G=2.54
EO='(effects (font (size 1.27 1.27)))'

def two(d,p): return ([("1","1")],[("2","2")],2*G,d,p)
SYMS={
 "R":two("Resistor","R"),"C":two("Capacitor","C"),"L":two("Inductor","L"),"FUSE":two("Fuse","F"),
 "D":([("A","1")],[("K","2")],2*G,"Diode","D"),
 "D_SOT23":([("A","1")],[("K","3")],2*G,"Small-signal diode SOT-23 (BAT54 class)","D"),
 "TB2":([("1","1")],[("2","2")],3*G,"2-pin terminal","J"),
 "NMOS":([("G","1")],[("D","2"),("S","3")],3*G,"N-MOSFET, pins G-D-S (verify part pinout)","Q"),
 "NMOS_SOT23":([("G","1")],[("D","3"),("S","2")],3*G,"N-MOSFET SOT-23 (2N7002: 1 G, 2 S, 3 D)","Q"),
 "XFMR_CT":([("P1","1"),("P2","2")],[("S1","3"),("CT","4"),("S2","5")],4*G,"Centre-tapped transformer","T"),
 "UCC21520":([("INA","1"),("INB","2"),("VCCI","3"),("VCCI_8","8"),("GND","4"),("DIS","5"),("DT","6")],
             [("VDDA","16"),("OUTA","15"),("VSSA","14"),("VDDB","11"),("OUTB","10"),("VSSB","9")],5*G,
             "UCC21520 DW16 dual isolated gate driver (pinout from TI datasheet SLUSCJ9)","U"),
 "UCC27524":([("ENA","1"),("INA","2"),("GND","3"),("INB","4")],[("ENB","8"),("OUTA","7"),("VDD","6"),("OUTB","5")],4*G,"UCC27524 dual low-side driver (SOIC-8)","U"),
 "ESP32":([("3V3","1"),("GND","14"),("IO25_PWM_AH","9"),("IO26_PWM_AL","10"),("IO27_PWM_BH","11"),("IO14_PWM_BL","12")],
          [("IO32_SR1","7"),("IO33_SR2","8"),("IO34_VSENSE","5"),("IO35_ISENSE","6"),("IO36_TSENSE","3"),("IO39_OCP_N","4"),("IO13_DRV_EN","15")],5*G,
          "ESP32 DevKitC-style 38-pin module; pad numbers = header position (left header 1-19)","U"),
 "R78":([("VIN","1"),("GND","2")],[("VOUT","3")],4*G,"RECOM R-78E3.3-0.5 class SIP-3 switching regulator (LM78xx pinout)","U"),
 "ISO_DCDC":([("VIN","1"),("GND_IN","2")],[("VO+","3"),("VO-","4")],4*G,"Isolated DC-DC bias module (placeholder pinout, match to chosen part)","U"),
 "INA180":([("IN+","3"),("IN-","4"),("GND","2")],[("OUT","1"),("VS","5")],4*G,"INA180A1 SOT-23-5 (pinout A: 1 OUT 2 GND 3 IN+ 4 IN- 5 VS)","U"),
 "LM393":([("IN1+","3"),("IN1-","2"),("IN2+","5"),("IN2-","6"),("GND","4")],[("OUT1","1"),("OUT2","7"),("VCC","8")],5*G,"LM393 dual open-collector comparator SOIC-8","U"),
}
def lib_symbol(name):
    L,R,hw,desc,pre=SYMS[name]; h=max(len(L),len(R))
    s=f'\t\t(symbol "CarEngineGen:{name}"\n\t\t\t(exclude_from_sim no)\n\t\t\t(in_bom yes)\n\t\t\t(on_board yes)\n'
    s+=f'\t\t\t(property "Reference" "{pre}" (at 0 {G*h+2.54:.2f} 0) {EO})\n\t\t\t(property "Value" "{name}" (at 0 -5.08 0) {EO})\n'
    for k in ("Footprint","Datasheet"): s+=f'\t\t\t(property "{k}" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
    s+=f'\t\t\t(property "Description" "{desc}" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
    s+=f'\t\t\t(symbol "{name}_0_1"\n\t\t\t\t(rectangle (start {-hw:.2f} {-G:.2f}) (end {hw:.2f} {G*h:.2f}) (stroke (width 0.254) (type default)) (fill (type background)))\n\t\t\t)\n\t\t\t(symbol "{name}_1_1"\n'
    for i,(pn,num) in enumerate(L): s+=f'\t\t\t\t(pin passive line (at {-(hw+G):.2f} {G*(h-1-i):.2f} 0) (length 2.54) (name "{pn}" (effects (font (size 1.0 1.0)))) (number "{num}" (effects (font (size 1.0 1.0)))))\n'
    for i,(pn,num) in enumerate(R): s+=f'\t\t\t\t(pin passive line (at {(hw+G):.2f} {G*(h-1-i):.2f} 180) (length 2.54) (name "{pn}" (effects (font (size 1.0 1.0)))) (number "{num}" (effects (font (size 1.0 1.0)))))\n'
    return s+'\t\t\t)\n\t\t\t(embedded_fonts no)\n\t\t)\n'

CFG96=dict(name="CarEngine_96V_14V",hv=False,title="96 V to 14 V isolated DC-DC (bench/prototype profile)",vin_txt="82-110 V DC",
  fuse="10 A DC fuse (5x20 holder)",cin="47uF 150V radial",rbleed="100k 2W",qpri="150V N-FET <=15 mohm (TO-220)",dboot="ES1D 200V fast",
  lr="~1-2 uH (tune by sim)",cblk="1uF 250V film",xfmr="Np:Ns:Ns = 4:1:1, 600 W / 100 kHz",tvs="TVS bidirectional, standoff >=110 V (clamp < 143 V: verify)",
  iso="1.5 kV",W=170,H=126,cx=85,gap=4.0,
  fixed=dict(T1=(85,68),U2=(85,15),U6=(85,33),CY1=(85,98),U3=(85,112)),
  fp=dict(J=("TB2_P5.08",5.08,2.6,1.4,11,8),F=("FUSE_P22.5",22.5,3.0,1.6,26,9),C=("CAPR_P5.0",5.0,2.4,1.1,11,11),RBL=("RAX_P12.5",12.5,2.0,1.0,15,6),
          CY=("YCAP_P7.5",7.5,2.0,1.0,11,6),Q=fplib.TO220,LR=("IND_P10",10,2.4,1.2,13,10),CBLK=("FILM_P10",10,2.4,1.2,12,7.5),
          iso_across=7.62,xf=(20,20,44,36)))
CFGHV=dict(name="CarEngine_Leaf400V_14V",hv=True,title="Leaf-pack (96S, 288-403 V) to 14 V isolated DC-DC",vin_txt="288-403 V DC (96S pack)",
  fuse="HV DC-rated fuse ~5 A",cin="4.7uF 500V film",rbleed="100k 3W (>=400V) x2 in series",qpri="650V SiC/SJ N-FET <=60 mohm (TO-247)",dboot="ES1J 600V fast",
  lr="~10 uH (tune by sim)",cblk="1uF 630V film",xfmr="Np:Ns:Ns = 16:1:1, 600 W / 100 kHz, reinforced isolation",tvs="TVS bidirectional, standoff >=420 V (clamp < 650 V: verify)",
  iso="reinforced >=3 kV",W=200,H=140,cx=100,gap=10.0,
  fixed=dict(T1=(100,74),U2=(100,15),U6=(100,36),CY1=(100,108),U3=(100,126)),
  fp=dict(J=("TB2_P5.08",5.08,2.6,1.4,11,8),F=("FUSE_P27.5",27.5,3.0,1.6,31,11),C=("FILM_P27.5",27.5,3.0,1.4,33,19),RBL=("RAX_P15",15,2.0,1.0,17,6),
          CY=("YCAP_P15",15,2.0,1.0,18,7),Q=fplib.TO247,LR=("IND_P12.5",12.5,2.4,1.2,15,12),CBLK=("FILM_P22.5",22.5,3.0,1.4,26,11),
          iso_across=12.7,xf=(26,26,56,42)))

def build(cfg):
    comps=[]
    def add(ref,sym,value,nets,fp,sec="P"): comps.append(dict(ref=ref,sym=sym,value=value,nets=nets,fp=fp,sec=sec,uuid=U()))
    f=cfg["fp"]; QF=f["Q"]
    def tht2(key): n,p,pad,dr,bw,bh=f[key]; return fplib.THT2(p,pad,dr,bw,bh,name=n)
    r=fplib.R0805()
    # ---- primary / input
    add("J1","TB2","VIN "+cfg["vin_txt"],{"1":"VBUS_RAW","2":"PGND"},tht2("J"))
    add("F1","FUSE",cfg["fuse"],{"1":"VBUS_RAW","2":"VBUS"},tht2("F"))
    add("D6","D",cfg["tvs"],{"A":"VBUS","K":"PGND"},fplib.SOD_SMC())
    add("C1","C",cfg["cin"],{"1":"VBUS","2":"PGND"},tht2("C")); add("C2","C",cfg["cin"],{"1":"VBUS","2":"PGND"},tht2("C"))
    if cfg["hv"]:
        add("RBL1","R",cfg["rbleed"],{"1":"VBUS","2":"BLEED_MID"},tht2("RBL")); add("RBL2","R",cfg["rbleed"],{"1":"BLEED_MID","2":"PGND"},tht2("RBL"))
    else: add("RBL1","R",cfg["rbleed"],{"1":"VBUS","2":"PGND"},tht2("RBL"))
    add("CY1","C","2.2nF Y1 safety cap (PGND-SGND)",{"1":"PGND","2":"SGND"},tht2("CY"),"X")
    for q,(g,d,s) in {"Q1":("GA_H","VBUS","SWA"),"Q2":("GA_L","SWA","PGND"),"Q3":("GB_H","VBUS","SWB"),"Q4":("GB_L","SWB","PGND")}.items():
        add(q,"NMOS",cfg["qpri"],{"G":g,"D":d,"S":s},QF(),"PA" if q in("Q1","Q2") else "PB")
    for i,(drv,gate,src) in enumerate([("HO_A","GA_H","SWA"),("LO_A","GA_L","PGND"),("HO_B","GB_H","SWB"),("LO_B","GB_L","PGND")],1):
        s="PA" if i<=2 else "PB"
        add(f"RG{i}","R","4.7R",{"1":drv,"2":gate},r,s); add(f"RGS{i}","R","10k",{"1":gate,"2":src},r,s)
    for leg,(ina,inb) in {"A":("PWM_AH","PWM_AL"),"B":("PWM_BH","PWM_BL")}.items():
        n="1" if leg=="A" else "2"; sw="SW"+leg; u="U2" if leg=="A" else "U3"; sp="PA" if leg=="A" else "PB"; ss="SA" if leg=="A" else "SB"
        add(u,"UCC21520","UCC21520DW (reinforced iso)",{"INA":ina,"INB":inb,"VCCI":"V3V3","VCCI_8":"V3V3","GND":"SGND","DIS":"DRV_DIS","DT":"DT_"+leg,
            "VDDA":"VBOOT_"+leg,"OUTA":"HO_"+leg,"VSSA":sw,"VDDB":"VPRI_15V","OUTB":"LO_"+leg,"VSSB":"PGND"},fplib.SOIC16W(rot180=True),"X")
        add("DB"+n,"D",cfg["dboot"],{"A":"VPRI_15V","K":"BOOT_K_"+leg},fplib.SOD_SMA(),sp)
        add("RBT"+n,"R","10R",{"1":"BOOT_K_"+leg,"2":"VBOOT_"+leg},r,sp)
        add("CB"+n,"C","1uF",{"1":"VBOOT_"+leg,"2":sw},r,sp); add("CD"+n,"C","1uF",{"1":"VPRI_15V","2":"PGND"},r,sp)
        add("CV"+n,"C","100nF",{"1":"V3V3","2":"SGND"},r,ss)
        add("RDT"+n,"R","20k (dead time ~ 10 ns/kohm, verify)",{"1":"DT_"+leg,"2":"SGND"},r,ss); add("CDT"+n,"C","2.2nF",{"1":"DT_"+leg,"2":"SGND"},r,ss)
    add("CDIS1","C","1nF",{"1":"DRV_DIS","2":"SGND"},r,"SA")
    add("LR1","L",cfg["lr"],{"1":"SWA","2":"PRI_L"},tht2("LR"),"PM"); add("CBLK1","C",cfg["cblk"],{"1":"PRI_L","2":"PRI_A"},tht2("CBLK"),"PM")
    px,sx,bw,bh=f["xf"]
    add("T1","XFMR_CT",cfg["xfmr"],{"P1":"PRI_A","P2":"SWB","S1":"SEC1","CT":"SEC_CT","S2":"SEC2"},fplib.XFMR(px,sx,bw,bh,name="XFMR_"+("HV" if cfg["hv"] else "LV")),"X")
    # ---- secondary
    for i,(sec,gate) in enumerate([("SEC1","GSR1"),("SEC2","GSR2")],5): add(f"Q{i}","NMOS","100V N-FET <=5 mohm (TO-220)",{"G":gate,"D":sec,"S":"SGND"},fplib.TO220(),"SM")
    for i,sec in enumerate(["SEC1","SEC2"],1):
        add(f"RSN{i}","R","10R 1W",{"1":sec,"2":f"SNUB{i}"},fplib.THT2(10,1.8,0.9,12,4.5,name="RPWR_P10"),"SM"); add(f"CSN{i}","C","1nF 100V",{"1":f"SNUB{i}","2":"SGND"},r,"SM")
    add("L1","L","~3 uH, Isat >= 46 A",{"1":"SEC_CT","2":"VOUT_RAW"},fplib.THT2(15,4.0,2.0,26,26,name="IND_PWR_P15"),"SM")
    for i in range(1,4): add(f"COUT{i}","C","100uF 25V polymer",{"1":"VOUT_RAW","2":"SGND"},fplib.THT2(3.5,1.8,0.9,9,9,name="CAPR_P3.5"),"SM")
    add("RSH1","R","2mR 3W shunt",{"1":"VOUT_RAW","2":"VOUT"},fplib.R2512(),"SM")
    add("COUT4","C","100uF 25V polymer",{"1":"VOUT","2":"SGND"},fplib.THT2(3.5,1.8,0.9,9,9,name="CAPR_P3.5"),"SM")
    add("U7","INA180","INA180A1 (20 V/V)",{"IN+":"VOUT_RAW","IN-":"VOUT","GND":"SGND","OUT":"ISENSE","VS":"V3V3"},fplib.SOT23_5(),"SM")
    add("CIS1","C","100nF",{"1":"V3V3","2":"SGND"},r,"SM")
    add("RG5","R","4.7R",{"1":"OUT_SR1","2":"GSR1"},r,"SM"); add("RG6","R","4.7R",{"1":"OUT_SR2","2":"GSR2"},r,"SM")
    add("J3","TB2","VOUT 14 V / 36 A",{"1":"VOUT","2":"SGND"},fplib.THT2(7.62,5.0,2.8,16,11,name="TB2_P7.62_PWR"),"SM")
    # ---- OCP latch + enable
    add("U8","LM393","LM393 (OCP comparator)",{"IN1+":"IREF","IN1-":"ISENSE","IN2+":"SGND","IN2-":"V3V3","GND":"SGND","OUT1":"OCP_N","OUT2":"NC_CMP2","VCC":"V3V3"},fplib.SOIC8(),"SA")
    add("RIREF1","R","8.2k",{"1":"V3V3","2":"IREF"},r,"SA"); add("RIREF2","R","10k",{"1":"IREF","2":"SGND"},r,"SA")
    add("CCMP1","C","100nF",{"1":"V3V3","2":"SGND"},r,"SA"); add("RFLT1","R","10k",{"1":"V3V3","2":"OCP_N"},r,"SA")
    add("D5","D_SOT23","BAT54 (OCP clamp on EN_G)",{"A":"EN_G","K":"OCP_N"},fplib.SOT23(),"SA")
    add("Q8","NMOS_SOT23","2N7002 (pulls DRV_DIS low when enabled)",{"G":"EN_G","D":"DRV_DIS","S":"SGND"},fplib.SOT23(),"SA")
    add("RGEN1","R","100k",{"1":"EN_G","2":"SGND"},r,"SA"); add("RGENS1","R","1k",{"1":"DRV_EN","2":"EN_G"},r,"SA")
    add("RDIS1","R","10k pullup (default = drivers disabled)",{"1":"V3V3","2":"DRV_DIS"},r,"SA")
    # ---- controller & aux
    add("U1","ESP32","ESP32 dev module (bench controller)",{"3V3":"V3V3","GND":"SGND","IO25_PWM_AH":"PWM_AH","IO26_PWM_AL":"PWM_AL","IO27_PWM_BH":"PWM_BH","IO14_PWM_BL":"PWM_BL",
        "IO32_SR1":"SR1","IO33_SR2":"SR2","IO34_VSENSE":"VSENSE","IO35_ISENSE":"ISENSE","IO36_TSENSE":"TSENSE","IO39_OCP_N":"OCP_N","IO13_DRV_EN":"DRV_EN"},fplib.ESP32DK(rot=True),"SB")
    for i,n in enumerate(["PWM_AH","PWM_AL","PWM_BH","PWM_BL","SR1","SR2"],1): add(f"RPD{i}","R","10k pulldown",{"1":n,"2":"SGND"},r,"SB")
    add("RFB1","R","47k",{"1":"VOUT","2":"VSENSE"},r,"SB"); add("RFB2","R","10k",{"1":"VSENSE","2":"SGND"},r,"SB"); add("CFB1","C","100nF",{"1":"VSENSE","2":"SGND"},r,"SB")
    add("RNTC1","R","10k NTC (on heatsink)",{"1":"V3V3","2":"TSENSE"},fplib.THT2(5.08,1.8,0.9,8,4,name="NTC_P5.08"),"SB"); add("RT2","R","10k",{"1":"TSENSE","2":"SGND"},r,"SB")
    add("J2","TB2","AUX 12 V in (start-up/bench)",{"1":"VAUX","2":"SGND"},fplib.THT2(5.08,2.6,1.4,11,8,name="TB2_P5.08"),"SB")
    add("D3","D","Schottky 40V 3A (aux OR-ing)",{"A":"VAUX","K":"VCTRL"},fplib.SOD_SMC(),"SB"); add("D4","D","Schottky 40V 3A (output OR-ing)",{"A":"VOUT","K":"VCTRL"},fplib.SOD_SMC(),"SB")
    add("U4","UCC27524","UCC27524",{"ENA":"VCTRL","INA":"SR1","GND":"SGND","INB":"SR2","ENB":"VCTRL","OUTA":"OUT_SR1","VDD":"VCTRL","OUTB":"OUT_SR2"},fplib.SOIC8(),"SB")
    add("CVC1","C","1uF",{"1":"VCTRL","2":"SGND"},r,"SB"); add("CVC2","C","10uF 25V",{"1":"VCTRL","2":"SGND"},r,"SB")
    add("U5","R78","RECOM R-78E3.3-0.5",{"VIN":"VCTRL","GND":"SGND","VOUT":"V3V3"},fplib.SIP(3,2.54,1.8,1.0,"SIP3_P2.54",11.5,8.5),"SB")
    add("CIN5","C","10uF 25V",{"1":"VCTRL","2":"SGND"},r,"SB"); add("COUT5","C","22uF 10V",{"1":"V3V3","2":"SGND"},r,"SB")
    add("U6","ISO_DCDC","Isolated 14V->15V >=1W, "+cfg["iso"],{"VIN":"VCTRL","GND_IN":"SGND","VO+":"VPRI_15V","VO-":"PGND"},fplib.ISO4(cfg["fp"]["iso_across"]),"X")
    for c in comps:  # verify every symbol pin has a pad number in footprint
        L,R,_,_,_=SYMS[c["sym"]]; pads={p[0] for p in c["fp"]["pads"]}
        for pn,num in L+R:
            assert num in pads,(c["ref"],pn,num,c["fp"]["name"]); assert pn in c["nets"],(c["ref"],pn)
        c["w"]=c["fp"]["crt"][2]-c["fp"]["crt"][0]; c["h"]=c["fp"]["crt"][3]-c["fp"]["crt"][1]
    return comps

# ---------------- schematic ----------------
def sch_emit(cfg,comps,outdir):
    NAME=cfg["name"]; ROOT=U()
    # use consecutive columns by section group
    colmap={"P":0,"PA":1,"PB":1,"PM":0,"X":3,"SM":4,"SA":5,"SB":6}
    COLX=[40+i*80 for i in range(7)]; ycur=[45]*7
    for c in comps:
        L,R,hw,_,_=SYMS[c["sym"]]; h=max(len(L),len(R)); c["sh"]=h; c["shw"]=hw
        col=colmap.get(c["sec"],0)
        if c["sec"]=="X": col=3 if c["ref"] in("T1","U6","CY1") else 2
        if c["ref"].startswith(("LR","CBLK")): col=3
        c["scol"]=col; c["sx"]=round(COLX[col]/G)*G; c["sy"]=round((ycur[col]+G*h+4*G)/G)*G; ycur[col]=c["sy"]+5*G
    o=[f'(kicad_sch\n\t(version 20250114)\n\t(generator "eeschema")\n\t(generator_version "9.0")\n\t(uuid "{ROOT}")\n\t(paper "A0")\n',
       f'\t(title_block (title "{cfg["title"]}") (date "2026-11-19") (rev "B") (comment 1 "Generated; verify in KiCad ERC before use") (comment 2 "Pinouts verified vs TI datasheets: UCC21520DW, INA180A1"))\n\t(lib_symbols\n']
    for s in SYMS: o.append(lib_symbol(s))
    o.append('\t)\n'); nets={}; wires=[]
    for c in comps:
        L,R,hw,desc,pre=SYMS[c["sym"]]; h=c["sh"]; X,Y=c["sx"],c["sy"]
        o.append(f'\t(symbol\n\t\t(lib_id "CarEngineGen:{c["sym"]}")\n\t\t(at {X:.2f} {Y:.2f} 0)\n\t\t(unit 1)\n\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp no)\n\t\t(uuid "{c["uuid"]}")\n'
          f'\t\t(property "Reference" "{c["ref"]}" (at {X:.2f} {Y-G*h-1.27:.2f} 0) {EO})\n\t\t(property "Value" "{c["value"]}" (at {X:.2f} {Y+G+1.27:.2f} 0) {EO})\n'
          f'\t\t(property "Footprint" "CarEngineGen:{c["fp"]["name"]}" (at {X:.2f} {Y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
          f'\t\t(property "Datasheet" "" (at {X:.2f} {Y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))\n\t\t(property "Description" "{desc}" (at {X:.2f} {Y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))\n')
        for side,lst in (("L",L),("R",R)):
            for i,(pn,num) in enumerate(lst):
                o.append(f'\t\t(pin "{num}" (uuid "{U()}"))\n'); net=c["nets"][pn]; py=Y-G*(h-1-i)
                if side=="L": ex=X-(hw+G); lx=ex-G; ang=180; j="right bottom"
                else: ex=X+(hw+G); lx=ex+G; ang=0; j="left bottom"
                wires.append((ex,py,lx,ang,j,net)); nets.setdefault(net,[]).append((c["ref"],pn,num))
        o.append(f'\t\t(instances (project "{NAME}" (path "/{ROOT}" (reference "{c["ref"]}") (unit 1))))\n\t)\n')
    for ex,py,lx,ang,j,net in wires:
        o.append(f'\t(wire (pts (xy {ex:.2f} {py:.2f}) (xy {lx:.2f} {py:.2f})) (stroke (width 0) (type default)) (uuid "{U()}"))\n')
        o.append(f'\t(label "{net}" (at {lx:.2f} {py:.2f} {ang}) (effects (font (size 1.27 1.27)) (justify {j})) (uuid "{U()}"))\n')
    heads=["PRIMARY: input, bridge A/B","","","RESONANT + XFMR + ISOLATORS","SECONDARY: sync rect, output","OCP LATCH, SENSE, FAULT","CONTROLLER, AUX, BIAS"]
    for i,hd in enumerate(heads):
        if hd: o.append(f'\t(text "{hd}" (exclude_from_sim no) (at {COLX[i]-12:.2f} 25 0) (effects (font (size 2.54 2.54) bold) (justify left)) (uuid "{U()}"))\n')
    warn=("HV WARNING: 288-403 V DC is lethal. Bench-test behind an isolation transformer, current-limited. Do not defeat Leaf contactors/interlocks/BMS." if cfg["hv"] else
          "Prototype profile 82-110 V DC. First tests <=60 V current-limited. Same architecture as the Leaf (HV) version.")
    notes=[warn,"Controller on the 14 V side; primary FETs via UCC21520 isolated drivers; 15 V primary bias from isolated module U6.",
      "Start-up: 12 V on J2 boots the ESP32; afterwards D4 keeps it alive from the output. Drivers are disabled by default (DRV_DIS pulled high).",
      "Hardware OCP: U8 compares ISENSE with IREF (~1.8 V = ~45 A); fault pulls EN_G low through D5, switching Q8 off, so DRV_DIS goes high. MCU also reads OCP_N."]
    for i,n in enumerate(notes): o.append(f'\t(text "{n}" (exclude_from_sim no) (at 40 {8+i*4} 0) (effects (font (size 1.8 1.8)) (justify left)) (uuid "{U()}"))\n')
    o.append('\t(sheet_instances (path "/" (page "1")))\n\t(embedded_fonts no)\n)\n')
    open(f"{outdir}/{NAME}.kicad_sch","w").write("".join(o)); return nets

# ---------------- PCB ----------------
PRI_PREFIX=("VBUS","SW","GA_","GB_","HO_","LO_","VBOOT","BOOT_K","VPRI","PRI_","BLEED","PGND")
def is_pri(n): return n.startswith(PRI_PREFIX)
def rects_overlap(a,b,m=0.0): return not (a[2]+m<=b[0] or b[2]+m<=a[0] or a[3]+m<=b[1] or b[3]+m<=a[1])

def place(cfg,comps):
    W,H,cx,gap=cfg["W"],cfg["H"],cfg["cx"],cfg["gap"]; fx=cfg["fixed"]
    T=[c for c in comps if c["ref"]=="T1"][0]
    t_top=fx["T1"][1]-T["h"]/2-3; t_bot=fx["T1"][1]+T["h"]/2+3
    xp1=cx-gap/2; xs0=cx+gap/2
    bands={"top":(3,t_top),"mid":(t_top,t_bot),"bot":(t_bot,H-3)}
    regions={"PA":(3,xp1,*bands["top"]),"PM":(3,xp1,*bands["mid"]),"PB":(3,xp1,*bands["bot"]),
             "SA":(xs0,W-3,*bands["top"]),"SM":(xs0,W-3,*bands["mid"]),"SB":(xs0,W-3,*bands["bot"])}
    placed=[]
    def box(c,x,y): return (x+c["fp"]["crt"][0],y+c["fp"]["crt"][1],x+c["fp"]["crt"][2],y+c["fp"]["crt"][3])
    for hx,hy in ((5,5),(W-5,5),(5,H-5),(W-5,H-5)): placed.append((hx-3,hy-3,hx+3,hy+3))
    for ref,(x,y) in fx.items():
        c=[c for c in comps if c["ref"]==ref][0]; c["x"],c["y"]=x,y; placed.append(box(c,x,y))
    # order: big first
    order={"PM":["J1","F1","C1","C2","D6","RBL1","RBL2","LR1","CBLK1"],"PA":["Q1","Q2","DB1","RBT1","CB1","CD1","RG1","RGS1","RG2","RGS2"],
           "PB":["Q3","Q4","DB2","RBT2","CB2","CD2","RG3","RGS3","RG4","RGS4"],
           "SM":["L1","Q5","Q6","COUT1","COUT2","COUT3","COUT4","RSH1","J3","U7","CIS1","RSN1","RSN2","CSN1","CSN2","RG5","RG6"],
           "SA":["CV1","RDT1","CDT1","CDIS1","U8","D5","Q8","RIREF1","RIREF2","CCMP1","RFLT1","RGEN1","RGENS1","RDIS1"],
           "SB":["CV2","RDT2","CDT2","U1","U5","U4","J2","D3","D4","CVC1","CVC2","CIN5","COUT5","RPD1","RPD2","RPD3","RPD4","RPD5","RPD6","RFB1","RFB2","CFB1","RNTC1","RT2"]}
    by={c["ref"]:c for c in comps}
    placed_refs=set(fx)
    def first_fit(c,reg,rtl=False,margin=0.8):
        x0,x1,y0,y1=reg; w,h=c["w"],c["h"]; ox,oy=-c["fp"]["crt"][0],-c["fp"]["crt"][1]
        ys=[y0+1+i*0.5 for i in range(int((y1-y0-h)/0.5))]
        for yy in ys:
            xs=[x0+1+i*0.5 for i in range(int((x1-x0-w)/0.5))]
            if rtl: xs=xs[::-1]
            for xx in xs:
                b=(xx,yy,xx+w,yy+h)
                if not any(rects_overlap(b,p,margin) for p in placed): return xx+ox,yy+oy
        return None
    for key,refs in order.items():
        for ref in refs:
            if ref not in by: continue
            c=by[ref]; reg=regions[key]
            u2y=fx["U2"][1]; u3y=fx["U3"][1]
            if ref in("CV1","RDT1","CDT1","CDIS1"): reg=(xs0,xs0+18,u2y-7,u2y+7)
            if ref in("CV2","RDT2","CDT2"): reg=(xs0,xs0+18,u3y-7,u3y+7)
            pos=first_fit(c,reg,rtl=(ref in("LR1","CBLK1") or key in("PA","PB")))
            if pos is None and reg is not regions[key]: pos=first_fit(c,regions[key])
            if pos is None:  # overflow: whole side
                side=(3,xp1,3,H-3) if key[0]=="P" else (xs0,W-3,3,H-3); pos=first_fit(c,side); c["overflow"]=True
            assert pos is not None,("cannot place",ref)
            c["x"],c["y"]=pos; placed.append(box(c,*pos)); placed_refs.add(ref)
    missing=[c["ref"] for c in comps if "x" not in c]; assert not missing,missing
    return regions

def pcb_emit(cfg,comps,regions,outdir):
    NAME=cfg["name"]; W,H,cx,gap=cfg["W"],cfg["H"],cfg["cx"],cfg["gap"]
    src=open(""+os.environ.get("PCB_TEMPLATE","CarEngine.kicad_pcb")+"",newline="").read().replace("\r\n","\n")
    head=src[:src.find("\t(footprint ")].replace('(paper "A4")','(paper "A3")')
    OX,OY=40,40  # board origin on sheet
    o=[head]
    for c in comps:
        nets={}
        L,R,_,_,_=SYMS[c["sym"]]
        for pn,num in L+R: nets[num]="/"+c["nets"][pn]
        o.append(fplib.sexp(c["fp"],"pcb",ref=c["ref"],value=c["value"],at=(OX+c["x"],OY+c["y"]),uid=U(),nets=nets,sym_uuid=c["uuid"],sch=NAME+".kicad_sch"))
    for k,(hx,hy) in enumerate(((5,5),(W-5,5),(5,H-5),(W-5,H-5)),1):
        o.append(fplib.sexp(fplib.HOLE(),"pcb",ref=f"H{k}",value="M3",at=(OX+hx,OY+hy),uid=U(),sym_uuid=None,sch=""))
    def line(x1,y1,x2,y2,layer,w=0.05,t="default"): return f'\t(gr_line (start {OX+x1} {OY+y1}) (end {OX+x2} {OY+y2}) (stroke (width {w}) (type {t})) (layer "{layer}") (uuid "{U()}"))\n'
    for a in ((0,0,W,0),(W,0,W,H),(W,H,0,H),(0,H,0,0)): o.append(line(*a,"Edge.Cuts"))
    xp1=cx-gap/2; xs0=cx+gap/2
    for (x0,y0,x1,y1) in ((3,3,xp1,H-3),(xs0,3,W-3,H-3)):
        o.append(f'\t(gr_rect (start {OX+x0} {OY+y0}) (end {OX+x1} {OY+y1}) (stroke (width 0.15) (type dash)) (fill no) (layer "Dwgs.User") (uuid "{U()}"))\n')
    for txt,x,y in (("PRIMARY (HV) - PGND pour on B.Cu",xp1/2,H-1),("SECONDARY (14 V) - SGND pour on B.Cu",(xs0+W)/2,H-1),("ISOLATION BARRIER",cx,H/2-0.0)):
        o.append(f'\t(gr_text "{txt}" (at {OX+x} {OY+y} {90 if "BARRIER" in txt else 0}) (layer "Dwgs.User") (uuid "{U()}") (effects (font (size 1.5 1.5) (thickness 0.2))))\n')
    o.append("\t(embedded_fonts no)\n)\n")
    open(f"{outdir}/{NAME}.kicad_pcb","w").write("".join(o))

def checks(cfg,comps):
    W,H=cfg["W"],cfg["H"]; rep=[]
    boxes=[(c["ref"],(c["x"]+c["fp"]["crt"][0],c["y"]+c["fp"]["crt"][1],c["x"]+c["fp"]["crt"][2],c["y"]+c["fp"]["crt"][3])) for c in comps]
    for i,(a,ba) in enumerate(boxes):
        if ba[0]<0 or ba[1]<0 or ba[2]>W or ba[3]>H: rep.append(f"OUTSIDE BOARD: {a}")
        for b,bb in boxes[i+1:]:
            if rects_overlap(ba,bb,0.0): rep.append(f"COURTYARD OVERLAP: {a} / {b}")
    # primary-to-secondary pad distance
    pri=[];sec=[]
    for c in comps:
        L,R,_,_,_=SYMS[c["sym"]]; num2pin={num:pn for pn,num in L+R}
        for (num,x,y,w,h,s,d) in c["fp"]["pads"]:
            if num not in num2pin: continue
            n=c["nets"][num2pin[num]]; r=(c["x"]+x-w/2,c["y"]+y-h/2,c["x"]+x+w/2,c["y"]+y+h/2)
            (pri if is_pri(n) else sec).append((c["ref"],num,n,r))
    best={}
    for a in pri:
        for b in sec:
            dx=max(a[3][0]-b[3][2],b[3][0]-a[3][2],0); dy=max(a[3][1]-b[3][3],b[3][1]-a[3][3],0); d=math.hypot(dx,dy)
            k=tuple(sorted((a[0],b[0])))
            if k not in best or d<best[k][0]: best[k]=(d,a[2],b[2])
    need=8.0 if cfg["hv"] else 4.0
    worst=sorted(best.items(),key=lambda kv:kv[1][0])[:8]
    return rep,worst,need

def preview(cfg,comps,path):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt; from matplotlib.patches import Rectangle
    W,H,cx,gap=cfg["W"],cfg["H"],cfg["cx"],cfg["gap"]
    fig,ax=plt.subplots(figsize=(14,14*H/W)); ax.add_patch(Rectangle((0,0),W,H,fill=False,lw=2))
    ax.add_patch(Rectangle((cx-gap/2,0),gap,H,color="#ffdddd",alpha=.5))
    for c in comps:
        x0,y0,x1,y1=c["fp"]["crt"]; col="#cfe3ff" if is_pri(next(iter(c["nets"].values()))) and c["sec"][0]=="P" else "#d5f5d5"
        if c["sec"]=="X": col="#ffe9b3"
        ax.add_patch(Rectangle((c["x"]+x0,c["y"]+y0),x1-x0,y1-y0,fc=col,ec="k",lw=.5))
        for (num,x,y,w,h,s,d) in c["fp"]["pads"]: ax.add_patch(Rectangle((c["x"]+x-w/2,c["y"]+y-h/2),w,h,fc="#b8860b",ec="none"))
        ax.text(c["x"],c["y"],c["ref"],ha="center",va="center",fontsize=6)
    ax.set_xlim(-2,W+2); ax.set_ylim(H+2,-2); ax.set_aspect("equal"); ax.set_title(cfg["name"]+" placement (blue=primary, green=secondary, amber=straddles barrier)")
    fig.savefig(path,dpi=110,bbox_inches="tight"); plt.close(fig)

def run(cfg,base,dname):
    outdir=f"{base}/{dname}"; shutil.rmtree(outdir,ignore_errors=True); os.makedirs(f"{outdir}/CarEngineGen.pretty")
    comps=build(cfg); nets=sch_emit(cfg,comps,outdir); regions=place(cfg,comps); pcb_emit(cfg,comps,regions,outdir)
    fps={c["fp"]["name"]:c["fp"] for c in comps}; fps["MountingHole_M3"]=fplib.HOLE()
    for n,fp in fps.items(): open(f"{outdir}/CarEngineGen.pretty/{n}.kicad_mod","w").write(fplib.sexp(fp,"lib"))
    open(f"{outdir}/fp-lib-table","w").write('(fp_lib_table\n\t(version 7)\n\t(lib (name "CarEngineGen")(type "KiCad")(uri "${KIPRJMOD}/CarEngineGen.pretty")(options "")(descr "Generated footprints for this project"))\n)\n')
    json.dump({"meta":{"filename":cfg["name"]+".kicad_pro","version":3}},open(f"{outdir}/{cfg['name']}.kicad_pro","w"),indent=2)
    with open(f"{outdir}/{cfg['name']}_netlist.md","w") as f:
        f.write(f"# Netlist: {cfg['title']}\n\n| Net | Pins |\n|---|---|\n")
        for n in sorted(nets): f.write(f"| {n} | {', '.join(f'{r}.{p}' for r,p,_ in nets[n])} |\n")
    with open(f"{outdir}/{cfg['name']}_BOM.csv","w",newline="") as f:
        w=csv.writer(f); w.writerow(["Ref","Value","Footprint","Qty-note"]); 
        for c in sorted(comps,key=lambda c:(re.sub(r'\d','',c["ref"]),int(re.sub(r'\D','',c["ref"]) or 0))): w.writerow([c["ref"],c["value"],"CarEngineGen:"+c["fp"]["name"],""])
    preview(cfg,comps,f"{outdir}/{cfg['name']}_placement.png")
    rep,worst,need=checks(cfg,comps)
    single=[n for n,p in nets.items() if len(p)<2]
    print(f"== {cfg['name']}: {len(comps)} parts, {len(nets)} nets, board {cfg['W']}x{cfg['H']} mm")
    print("  single-pin nets:",single or "none"); print("  placement problems:",rep or "none")
    print(f"  closest primary<->secondary pad pairs (need >= {need} mm; straddlers are by design):")
    for k,(d,a,b) in worst: print(f"    {k[0]}-{k[1]}: {d:.1f} mm ({a} / {b})")
    ov=[c["ref"] for c in comps if c.get("overflow")]; print("  overflow-placed:",ov or "none")

if __name__=="__main__":
    base=sys.argv[1]
    run(CFG96,base,"converter_96V"); run(CFGHV,base,"converter_Leaf400V")
