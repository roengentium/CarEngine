"""Footprint builders: each returns dict(name, descr, smd, pads, crt(x0,y0,x1,y1), silk=[(x1,y1,x2,y2)], pin1=(x,y)|None).
Pad: (num, x, y, w, h, shape, drill)  drill=None for SMD."""
import math
def _fmt(v): return f"{v:.3f}".rstrip("0").rstrip(".") if abs(v)>1e-9 else "0"

def R0805(): 
    return dict(name="R0805",descr="0805 resistor/capacitor",smd=True,
        pads=[("1",-1.0,0,1.0,1.45,"roundrect",None),("2",1.0,0,1.0,1.45,"roundrect",None)],
        crt=(-1.9,-1.0,1.9,1.0),silk=[(-0.3,-0.8,0.3,-0.8),(-0.3,0.8,0.3,0.8)],pin1=None)
def SOD_SMA(): return _diode("SMA",2.0,2.2,1.9,5.4,3.0)
def SOD_SMC(): return _diode("SMC",3.4,3.2,3.0,9.0,6.4)
def _diode(n,px,pw,ph,cw,ch):
    return dict(name=n,descr=f"{n} diode, pad1=anode, pad2=cathode (bar side)",smd=True,
        pads=[("1",-px,0,pw,ph,"roundrect",None),("2",px,0,pw,ph,"roundrect",None)],
        crt=(-cw/2,-ch/2,cw/2,ch/2),silk=[(px-1.0,-ch/2+0.3,px-1.0,ch/2-0.3)],pin1=None)
def R2512():
    return dict(name="R2512",descr="2512 shunt resistor",smd=True,
        pads=[("1",-3.1,0,1.6,3.2,"roundrect",None),("2",3.1,0,1.6,3.2,"roundrect",None)],
        crt=(-4.4,-2.0,4.4,2.0),silk=[],pin1=None)
def SOT23():
    return dict(name="SOT23",descr="SOT-23-3 (1,2 left; 3 right)",smd=True,
        pads=[("1",-1.0,-0.95,1.0,0.7,"roundrect",None),("2",-1.0,0.95,1.0,0.7,"roundrect",None),("3",1.0,0,1.0,0.7,"roundrect",None)],
        crt=(-1.9,-1.7,1.9,1.7),silk=[],pin1=(-1.9,-1.0))
def SOT23_5():
    return dict(name="SOT23_5",descr="SOT-23-5 (1,2,3 bottom L-R; 4 top right; 5 top left)",smd=True,
        pads=[("1",-0.95,1.3,0.6,1.1,"roundrect",None),("2",0,1.3,0.6,1.1,"roundrect",None),("3",0.95,1.3,0.6,1.1,"roundrect",None),
              ("4",0.95,-1.3,0.6,1.1,"roundrect",None),("5",-0.95,-1.3,0.6,1.1,"roundrect",None)],
        crt=(-1.8,-2.2,1.8,2.2),silk=[],pin1=(-1.6,1.9))
def SOIC8():
    pads=[]
    for i in range(4): pads.append((str(i+1),-2.7,-1.905+1.27*i,1.55,0.6,"roundrect",None))
    for i in range(4): pads.append((str(5+i),2.7,1.905-1.27*i,1.55,0.6,"roundrect",None))
    return dict(name="SOIC8",descr="SOIC-8 3.9mm",smd=True,pads=pads,crt=(-3.7,-2.9,3.7,2.9),silk=[],pin1=(-3.4,-2.6))
def SOIC16W(rot180=False):
    pads=[]
    for i in range(8): pads.append((str(i+1),-4.65,-4.445+1.27*i,2.0,0.6,"roundrect",None))
    for i in range(8): pads.append((str(9+i),4.65,4.445-1.27*i,2.0,0.6,"roundrect",None))
    if rot180: pads=[(n,-x,-y,w,h,s,d) for n,x,y,w,h,s,d in pads]
    return dict(name="SOIC16W"+("_R180" if rot180 else ""),descr="SOIC-16 wide (DW), 10.3x7.5; R180 = pins 1-8 on the right",smd=True,
        pads=pads,crt=(-6.0,-5.9,6.0,5.9),silk=[],pin1=((3.9,-5.4) if rot180 else (-3.9,-5.4)) if False else ((5.9,5.4) if rot180 else (-5.9,-5.4)))
def THT2(pitch,pad,drill,bw,bh,name=None):
    nm=name or f"THT2_P{pitch}_B{bw}x{bh}"
    return dict(name=nm,descr=f"2-pin THT pitch {pitch}mm, body {bw}x{bh}",smd=False,
        pads=[("1",-pitch/2,0,pad,pad,"circle",drill),("2",pitch/2,0,pad,pad,"circle",drill)],
        crt=(-bw/2,-bh/2,bw/2,bh/2),silk=[(-bw/2,-bh/2,bw/2,-bh/2),(bw/2,-bh/2,bw/2,bh/2),(bw/2,bh/2,-bw/2,bh/2),(-bw/2,bh/2,-bw/2,-bh/2)],pin1=None)
def TO220():
    return dict(name="TO220V",descr="TO-220-3 vertical, 1=G 2=D 3=S, origin at centre pin; tab upward (-y)",smd=False,
        pads=[("1",-2.54,0,1.9,2.0,"rect",1.1),("2",0,0,1.9,2.0,"oval",1.1),("3",2.54,0,1.9,2.0,"oval",1.1)],
        crt=(-5.4,-10.0,5.4,3.0),silk=[(-5.1,-4.5,5.1,-4.5),(5.1,-4.5,5.1,1.5),(5.1,1.5,-5.1,1.5),(-5.1,1.5,-5.1,-4.5)],pin1=None)
def TO247():
    return dict(name="TO247V",descr="TO-247-3 vertical, 1=G 2=D 3=S (verify vs part), origin at centre pin",smd=False,
        pads=[("1",-5.45,0,2.6,3.6,"rect",1.6),("2",0,0,2.6,3.6,"oval",1.6),("3",5.45,0,2.6,3.6,"oval",1.6)],
        crt=(-8.4,-21.5,8.4,3.2),silk=[(-7.9,-5.0,7.9,-5.0),(7.9,-5.0,7.9,2.0),(7.9,2.0,-7.9,2.0),(-7.9,2.0,-7.9,-5.0)],pin1=None)
def SIP(n,pitch,pad,drill,name,bw,bh):
    x0=-(n-1)*pitch/2
    return dict(name=name,descr=f"{n}-pin SIP, pitch {pitch}",smd=False,
        pads=[(str(i+1),x0+i*pitch,0,pad,pad,"rect" if i==0 else "circle",drill) for i in range(n)],
        crt=(-bw/2,-bh/2,bw/2,bh/2),silk=[(-bw/2,-bh/2,bw/2,-bh/2),(bw/2,-bh/2,bw/2,bh/2),(bw/2,bh/2,-bw/2,bh/2),(-bw/2,bh/2,-bw/2,-bh/2)],pin1=None)
def ISO4(across,within=5.08):
    xs={"3":-(across/2+within),"4":-across/2,"2":across/2,"1":across/2+within}
    pads=[(k,x,0,1.9,1.9,"rect" if k=="3" else "circle",1.1) for k,x in xs.items()]
    bw=across+2*within+3.2
    return dict(name=f"ISO4_X{across}",descr="Isolated DC-DC module placeholder: pads 3,4 = primary side (VO+,VO-), 2,1 = secondary side (GND,VIN). Match to real module.",smd=False,
        pads=pads,crt=(-bw/2,-3.2,bw/2,3.2),silk=[(-bw/2,-3.2,bw/2,-3.2),(bw/2,-3.2,bw/2,3.2),(bw/2,3.2,-bw/2,3.2),(-bw/2,3.2,-bw/2,-3.2)],pin1=None)
def ESP32DK(rot=False):
    pads=[]
    for i in range(19): pads.append((str(i+1),-12.7,-22.86+2.54*i,1.7,1.7,"rect" if i==0 else "circle",1.0))
    for i in range(19): pads.append((str(20+i),12.7,-22.86+2.54*i,1.7,1.7,"circle",1.0))
    crt=(-14.4,-27.5,14.4,27.5); sk=[(-14.0,-27.0,14.0,-27.0),(14.0,-27.0,14.0,27.0),(14.0,27.0,-14.0,27.0),(-14.0,27.0,-14.0,-27.0)]
    if rot:
        pads=[(n,-y,x,w,h,s,d) for n,x,y,w,h,s,d in pads]; crt=(-27.5,-14.4,27.5,14.4)
        sk=[(-27.0,-14.0,27.0,-14.0),(27.0,-14.0,27.0,14.0),(27.0,14.0,-27.0,14.0),(-27.0,14.0,-27.0,-14.0)]
    return dict(name="ESP32_DEVKIT38"+("_R90" if rot else ""),descr="ESP32 DevKitC-style 38-pin module, rows 25.4mm apart (VERIFY vs your board). Left header = pads 1-19, right = 20-38. R90: rotated, rows run along X.",
        smd=False,pads=pads,crt=crt,silk=sk,pin1=None)
def XFMR(px,sx,bw,bh,py=6.0,sy=10.0,name="XFMR"):
    pads=[("1",-px,-py,3.6,3.6,"circle",1.8),("2",-px,py,3.6,3.6,"circle",1.8),
          ("3",sx,-sy,5.0,5.0,"circle",2.6),("4",sx,0,5.0,5.0,"circle",2.6),("5",sx,sy,5.0,5.0,"circle",2.6)]
    return dict(name=name,descr="Centre-tapped power transformer placeholder: 1,2 primary (left); 3,4(CT),5 secondary (right). Custom-wound part, set real pads.",smd=False,
        pads=pads,crt=(-bw/2,-bh/2,bw/2,bh/2),silk=[(-bw/2,-bh/2,bw/2,-bh/2),(bw/2,-bh/2,bw/2,bh/2),(bw/2,bh/2,-bw/2,bh/2),(-bw/2,bh/2,-bw/2,-bh/2)],pin1=None)
def HOLE():
    return dict(name="MountingHole_M3",descr="M3 mounting hole",smd=False,pads=[("",0,0,3.2,3.2,"npth",3.2)],crt=(-3,-3,3,3),silk=[],pin1=None)

def sexp(fp, mode, ref="REF**", value="", at=(0,0), uid=None, nets=None, sym_uuid=None, sch="", uuidf=None):
    """mode 'lib' (.kicad_mod) or 'pcb' (instance). nets: {padnum: netname}"""
    import uuid as _u
    U=lambda: str(_u.uuid4())
    nets=nets or {}
    o=[]
    if mode=="lib":
        o.append(f'(footprint "{fp["name"]}"\n\t(version 20260206)\n\t(generator "pcbnew")\n\t(generator_version "10.0")\n\t(layer "F.Cu")\n')
    else:
        o.append(f'\t(footprint "CarEngineGen:{fp["name"]}"\n\t\t(layer "F.Cu")\n\t\t(uuid "{uid}")\n\t\t(at {_fmt(at[0])} {_fmt(at[1])})\n')
    I="\t" if mode=="lib" else "\t\t"
    x0,y0,x1,y1=fp["crt"]
    o.append(f'{I}(descr "{fp["descr"]}")\n')
    eff='(effects (font (size 1 1) (thickness 0.15)))'
    o.append(f'{I}(property "Reference" "{ref}" (at 0 {_fmt(y0-1.3)} 0) (layer "F.SilkS") (uuid "{U()}") {eff})\n')
    o.append(f'{I}(property "Value" "{value or fp["name"]}" (at 0 {_fmt(y1+1.3)} 0) (layer "F.Fab") (uuid "{U()}") {eff})\n')
    o.append(f'{I}(property "Datasheet" "" (at 0 0 0) (layer "F.Fab") (hide yes) (uuid "{U()}") (effects (font (size 1.27 1.27))))\n')
    o.append(f'{I}(property "Description" "" (at 0 0 0) (layer "F.Fab") (hide yes) (uuid "{U()}") (effects (font (size 1.27 1.27))))\n')
    if mode=="pcb" and sym_uuid:
        o.append(f'{I}(path "/{sym_uuid}")\n{I}(sheetname "/")\n{I}(sheetfile "{sch}")\n')
    o.append(f'{I}(attr {"smd" if fp["smd"] else "through_hole"})\n')
    for (a,b,c,d) in fp["silk"]:
        o.append(f'{I}(fp_line (start {_fmt(a)} {_fmt(b)}) (end {_fmt(c)} {_fmt(d)}) (stroke (width 0.12) (type solid)) (layer "F.SilkS") (uuid "{U()}"))\n')
    if fp.get("pin1"):
        px,py=fp["pin1"]; o.append(f'{I}(fp_circle (center {_fmt(px)} {_fmt(py)}) (end {_fmt(px+0.3)} {_fmt(py)}) (stroke (width 0.12) (type solid)) (fill yes) (layer "F.SilkS") (uuid "{U()}"))\n')
    o.append(f'{I}(fp_rect (start {_fmt(x0)} {_fmt(y0)}) (end {_fmt(x1)} {_fmt(y1)}) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd") (uuid "{U()}"))\n')
    for (num,x,y,w,h,shape,drill) in fp["pads"]:
        if shape=="npth":
            o.append(f'{I}(pad "" np_thru_hole circle (at {_fmt(x)} {_fmt(y)}) (size {_fmt(w)} {_fmt(h)}) (drill {_fmt(drill)}) (layers "*.Cu" "*.Mask") (uuid "{U()}"))\n'); continue
        if drill is None:
            s=f'{I}(pad "{num}" smd {shape} (at {_fmt(x)} {_fmt(y)}) (size {_fmt(w)} {_fmt(h)}) (layers "F.Cu" "F.Mask" "F.Paste")'
            if shape=="roundrect": s+=' (roundrect_rratio 0.25)'
        else:
            s=f'{I}(pad "{num}" thru_hole {shape} (at {_fmt(x)} {_fmt(y)}) (size {_fmt(w)} {_fmt(h)}) (drill {_fmt(drill)}) (layers "*.Cu" "*.Mask") (remove_unused_layers no)'
        if mode=="pcb" and num in nets: s+=f' (net "{nets[num]}")'
        s+=f' (uuid "{U()}"))\n'
        o.append(s)
    o.append(f'{I}(embedded_fonts no)\n')
    o.append(")\n" if mode=="lib" else "\t)\n")
    return "".join(o)
