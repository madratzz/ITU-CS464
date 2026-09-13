import json, math, os

# ---------- palette (identical to Lecture 01 — the course's shared visual system) ----------
BG      = "#14171C"
SURFACE = "#1B2027"
SURFACE2= "#232A34"
BORDER  = "rgba(255,255,255,0.10)"
BORDER2 = "rgba(255,255,255,0.16)"
TEXT    = "#EEF1F5"
MUTED   = "#9AA2B1"
FAINT   = "#5C6472"
ACCENT  = "#FF8A3D"
ACCENT_SOFT = "rgba(255,138,61,0.14)"
ACCENT2 = "#55D6C2"
ACCENT2_SOFT = "rgba(85,214,194,0.14)"
ACCENT3 = "#6C8CFF"
ACCENT3_SOFT = "rgba(108,140,255,0.14)"
ACCENT4 = "#FF4FA3"
ACCENT4_SOFT = "rgba(255,79,163,0.14)"

ACCENT_GLOW  = "rgba(255,138,61,0.55)"
ACCENT2_GLOW = "rgba(85,214,194,0.50)"
ACCENT3_GLOW = "rgba(108,140,255,0.50)"
ACCENT4_GLOW = "rgba(255,79,163,0.50)"
INK_GLOW     = "rgba(0,0,0,0.55)"

DISPLAY = "'Instrument Sans', 'Helvetica Neue', Arial, sans-serif"
BODYF   = "'Instrument Sans', 'Helvetica Neue', Arial, sans-serif"
MONOF   = "'Space Mono', ui-monospace, 'SF Mono', Menlo, Consolas, monospace"

W, H = 1280, 720
MX = 96

# ---------- shared helper library (verbatim from Lecture 01's build_doc.py) ----------

def glow(color, blur=30, x=None, y=None):
    s = {"blur": blur, "color": color}
    if x is not None: s["x"] = x
    if y is not None: s["y"] = y
    return s

def grad(angle, *stops):
    n = len(stops) - 1
    return {"angle": angle, "stops": [{"at": (i / n if n else 0), "color": c} for i, c in enumerate(stops)]}

def orbit_path(radius, start_deg=-90, steps=48, cw=True, ry=None):
    ry = radius if ry is None else ry
    a0 = math.radians(start_deg)
    x0, y0 = radius * math.cos(a0), ry * math.sin(a0)
    pts = []
    for i in range(steps + 1):
        a = a0 + (1 if cw else -1) * 2 * math.pi * i / steps
        pts.append("%.2f,%.2f" % (radius * math.cos(a) - x0, ry * math.sin(a) - y0))
    return "M0,0 L" + " L".join(pts[1:])

def orbit_pos(cx, cy, radius, deg, size, ry=None):
    ry = radius if ry is None else ry
    a = math.radians(deg)
    return cx + radius * math.cos(a) - size / 2.0, cy + ry * math.sin(a) - size / 2.0

def txt(id,x,y,w,h,html,size,color=TEXT,weight=400,family=BODYF,align="left",valign="top",lh=1.25,
        role=None,shadow=None,extra=None):
    e = {"id":id,"type":"text","x":x,"y":y,"w":w,"h":h,"rotation":0,"opacity":1,
         "html":html,"fontSize":size,"fontFamily":family,"fontWeight":weight,
         "color":color,"align":align,"valign":valign,"lineHeight":lh}
    if role: e["role"] = role
    if shadow: e["shadow"] = shadow
    if extra: e.update(extra)
    return e

def rect(id,x,y,w,h,fill,radius=0,stroke=None,strokeWidth=0,opacity=1,gradient=None,shadow=None,extra=None):
    e = {"id":id,"type":"shape","shape":"rect","x":x,"y":y,"w":w,"h":h,"rotation":0,
         "opacity":opacity,"fill":fill,"stroke":stroke or "transparent","strokeWidth":strokeWidth,"radius":radius}
    if gradient: e["fillGradient"] = gradient
    if shadow: e["shadow"] = shadow
    if extra: e.update(extra)
    return e

def line(id,x,y,w,h,color,strokeWidth=2,dashed=False,opacity=1,lineEnd=None,lineStart=None,extra=None):
    e = {"id":id,"type":"shape","shape":"line","x":x,"y":y,"w":w,"h":h,"rotation":0,
         "opacity":opacity,"fill":color,"stroke":color,"strokeWidth":strokeWidth,
         "strokeStyle":"dashed" if dashed else "solid"}
    if lineEnd: e["lineEnd"] = lineEnd
    if lineStart: e["lineStart"] = lineStart
    if extra: e.update(extra)
    return e

def path_shape(id,x,y,w,h,d,stroke,strokeWidth=2,strokeStyle="solid",fill="transparent",radius=0,extra=None):
    e = {"id":id,"type":"shape","shape":"path","x":x,"y":y,"w":w,"h":h,"rotation":0,"opacity":1,
         "fill":fill,"stroke":stroke,"strokeWidth":strokeWidth,"radius":radius,"strokeStyle":strokeStyle,
         "d":d,"pathBox":[0,0,w,h]}
    if extra: e.update(extra)
    return e

def ellipse(id,x,y,w,h,fill,stroke=None,strokeWidth=0,opacity=1,dashed=False,gradient=None,shadow=None,extra=None):
    e = {"id":id,"type":"shape","shape":"ellipse","x":x,"y":y,"w":w,"h":h,"rotation":0,
         "opacity":opacity,"fill":fill,"stroke":stroke or "transparent","strokeWidth":strokeWidth,
         "strokeStyle":"dashed" if dashed else "solid"}
    if gradient: e["fillGradient"] = gradient
    if shadow: e["shadow"] = shadow
    if extra: e.update(extra)
    return e

def ring(id,cx,cy,d,stroke,strokeWidth=1.5,dashed=True,march=None,opacity=1,shadow=None,extra=None):
    e = ellipse(id,cx-d/2.0,cy-d/2.0,d,d,"rgba(0,0,0,0)",stroke=stroke,strokeWidth=strokeWidth,
                opacity=opacity,dashed=dashed,shadow=shadow)
    if march:
        e["fx"] = {"loop":{"type":"dash-march","distance":march[0],"duration":march[1]}}
    if extra: e.update(extra)
    return e

def body(id,cx,cy,radius,deg,size,fill,duration=18,cw=True,gradient=None,shadow=None,ry=None,extra=None):
    x,y = orbit_pos(cx,cy,radius,deg,size,ry=ry)
    e = ellipse(id,x,y,size,size,fill,gradient=gradient,shadow=shadow)
    e["fx"] = {"loop":{"type":"motion-path","duration":duration,
                        "path":orbit_path(radius,start_deg=deg,cw=cw,ry=ry)}}
    if extra: e.update(extra)
    return e

def orbit_motif(p, cx, cy, d_outer, core=86, c1=ACCENT, c2=ACCENT4, g1=ACCENT_GLOW,
                ring_col="rgba(255,138,61,0.30)", label=None):
    r_out = d_outer / 2.0
    els = [
        ring(f"{p}r1", cx, cy, d_outer, ring_col, strokeWidth=1.5, march=(34, 11)),
        ring(f"{p}r2", cx, cy, d_outer * 0.62, "rgba(255,255,255,0.08)", strokeWidth=1, dashed=False),
        ellipse(f"{p}core", cx-core/2.0, cy-core/2.0, core, core, c1,
                gradient=grad(35, c1, c2), shadow=glow(g1, 70)),
        body(f"{p}b1", cx, cy, r_out, -90, 12, c2, duration=26, shadow=glow(g1, 16)),
        body(f"{p}b2", cx, cy, r_out * 0.62, 40, 9, "#FFFFFF", duration=17, cw=False,
             shadow=glow("rgba(255,255,255,0.45)", 12)),
        body(f"{p}b3", cx, cy, r_out, 155, 8, c1, duration=26, shadow=glow(g1, 12)),
    ]
    if label:
        els.append(txt(f"{p}lbl", cx-core/2.0, cy-core/2.0, core, core, label, 13, weight=800,
                       family=DISPLAY, color="#1A1004", align="center", valign="middle", lh=1.2,
                       extra={"letterSpacing":1}))
    return els

def stars(p, spec):
    out = []
    for i, (x, y, s, c, r, dur) in enumerate(spec):
        out.append(body(f"{p}s{i}", x, y, r, -90 + i * 47, s, c, duration=dur, cw=(i % 2 == 0)))
    return out

def chip(id,x,y,w,h,label,col):
    return [
        rect(f"{id}bg",x,y,w,h,BG,radius=8,opacity=0.35,stroke=col,strokeWidth=1),
        txt(f"{id}t",x,y,w,h,label,12.5,color=col,weight=700,family=MONOF,align="center",valign="middle"),
    ]

def social_badge(id,cx,cy,d,glyph,col,glyph_size=None,extra=None):
    r = d/2.0
    gs = glyph_size or d*0.46
    ring_e = ellipse(f"{id}bg",cx-r,cy-r,d,d,"rgba(0,0,0,0)",stroke=col,strokeWidth=1.5)
    txt_e = txt(f"{id}g",cx-r,cy-r,d,d,glyph,gs,color=col,weight=800,family=DISPLAY,
                align="center",valign="middle")
    if extra:
        ring_e.update(extra)
        txt_e.update(extra)
    return [ring_e, txt_e]

def kicker(id,x,y,label,color=ACCENT,size=15,w=800):
    upper = label.upper().replace("&MIDDOT;","&middot;").replace("&AMP;","&amp;").replace("&NDASH;","&ndash;").replace("&MDASH;","&mdash;")
    return txt(id,x,y,w,24,upper,size,color=color,weight=700,family=MONOF,
                extra={"letterSpacing":2})

def scene_id(n):
    return f"s{n}"

def slide(n, elements, notes, bg=BG, transition="fade"):
    return {"id":scene_id(n),"background":bg,"transition":transition,"notes":notes,"elements":elements}

slides = []

def footer(n, total=None, label="CS464 · GAME DEVELOPMENT"):
    return [
        txt(f"foot-l-{n}", MX, 664, 500, 28, label, 11, color=FAINT, family=MONOF, extra={"letterSpacing":1.5}),
        txt(f"foot-r-{n}", W-MX-160, 664, 160, 28, "{{page:2}} / {{pages}}", 11, color=FAINT, family=MONOF,
            align="right", extra={"letterSpacing":1.5}),
    ]

TOTAL = 41

# card helper reused across this deck — a labelled panel with a coloured left bar
def panel(id_prefix, x, y, w, h, kick, kcol, title, body_html, bodycol=MUTED, bg=SURFACE,
          border=BORDER, barcol=None, order=None, title_size=22, body_size=15.5, lh=1.55):
    fx = {"fx":{"enter":"fade-up","order":order}} if order is not None else {}
    els = [
        rect(f"{id_prefix}bg",x,y,w,h,bg,radius=14,stroke=border,strokeWidth=1,extra=dict(fx)),
    ]
    if barcol:
        els.append(rect(f"{id_prefix}bar",x,y,w,4,barcol,extra=dict(fx)))
    yy = y + 26
    if kick:
        els.append(txt(f"{id_prefix}k",x+28,yy,w-56,22,kick,12.5,color=kcol,weight=700,family=MONOF,
                        extra={"letterSpacing":2, **fx}))
        yy += 30
    if title:
        els.append(txt(f"{id_prefix}t",x+28,yy,w-56,40,title,title_size,weight=700,family=DISPLAY,extra=dict(fx)))
        yy += 42
    if body_html:
        els.append(txt(f"{id_prefix}b",x+28,yy,w-56,y+h-yy-18,body_html,body_size,color=bodycol,lh=lh,extra=dict(fx)))
    return els


teaching_states = []

def shot(id,key,x,y,w,h):
    return {"id":id,"type":"image","x":x,"y":y,"w":w,"h":h,"rotation":0,"opacity":1,
            "src":"asset:unity-"+key,"fit":"contain"}

def heading(n,title,sub,col=ACCENT):
    return [rect(f"bg{n}",0,0,W,H,BG),kicker(f"k{n}",96,60,sub,color=col),
            txt(f"t{n}",96,94,1088,70,title,44,weight=800)]

def credit(n,detail="Unity 6.0 Manual · Unity Technologies"):
    return [txt(f"source{n}",96,632,1088,20,detail,11,color=MUTED,family=MONOF)]+footer(n)

def button(id,label,target,x=900,y=571,w=284):
    return txt(id,x,y,w,42,label,16,color=ACCENT2,weight=700,align="center",valign="middle",
               extra={"link":target})

def state(n,key,els,notes):
    teaching_states.append({"id":key,"stateOf":f"s{n}","background":BG,"transition":"morph","elements":els,"notes":notes})

def focus(id,x,y,w,h,col=ACCENT):
    return rect(id,x,y,w,h,"transparent",stroke=col,strokeWidth=3)


# ============================================================ 1. COVER
els = [
    rect("bg1",0,0,W,H,BG),
    rect("cf2", MX, 96, 64, 3, ACCENT2, shadow=glow(ACCENT2_GLOW, 18)),
    txt("k1", MX, 132, 700, 30, "CS464 &middot; GAME DEVELOPMENT &middot; FALL 2025", 15, color=ACCENT2,
        weight=700, family=MONOF, extra={"letterSpacing":3}),
    txt("t1", MX, 230, 1088, 220, "Lecture 02", 128, color=TEXT, weight=800, family=DISPLAY,
        extra={"letterSpacing":-2}),
    txt("t1b", MX, 372, 1090, 90, "Inside Unity", 34, color=MUTED, weight=400, family=BODYF),
    rect("cf3", MX, 500, 340, 2, BORDER2),
    {"id":"cvph","type":"image","x":128-32,"y":559-32,"w":64,"h":64,"rotation":0,"opacity":1,
     "src":"asset:photo-instructor","fit":"cover","radius":32},
    ring("cvphborder",128,559,64,"rgba(85,214,194,0.35)",strokeWidth=1.5,dashed=False),
    txt("instr1", 180, 528, 600, 34, "Muhammad Raza Butt &nbsp;&middot;&nbsp; Information Technology University", 17,
        color=MUTED, family=BODYF),
    txt("instr2", 180, 560, 600, 30, "hello@madratzz.net &nbsp;&middot;&nbsp; muhammadraza.vf@itu.edu.pk", 13.5, color=FAINT, family=MONOF),
] + social_badge("cvsocx", 189, 602, 18, "X", ACCENT2) + [
    txt("cvsoc1t", 204, 592, 100, 20, "@imadratzz", 12, color=MUTED, family=MONOF),
] + social_badge("cvsocin", 320, 602, 18, "in", ACCENT2) + [
    txt("cvsoc2t", 335, 592, 110, 20, "/madratzz", 12, color=MUTED, family=MONOF),
    ellipse("cvlogoglow", 986-190, 286-190, 380, 380, ACCENT2, opacity=0.16,
            shadow=glow(ACCENT2_GLOW, 90),
            extra={"fx":{"ambient":"kenburns","ken":{"dir":"drift","scale":1.06,"duration":20}}}),
    ring("cvlogor1", 986, 286, 300, "rgba(85,214,194,0.32)", strokeWidth=1.5, dashed=True, march=(34,11)),
    ring("cvlogor2", 986, 286, 198, "rgba(255,255,255,0.08)", strokeWidth=1, dashed=False),
    {"id":"cvlogo","type":"image","x":986-120,"y":286-135,"w":240,"h":271,"rotation":0,"opacity":1,
     "src":"asset:logo-unity","fit":"contain"},
]
slides.append(slide(1, els, "We open Unity's version-control and project-structure story today — no laptops open yet, this half is still concepts. Callback to last lecture's 'next up' slide: this is exactly what was promised. Teal is this lecture's colour, same as Act II on the 15-week arc.", transition="none"))

# ============================================================ 2. AGENDA
agenda_parts = [
    ("PART 1", "Version Control", ACCENT2, [
        "01&nbsp;&nbsp;Why solo file-juggling breaks down",
        "02&nbsp;&nbsp;Git's model &amp; the everyday loop",
        "03&nbsp;&nbsp;Branching, merging &amp; remotes",
        "04&nbsp;&nbsp;Pull requests &amp; code review",
        "05&nbsp;&nbsp;Making Unity projects behave",
        "06&nbsp;&nbsp;A workflow checklist",
    ]),
    ("PART 2", "Unity Editor Overview", ACCENT, [
        "01&nbsp;&nbsp;The editor at a glance",
        "02&nbsp;&nbsp;Scene View vs Game View",
        "03&nbsp;&nbsp;Hierarchy &amp; Inspector",
        "04&nbsp;&nbsp;Project window &amp; Console",
        "05&nbsp;&nbsp;Toolbar &amp; Play Mode",
    ]),
    ("PART 3", "Scene &amp; GameObject Hierarchy", ACCENT3, [
        "01&nbsp;&nbsp;GameObjects &amp; Components",
        "02&nbsp;&nbsp;The Transform, parent-child nesting",
        "03&nbsp;&nbsp;Organizing a scene like a pro",
        "04&nbsp;&nbsp;Scenes at scale",
        "05&nbsp;&nbsp;Recap &amp; what's next",
    ]),
]
els = [
    rect("bg2",0,0,W,H,BG),
    kicker("k2",MX,72,"Today's session", color=ACCENT2),
    txt("t2",MX,104,1000,70,"Agenda",56,weight=800,family=DISPLAY),
]
agx = [96, 470, 844]
for pi, (part_label, part_title, part_col, items) in enumerate(agenda_parts):
    x = agx[pi]
    fx0 = {"fx":{"enter":"fade-up","order":0}}
    els += [
        rect(f"agc{pi}",x,232,340,392,SURFACE,radius=14,stroke=BORDER,strokeWidth=1,extra=dict(fx0)),
        rect(f"agc{pi}bar",x,232,340,6,part_col,radius=0,extra=dict(fx0)),
        txt(f"agc{pi}k",x+26,264,288,26,part_label,12.5,color=part_col,weight=700,family=MONOF,extra={"letterSpacing":2,**fx0}),
        txt(f"agc{pi}t",x+26,290,288,64,part_title,19,weight=700,family=DISPLAY,lh=1.2,extra=dict(fx0)),
    ]
    for i, item in enumerate(items):
        els.append(txt(f"agc{pi}i{i}",x+26,368+i*40,292,36,item,14.5,color=MUTED,extra={"fx":{"enter":"fade-up","order":i+1}}))
els += footer(2)
slides.append(slide(2, els, "Three parts today, not two — version control comes first this term, then the Unity Environment Tour (moved out of lab and into the lecture itself), before we open the scene graph. All three feed CLO-2 directly. Today's lab (Git Setup & Your First Commit) is where Part 1 gets practiced hands-on."))

# ============================================================ 3. RECAP
els = [
    rect("bg3",0,0,W,H,BG),
    kicker("k3",MX,72,"Before we start", color=ACCENT),
    txt("t3",MX,104,1000,70,"Last Time, Quickly",56,weight=800,family=DISPLAY),
]
recap_items = [
    ("The Magic Circle","A boundary, held up by agreement, that separates play from ordinary life.",ACCENT),
    ("MDA","Mechanics you build &rarr; Dynamics that emerge &rarr; Aesthetics the player feels.",ACCENT2),
    ("Bartle's Types","Achievers, Explorers, Socializers, Killers &mdash; four reasons people play.",ACCENT3),
]
for i,(name,desc,col) in enumerate(recap_items):
    y = 232 + i*128
    fx = {"fx":{"enter":"fade-up","order":i}}
    els += [
        rect(f"rc{i}",96,y,600,110,SURFACE,radius=12,stroke=BORDER,strokeWidth=1,extra=fx),
        rect(f"rc{i}bar",96,y,4,110,col,extra=fx),
        txt(f"rc{i}t",96+28,y+16,540,26,name,17,weight=700,family=DISPLAY,color=col,extra=fx),
        txt(f"rc{i}d",96+28,y+46,540,56,desc,14,color=MUTED,lh=1.45,extra=fx),
    ]
els += [
    rect("shiftbg",752,232,432,392,ACCENT2_SOFT,radius=16,stroke="rgba(85,214,194,0.35)",strokeWidth=1,
         extra={"fx":{"enter":"fade-up","order":3}}),
    txt("shiftk",752+32,264,368,24,"THE SHIFT",13,color=ACCENT2,weight=700,family=MONOF,
        extra={"letterSpacing":2,"fx":{"enter":"fade-up","order":3}}),
    txt("shiftt",752+32,296,368,120,"Theory becomes tools.",30,weight=800,family=DISPLAY,lh=1.2,
        extra={"fx":{"enter":"fade-up","order":3}}),
    txt("shiftd",752+32,414,368,180,
        "Everything from here is about the two things every Unity project needs before you write a single line of gameplay code: a safe place to keep your work, and a clean way to organize a scene.",
        16,color=TEXT,lh=1.6,extra={"fx":{"enter":"fade-up","order":3}}),
] + footer(3)
slides.append(slide(3, els, "Sixty seconds, not a re-teach — just enough to confirm the vocabulary stuck. The point of this slide is the right-hand card: name the shift explicitly, because the room's mode changes today from discussion to tooling."))

# ============================================================ 4. LEARNING OUTCOMES FOR TODAY
els = [
    rect("bg4",0,0,W,H,BG),
    kicker("k4",MX,72,"By the end of today", color=ACCENT2),
    txt("t4",MX,104,1088,70,"Learning Outcomes",56,weight=800,family=DISPLAY),
    rect("clobox",96,182,1088,116,SURFACE2,radius=14,stroke=BORDER2,strokeWidth=1),
    txt("clok",96+32,198,120,22,"CLO-2",13,color=ACCENT2,weight=700,family=MONOF,extra={"letterSpacing":2}),
    txt("clot",96+32,222,1024,46,
        "Configure the Unity environment, version control, and basic scene hierarchy.",
        18,color=TEXT),
    txt("clob",96+32,266,1024,20,"Bloom Level &mdash; L2 &middot; Understand",13.5,color=MUTED,family=MONOF),
]
clo_parts = [
    ("Version Control","Git's model, the daily loop, and Unity-specific gotchas.","THIS LECTURE &middot; PART 1", ACCENT2),
    ("Unity Environment","Editor layout, the core windows, and Play Mode.","THIS LECTURE &middot; PART 2", ACCENT),
    ("Scene Hierarchy","GameObjects, Components, and how a scene is organized.","THIS LECTURE &middot; PART 3", ACCENT3),
]
xs3 = [96, 464, 832]
for i,(name,desc,status,col) in enumerate(clo_parts):
    x = xs3[i]
    fx = {"fx":{"enter":"fade-up","order":i}}
    els += [
        rect(f"clp{i}",x,320,320,260,SURFACE,radius=14,stroke=col,strokeWidth=1.5,extra=fx),
        rect(f"clp{i}bar",x,320,320,4,col,extra=fx),
        txt(f"clp{i}n",x+24,352,272,18,f"0{i+1}",11,color=FAINT,weight=700,family=MONOF,extra={"letterSpacing":2,**fx}),
        txt(f"clp{i}t",x+24,374,272,64,name,21,weight=800,family=DISPLAY,lh=1.15,extra=fx),
        txt(f"clp{i}d",x+24,442,272,86,desc,14,color=MUTED,lh=1.45,extra=fx),
        rect(f"clp{i}sbg",x+24,536,272,26,"rgba(0,0,0,0)",radius=6,stroke=col,strokeWidth=1,extra=fx),
        txt(f"clp{i}s",x+24,536,272,26,status,10.5,color=col,weight=700,family=MONOF,align="center",
            valign="middle",extra={"letterSpacing":1.5,**fx}),
    ]
els += footer(4)
slides.append(slide(4, els, "CLO-2 has three parts and today covers all of them in one sitting — the environment tour moved out of lab and into the lecture itself. Part 1 is version control (the scaffolding for working with git), Part 2 opens Unity together for real, Part 3 is the scene graph."))

# ============================================================ 5. SECTION BREAK — VERSION CONTROL
els = [
    rect("bg5",0,0,W,H,BG),
    rect("sb5line",MX,300,120,4,ACCENT2,shadow=glow(ACCENT2_GLOW,18),
         extra={"fx":{"enter":"fade-up","order":0,"ambient":"kenburns","ken":{"dir":"drift","scale":1.0,"duration":18}}}),
    txt("sb5k",MX,326,700,28,"PART 1 OF TODAY",15,color=ACCENT2,weight=700,family=MONOF,extra={"letterSpacing":3,"fx":{"enter":"fade-up","order":0}}),
    txt("sb5t",MX,346,1088,160,"Version Control for<br>Game Projects",58,weight=800,family=DISPLAY,extra={"letterSpacing":-1,"fx":{"enter":"fade-up","order":1}}),
    txt("sb5s",MX,556,1000,40,"Your project's memory: every change, who made it, and how to undo it.",20,color=MUTED,
        extra={"fx":{"enter":"fade-up","order":2}}),
] + footer(5)
slides.append(slide(5, els, "Ask the room: who has ever lost work, or ended up with three folders called 'final', 'final2', and 'final_actually_final'? Nearly every hand goes up — that shared pain is the whole motivation for this section.", transition="fade"))

# ============================================================ 6. THE PROBLEM
els = [
    rect("bg6",0,0,W,H,BG),
    kicker("k6",MX,72,"Why bother", color=ACCENT2),
    txt("t6",MX,104,1088,70,"The Problem This Solves",50,weight=800,family=DISPLAY),
]
els += panel("p6a",96,206,528,400,"WITHOUT VERSION CONTROL",FAINT,None,
    "&#8226;&nbsp; <s>MyGame_v2_FINAL.zip</s><br>"
    "&#8226;&nbsp; <s>MyGame_v2_FINAL_fixed(1).zip</s><br>"
    "&#8226;&nbsp; <s>MyGame_ACTUALLY_FINAL.zip</s><br><br>"
    "Which folder is the real one? Overwrite a file by accident and it's gone. "
    "Two people edit the same scene and one of you just loses an evening.",
    bodycol=MUTED, bg=SURFACE, border=BORDER, barcol=FAINT, order=0, body_size=17, lh=1.7)
els += panel("p6b",656,206,528,400,"WITH VERSION CONTROL",ACCENT2,None,
    "One project folder. Each commit is a labelled snapshot you can return to, "
    "compare, or undo. Two people can work on the same project at once and merge "
    "their changes back together on purpose, not by accident.",
    bodycol=TEXT, bg=ACCENT2_SOFT, border="rgba(85,214,194,0.35)", barcol=ACCENT2, order=1, body_size=17, lh=1.75)
els += footer(6)
slides.append(slide(6, els, "The strikethrough filenames usually get a laugh of recognition — lean into it. Emphasize that Git protects committed work. Unsaved and uncommitted changes are not automatically recoverable."))

# ============================================================ 7. WHAT IS VERSION CONTROL
els = [
    rect("bg7",0,0,W,H,BG),
    kicker("k7",MX,72,"Defining our terms", color=ACCENT2),
    txt("t7",MX,104,1088,64,"What Is Version Control?",46,weight=800,family=DISPLAY),
    rect("qc7",96,196,1088,120,SURFACE2,radius=14,stroke=BORDER2,strokeWidth=1),
    txt("qc7q",96+32,216,1024,56,
        "A system that records changes to a set of files over time, so you can recall "
        "any specific version later &mdash; and see exactly who changed what, and why.",
        19,color=TEXT,lh=1.4),
    txt("qc7a",96+32,278,1024,22,"&mdash; the working definition this whole section builds on",13.5,color=MUTED,family=MONOF),
    txt("snapk",MX,348,600,24,"THE CORE IDEA: COMMITTED SNAPSHOTS",13,color=ACCENT2,weight=700,family=MONOF,extra={"letterSpacing":1.5}),
    txt("snapd",MX,378,1088,90,
        "Git doesn't keep a second copy of your project per save. It keeps a chain of "
        "<b>snapshots</b> &mdash; each one a restorable picture of tracked files, "
        "with unchanged file content reused between snapshots. Saving a file alone does not create a commit.",
        17,color=MUTED,lh=1.65),
] + footer(7)
slides.append(slide(7, els, "Keep this conceptual and slow — for most students this is the first time they've heard 'version control' defined precisely rather than just 'the thing GitHub does'. The snapshot idea is the one mental model everything else in this section hangs off."))

# ============================================================ 8. WHY GIT
git_stats = [
    ("2005","Born from the Linux kernel","Linus Torvalds began Git for Linux kernel development, emphasizing speed and distributed work.",ACCENT2),
    ("Distributed","History on your computer","A normal full clone carries committed history. Uncommitted work and LFS data need separate care.",ACCENT3),
    ("Free &amp; Open","No cost, no lock-in","Same tool whether you're solo, at a studio, or on a student project.",ACCENT4),
    ("Team Workflow","A practical course choice","Git supports branches and code review. Studios also use other version-control systems.",ACCENT),
]
els = [
    rect("bg8",0,0,W,H,BG),
    kicker("k8",MX,72,"Why git, specifically", color=ACCENT2),
    txt("t8",MX,104,1000,70,"Why Git",56,weight=800,family=DISPLAY),
]
xs4 = [96, 374, 652, 930]
for i,(num,label,desc,col) in enumerate(git_stats):
    x = xs4[i]
    fx = {"fx":{"enter":"fade-up","order":i}}
    els += [
        rect(f"gs{i}",x,232,254,300,SURFACE,radius=14,stroke=BORDER,strokeWidth=1,extra=fx),
        txt(f"gs{i}n",x+22,254,210,70,num,24,color=col,weight=800,family=DISPLAY,lh=1.15,extra=fx),
        txt(f"gs{i}l",x+22,330,210,50,label,15,weight=700,family=DISPLAY,color=TEXT,lh=1.2,extra=fx),
        rect(f"gs{i}div",x+22,384,206,1,BORDER,extra=fx),
        txt(f"gs{i}d",x+22,400,206,118,desc,13,color=MUTED,lh=1.5,extra=fx),
    ]
els += footer(8)
slides.append(slide(8, els, "Git is a useful course choice, not a universal studio standard. Normal clones preserve committed Git history, but shallow clones, partial clones and LFS differ. Source: https://git-scm.com/book/en/v2/Getting-Started-A-Short-History-of-Git"))

# ============================================================ 9. STAGED CONTENT IS A SNAPSHOT
staging_steps = [
    (6,4,4,"Edit Player.cs: speed becomes 6.","Stage this version","s9-staged"),
    (6,6,4,"git add records speed = 6 in the staging area.","Edit again, without staging","s9-edited"),
    (8,6,4,"Now speed = 8 on disk. Which value will a commit record?","Commit and reveal","s9-committed"),
    (8,6,6,"The commit records 6. The edit to 8 remains unstaged.","Replay example","s9"),
]
for j,(working,staged,committed,explain,label,target) in enumerate(staging_steps):
    els=heading(9,"Git's Three Trees","One tracked script, three versions of its content",ACCENT2)
    for i,(name,value,col,soft) in enumerate([
        ("WORKING DIRECTORY",working,ACCENT,ACCENT_SOFT),
        ("STAGING AREA",staged,ACCENT2,ACCENT2_SOFT),
        ("LAST COMMIT",committed,ACCENT3,ACCENT3_SOFT)]):
        x=[96,470,844][i]
        els += [rect(f"stage-box{i}",x,241,340,230,soft,radius=14,stroke=col,strokeWidth=1.5),
                txt(f"stage-label{i}",x+24,269,292,30,name,14,color=col,weight=700,family=MONOF),
                txt(f"stage-file{i}",x+24,321,292,30,"Player.cs",19,color=MUTED,family=MONOF),
                txt(f"stage-value{i}",x+24,368,292,61,f"speed = {value}",32,weight=700)]
    els += [txt("stage-explain",96,505,1088,65,explain,25,weight=700),
            button("stage-next",label,target,744,580,440),
            txt("stage-note",96,578,610,42,"git add copies content. It does not move or delete your file.",16,color=MUTED,lh=1.4),
           ]+footer(9)
    notes="Begin with an existing tracked Player.cs whose speed is 4 in the last commit. The working copy has already been edited to 6. Click through Stage, Edit again, Commit. Ask students to predict 6 or 8 before committing. The index retains the content captured by git add until staged again. The repository stores all reachable commits; the right panel shows only its latest snapshot for this example. Source: https://git-scm.com/book/en/v2/Appendix-C%3A-Git-Commands-Basic-Snapshotting"
    if not j:slides.append(slide(9,els,notes))
    else:state(9,["s9-staged","s9-edited","s9-committed"][j-1],els,notes)

# ============================================================ 10-12. THE EVERYDAY LOOP (walking chain, mirrors the MDA trio pattern)
LOOP_STEPS = [
    ("01","Edit &amp; Stage","git add",ACCENT,ACCENT_SOFT,ACCENT_GLOW),
    ("02","Commit","git commit",ACCENT2,ACCENT2_SOFT,ACCENT2_GLOW),
    ("03","Sync","git push / pull",ACCENT3,ACCENT3_SOFT,ACCENT3_GLOW),
]
LOOP_X, LOOP_W, LOOP_ROW_H = 808, 376, 108
LOOP_ROW_Y = [208, 338, 468]

def loop_chain(active):
    els = []
    for i, (num, name, cmd, col, soft, gl) in enumerate(LOOP_STEPS):
        y = LOOP_ROW_Y[i]
        on = (i == active)
        done = (i < active)
        els.append(rect(f"loopstep{i}", LOOP_X, y, LOOP_W, LOOP_ROW_H,
                        soft if on else "rgba(255,255,255,0.02)", radius=14,
                        stroke=col if on else BORDER, strokeWidth=1.5 if on else 1,
                        shadow=glow(gl, 30) if on else None))
        els.append(ellipse(f"loopdot{i}", LOOP_X+28, y+30, 10, 10,
                           col if on else ("rgba(154,162,177,0.5)" if done else "rgba(92,100,114,0.5)"),
                           shadow=glow(gl, 14) if on else None))
        els.append(txt(f"loopnum{i}", LOOP_X+50, y+26, 60, 18, num, 11,
                       color=col if on else FAINT, weight=700, family=MONOF,
                       extra={"letterSpacing":2}))
        els.append(txt(f"loopname{i}", LOOP_X+28, y+50, LOOP_W-56, 30, name, 21,
                       color=TEXT if on else ("rgba(154,162,177,0.65)" if done else "rgba(154,162,177,0.4)"),
                       weight=800, family=DISPLAY))
        els.append(txt(f"loopcmd{i}", LOOP_X+28, y+80, LOOP_W-56, 20, cmd, 12,
                       color=col if on else FAINT, family=MONOF, extra={"letterSpacing":0.5}))
        if i < 2:
            els.append(rect(f"looplink{i}", LOOP_X+32, y+LOOP_ROW_H, 2, 22, BORDER2))
    els.append(txt("loopchainnote", LOOP_X, 598, LOOP_W, 60,
                   "Then you're back at step one. Every lab, every day &mdash; the same three-step loop.",
                   12.5, color=FAINT, lh=1.5))
    return els

def loop_slide(n, part, title, col, soft, gl, defn, exk, exbody, bgid):
    return [
        rect(bgid,0,0,W,H,BG),
        kicker(f"kloop{n}",MX,72,f"The everyday loop, step {part} of 3", color=col),
        txt(f"tloop{n}",MX,104,660,70,title,50,weight=800,family=DISPLAY,role="title"),
        rect("loopbox",96,208,680,370,soft,radius=16,stroke=col,strokeWidth=1.5,
             shadow=glow(gl,34)),
        txt(f"loopdef{n}",96+40,244,600,110,defn,18.5,color=TEXT,lh=1.5),
        rect(f"loopdiv{n}",96+40,368,600,1,col,opacity=0.3),
        txt(f"loopexk{n}",96+40,390,600,22,exk,12,color=col,weight=700,family=MONOF,
            extra={"letterSpacing":2}),
        txt(f"loopex{n}",96+40,418,600,190,exbody,16.5,color=MUTED,lh=1.75),
    ]

els = loop_slide(17,1,"Edit &amp; Stage",ACCENT,ACCENT_SOFT,ACCENT_GLOW,
    "You change files like normal &mdash; write code, tweak a prefab, drop in a texture. "
    "<code>git add</code> tells git exactly which of those changes belong in the next snapshot.",
    "COMMANDS YOU'LL ACTUALLY TYPE",
    "git status &nbsp;&mdash;&nbsp; see what changed<br>"
    "git add Assets/Player.cs &nbsp;&mdash;&nbsp; stage its current content<br>"
    "git add . &nbsp;&mdash;&nbsp; stage changes under this folder",
    "bg10") + loop_chain(0) + footer(10)
slides.append(slide(10, els, "Staging is the concept students trip on most: it's not saving, it's choosing. You can edit five files and stage only two — the other three simply aren't part of the next snapshot yet.", transition="fade"))

els = loop_slide(18,2,"Commit",ACCENT2,ACCENT2_SOFT,ACCENT2_GLOW,
    "A commit records the staged content as a snapshot in the local repository. "
    "It cannot silently change later &mdash; that's what makes it a safe point to return to.",
    "COMMANDS YOU'LL ACTUALLY TYPE",
    "git commit -m &quot;Add double-jump input&quot;<br><br>"
    "Write the message like a headline: what changed, not how you felt about it.",
    "bg11") + loop_chain(1) + footer(11)
slides.append(slide(11, els, "Push the habit of small, frequent, honestly-described commits early — 'stuff' or 'fix' as a message is a habit that costs someone (often future-you) real time later. A good commit message answers 'what' in a short sentence.", transition="morph"))

els = loop_slide(19,3,"Sync",ACCENT3,ACCENT3_SOFT,ACCENT3_GLOW,
    "Your commits live locally until you <code>push</code> them to a shared remote (GitHub). "
    "<code>pull</code> fetches remote commits and integrates them into your current branch.",
    "COMMANDS YOU'LL ACTUALLY TYPE",
    "git pull &nbsp;&mdash;&nbsp; get the latest before you start<br>"
    "git push &nbsp;&mdash;&nbsp; share your commits when you're done<br><br>"
    "Start with a clean working tree, then pull. Sync often to reduce divergence.",
    "bg12") + loop_chain(2) + footer(12)
slides.append(slide(12, els, "This is where solo work becomes team work. Drill the 'pull before you push, pull before you start' habit — it's the cheapest possible insurance against the merge conflicts we look at in two slides. Pull fetches and then integrates using the configured merge or rebase policy. Commit or stash local work first.", transition="morph"))

# ============================================================ 13. REMOTES & GITHUB WORKFLOW
els = [
    rect("bg20",0,0,W,H,BG),
    kicker("k20",MX,72,"Where 'push' and 'pull' actually go", color=ACCENT2),
    txt("t20",MX,104,1088,64,"Remotes &amp; the GitHub Workflow",42,weight=800,family=DISPLAY),
]
RGY, RGH = 206, 200
els += [
    rect("rglocal",96,RGY,440,RGH,ACCENT2_SOFT,radius=14,stroke="rgba(85,214,194,0.35)",strokeWidth=1.5,
         extra={"fx":{"enter":"fade-up","order":0}}),
    txt("rglocalk",96+32,RGY+26,376,22,"YOUR COMPUTER",12.5,color=ACCENT2,weight=700,family=MONOF,
        extra={"letterSpacing":2,"fx":{"enter":"fade-up","order":0}}),
    txt("rglocalt",96+32,RGY+54,376,36,"Local Repository",21,weight=800,family=DISPLAY,
        extra={"fx":{"enter":"fade-up","order":0}}),
    txt("rglocald",96+32,RGY+96,376,90,
        "The repo you've been committing to all lecture &mdash; every commit lands here first, offline, before it goes anywhere else.",
        14.5,color=TEXT,lh=1.5,extra={"fx":{"enter":"fade-up","order":0}}),
    rect("rgremote",744,RGY,440,RGH,ACCENT3_SOFT,radius=14,stroke="rgba(108,140,255,0.35)",strokeWidth=1.5,
         extra={"fx":{"enter":"fade-up","order":1}}),
    txt("rgremotek",744+32,RGY+26,376,22,"GITHUB",12.5,color=ACCENT3,weight=700,family=MONOF,
        extra={"letterSpacing":2,"fx":{"enter":"fade-up","order":1}}),
    txt("rgremotet",744+32,RGY+54,376,36,"origin",21,weight=800,family=DISPLAY,
        extra={"fx":{"enter":"fade-up","order":1}}),
    txt("rgremoted",744+32,RGY+96,376,90,
        "The shared copy your team pushes to and pulls from. A normal clone names its source remote &ldquo;origin&rdquo;; you can rename it.",
        14.5,color=TEXT,lh=1.5,extra={"fx":{"enter":"fade-up","order":1}}),
    line("rgpush",556,266,168,1,ACCENT2,strokeWidth=3,dashed=True,lineEnd="arrow",
         extra={"fx":{"loop":{"type":"dash-march","distance":14,"duration":1.6}}}),
    txt("rgpusht",556,240,168,20,"git push",13,color=ACCENT2,family=MONOF,align="center",extra={"letterSpacing":1}),
    line("rgpull",556,332,168,1,ACCENT3,strokeWidth=3,dashed=True,lineStart="arrow",
         extra={"fx":{"loop":{"type":"dash-march","distance":-14,"duration":1.6}}}),
    txt("rgpullt",556,340,168,20,"git pull",13,color=ACCENT3,family=MONOF,align="center",extra={"letterSpacing":1}),
    rect("rgcmdbox",96,432,1088,172,SURFACE,radius=14,stroke=BORDER,strokeWidth=1),
    txt("rgcmdk",96+32,456,600,22,"COMMANDS YOU'LL ACTUALLY TYPE",12,color=ACCENT2,weight=700,family=MONOF,
        extra={"letterSpacing":1.5}),
    txt("rgcmdb",96+32,486,1008,110,
        "git clone &lt;url&gt; &nbsp;&mdash;&nbsp; download an existing remote repo, wired up as &ldquo;origin&rdquo; automatically<br>"
        "git remote -v &nbsp;&mdash;&nbsp; see which remote(s) a repo is wired to, and their URLs<br>"
        "On main: git push origin main &nbsp; or &nbsp; git pull origin main",
        15,color=MUTED,family=MONOF,lh=1.85),
] + footer(13)
slides.append(slide(13, els, "Everything in the everyday loop's 'Sync' step has been pointing at a remote this whole time — this slide just names it. 'origin' is a convention, not a keyword; a repo can have more than one remote, though student projects almost never need to. Today's lab starts with git clone, which wires up origin for you automatically."))

# ============================================================ 14. BRANCHING MODEL
els = [
    rect("bg13",0,0,W,H,BG),
    kicker("k13",MX,72,"Working without stepping on each other", color=ACCENT2),
    txt("t13",MX,104,1088,64,"Branches",50,weight=800,family=DISPLAY),
    txt("t13b",MX,172,1000,30,"A branch names a line of work. New commits move that branch forward.",17,color=MUTED),
]
MAINY, FEATY = 360, 470
BX0, BX1 = 140, 1140
els += [
    line("mainline",BX0,MAINY,BX1-BX0,2,ACCENT2,strokeWidth=3),
    txt("mainlbl",BX0,MAINY-34,200,22,"main",15,color=ACCENT2,weight=700,family=MONOF),
]
main_dots = [BX0+40, BX0+220, 760, BX1-60]
for i,x in enumerate(main_dots):
    els.append(ellipse(f"maindot{i}",x-7,MAINY-7,14,14,ACCENT2,shadow=glow(ACCENT2_GLOW,14),
                        extra={"fx":{"enter":"fade-up","order":i}}))
FORKX, MERGEX = BX0+220, 760
els += [
    line("branchfork",FORKX,MAINY,90,FEATY-MAINY,ACCENT3,strokeWidth=2.5,dashed=True,
         extra={"fx":{"loop":{"type":"dash-march","distance":14,"duration":1.6}}}),
    line("branchline",FORKX+90,FEATY,280,2,ACCENT3,strokeWidth=3),
    path_shape("branchmerge",FORKX+370,MAINY,30,FEATY-MAINY,"M0,110 L30,0",ACCENT3,strokeWidth=2.5,strokeStyle="dashed",
         extra={"fx":{"loop":{"type":"dash-march","distance":14,"duration":1.6}}}),
    txt("featlbl",FORKX,FEATY-34,320,22,"feature/double-jump",15,color=ACCENT3,weight=700,family=MONOF),
]
feat_dots = [FORKX+90, FORKX+230, FORKX+370]
for i,x in enumerate(feat_dots):
    els.append(ellipse(f"featdot{i}",x-7,FEATY-7,14,14,ACCENT3,shadow=glow(ACCENT3_GLOW,14),
                        extra={"fx":{"enter":"fade-up","order":i+4}}))
els += [
    txt("forklbl",FORKX-10,MAINY+14,150,20,"branch",11,color=FAINT,family=MONOF,extra={"letterSpacing":1}),
    txt("mergelbl",MERGEX-70,MAINY+14,150,20,"merge",11,color=FAINT,family=MONOF,extra={"letterSpacing":1}),
    rect("branchnote",96,560,1088,80,SURFACE,radius=12,stroke=BORDER,strokeWidth=1),
    txt("branchnotet",96+28,578,1032,52,
        "Commits on <b>feature/double-jump</b> leave the <b>main</b> branch unchanged until you integrate them. "
        "Commit or stash before switching branches: uncommitted edits can follow you.",
        15.5,color=MUTED,lh=1.5),
] + footer(14)
slides.append(slide(14, els, "The mental model: main is the trunk that always works. A feature branch is a sandbox off to the side. This is the single idea that makes it safe to experiment — walk your finger along the diagram as you narrate fork, work, merge."))

# ============================================================ 15. MERGE CONFLICTS
els = [
    rect("bg14",0,0,W,H,BG),
    kicker("k14",MX,72,"When two people touch the same lines", color=ACCENT2),
    txt("t14",MX,104,1088,64,"Merge Conflicts",50,weight=800,family=DISPLAY),
    rect("mcbox",96,196,600,412,SURFACE2,radius=14,stroke=BORDER2,strokeWidth=1),
    txt("mck",96+28,220,540,22,"WHAT IT LOOKS LIKE",12.5,color=ACCENT3,weight=700,family=MONOF,extra={"letterSpacing":2}),
    txt("mccode",96+28,252,544,340,
        "&lt;&lt;&lt;&lt;&lt;&lt;&lt; HEAD<br>"
        "playerSpeed = 6.5f;<br>"
        "=======<br>"
        "playerSpeed = 8.0f;<br>"
        "&gt;&gt;&gt;&gt;&gt;&gt;&gt; feature/tuning",
        16.5,color=TEXT,family=MONOF,lh=1.85),
]
resolve_steps = [
    "Open the file &mdash; git marks exactly where the two versions disagree.",
    "Decide: keep one side, the other, or write a new line combining both.",
    "Delete the &lt;&lt;&lt;&lt;&lt;&lt;&lt; / ======= / &gt;&gt;&gt;&gt;&gt;&gt;&gt; marker lines.",
    "Test the result, stage the file, then commit to complete this merge.",
]
for i,step in enumerate(resolve_steps):
    y = 232 + i*92
    fx = {"fx":{"enter":"fade-up","order":i}}
    els += [
        ellipse(f"rs{i}dot",728,y+2,26,26,ACCENT2_SOFT,stroke=ACCENT2,strokeWidth=1.5,extra=fx),
        txt(f"rs{i}n",728,y+2,26,26,str(i+1),13,color=ACCENT2,weight=800,family=DISPLAY,align="center",valign="middle",extra=fx),
        txt(f"rs{i}t",772,y-6,392,70,step,15,color=MUTED,lh=1.45,extra=fx),
    ]
els += footer(15)
slides.append(slide(15, els, "This is not a rare failure mode — it's a normal Tuesday on a team project. Demystify it: a conflict is git honestly saying 'I don't know which of these you want', not a sign something is broken. Live-resolve one during lab if time allows."))

# ============================================================ 16. PULL REQUESTS & CODE REVIEW
pr_steps = [
    ("1","Push Your Branch","<code>git push origin feature/double-jump</code> &mdash; your branch, now visible on GitHub."),
    ("2","Open a Pull Request","Propose merging your branch into <code>main</code>. GitHub shows exactly what changed, line by line."),
    ("3","Teammate Reviews","They read the diff, leave comments, request changes, or approve &mdash; before anything touches main."),
    ("4","Merge","Once approved, merge the PR. <code>main</code> has the change, and a permanent record of who reviewed it."),
]
els = [
    rect("bg23",0,0,W,H,BG),
    kicker("k23",MX,72,"The step between 'it works on my machine' and main", color=ACCENT2),
    txt("t23",MX,104,1088,64,"Pull Requests &amp; Code Review",42,weight=800,family=DISPLAY),
]
prx = [96, 376, 656, 936]
for i,(n,name,desc) in enumerate(pr_steps):
    x = prx[i]
    fx = {"fx":{"enter":"fade-up","order":i}}
    els += [
        rect(f"pr{i}",x,206,248,210,SURFACE,radius=14,stroke=ACCENT2,strokeWidth=1.5,extra=fx),
        rect(f"pr{i}nbg",x+24,230,38,38,BG,radius=19,stroke=ACCENT2,strokeWidth=1.5,extra=fx),
        txt(f"pr{i}n",x+24,230,38,38,n,16,weight=800,family=MONOF,color=ACCENT2,align="center",valign="middle",extra=fx),
        txt(f"pr{i}t",x+24,280,200,46,name,17,weight=700,family=DISPLAY,lh=1.2,extra=fx),
        txt(f"pr{i}d",x+24,330,200,78,desc,12,color=MUTED,lh=1.35,extra=fx),
    ]
els += [
    rect("prwhybox",96,444,1088,160,ACCENT2_SOFT,radius=16,stroke="rgba(85,214,194,0.35)",strokeWidth=1,
         extra={"fx":{"enter":"fade-up","order":4}}),
    txt("prwhyk",96+40,472,1008,22,"WHY BOTHER",12.5,color=ACCENT2,weight=700,family=MONOF,
        extra={"letterSpacing":2,"fx":{"enter":"fade-up","order":4}}),
    txt("prwhyb",96+40,500,1008,90,
        "A pull request is a checkpoint, not paperwork: a second pair of eyes catches bugs, spots a conflict early, "
        "and leaves your team a running log of what changed and why &mdash; the same review habit real studios use, "
        "for the same reasons.",
        16,color=TEXT,lh=1.6,extra={"fx":{"enter":"fade-up","order":4}}),
] + footer(16)
slides.append(slide(16, els, "This is the piece that turns 'I know git commands' into 'I can work on a team repo' — most students have only ever pushed straight to main. Frame it plainly: our recommended team rule is to review before merging. GitHub only enforces it when repository protections require approval. Worth demoing live on GitHub if a projector's handy."))

# ============================================================ 17. WHY UNITY PROJECTS ARE DIFFERENT
els = [
    rect("bg15",0,0,W,H,BG),
    kicker("k15",MX,72,"The part git wasn't built for", color=ACCENT2),
    txt("t15",MX,104,1088,64,"Why Unity Projects Are Different",42,weight=800,family=DISPLAY),
]
els += panel("wu1",96,206,528,400,"CODE (.cs)",ACCENT2,None,
    "Git often merges edits to different lines automatically.<br><br>"
    "Overlapping edits can conflict. Read the result and test it before committing.",
    bodycol=TEXT,bg=ACCENT2_SOFT,border=ACCENT2,barcol=ACCENT2,order=0,body_size=19,lh=1.6)
els += panel("wu2",656,206,528,400,"SCENES AND PREFABS",ACCENT3,None,
    "With <b>Force Text</b> serialization, .unity and .prefab files use YAML.<br><br>"
    "UnityYAMLMerge can merge these structures. Review the result in Unity. "
    "Coordinate shared scene edits and use prefabs to reduce overlap.",
    bodycol=TEXT,bg=ACCENT3_SOFT,border=ACCENT3,barcol=ACCENT3,order=1,body_size=18,lh=1.6)
els += footer(17)
slides.append(slide(17, els, "Scenes and prefabs can both use YAML. Binary art assets need a different workflow. Force Text is under Project Settings > Editor > Asset Serialization. Git integration of UnityYAMLMerge requires configuration. Source: https://docs.unity3d.com/6000.0/Documentation/Manual/SmartMerge.html"))

# ============================================================ 18. .GITIGNORE FOR UNITY
gi_rows = [{"cells":[{"html":"Ignore (never commit)","bold":True},{"html":"Why","bold":True}]}]
gi_data = [
    ("Library/","Unity's rebuildable local cache &mdash; gigabytes, regenerates automatically."),
    ("Temp/, Obj/, Logs/","Scratch files from the last build/compile."),
    ("Build/, Builds/","Your exported game &mdash; a product, not a source file."),
    ("UserSettings/, .vs/, .idea/","Your personal editor layout &mdash; not your teammates' business."),
    ("*.csproj, *.sln","Generated by Unity or its IDE integration."),
]
for name,why in gi_data:
    gi_rows.append({"cells":[{"html":f"<code>{name}</code>"},{"html":why}]})
els = [
    rect("bg16",0,0,W,H,BG),
    kicker("k16",MX,72,"The single most-copied file in any Unity repo", color=ACCENT2),
    txt("t16",MX,104,1000,70,".gitignore for Unity",50,weight=800,family=DISPLAY),
    {"id":"gitable","type":"table","x":96,"y":198,"w":700,"h":330,"rotation":0,"opacity":1,
     "fx":{"enter":"fade-up"},
     "columns":[{"w":0.4},{"w":0.6}],
     "header":True,
     "rows":gi_rows,
     "style":{"headerBg":SURFACE2,"headerColor":TEXT,"zebra":True,"borderColor":BORDER,
              "borderWidth":1,"cellPadX":18,"cellPadY":12,"fontSize":14,"color":MUTED,"radius":12}},
    rect("gikeep",836,198,348,330,ACCENT2_SOFT,radius=14,stroke="rgba(85,214,194,0.35)",strokeWidth=1),
    txt("gikeepk",836+28,222,292,22,"ALWAYS TRACK",12.5,color=ACCENT2,weight=700,family=MONOF,extra={"letterSpacing":2}),
    txt("gikeepb",836+28,254,292,250,
        "<code>Assets/</code><br>"
        "<code>Packages/</code><br>"
        "<code>ProjectSettings/</code><br>"
        "<code>Assets/**/*.meta</code><br><br>"
        "This is the actual project &mdash; source, not output.",
        15,color=TEXT,lh=1.9),
    txt("gisrc",96,548,1088,24,"Start from GitHub’s community template: <code>github.com/github/gitignore/blob/main/Unity.gitignore</code>.",
        13.5,color=FAINT,family=MONOF),
] + footer(18)
slides.append(slide(18, els, "Don't make them memorize this list — point out it's one download, added once, per project, on day one. The teaching point is the CATEGORY of thing to ignore (generated/local/output), not the specific folder names."))

# ============================================================ 19. THE .meta GOTCHA
els = [
    rect("bg17",0,0,W,H,BG),
    kicker("k17",MX,72,"The mistake that eats a whole lab session", color=ACCENT),
    txt("t17",MX,104,1088,64,"Don't Ignore .meta Files",46,weight=800,family=DISPLAY),
    rect("metawarn",96,206,1088,150,ACCENT_SOFT,radius=14,stroke="rgba(255,138,61,0.35)",strokeWidth=1),
    txt("metawarnk",96+32,230,1024,24,"EVERY ASSET GETS A .meta FILE &mdash; TRACK IT TOO",13,color=ACCENT,weight=700,family=MONOF,extra={"letterSpacing":1.5}),
    txt("metawarnb",96+32,262,1024,80,
        "The .meta file stores the asset's GUID &mdash; the ID serialized asset references use to "
        "reference that asset. Untrack it, and Unity may hand a different GUID to a teammate's "
        "copy, silently breaking every reference to that asset.",
        16.5,color=TEXT,lh=1.55),
    txt("metasympk",96,392,1000,24,"HOW IT SHOWS UP IN THE WILD",12.5,color=FAINT,weight=700,family=MONOF,extra={"letterSpacing":1.5}),
    txt("metasymp",96,420,1088,90,
        "Missing asset references or Missing (Mono Script) can mean that an asset or its .meta file was lost. "
        "Restore the original pair from Git. Pink materials usually indicate a shader or render-pipeline problem.",
        17,color=MUTED,lh=1.6),
    rect("metafix",96,522,1088,70,SURFACE,radius=12,stroke=BORDER,strokeWidth=1),
    txt("metafixt",96+28,542,1032,32,"MOVE AS A PAIR &mdash; use the Project window so Unity moves the asset and its .meta file together.",
        14.5,color=MUTED,lh=1.45),
] + footer(19)
slides.append(slide(19, els, "Meta files preserve GUIDs and import settings, including for folders. If moving files outside Unity, move their meta files with them. Restore lost originals rather than regenerating GUIDs. Source: https://docs.unity3d.com/6000.0/Documentation/Manual/AssetMetadata.html"))

# ============================================================ 20. GIT LFS FOR BINARY ASSETS
els = [
    rect("bg18",0,0,W,H,BG),
    kicker("k18",MX,72,"When your assets outgrow plain git", color=ACCENT2),
    txt("t18",MX,104,1088,64,"Git LFS for Binary Assets",46,weight=800,family=DISPLAY),
    txt("t18b",MX,172,1000,30,"Large binary assets can make ordinary Git history expensive to clone.",17,color=MUTED),
]
els += panel("lfs1",96,220,528,340,"WITHOUT LFS",FAINT,None,
    "Every version of every texture you've ever committed stays in the repo's "
    "reachable history, even after you delete the current file. Edit a 50MB texture 10 "
    "times and storage can approach 500MB before compression or deduplication.",
    bodycol=MUTED,bg=SURFACE,border=BORDER,barcol=FAINT,order=0,body_size=16,lh=1.7)
els += panel("lfs2",656,220,528,340,"WITH GIT LFS",ACCENT2,None,
    "Git tracks a small pointer file instead of the binary. The actual asset content "
    "lives in separate LFS storage, fetched only when you check out that version. "
    "The repo itself stays small and fast to clone.",
    bodycol=TEXT,bg=ACCENT2_SOFT,border="rgba(85,214,194,0.35)",barcol=ACCENT2,order=1,body_size=16,lh=1.7)
els += [
    txt("lfscmd",96,574,1088,80,"git lfs install<br>git lfs track &quot;*.fbx&quot; &quot;*.wav&quot;<br>git add .gitattributes &nbsp; &mdash; commit the tracking rules too",
        14.5,color=FAINT,family=MONOF),
] + footer(20)
slides.append(slide(20, els, "Choose LFS for large binary asset types your team actually uses. Install Git LFS on every machine, commit .gitattributes, and check storage quotas. Tracking patterns do not migrate existing Git history. Source: https://git-lfs.com/"))

# ============================================================ 21. COMMON PITFALLS & RECOVERY
pitfalls = [
    ("Committed Library/ by accident","Add it to .gitignore, then <code>git rm -r --cached Library</code> to untrack it without deleting your files.",ACCENT),
    ("Wrote a terrible commit message","For a shared commit, usually leave it and improve the next message. Amend only unshared commits you intend to rewrite.",ACCENT2),
    ("Realized the last commit was wrong","<code>git revert HEAD</code> adds a new commit that undoes it &mdash; safe, and keeps the history honest.",ACCENT3),
    ("Uncommitted changes you want gone","Review <code>git diff -- &lt;file&gt;</code> first. <code>git restore -- &lt;file&gt;</code> discards unstaged edits to a tracked file.",ACCENT4),
]
els = [
    rect("bg19",0,0,W,H,BG),
    kicker("k19",MX,72,"You will do at least one of these", color=ACCENT2),
    txt("t19",MX,104,1088,70,"Common Pitfalls &amp; Recovery",44,weight=800,family=DISPLAY),
]
for i,(problem,fix,col) in enumerate(pitfalls):
    y = 206 + i*112
    fx = {"fx":{"enter":"fade-up","order":i}}
    els += [
        rect(f"pf{i}",96,y,1088,96,SURFACE,radius=12,stroke=BORDER,strokeWidth=1,extra=fx),
        rect(f"pf{i}bar",96,y,4,96,col,extra=fx),
        txt(f"pf{i}p",96+28,y+14,1032,26,problem,16.5,weight=700,family=DISPLAY,color=col,extra=fx),
        txt(f"pf{i}f",96+28,y+44,1032,44,fix,14.5,color=MUTED,lh=1.4,extra=fx),
    ]
els += footer(21)
slides.append(slide(21, els, "The framing that matters here: almost every git mistake is recoverable, which is the entire point of version control. Say this out loud — students are often more afraid of git than of the bug they're trying to fix."))

# ============================================================ 22. WORKFLOW CHECKLIST
els = [
    rect("bg20",0,0,W,H,BG),
    kicker("k20",MX,72,"Before you write a line of gameplay code", color=ACCENT2),
    txt("t20",MX,104,1088,70,"Your Project's Workflow Checklist",40,weight=800,family=DISPLAY),
    rect("wc1",96,206,1088,410,SURFACE,radius=14,stroke=BORDER,strokeWidth=1,extra={"fx":{"enter":"fade-up","order":0}}),
    txt("wc1b",96+40,240,1008,360,
        "&#9679;&nbsp; Create the repository <b>before</b> you create a single asset<br>"
        "&#9679;&nbsp; Add a Unity .gitignore on day one &mdash; not after the first bloated commit<br>"
        "&#9679;&nbsp; Commit early, commit often, write messages a stranger could understand<br>"
        "&#9679;&nbsp; One feature branch per feature or level &mdash; keep main always working<br>"
        "&#9679;&nbsp; Never commit <code>Library/</code> or <code>Temp/</code><br>"
        "&#9679;&nbsp; Start clean, pull before editing, and push finished commits",
        20, color=TEXT, lh=2.15, extra={"fx":{"enter":"fade-up","order":0}}),
] + footer(22)
slides.append(slide(22, els, "This is the slide to screenshot. Every item on it is something a past student learned the hard way — frame it as inherited wisdom, not an arbitrary rulebook. Today's lab walks through the first three items live."))

# ============================================================ 23. VERSION CONTROL RECAP
els = [
    rect("bg21",0,0,W,H,BG),
    kicker("k21",MX,72,"Part 1, in one breath", color=ACCENT2),
    txt("t21",MX,104,1000,70,"Version Control Recap",50,weight=800,family=DISPLAY),
    rect("vcrbox",96,220,1088,360,ACCENT2_SOFT,radius=16,stroke="rgba(85,214,194,0.35)",strokeWidth=1),
    txt("vcrb",144,256,992,290,
        "<b>git add</b> stages the current content. <b>git commit</b> records that staged snapshot locally.<br><br>"
        "<b>push</b> shares commits. <b>pull</b> fetches and integrates remote work.<br><br>"
        "Track source assets, their .meta files, Packages and ProjectSettings. Ignore generated caches. "
        "Use text serialization for scenes/prefabs and consider LFS for large binary assets.",
        21,color=TEXT,lh=1.55),
] + footer(23)
slides.append(slide(23, els, "Read this slide slowly, it's the entire section in five sentences. If a student remembers nothing else from Part 1, this paragraph is what they should retain."))

# ============================================================ 24. SECTION BREAK — UNITY EDITOR OVERVIEW
els = [
    rect("bg5",0,0,W,H,BG),
    rect("sb5line",MX,300,120,4,ACCENT,shadow=glow(ACCENT_GLOW,18),
         extra={"fx":{"enter":"fade-up","order":0,"ambient":"kenburns","ken":{"dir":"drift","scale":1.0,"duration":18}}}),
    txt("sb5k",MX,326,700,28,"PART 2 OF TODAY",15,color=ACCENT,weight=700,family=MONOF,extra={"letterSpacing":3,"fx":{"enter":"fade-up","order":0}}),
    txt("sb5t",MX,346,820,160,"The Unity Editor,<br>From the Outside In",58,weight=800,family=DISPLAY,extra={"letterSpacing":-1,"fx":{"enter":"fade-up","order":1}}),
    txt("sb5s",MX,556,820,40,"Git's behind you &mdash; now the windows you'll live in every single lab.",20,color=MUTED,
        extra={"fx":{"enter":"fade-up","order":2}}),
    ellipse("sb5logoglow", 878, 210, 300, 300, ACCENT, opacity=0.14,
            shadow=glow(ACCENT_GLOW, 80),
            extra={"fx":{"enter":"fade-up","order":1,"ambient":"kenburns","ken":{"dir":"drift","scale":1.05,"duration":20}}}),
    ring("sb5logor1", 1028, 360, 240, "rgba(255,138,61,0.32)", strokeWidth=1.5, dashed=True, march=(28,10),
         extra={"fx":{"enter":"fade-up","order":1}}),
    ring("sb5logor2", 1028, 360, 158, "rgba(255,255,255,0.08)", strokeWidth=1, dashed=False,
         extra={"fx":{"enter":"fade-up","order":1}}),
    {"id":"sb5logo","type":"image","x":940,"y":261,"w":176,"h":199,"rotation":0,"opacity":0.92,
     "src":"asset:logo-unity","fit":"contain","fx":{"enter":"fade-up","order":1}},
] + footer(24)
slides.append(slide(24, els, "Second section break of the lecture, and the first time this course opens Unity together as a group activity rather than a slide. Orange is this lecture's Part 2 colour — same family as Lecture 01's own identity colour on the 15-week arc. Git is already behind the room; this is 'the tool' itself, before the scene graph.", transition="fade"))

# ============================================================ 25–30. SCREENSHOT TOUR
# Screenshot has a real custom layout: hierarchy in middle, inspector on the right.
focus_regions=[(526,198,164,199,"1. Hierarchy","Select a GameObject.<br>Children nest beneath parents."),
 (696,198,175,449,"2. Inspector","Inspect the selected object's components and values."),
 (96,198,430,429,"3. Scene view","Navigate and arrange objects.<br>This is the editor's viewpoint."),
 (526,401,170,232,"4. Project","Browse assets and packages.<br>Git also tracks ProjectSettings.")]
for j,(x,y,w,h,label,body_text) in enumerate(focus_regions):
    els=heading(25,"The Editor at a Glance","A real Unity workspace · layouts are customizable")
    els += [shot("tour-screen","editor",96,190,783,501),
            focus("tour-focus",x,y,w,min(h,420)),
            txt("tour-step",908,210,276,52,label,25,weight=800,color=ACCENT),
            txt("tour-explain",908,280,276,145,body_text,21,lh=1.5),
            txt("tour-layout",908,450,276,95,"Follow the panel names. Your layout may look different.",16,color=MUTED,lh=1.5),
            button("tour-next","Next panel" if j<3 else "Replay tour",f"s25-tour-{j+1}" if j<3 else "s25"),
            txt("tour-credit",96,615,780,18,"Unity Manual · Project window screenshot · Unity Technologies",10.5,color=MUTED),
           ]+footer(25)
    # Keep the full screenshot inside the content band, at its original aspect ratio.
    els[3].update(y=186,h=430,w=672)
    # Region coordinates are derived from the original 783 x 501 screenshot.
    reg=els[4]; reg.update(x=96+(x-96)*672/783,y=186+(y-190)*430/501,w=w*672/783,h=h*430/501)
    notes="Click Next panel to morph the highlight through the actual screenshot. Ask students to locate the same panel in their layout. The screenshot shows Cube (11) selected, with its Transform and other components in the Inspector. Source: https://docs.unity3d.com/6000.0/Documentation/Manual/ProjectView.html"
    if j==0:slides.append(slide(25,els,notes))
    else:state(25,f"s25-tour-{j}",els,notes)

els=heading(26,"Scene View vs Game View","Editor viewpoint and camera output")+[
    txt("scene-label",96,182,510,32,"SCENE VIEW",17,color=ACCENT,weight=700),
    txt("game-label",656,182,528,32,"GAME VIEW",17,color=ACCENT,weight=700),
    shot("scene-shot","gizmo",96,225,500,310),shot("game-shot","game",656,225,528,310),
    txt("scene-desc",96,550,510,68,"Navigate freely to place objects.<br>Moving this view does not move the game camera.",18,color=TEXT,lh=1.45),
    txt("game-desc",656,550,528,68,"Preview the cameras and UI.<br>Gizmos can be toggled here too.",18,color=TEXT,lh=1.45),
]+credit(26,"Unity Manual · Transforms / Game view · Different example scenes")
slides.append(slide(26,els,"These screenshots show different Unity example scenes, not a before/after pair. Ask: if I orbit the Scene view, will the player's camera change? No. Game view can show gizmos when enabled; those editor overlays do not ship. Sources: https://docs.unity3d.com/6000.0/Documentation/Manual/class-Transform.html and https://docs.unity3d.com/6000.0/Documentation/Manual/GameView.html"))

# Selection relation is visible in one real editor capture.
for j in range(2):
    els=heading(27,"Selection Links the Windows","Hierarchy selection appears in the Inspector")+[
        shot("selection-shot","editor",96,188,672,430),
        focus("selection-focus",96+(433 if j==0 else 599)*672/783,188+(20 if j==0 else 40)*430/501,(163 if j==0 else 183)*672/783,(206 if j==0 else 395)*430/501,ACCENT3),
        txt("selection-title",818,211,366,66,"1. Select an object" if j==0 else "2. Read its components",26,color=ACCENT3,weight=800),
        txt("selection-body",818,300,366,195,"The Hierarchy lists GameObjects in all loaded scenes.<br><br>Children appear indented beneath their parent." if j==0 else "Cube (11) is selected.<br><br>The Inspector shows its Transform, Mesh Renderer and collider.",22,lh=1.5),
        button("selection-next","Show Inspector" if j==0 else "Replay selection","s27-inspector" if j==0 else "s27",818,w=366),
    ]+credit(27,"Unity Manual · Project window context · Inspector follows selection unless locked")
    notes="Selection drives the Inspector unless it is locked. The selected cube is visible with an outline in Scene view. This is the same screenshot as the overview so students can follow one object. Sources: https://docs.unity3d.com/6000.0/Documentation/Manual/ProjectView.html and https://docs.unity3d.com/6000.0/Documentation/Manual/UsingTheInspector.html"
    if not j:slides.append(slide(27,els,notes))
    else:state(27,"s27-inspector",els,notes)

els=heading(28,"The Project Window &amp; Console","Assets on disk and diagnostic messages")+[
    txt("project-label",96,190,1088,32,"PROJECT WINDOW",18,color=ACCENT2,weight=700),
    shot("project-shot","project",96,226,1088,255),
    txt("project-copy",96,505,1088,58,"Browse Assets and Packages. Unity hides .meta files here.<br>Git also tracks ProjectSettings, which is outside this asset list.",21,lh=1.4),
    button("project-next","Open Console example","s28-console",900,581),
]+credit(28)
slides.append(slide(28,els,"Ask which folders Git should track beyond this asset browser. Then click Open Console example. The source screenshot shows a material context menu, not a Git menu. Sources: https://docs.unity3d.com/6000.0/Documentation/Manual/ProjectView.html and https://docs.unity3d.com/6000.0/Documentation/Manual/Console.html"))
els=heading(28,"The Project Window &amp; Console","Assets on disk and diagnostic messages")+[
    txt("project-label",96,190,1088,32,"CONSOLE",18,color=ACCENT,weight=700),
    shot("console-shot","console",96,239,790,344),
    txt("console-copy",918,242,266,250,"1. Select a message.<br><br>2. Read its details and stack trace.<br><br>3. Inspect the reported script line.",21,lh=1.5),
    button("project-next","Back to Project","s28",900,581),
]+credit(28)
state(28,"s28-console",els,"The messages are from Unity's documentation example, not this course project. Errors provide clues, not necessarily the root cause. Double-click a script message to navigate to code. Source: https://docs.unity3d.com/6000.0/Documentation/Manual/Console.html")

els=heading(29,"Toolbar &amp; Transform Tools","Unity 6 places tools in the Scene view overlay")+[
    shot("toolbar-shot","toolbar",96,185,760,345),
    txt("tool-keys",891,207,293,250,"<b>Q</b> View / Hand<br><b>W</b> Move<br><b>E</b> Rotate<br><b>R</b> Scale<br><b>T</b> Rect<br><b>Y</b> Transform",21,lh=1.65),
    txt("play-controls",96,552,760, 60,"Play runs the scene. Pause holds it.<br>Step advances one frame while paused.",21,lh=1.4),
    txt("tool-focus",891,506,293,110,"Shortcuts apply in Scene view and can be customized.",17,color=MUTED,lh=1.5),
]+credit(29,"Unity Manual · Toolbar screenshot (Unity 6 Preview) · Control placement varies by version")
slides.append(slide(29,els,"The source image labels Unity 6 Preview, so identify it as such. Compare the Play/Pause/Step controls at top center with the transform overlay inside Scene view. Rect works with both 2D and 3D objects, and is especially useful for UI. Sources: https://docs.unity3d.com/6000.0/Documentation/Manual/Toolbar.html and https://docs.unity3d.com/6000.0/Documentation/Manual/PositioningGameObjects.html"))

# Explicit teaching values beside an untouched screenshot; never fake Unity UI values.
for j,(phase,value,explain) in enumerate([
    ("EDIT MODE",0,"Saved scene: the object's X position is 0."),
    ("PLAY MODE",3,"During Play, move the scene object to X = 3. Predict what happens when we stop."),
    ("STOPPED",0,"Stopping restores this scene object's X position to 0. Reapply useful changes in Edit Mode and save.")]):
    els=heading(30,"Play Mode: What Reverts?","Predict first, then reveal the result")+[
        shot("play-controls-shot","play",96,184,130, 30),
        shot("play-reference","transform",96,221,500,165),
        txt("play-ref-label",96,402,500,58,"Actual Inspector reference<br>Teaching values shown at right",16,color=MUTED,lh=1.45),
        txt("play-phase",688,204,496,30,phase,18,color=ACCENT,weight=700),
        txt("play-value",688,251,496,90,f"X = {value}",64,weight=800),
        txt("play-explain",688,361,496,125,explain,22,lh=1.5),
        txt("play-caveat",96,509,500,99,"Scene-object edits revert on Stop.<br>Asset edits, such as materials or ScriptableObjects, may persist.",18,color=MUTED,lh=1.5),
        button("play-next",["Enter Play + change X","Stop and reveal","Replay example"][j],["s30-play","s30-stop","s30"][j],688,w=496),
    ]+credit(30)
    notes="Click through the example. This animation changes teaching labels, not the source screenshot. The exception matters: changing an asset on disk during Play can persist. Copy useful component values, stop, paste them back and save the scene. Asset persistence: https://docs.unity3d.com/6000.1/Documentation/Manual/class-ScriptableObject.html Sources: https://docs.unity3d.com/6000.0/Documentation/Manual/GameView.html and https://docs.unity3d.com/6000.0/Documentation/Manual/class-Transform.html"
    if not j:slides.append(slide(30,els,notes))
    else:state(30,["s30-play","s30-stop"][j-1],els,notes)

# ============================================================ 31. SECTION BREAK — SCENE & GAMEOBJECT HIERARCHY
els = [
    rect("bg22",0,0,W,H,BG),
    rect("sb22line",MX,300,120,4,ACCENT3,shadow=glow(ACCENT3_GLOW,18),
         extra={"fx":{"enter":"fade-up","order":0,"ambient":"kenburns","ken":{"dir":"drift","scale":1.0,"duration":18}}}),
    txt("sb22k",MX,326,700,28,"PART 3 OF TODAY",15,color=ACCENT3,weight=700,family=MONOF,extra={"letterSpacing":3,"fx":{"enter":"fade-up","order":0}}),
    txt("sb22t",MX,346,1088,160,"Scene &amp; GameObject<br>Hierarchy",58,weight=800,family=DISPLAY,extra={"letterSpacing":-1,"fx":{"enter":"fade-up","order":1}}),
    txt("sb22s",MX,556,1000,40,"Scenes organize GameObjects. Components give those objects capabilities.",20,color=MUTED,
        extra={"fx":{"enter":"fade-up","order":2}}),
] + footer(31)
slides.append(slide(31, els, "Third part, same energy shift as the git section — but this time it's the part they'll be staring at in the editor every single lab from here on. This is the vocabulary for reading anyone's Hierarchy panel, including their own, six weeks from now.", transition="fade"))

# ============================================================ 32. WHAT IS A SCENE
els = [
    rect("bg23",0,0,W,H,BG),
    kicker("k23",MX,72,"Defining our terms", color=ACCENT3),
    txt("t23",MX,104,1088,64,"What Is a Scene?",50,weight=800,family=DISPLAY),
    rect("qc23",96,196,1088,110,SURFACE2,radius=14,stroke=BORDER2,strokeWidth=1),
    txt("qc23q",96+32,216,1024,50,
        "A Scene stores a collection of GameObjects and scene settings. "
        "Use scenes for a level, a menu, or part of a larger world.",18,color=TEXT,lh=1.4),
    txt("qc23a",96+32,268,1024,22,"Multiple scenes can be loaded together.",13.5,color=MUTED,family=MONOF),
]
scene_facts = [
    ("Saved as a file","A Scene is a <code>.unity</code> file &mdash; YAML when using Force Text serialization. Git can diff it; UnityYAMLMerge can help merge it.",ACCENT2),
    ("A project has many","MainMenu, Level01, Level02 &mdash; separate scenes, loaded one (or more) at a time.",ACCENT3),
    ("A tree of objects","Open a scene and the Hierarchy panel is what you're actually looking at.",ACCENT4),
]
for i,(name,desc,col) in enumerate(scene_facts):
    x = [96,470,844][i]
    fx = {"fx":{"enter":"fade-up","order":i}}
    els += [
        rect(f"sf{i}",x,340,340,220,SURFACE,radius=14,stroke=BORDER,strokeWidth=1,extra=fx),
        rect(f"sf{i}bar",x,340,340,4,col,extra=fx),
        txt(f"sf{i}t",x+24,368,292,30,name,17,weight=700,family=DISPLAY,color=col,extra=fx),
        txt(f"sf{i}d",x+24,404,292,140,desc,14.5,color=MUTED,lh=1.55,extra=fx),
    ]
els += footer(32)
slides.append(slide(32, els, "Scenes and prefabs both support text serialization. A scene is a saved collection, not necessarily the entire runtime world. Source: https://docs.unity3d.com/6000.0/Documentation/Manual/SmartMerge.html"))

# ============================================================ 33. GAMEOBJECTS AND COMPONENTS
els=heading(33,"GameObjects &amp; Components","A GameObject holds components",ACCENT3)+[
    shot("components-shot","editor",96,188,672,430),
    focus("components-focus",610,257,157,265,ACCENT3),
    txt("components-title",818,205,366, 80,"One object, several capabilities",27,weight=800,color=ACCENT3),
    txt("components-list",818,295,366,263,"<b>Transform</b> stores placement.<br><br><b>Mesh Renderer</b> displays a mesh.<br><br><b>Collider</b> defines a collision shape.<br><br>Scripts can add custom behavior.",19,lh=1.4),
    txt("components-note",818,568,366,46,"UI objects use RectTransform, a specialized Transform.",15,color=MUTED,lh=1.4),
]+credit(33)
slides.append(slide(33,els,"The Inspector shows an actual 3D cube, so name the components visible in this example. A 2D player would instead use Sprite Renderer, Collider 2D and often Rigidbody 2D. Transform cannot be removed. GameObjects also have identity and active state. Sources: https://docs.unity3d.com/6000.0/Documentation/Manual/class-Transform.html and https://docs.unity3d.com/6000.0/Documentation/Manual/UsingTheInspector.html"))

for j,(label,row,explain) in enumerate([
    ("Position",44,"Where the object is, relative to its parent."),
    ("Rotation",82,"Its orientation relative to its parent. The Inspector displays degrees."),
    ("Scale",118,"Its size relative to its parent. A scale of 1 keeps the original size.")]):
    els=heading(34,"The Transform Component","Position, rotation and scale",ACCENT3)+[
        shot("transform-shot","transform",96,229,650,215),
        focus("transform-row",106,229+row*1.3,630, 42,ACCENT3),
        txt("transform-name",818,235,366, 50,label,32,weight=800,color=ACCENT3),
        txt("transform-desc",818,313,366,155,explain,23,lh=1.5),
        txt("transform-rule",96,492,650,110,"Inspector values are local to the parent.<br>For a root object, local position and rotation are also world position and rotation.",20,lh=1.5),
        button("transform-next","Next property" if j<2 else "Replay properties",f"s34-{j+1}" if j<2 else "s34",818,w=366),
    ]+credit(34)
    notes="Click to move the highlight across the real Inspector rows. X/Y/Z are not screen pixels. Scale is dimensionless. A UI RectTransform adds layout properties. Source: https://docs.unity3d.com/6000.0/Documentation/Manual/class-Transform.html"
    if not j:slides.append(slide(34,els,notes))
    else:state(34,f"s34-{j}",els,notes)

# Adapt the existing hierarchy diagram into a numerical before/after morph.
for j in range(2):
    offset=170*j
    els=heading(35,"Parents Move Their Children","Local stays fixed while world position changes",ACCENT3)+[
        shot("parent-reference","hierarchy",96,205,280,314),
        txt("parent-ref-label",96,541,280, 60,"Actual Unity Hierarchy<br>Child 3 is inside Child 2",16,color=MUTED,lh=1.4),
        txt("parent-example",430,196,754, 30,"TEACHING EXAMPLE · X AXIS ONLY",13,color=ACCENT3,family=MONOF),
        rect("parent-body",450+offset,267,240, 70,ACCENT3_SOFT,radius=10,stroke=ACCENT3,strokeWidth=2),
        txt("parent-name",470+offset,280,200,44,f"Parent X = {2+3*j}",22,weight=700),
        rect("child-body",560+offset,364,240,70,ACCENT2_SOFT,radius=10,stroke=ACCENT2,strokeWidth=2),
        txt("child-name",580+offset,377,200,44,"Child local X = 1",19,weight=700),
        line("parent-join",570+offset,337,110,27,ACCENT3,strokeWidth=2),
        txt("parent-equation",430,472,754,45,f"World X = parent X + local X = {2+3*j} + 1 = {3+3*j}",24,weight=700),
        txt("parent-assume",430,529,754, 60,"Assume no parent rotation and scale (1, 1, 1).<br>Rotation and scale also affect a child's world transform.",17,color=MUTED,lh=1.4),
        button("parent-next","Move parent +3" if not j else "Reset positions","s35-moved" if not j else "s35",900,590,284),
    ]+credit(35)
    notes="Ask for the child's local and world X before clicking Move parent +3. Both boxes translate together, local X stays 1, world X changes from 3 to 6. The screenshot establishes actual nesting; the separate diagram is a simplified teaching example. Deleting or disabling a parent also affects descendants. Source: https://docs.unity3d.com/6000.0/Documentation/Manual/class-Transform.html"
    if not j:slides.append(slide(35,els,notes))
    else:state(35,"s35-moved",els,notes)

# ============================================================ 36. ORGANIZING A SCENE
els=heading(36,"Organizing a Scene","Purposeful grouping keeps the Hierarchy readable",ACCENT3)+[
    shot("organization-shot","parenting",96,191,300,438),
    txt("organization-example",440,198,744, 50,"Read a real scene hierarchy",28,weight=800,color=ACCENT3),
    txt("organization-copy",440,269,744,257,
        "<b>GameSystem</b> groups shared systems.<br><br>"
        "<b>Character</b> contains CharacterRoot and Audio.<br><br>"
        "<b>Target</b> groups several enemy instances.<br><br>"
        "Descriptive parents help you find and manipulate related objects.",22,lh=1.4),
    txt("organization-rule",440,548,744,76,"Empty parents are GameObjects, not folders. They still have a Transform cost.<br>Keep organizational parents at position 0, rotation 0 and scale 1.",17,color=MUTED,lh=1.5),
]+credit(36)
slides.append(slide(36,els,"Use the actual GameSystem, Character and Target rows to explain purposeful grouping. Prefab instance names can appear blue, as in this example. These are GameObjects, not filesystem directories or namespaces; duplicate names remain possible. Avoid needless deep nesting. Source: https://docs.unity3d.com/6000.0/Documentation/Manual/class-Transform.html"))

# ============================================================ 37. SCENES AT SCALE
els = [
    rect("bg28",0,0,W,H,BG),
    kicker("k28",MX,72,"A quick look ahead", color=ACCENT3),
    txt("t28",MX,104,1088,64,"Scenes at Scale",50,weight=800,family=DISPLAY),
    rect("scb",96,222,1088,340,SURFACE,radius=14,stroke=BORDER,strokeWidth=1),
    txt("scbk",96+40,256,1008,24,"ONE PROJECT, MANY SCENES",13,color=ACCENT3,weight=700,family=MONOF,extra={"letterSpacing":1.5}),
    txt("scbb",96+40,288,1008,120,
        "MainMenu.unity, Level01.unity, Level02.unity, GameOver.unity &mdash; a real project "
        "is a small library of scenes, not one giant one. Only one loads at a time by default; "
        "your code decides which to load and when.",
        17,color=TEXT,lh=1.65),
    rect("scbdiv",96+40,412,1008,1,BORDER),
    txt("scbfuture",96+40,432,1008,90,
        "How scenes actually get loaded, unloaded, and handed data between them &mdash; that's "
        "a later lecture, once you have scripts to drive it. Today, just the intuition: "
        "Single loading replaces loaded scenes; Additive loading keeps existing scenes alongside the new one.",
        15.5,color=MUTED,lh=1.6),
] + footer(37)
slides.append(slide(37, els, "Deliberately light-touch — the point is only to stop 'a game is one giant scene' from becoming a misconception, not to teach SceneManager yet. That's Bloom L2 territory: understand it exists, don't implement it yet."))

# ============================================================ 38. WORKED COMMIT
els=heading(38,"A Scene Edit Becomes a Commit","Existing scene, new Player GameObject",ACCENT2)+[
    txt("commit-action",96,199,1088,80,"Add a Player to an <b>existing, tracked scene</b> and save it.<br>Assume the sprite and PlayerController script already exist in Git.",23,lh=1.5),
    txt("commit-status",96,314,1088,70,"git status --short<br> M Assets/Scenes/Level01.unity",23,color=ACCENT2,family=MONOF,lh=1.5),
    txt("commit-meta",96,408,1088,77,"The scene's .meta file usually stays unchanged: its GUID identifies the scene.<br>A new asset needs its own .meta file committed alongside it.",21,lh=1.5),
    txt("commit-commands",96,522,1088, 90,"git add Assets/Scenes/Level01.unity<br>git diff --cached<br>git commit -m &quot;Add Player to Level01&quot;",18,color=ACCENT2,family=MONOF,lh=1.55),
]+footer(38)
slides.append(slide(38,els,"Read git status after saving. Editing scene contents changes the .unity file, not necessarily the existing .meta file. If you also create PlayerController.cs, stage that script and its .meta; new sprites and folders need their pairs too. A newly created scene needs both scene and meta. Sources: https://docs.unity3d.com/6000.0/Documentation/Manual/AssetMetadata.html and https://git-scm.com/docs/git-add"))

# ============================================================ 39. KEY TAKEAWAYS
els = [
    rect("bg30",0,0,W,H,BG),
    kicker("k30",MX,72,"If you remember nothing else", color=ACCENT2),
    txt("t30",MX,104,1088,70,"Key Takeaways",56,weight=800,family=DISPLAY),
]
takeaways = [
    ("Commit focused changes","Small, focused commits make changes easier to review and recover. Push important work to a remote.",ACCENT2),
    ("Components give objects capabilities","Components provide capabilities. Every GameObject has a Transform, or a RectTransform for UI.",ACCENT3),
    ("Keep the project easy to navigate","A clean .gitignore and a tidy Hierarchy make teamwork easier from the first lab.",ACCENT4),
]
for i,(t,d,col) in enumerate(takeaways):
    y = 232 + i*136
    fx = {"fx":{"enter":"fade-up","order":i}}
    els += [
        rect(f"tk{i}",96,y,1088,116,SURFACE,radius=14,stroke=BORDER,strokeWidth=1,extra=fx),
        rect(f"tk{i}bar",96,y,5,116,col,extra=fx),
        txt(f"tk{i}n",96+32,y+18,60,30,f"0{i+1}",18,color=col,weight=800,family=MONOF,extra=fx),
        txt(f"tk{i}t",96+100,y+18,940,32,t,21,weight=800,family=DISPLAY,extra=fx),
        txt(f"tk{i}d",96+100,y+56,940,50,d,15.5,color=MUTED,lh=1.4,extra=fx),
    ]
els += footer(39)
slides.append(slide(39, els, "Read these three out loud slowly, same as Lecture 01's takeaways slide — this is the version students should be able to repeat back next week, even once the command syntax has faded."))

# ============================================================ 40. NEXT UP
els = [
    rect("bg31",0,0,W,H,BG),
    kicker("k31",MX,72,"Looking ahead"),
    txt("t31",MX,104,1088,70,"Next Up",56,weight=800,family=DISPLAY),
    rect("nx1",96,232,528,246,SURFACE,radius=14,stroke=BORDER,strokeWidth=1,extra={"fx":{"enter":"fade-up","order":0}}),
    rect("nx1bar",96,232,528,6,ACCENT2,extra={"fx":{"enter":"fade-up","order":0}}),
    txt("nx1k",96+32,264,460,24,"TODAY'S LAB",13,color=ACCENT2,weight=700,family=MONOF,extra={"letterSpacing":2,"fx":{"enter":"fade-up","order":0}}),
    txt("nx1t",96+32,294,460,44,"Git Setup &amp; Your First Commit",22,weight=700,family=DISPLAY,extra={"fx":{"enter":"fade-up","order":0}}),
    txt("nx1d",96+32,346,460,110,"Install Git, create a GitHub account, initialize a Unity repo with the right .gitignore, and make your first real commit.",16.5,color=MUTED,lh=1.6,extra={"fx":{"enter":"fade-up","order":0}}),
    rect("nx2",656,232,528,246,SURFACE,radius=14,stroke=BORDER,strokeWidth=1,extra={"fx":{"enter":"fade-up","order":1}}),
    rect("nx2bar",656,232,528,6,ACCENT3,extra={"fx":{"enter":"fade-up","order":1}}),
    txt("nx2k",656+32,264,460,24,"UPCOMING TOPICS",13,color=ACCENT3,weight=700,family=MONOF,extra={"letterSpacing":2,"fx":{"enter":"fade-up","order":1}}),
    txt("nx2t",656+32,294,460,44,"Components, Materials &amp; Prefabs",22,weight=700,family=DISPLAY,extra={"fx":{"enter":"fade-up","order":1}}),
    txt("nx2d",656+32,346,460,110,"Explore lights and materials, build reusable prefabs, and block out a level. C# scripting follows in the course outline.",16.5,color=MUTED,lh=1.6,extra={"fx":{"enter":"fade-up","order":1}}),
    rect("nxread",96,510,1088,74,ACCENT2_SOFT,radius=12,stroke="rgba(85,214,194,0.3)",strokeWidth=1,extra={"fx":{"enter":"fade-up","order":2}}),
    txt("nxreadt",96+28,533,1032,30,"Before then: install <b>Git</b> and create a free <b>GitHub</b> account &mdash; bring a laptop with both ready for lab.",16.5,color=TEXT,extra={"fx":{"enter":"fade-up","order":2}}),
] + footer(40)
slides.append(slide(40, els, "The course outline places components, lights, materials and prefabs before C# scripting. Lecture numbering has shifted, so this card names upcoming topics without asserting a date. Source: course/CS464-Course-Outline.docx, Weeks 4–5. Lab practice: Git setup and a first commit."))

# ============================================================ 41. THANK YOU
els = [
    rect("bg32",0,0,W,H,BG),
    rect("tf2", MX, 220, 64, 3, ACCENT2, shadow=glow(ACCENT2_GLOW, 18),
         extra={"fx":{"enter":"fade-up","order":0,"ambient":"kenburns","ken":{"dir":"drift","scale":1.0,"duration":16}}}),
    txt("tyk",MX,256,700,28,"SEE YOU IN LAB",15,color=ACCENT2,weight=700,family=MONOF,extra={"letterSpacing":3,"fx":{"enter":"fade-up","order":0}}),
    txt("tyt",MX,292,1088,120,"Questions?",76,weight=800,family=DISPLAY,extra={"letterSpacing":-1,"fx":{"enter":"fade-up","order":1}}),
    rect("tydiv",MX,428,340,2,BORDER2,extra={"fx":{"enter":"fade-up","order":2}}),
    txt("typrompt",MX,456,760,80,"One thing to bring to lab: create a Git repository for any folder on your computer and make one real commit.",19,color=MUTED,lh=1.55,extra={"fx":{"enter":"fade-up","order":2}}),
    txt("tycontact",MX,560,700,30,"hello@madratzz.net &nbsp;&middot;&nbsp; muhammadraza.vf@itu.edu.pk",15,color=FAINT,family=MONOF,extra={"fx":{"enter":"fade-up","order":3}}),
] + footer(41)
slides.append(slide(41, els, "Close on the discussion prompt — a soft assignment that gets everyone touching git before lab even starts. Stay after for individual questions, especially from anyone whose laptop needs Git installed."))

# Ambient motion sits behind the slide content. Reuse ids on optional states so
# opening a teaching example does not introduce a new layer of decorative motion.
def ambient_background(col, expressive=False):
    elements = []
    if expressive:
        elements.append(ellipse(
            "ambient-haze", 906, 66, 270, 270, col, opacity=0.045,
            extra={"blur": 65, "fx": {"ambient": "kenburns",
                   "ken": {"dir": "drift", "scale": 1.10, "duration": 24}}}))
    positions = ([(40, 146, 3), (58, 386, 4), (43, 594, 3),
                  (1218, 124, 3), (1236, 299, 4), (1220, 505, 3)]
                 if expressive else [(43, 198, 2.5), (1234, 550, 2.5)])
    for i, (x, y, size) in enumerate(positions):
        particle = ellipse(f"ambient-particle-{i}", x, y, size, size,
                           col, opacity=0.24 if expressive else 0.12)
        particle["fx"] = {"loop": {"type": "motion-path",
            "path": orbit_path(4 if expressive else 2, start_deg=-90,
                               ry=12 if expressive else 5),
            "duration": 28 + i * 5}}
        elements.append(particle)
    return elements


def apply_3d_logo(element):
    # The transparent Blender render includes eased assembly and fading ripples.
    # Its square frame has padding, so enlarge the slot to retain logo size.
    cx, cy = element["x"] + element["w"] / 2, element["y"] + element["h"] / 2
    side = element["h"] * (1.30 * 5.2 / 3.9)
    element.update(x=cx-side/2, y=cy-side/2, w=side, h=side,
                   src="asset:logo-unity-3d", opacity=1)
    element.pop("fx", None)


section_colors = {1: ACCENT2, 5: ACCENT2, 24: ACCENT, 31: ACCENT3, 41: ACCENT2}
for current in slides + teaching_states:
    number = int(current.get("stateOf", current["id"])[1:])
    col = section_colors.get(number, ACCENT2 if number < 24 else
                             ACCENT if number < 31 else ACCENT3)
    current["elements"][1:1] = ambient_background(col, number in section_colors)

    # Soften the existing logo glow and retain the previously overridden ring loop.
    for element in current["elements"]:
        if element["id"] in ("cvlogo", "sb5logo"):
            apply_3d_logo(element)
        elif element["id"] in ("cvlogoglow", "sb5logoglow"):
            element.update(opacity=0.06, blur=38)
            element["fx"] = {"ambient": "kenburns",
                             "ken": {"dir": "drift", "scale": 1.08, "duration": 12}}
        elif element["id"] in ("cvlogor1", "sb5logor1"):
            element["fx"] = {"loop": {"type": "dash-march", "distance": 34,
                                      "duration": 24}}

    if number in (5, 31, 41):
        cx, cy = 1032, 318
        logo = {"id": "ambient-unity-logo", "type": "image", "x": cx-77,
                "y": cy-87, "w": 154, "h": 174, "rotation": 0,
                "opacity": 0.84, "src": "asset:logo-unity", "fit": "contain"}
        apply_3d_logo(logo)
        current["elements"] += [
            ellipse("ambient-logo-glow", cx-130, cy-130, 260, 260,
                    col, opacity=0.06, extra={"blur": 38,
                    "fx": {"ambient": "kenburns", "ken": {
                        "dir": "drift", "scale": 1.08, "duration": 12}}}),
            ring("ambient-logo-ring", cx, cy, 226, col, strokeWidth=1.2,
                 opacity=0.25, march=(34, 24)),
            logo,
        ]

print(f"Main slides built: {len(slides)}; animation states: {len(teaching_states)}")

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = json.load(open(os.path.join(HERE, "fonts", "fonts.json"), encoding="utf-8"))
PHOTO = json.load(open(os.path.join(HERE, "fonts", "photo-asset.json"), encoding="utf-8"))
LOGO = json.load(open(os.path.join(HERE, "fonts", "unity-logo-asset.json"), encoding="utf-8"))
import base64
from pathlib import Path
screenshot_dir = Path(HERE) / "screenshots"
screenshot_sources = json.loads((screenshot_dir / "sources.json").read_text())
used_screenshots = {e["src"][6:] for sl in slides + teaching_states for e in sl["elements"] if e.get("src", "").startswith("asset:unity-")}
SCREENSHOTS = {"unity-" + item["id"]: "data:image/png;base64," + base64.b64encode((screenshot_dir / item["file"]).read_bytes()).decode() for item in screenshot_sources if "unity-" + item["id"] in used_screenshots}
ASSETS = {**FONTS, **PHOTO, **LOGO, **SCREENSHOTS}
ASSETS["logo-unity-3d"] = "data:image/webp;base64," + base64.b64encode(
    (Path(HERE) / "logo-3d" / "unity-logo-assembly.webp").read_bytes()).decode()
# State slides are optional, presenter-controlled animations, excluded from page totals.
slides.extend(teaching_states)

doc = {
    "format": "bento/slides",
    "version": 1,
    "title": "CS464 — Lecture 02: Inside Unity",
    "size": {"width": W, "height": H},
    "theme": {
        "background": BG,
        "color": TEXT,
        "accent": ACCENT2,
        "fontFamily": BODYF
    },
    "meta": {
        "author": "Muhammad Raza Butt",
        "company": "Information Technology University",
        "subject": "CS464 — Game Development",
        "event": "Lecture 02"
    },
    "fonts": [
        {"family": "Instrument Sans", "asset": "font-instrument", "weight": "100 900"},
        {"family": "Space Mono", "asset": "font-spacemono", "weight": "400"},
        {"family": "Space Mono", "asset": "font-spacemono-bold", "weight": "700"},
    ],
    "assets": ASSETS,
    "present": {"progress": True},
    "slides": slides
}

json_str = json.dumps(doc, ensure_ascii=False)
json_str_escaped = json_str.replace("<", "\\u003c")

path = os.path.join(HERE, "..", "CS464-Lecture-02-Inside-Unity.bento.html")
content = open(path, encoding="utf-8").read()

import re
pattern = re.compile(r'(<script type="application/bento\+json" id="bento-doc">)(.*?)(</script>)', re.S)
new_content, n = pattern.subn(lambda m: m.group(1) + json_str_escaped + m.group(3), content, count=1)
if n != 1:
    raise SystemExit(f"Expected exactly 1 bento-doc block, found {n} substitutions")

with open(path, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"Wrote {path} ({len(new_content)} bytes)")
