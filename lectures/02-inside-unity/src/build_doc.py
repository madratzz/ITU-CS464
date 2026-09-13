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

TOTAL = 39

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


# ============================================================ 1. COVER
els = [
    rect("bg1",0,0,W,H,BG),
    rect("cf2", MX, 96, 64, 3, ACCENT2, shadow=glow(ACCENT2_GLOW, 18)),
    txt("k1", MX, 132, 700, 30, "CS464 &middot; GAME DEVELOPMENT &middot; FALL 2025", 15, color=ACCENT2,
        weight=700, family=MONOF, extra={"letterSpacing":3}),
    txt("t1", MX, 230, 1100, 220, "Lecture 02", 128, color=TEXT, weight=800, family=DISPLAY,
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
    {"id":"cvlogo","type":"image","x":986-120,"y":286-135,"w":240,"h":271,"rotation":0,"opacity":1,
     "src":"asset:logo-unity","fit":"contain"},
]
slides.append(slide(1, els, "We open Unity's version-control and project-structure story today — no laptops open yet, this half is still concepts. Callback to last lecture's 'next up' slide: this is exactly what was promised. Teal is this lecture's colour, same as Act II on the 15-week arc.", transition="none"))

# ============================================================ 2. AGENDA
agenda_parts = [
    ("PART 1", "Unity Editor Overview", ACCENT, [
        "01&nbsp;&nbsp;The editor at a glance",
        "02&nbsp;&nbsp;Scene View vs Game View",
        "03&nbsp;&nbsp;Hierarchy &amp; Inspector",
        "04&nbsp;&nbsp;Project window &amp; Console",
        "05&nbsp;&nbsp;Toolbar &amp; Play Mode",
    ]),
    ("PART 2", "Version Control", ACCENT2, [
        "01&nbsp;&nbsp;Why solo file-juggling breaks down",
        "02&nbsp;&nbsp;Git's model &amp; the everyday loop",
        "03&nbsp;&nbsp;Branching &amp; merge conflicts",
        "04&nbsp;&nbsp;Making Unity projects behave",
        "05&nbsp;&nbsp;A workflow checklist",
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
slides.append(slide(2, els, "Three parts today, not two — the Unity Environment Tour moved out of lab and into the lecture itself, so we walk the editor together before touching git or the scene graph. All three feed CLO-2 directly. Today's lab (Git Setup & Your First Commit) is where Part 2 gets practiced hands-on."))

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
    txt("t4",MX,104,1100,70,"Learning Outcomes",56,weight=800,family=DISPLAY),
    rect("clobox",96,182,1088,94,SURFACE2,radius=14,stroke=BORDER2,strokeWidth=1),
    txt("clok",96+32,198,120,22,"CLO-2",13,color=ACCENT2,weight=700,family=MONOF,extra={"letterSpacing":2}),
    txt("clot",96+32,222,1024,46,
        "Configure the Unity environment, version control, and basic scene hierarchy.",
        18,color=TEXT),
    txt("clob",96+32,266,1024,20,"Bloom Level &mdash; L2 &middot; Understand",13.5,color=MUTED,family=MONOF),
]
clo_parts = [
    ("Unity Environment","Editor layout, the core windows, and Play Mode.","THIS LECTURE &middot; PART 1", ACCENT),
    ("Version Control","Git's model, the daily loop, and Unity-specific gotchas.","THIS LECTURE &middot; PART 2", ACCENT2),
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
slides.append(slide(4, els, "CLO-2 has three parts and today covers all of them in one sitting — the environment tour moved out of lab and into the lecture itself. Part 1 is conceptual (we open Unity together for real), Parts 2-3 are scaffolding for git and the scene graph."))

# ============================================================ 5. SECTION BREAK — UNITY EDITOR OVERVIEW
els = [
    rect("bg5",0,0,W,H,BG),
    rect("sb5line",MX,300,120,4,ACCENT,shadow=glow(ACCENT_GLOW,18),
         extra={"fx":{"enter":"fade-up","order":0,"ambient":"kenburns","ken":{"dir":"drift","scale":1.0,"duration":18}}}),
    txt("sb5k",MX,326,700,28,"PART 1 OF TODAY",15,color=ACCENT,weight=700,family=MONOF,extra={"letterSpacing":3,"fx":{"enter":"fade-up","order":0}}),
    txt("sb5t",MX,346,820,160,"The Unity Editor,<br>From the Outside In",58,weight=800,family=DISPLAY,extra={"letterSpacing":-1,"fx":{"enter":"fade-up","order":1}}),
    txt("sb5s",MX,556,820,40,"Before git, before scenes &mdash; the windows you'll live in every single lab.",20,color=MUTED,
        extra={"fx":{"enter":"fade-up","order":2}}),
    ellipse("sb5logoglow", 878, 210, 300, 300, ACCENT, opacity=0.14,
            shadow=glow(ACCENT_GLOW, 80),
            extra={"fx":{"enter":"fade-up","order":1,"ambient":"kenburns","ken":{"dir":"drift","scale":1.05,"duration":20}}}),
    {"id":"sb5logo","type":"image","x":940,"y":261,"w":176,"h":199,"rotation":0,"opacity":0.92,
     "src":"asset:logo-unity","fit":"contain","fx":{"enter":"fade-up","order":1}},
] + footer(5)
slides.append(slide(5, els, "First section break of the lecture, and the first time this course opens Unity together as a group activity rather than a slide. Orange is Part 1's colour on the 15-week arc — same family as Lecture 01's own identity colour, since this is still 'the tool', not yet git or the scene graph.", transition="fade"))

# ============================================================ 6. THE EDITOR AT A GLANCE
els = [
    rect("bg6",0,0,W,H,BG),
    kicker("k6",MX,72,"Six windows, one workspace", color=ACCENT),
    txt("t6",MX,104,1100,70,"The Editor at a Glance",50,weight=800,family=DISPLAY),
    rect("eaogframe",96,196,1088,428,SURFACE2,radius=14,stroke=BORDER2,strokeWidth=1),
    rect("eaogtoolbar",112,212,1056,32,BG,radius=8,stroke=BORDER,strokeWidth=1),
    txt("eaogtoolbart",112+20,219,900,18,
        "&#9664;&nbsp;&nbsp;&#9654;&nbsp;&nbsp;&#9723;&nbsp;&nbsp;&nbsp;&nbsp;&#9635;&nbsp;&nbsp;&#8635;&nbsp;&nbsp;&#9639;&nbsp;&nbsp;&#9640;&nbsp;&nbsp;&nbsp;&nbsp;&#9654;&nbsp;PLAY",
        12.5,color=MUTED,family=MONOF,extra={"letterSpacing":1}),
]
panels6 = [
    ("eaoghier", 112, 256, 204, 240, ACCENT3, "HIERARCHY", "Every object<br>in the scene"),
    ("eaogscene", 328, 256, 536, 240, ACCENT, "SCENE / GAME", "What you're building, and what the player will actually see"),
    ("eaoginsp", 876, 256, 292, 240, ACCENT3, "INSPECTOR", "Details of<br>whatever is selected"),
]
for pid,x,y,w,h,col,label,desc in panels6:
    els += [
        rect(f"{pid}bg",x,y,w,h,BG,radius=10,stroke=col,strokeWidth=1.5),
        txt(f"{pid}k",x+16,y+14,w-32,20,label,11.5,color=col,weight=700,family=MONOF,extra={"letterSpacing":1.5}),
        txt(f"{pid}d",x+16,y+42,w-32,h-58,desc,14,color=MUTED,lh=1.4),
    ]
bottom6 = [
    ("eaogproj", 112, 508, 516, 100, ACCENT2, "PROJECT", "Every file in your game &mdash; assets, scripts, scenes &mdash; laid out like folders on disk"),
    ("eaogcons", 640, 508, 528, 100, ACCENT, "CONSOLE", "Errors, warnings, and your own <code>Debug.Log()</code> output, in one place"),
]
for pid,x,y,w,h,col,label,desc in bottom6:
    els += [
        rect(f"{pid}bg",x,y,w,h,BG,radius=10,stroke=col,strokeWidth=1.5),
        txt(f"{pid}k",x+18,y+12,w-36,20,label,11.5,color=col,weight=700,family=MONOF,extra={"letterSpacing":1.5}),
        txt(f"{pid}d",x+18,y+36,w-36,52,desc,13.5,color=MUTED,lh=1.4),
    ]
els += footer(6)
slides.append(slide(6, els, "Walk the room through the real Unity editor on screen while this slide is up, panel by panel — this is the moment the lecture becomes hands-on even without laptops open. Colour is a preview, not decoration: blue panels come back in Part 3, teal comes back in Part 2."))

# ============================================================ 7. SCENE VIEW VS GAME VIEW
els = [
    rect("bg7",0,0,W,H,BG),
    kicker("k7",MX,72,"Two windows, two jobs", color=ACCENT),
    txt("t7",MX,104,1100,64,"Scene View vs Game View",46,weight=800,family=DISPLAY),
]
els += panel("p7a",96,206,528,400,"SCENE VIEW",ACCENT,None,
    "Your workshop. Move, rotate, and place objects by hand, from whatever angle helps "
    "you work &mdash; fly around, zoom in, look at the level from above.<br><br>"
    "What you see here is <b>authoring data</b>, not the finished picture. Camera "
    "icons, collider outlines, and light gizmos all show up here and nowhere else.",
    bodycol=TEXT, bg=SURFACE, border="rgba(255,138,61,0.35)", barcol=ACCENT, order=0, body_size=16, lh=1.7)
els += panel("p7b",656,206,528,400,"GAME VIEW",ACCENT,None,
    "The player's window. Renders exactly what your active <b>Camera</b> sees, at the "
    "resolution and aspect ratio you're targeting.<br><br>"
    "No gizmos, no icons &mdash; if it isn't visible here, it isn't visible in the "
    "shipped game. This is the view that matters the moment you hit Play.",
    bodycol=TEXT, bg=SURFACE, border="rgba(255,138,61,0.35)", barcol=ACCENT, order=1, body_size=16, lh=1.7)
els += footer(7)
slides.append(slide(7, els, "Cue the room to actually toggle between these two tabs while this slide is up. The classic beginner confusion is dragging an object around thinking they're editing gameplay when they're actually just repositioning their own camera view in Scene view — worth calling out explicitly."))

# ============================================================ 8. THE HIERARCHY & INSPECTOR
els = [
    rect("bg8",0,0,W,H,BG),
    kicker("k8",MX,72,"Where objects live, and what they're made of", color=ACCENT),
    txt("t8",MX,104,1100,64,"The Hierarchy &amp; Inspector",44,weight=800,family=DISPLAY),
]
els += panel("p8a",96,206,528,340,"HIERARCHY",ACCENT3,None,
    "The tree of every GameObject in the open scene, nested parent inside child. "
    "Click a name here and it's selected everywhere else in the editor at once.",
    bodycol=TEXT, bg=SURFACE, border="rgba(108,140,255,0.35)", barcol=ACCENT3, order=0, body_size=16, lh=1.7)
els += panel("p8b",656,206,528,340,"INSPECTOR",ACCENT3,None,
    "Everything about whatever's currently selected &mdash; its Transform, and every "
    "Component attached to it, each with fields you can read and edit live.",
    bodycol=TEXT, bg=SURFACE, border="rgba(108,140,255,0.35)", barcol=ACCENT3, order=1, body_size=16, lh=1.7)
els += [
    txt("p8note",96,562,1088,40,
        "Part 3 goes deep on how to read and organize this tree &mdash; for now, just know where to look.",
        14.5,color=MUTED,extra={"fx":{"enter":"fade-up","order":2}}),
] + footer(8)
slides.append(slide(8, els, "Deliberately brief — this is a preview, not the lesson. Part 3 (Scene & GameObject Hierarchy) is where GameObjects, Components, and this exact panel get taught properly. Today they just need to recognize the two panels and know they're linked."))

# ============================================================ 9. THE PROJECT WINDOW & CONSOLE
els = [
    rect("bg9",0,0,W,H,BG),
    kicker("k9",MX,72,"Your files, and what they're telling you", color=ACCENT),
    txt("t9",MX,104,1100,64,"The Project Window &amp; Console",42,weight=800,family=DISPLAY),
]
els += panel("p9a",96,206,528,340,"PROJECT WINDOW",ACCENT2,None,
    "Every file that makes up your game &mdash; scripts, scenes, sprites, sounds "
    "&mdash; organized exactly like folders on disk. This is what version control "
    "actually tracks.",
    bodycol=TEXT, bg=SURFACE, border="rgba(85,214,194,0.35)", barcol=ACCENT2, order=0, body_size=16, lh=1.7)
els += panel("p9b",656,206,528,340,"CONSOLE",ACCENT,None,
    "Where errors, warnings, and your own <code>Debug.Log()</code> calls show up. "
    "The first place to look the moment something breaks &mdash; a red line here "
    "means Unity is telling you exactly what and where.",
    bodycol=TEXT, bg=SURFACE, border="rgba(255,138,61,0.35)", barcol=ACCENT, order=1, body_size=16, lh=1.7)
els += [
    txt("p9note",96,562,1088,40,
        "Part 2 picks this up directly &mdash; the Project window is the folder version control keeps a history of.",
        14.5,color=MUTED,extra={"fx":{"enter":"fade-up","order":2}}),
] + footer(9)
slides.append(slide(9, els, "The Project-window-is-what-git-tracks line is the bridge to Part 2 — plant it here so it isn't a cold start when the version control section opens. The Console callout is worth lingering on: most first bugs are diagnosed here before students think to look anywhere else."))

# ============================================================ 10. THE TOOLBAR & TRANSFORM TOOLS
tools10 = [
    ("Q","Hand","Pan the Scene view",ACCENT),
    ("W","Move","Translate an object",ACCENT2),
    ("E","Rotate","Turn an object",ACCENT3),
    ("R","Scale","Resize an object",ACCENT4),
    ("T","Rect","2D / UI rect transform",ACCENT),
]
playback10 = [
    ("&#9654;","Play","Runs the game in the Game view",ACCENT),
    ("&#9208;","Pause","Freezes the running game",ACCENT),
    ("&#9197;","Step","Advances exactly one frame",ACCENT),
]
els = [
    rect("bg10",0,0,W,H,BG),
    kicker("k10",MX,72,"The buttons you'll press without thinking, by week 3", color=ACCENT),
    txt("t10",MX,104,1100,64,"The Toolbar &amp; Transform Tools",42,weight=800,family=DISPLAY),
    txt("t10k",MX,196,600,24,"TRANSFORM TOOLS &mdash; LEFT SIDE OF THE TOOLBAR",12,color=FAINT,weight=700,family=MONOF,extra={"letterSpacing":1.5}),
]
tx10 = 96
for i,(key,name,desc,col) in enumerate(tools10):
    x = tx10 + i*206
    fx = {"fx":{"enter":"fade-up","order":i}}
    els += [
        rect(f"tt{i}",x,228,190,150,SURFACE,radius=12,stroke=col,strokeWidth=1.5,extra=fx),
        rect(f"tt{i}kbg",x+18,246,36,36,BG,radius=8,stroke=col,strokeWidth=1,extra=fx),
        txt(f"tt{i}k",x+18,246,36,36,key,15,weight=800,family=MONOF,color=col,align="center",valign="middle",extra=fx),
        txt(f"tt{i}n",x+18,296,154,26,name,16.5,weight=700,family=DISPLAY,extra=fx),
        txt(f"tt{i}d",x+18,324,154,44,desc,12.5,color=MUTED,lh=1.35,extra=fx),
    ]
els += [
    txt("t10k2",MX,406,600,24,"PLAYBACK CONTROLS &mdash; CENTER OF THE TOOLBAR",12,color=FAINT,weight=700,family=MONOF,extra={"letterSpacing":1.5}),
]
for i,(glyph,name,desc,col) in enumerate(playback10):
    x = 96 + i*366
    fx = {"fx":{"enter":"fade-up","order":5+i}}
    els += [
        rect(f"pb{i}",x,438,344,168,SURFACE,radius=12,stroke=BORDER,strokeWidth=1,extra=fx),
        txt(f"pb{i}g",x+24,458,60,60,glyph,26,color=col,align="center",valign="middle",extra=fx),
        txt(f"pb{i}n",x+96,466,220,30,name,19,weight=700,family=DISPLAY,extra=fx),
        txt(f"pb{i}d",x+96,500,220,80,desc,13.5,color=MUTED,lh=1.4,extra=fx),
    ]
els += footer(10)
slides.append(slide(10, els, "Have these five letters — Q W E R T — up on the projector and actually cycle through them live in the editor; the muscle memory starts today. The Play/Pause/Step row is the setup for the very next slide, which is the one gotcha worth a slide of its own."))

# ============================================================ 11. PLAY MODE — THE ONE GOTCHA
steps11 = [
    ("1","Press Play",ACCENT),
    ("2","Tweak values to test",ACCENT),
    ("3","Press Play again &mdash; changes revert",ACCENT),
]
els = [
    rect("bg11",0,0,W,H,BG),
    kicker("k11",MX,72,"The mistake every beginner makes exactly once", color=ACCENT),
    txt("t11",MX,104,1100,64,"Play Mode &mdash; The One Gotcha",44,weight=800,family=DISPLAY),
    rect("gotchabox",96,206,1088,190,ACCENT_SOFT,radius=16,stroke="rgba(255,138,61,0.35)",strokeWidth=1,
         extra={"fx":{"enter":"fade-up","order":0}}),
    txt("gotchak",96+40,236,1008,24,"PLAY MODE IS A PREVIEW, NOT A SAVE",13,color=ACCENT,weight=700,family=MONOF,
        extra={"letterSpacing":1.5,"fx":{"enter":"fade-up","order":0}}),
    txt("gotchab",96+40,268,1008,110,
        "Tweak a value while the game is running to test it live &mdash; that's exactly what Play Mode "
        "is for. But the instant you stop, <b>every change you made while playing snaps back</b> to how "
        "it was before you pressed Play. Unity does this on purpose: Play Mode is a sandbox, not your "
        "working copy.",
        16.5,color=TEXT,lh=1.65,extra={"fx":{"enter":"fade-up","order":0}}),
]
sx11 = 96
for i,(n,label,col) in enumerate(steps11):
    x = sx11 + i*366
    fx = {"fx":{"enter":"fade-up","order":1+i}}
    els += [
        rect(f"st{i}",x,432,344,120,SURFACE,radius=12,stroke=BORDER,strokeWidth=1,extra=fx),
        rect(f"st{i}nbg",x+24,456,40,40,BG,radius=20,stroke=col,strokeWidth=1.5,extra=fx),
        txt(f"st{i}n",x+24,456,40,40,n,17,weight=800,family=MONOF,color=col,align="center",valign="middle",extra=fx),
        txt(f"st{i}l",x+80,462,244,60,label,15.5,color=TEXT,lh=1.35,extra=fx),
    ]
els += [
    txt("gotchatip",96,572,1088,32,
        "Unity's cue: the whole editor tints slightly while Play Mode is running &mdash; that tint is your reminder that nothing here is permanent yet.",
        13.5,color=MUTED,extra={"fx":{"enter":"fade-up","order":4}}),
] + footer(11)
slides.append(slide(11, els, "This single slide will save more office-hours confusion than almost anything else in the lecture — 'I changed my player's speed and it disappeared' is the single most common early support question. Make them say back to you: edit while stopped, test while playing, never the reverse."))

# ============================================================ 12. SECTION BREAK — VERSION CONTROL
els = [
    rect("bg5",0,0,W,H,BG),
    rect("sb5line",MX,300,120,4,ACCENT2,shadow=glow(ACCENT2_GLOW,18),
         extra={"fx":{"enter":"fade-up","order":0,"ambient":"kenburns","ken":{"dir":"drift","scale":1.0,"duration":18}}}),
    txt("sb5k",MX,326,700,28,"PART 2 OF TODAY",15,color=ACCENT2,weight=700,family=MONOF,extra={"letterSpacing":3,"fx":{"enter":"fade-up","order":0}}),
    txt("sb5t",MX,346,1120,160,"Version Control for<br>Game Projects",58,weight=800,family=DISPLAY,extra={"letterSpacing":-1,"fx":{"enter":"fade-up","order":1}}),
    txt("sb5s",MX,556,1000,40,"Your project's memory: every change, who made it, and how to undo it.",20,color=MUTED,
        extra={"fx":{"enter":"fade-up","order":2}}),
] + footer(12)
slides.append(slide(12, els, "Ask the room: who has ever lost work, or ended up with three folders called 'final', 'final2', and 'final_actually_final'? Nearly every hand goes up — that shared pain is the whole motivation for this section.", transition="fade"))

# ============================================================ 13. THE PROBLEM
els = [
    rect("bg6",0,0,W,H,BG),
    kicker("k6",MX,72,"Why bother", color=ACCENT2),
    txt("t6",MX,104,1100,70,"The Problem This Solves",50,weight=800,family=DISPLAY),
]
els += panel("p6a",96,206,528,400,"WITHOUT VERSION CONTROL",FAINT,None,
    "&#8226;&nbsp; <s>MyGame_v2_FINAL.zip</s><br>"
    "&#8226;&nbsp; <s>MyGame_v2_FINAL_fixed(1).zip</s><br>"
    "&#8226;&nbsp; <s>MyGame_ACTUALLY_FINAL.zip</s><br><br>"
    "Which folder is the real one? Overwrite a file by accident and it's gone. "
    "Two people edit the same scene and one of you just loses an evening.",
    bodycol=MUTED, bg=SURFACE, border=BORDER, barcol=FAINT, order=0, body_size=17, lh=1.7)
els += panel("p6b",656,206,528,400,"WITH VERSION CONTROL",ACCENT2,None,
    "One project folder. Every change is a labelled snapshot you can return to, "
    "compare, or undo. Two people can work on the same project at once and merge "
    "their changes back together on purpose, not by accident.",
    bodycol=TEXT, bg=ACCENT2_SOFT, border="rgba(85,214,194,0.35)", barcol=ACCENT2, order=1, body_size=17, lh=1.75)
els += footer(13)
slides.append(slide(13, els, "The strikethrough filenames usually get a laugh of recognition — lean into it. The right card is the whole pitch for git in one paragraph: it's not about typing commands, it's about never losing work again."))

# ============================================================ 14. WHAT IS VERSION CONTROL
els = [
    rect("bg7",0,0,W,H,BG),
    kicker("k7",MX,72,"Defining our terms", color=ACCENT2),
    txt("t7",MX,104,1100,64,"What Is Version Control?",46,weight=800,family=DISPLAY),
    rect("qc7",96,196,1088,120,SURFACE2,radius=14,stroke=BORDER2,strokeWidth=1),
    txt("qc7q",96+32,216,1024,56,
        "A system that records changes to a set of files over time, so you can recall "
        "any specific version later &mdash; and see exactly who changed what, and why.",
        19,color=TEXT,lh=1.4),
    txt("qc7a",96+32,278,1024,22,"&mdash; the working definition this whole section builds on",13.5,color=MUTED,family=MONOF),
    txt("snapk",MX,348,600,24,"THE CORE IDEA: SNAPSHOTS, NOT COPIES",13,color=ACCENT2,weight=700,family=MONOF,extra={"letterSpacing":1.5}),
    txt("snapd",MX,378,1088,90,
        "Git doesn't keep a second copy of your project per save. It keeps a chain of "
        "<b>snapshots</b> &mdash; each one a complete, restorable picture of every file, "
        "stored efficiently by only recording what actually changed.",
        17,color=MUTED,lh=1.65),
] + footer(14)
slides.append(slide(14, els, "Keep this conceptual and slow — for most students this is the first time they've heard 'version control' defined precisely rather than just 'the thing GitHub does'. The snapshot idea is the one mental model everything else in this section hangs off."))

# ============================================================ 15. WHY GIT
git_stats = [
    ("2005","Born from the Linux kernel","Linus Torvalds wrote it because no existing tool could handle a project that size.",ACCENT2),
    ("Distributed","Every clone is a full backup","No single server holds the only copy of your project's history.",ACCENT3),
    ("Free &amp; Open","No cost, no lock-in","Same tool whether you're solo, at a studio, or on a student project.",ACCENT4),
    ("Industry Standard","What you'll use at any studio","Unity, Unreal, and virtually every modern dev team default to it.",ACCENT),
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
els += footer(15)
slides.append(slide(15, els, "You don't need the kernel-development backstory in depth — the one-liner is enough: git was built to solve version control at a scale and speed nothing else could, which is exactly why it won."))

# ============================================================ 16. GIT'S MENTAL MODEL — THE THREE TREES
els = [
    rect("bg9",0,0,W,H,BG),
    kicker("k9",MX,72,"The model in your head", color=ACCENT2),
    txt("t9",MX,104,1100,70,"Git's Three Trees",56,weight=800,family=DISPLAY),
]
tree_boxes = [
    ("Working Directory","The files on your disk right now &mdash; whatever you're actively editing in Unity or your code editor.",ACCENT,ACCENT_SOFT),
    ("Staging Area","A holding pen. You choose exactly which changed files go into the <i>next</i> snapshot.",ACCENT2,ACCENT2_SOFT),
    ("Repository","The permanent history &mdash; every snapshot you've ever committed, forever recoverable.",ACCENT3,ACCENT3_SOFT),
]
txs3 = [96, 470, 844]
for i,(title,desc,col,soft) in enumerate(tree_boxes):
    x = txs3[i]
    fx = {"fx":{"enter":"fade-up","order":i}}
    els += [
        rect(f"tb{i}",x,280,340,260,soft,radius=14,stroke=col,strokeWidth=1.5,extra=fx),
        txt(f"tb{i}lbl",x+28,306,284,40,title.upper(),14.5,color=col,weight=700,family=MONOF,extra={"letterSpacing":1.2,**fx}),
        txt(f"tb{i}d",x+28,352,284,170,desc,15.5,color=TEXT,lh=1.55,extra=fx),
    ]
els += [
    line("arr91",436,409,34,1,MUTED,strokeWidth=3,lineEnd="arrow"),
    line("arr92",810,409,34,1,MUTED,strokeWidth=3,lineEnd="arrow"),
    txt("cmd91",96,232,340,26,"git add",14,color=ACCENT,family=MONOF,align="center",extra={"letterSpacing":1}),
    txt("cmd92",470,232,340,26,"git commit",14,color=ACCENT2,family=MONOF,align="center",extra={"letterSpacing":1}),
] + footer(16)
slides.append(slide(16, els, "This is THE diagram for today's whole git section — refer back to it verbally in every slide that follows. Files move left to right by your own explicit choice at each arrow; nothing moves to the next tree automatically."))

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
    "git add Assets/Player.cs &nbsp;&mdash;&nbsp; stage one file<br>"
    "git add . &nbsp;&mdash;&nbsp; stage everything changed",
    "bg10") + loop_chain(0) + footer(17)
slides.append(slide(17, els, "Staging is the concept students trip on most: it's not saving, it's choosing. You can edit five files and stage only two — the other three simply aren't part of the next snapshot yet.", transition="morph"))

els = loop_slide(18,2,"Commit",ACCENT2,ACCENT2_SOFT,ACCENT2_GLOW,
    "A commit seals whatever is staged into a permanent, named snapshot in the repository. "
    "It cannot silently change later &mdash; that's what makes it a safe point to return to.",
    "COMMANDS YOU'LL ACTUALLY TYPE",
    "git commit -m &quot;Add double-jump input&quot;<br><br>"
    "Write the message like a headline: what changed, not how you felt about it.",
    "bg11") + loop_chain(1) + footer(18)
slides.append(slide(18, els, "Push the habit of small, frequent, honestly-described commits early — 'stuff' or 'fix' as a message is a habit that costs someone (often future-you) real time later. A good commit message answers 'what' in five words."))

els = loop_slide(19,3,"Sync",ACCENT3,ACCENT3_SOFT,ACCENT3_GLOW,
    "Your commits live locally until you <code>push</code> them to a shared remote (GitHub). "
    "<code>pull</code> brings your teammates' commits back down to you.",
    "COMMANDS YOU'LL ACTUALLY TYPE",
    "git pull &nbsp;&mdash;&nbsp; get the latest before you start<br>"
    "git push &nbsp;&mdash;&nbsp; share your commits when you're done<br><br>"
    "Pull first, every session. It's the single habit that prevents most conflicts.",
    "bg12") + loop_chain(2) + footer(19)
slides.append(slide(19, els, "This is where solo work becomes team work. Drill the 'pull before you push, pull before you start' habit — it's the cheapest possible insurance against the merge conflicts we look at in two slides."))

# ============================================================ 20. BRANCHING MODEL
els = [
    rect("bg13",0,0,W,H,BG),
    kicker("k13",MX,72,"Working without stepping on each other", color=ACCENT2),
    txt("t13",MX,104,1100,64,"Branches",50,weight=800,family=DISPLAY),
    txt("t13b",MX,172,1000,30,"A branch is a parallel line of commits &mdash; safe to experiment on.",17,color=MUTED),
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
    line("branchfork",FORKX,MAINY,MERGEX-FORKX,FEATY-MAINY,ACCENT3,strokeWidth=2.5,dashed=True,
         extra={"fx":{"loop":{"type":"dash-march","distance":14,"duration":1.6}}}),
    line("branchline",FORKX,FEATY,MERGEX-FORKX,2,ACCENT3,strokeWidth=3),
    line("branchmerge",FORKX,FEATY,MERGEX-FORKX,MAINY-FEATY,ACCENT3,strokeWidth=2.5,dashed=True,
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
        "Nothing you do on <b>feature/double-jump</b> touches <b>main</b> until you deliberately merge it back. "
        "Break something? Delete the branch &mdash; main was never at risk.",
        15.5,color=MUTED,lh=1.5),
] + footer(20)
slides.append(slide(20, els, "The mental model: main is the trunk that always works. A feature branch is a sandbox off to the side. This is the single idea that makes it safe to experiment — walk your finger along the diagram as you narrate fork, work, merge."))

# ============================================================ 21. MERGE CONFLICTS
els = [
    rect("bg14",0,0,W,H,BG),
    kicker("k14",MX,72,"When two people touch the same lines", color=ACCENT2),
    txt("t14",MX,104,1100,64,"Merge Conflicts",50,weight=800,family=DISPLAY),
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
    "Stage and commit &mdash; the conflict is resolved.",
]
for i,step in enumerate(resolve_steps):
    y = 232 + i*92
    fx = {"fx":{"enter":"fade-up","order":i}}
    els += [
        ellipse(f"rs{i}dot",728,y+2,26,26,ACCENT2_SOFT,stroke=ACCENT2,strokeWidth=1.5,extra=fx),
        txt(f"rs{i}n",728,y+2,26,26,str(i+1),13,color=ACCENT2,weight=800,family=DISPLAY,align="center",valign="middle",extra=fx),
        txt(f"rs{i}t",772,y-6,392,70,step,15,color=MUTED,lh=1.45,extra=fx),
    ]
els += footer(21)
slides.append(slide(21, els, "This is not a rare failure mode — it's a normal Tuesday on a team project. Demystify it: a conflict is git honestly saying 'I don't know which of these you want', not a sign something is broken. Live-resolve one during lab if time allows."))

# ============================================================ 22. WHY UNITY PROJECTS ARE DIFFERENT
els = [
    rect("bg15",0,0,W,H,BG),
    kicker("k15",MX,72,"The part git wasn't built for", color=ACCENT2),
    txt("t15",MX,104,1100,64,"Why Unity Projects Are Different",42,weight=800,family=DISPLAY),
]
els += panel("wu1",96,206,528,400,"A CODE FILE (.cs)",ACCENT2,None,
    "Plain text. Two people's edits on different lines merge automatically &mdash; git "
    "was designed around exactly this.<br><br>"
    "A conflict is rare, visible, and fixable by reading a few lines.",
    bodycol=TEXT,bg=ACCENT2_SOFT,border="rgba(85,214,194,0.35)",barcol=ACCENT2,order=0,body_size=16.5,lh=1.7)
els += panel("wu2",656,206,528,400,"A SCENE OR PREFAB (.unity / .prefab)",ACCENT3,None,
    "Effectively a big structured data file. Two people's edits usually can't be "
    "merged line-by-line &mdash; git can only pick one side or ask a human to redo the work.<br><br>"
    "This is why teams split scenes/prefabs by owner and merge less often on shared ones.",
    bodycol=TEXT,bg=ACCENT3_SOFT,border="rgba(108,140,255,0.35)",barcol=ACCENT3,order=1,body_size=16.5,lh=1.7)
els += footer(22)
slides.append(slide(22, els, "Set expectations honestly: git is a text-diffing tool wearing a binary-file trenchcoat when it comes to scenes and prefabs. The fix isn't a tool, it's a workflow — communicate who's touching what before you touch it."))

# ============================================================ 23. .GITIGNORE FOR UNITY
gi_rows = [{"cells":[{"html":"Ignore (never commit)","bold":True},{"html":"Why","bold":True}]}]
gi_data = [
    ("Library/","Unity's rebuildable local cache &mdash; gigabytes, regenerates automatically."),
    ("Temp/, Obj/, Logs/","Scratch files from the last build/compile."),
    ("Build/, Builds/","Your exported game &mdash; a product, not a source file."),
    ("UserSettings/, .vs/, .idea/","Your personal editor layout &mdash; not your teammates' business."),
    ("*.csproj, *.sln","Regenerated by Unity every time it opens."),
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
    txt("gisrc",96,548,1088,24,"Unity ships an official template &mdash; start from <code>github.com/github/gitignore/blob/main/Unity.gitignore</code>.",
        13.5,color=FAINT,family=MONOF),
] + footer(23)
slides.append(slide(23, els, "Don't make them memorize this list — point out it's one download, added once, per project, on day one. The teaching point is the CATEGORY of thing to ignore (generated/local/output), not the specific folder names."))

# ============================================================ 24. THE .meta GOTCHA
els = [
    rect("bg17",0,0,W,H,BG),
    kicker("k17",MX,72,"The mistake that eats a whole lab session", color=ACCENT),
    txt("t17",MX,104,1100,64,"Don't Ignore .meta Files",46,weight=800,family=DISPLAY),
    rect("metawarn",96,206,1088,150,ACCENT_SOFT,radius=14,stroke="rgba(255,138,61,0.35)",strokeWidth=1),
    txt("metawarnk",96+32,230,1024,24,"EVERY ASSET GETS A .meta FILE &mdash; TRACK IT TOO",13,color=ACCENT,weight=700,family=MONOF,extra={"letterSpacing":1.5}),
    txt("metawarnb",96+32,262,1024,80,
        "The .meta file stores the asset's GUID &mdash; the ID every scene and script uses to "
        "reference that asset. Untrack it, and Unity may hand a different GUID to a teammate's "
        "copy, silently breaking every reference to that asset.",
        16.5,color=TEXT,lh=1.55),
    txt("metasympk",96,392,1000,24,"HOW IT SHOWS UP IN THE WILD",12.5,color=FAINT,weight=700,family=MONOF,extra={"letterSpacing":1.5}),
    txt("metasymp",96,420,1088,90,
        "A teammate pulls your commit and every sprite in the scene shows up pink, or the inspector "
        "says &ldquo;Missing (Mono Script)&rdquo; on a component that was working five minutes ago. "
        "Nine times out of ten: a .meta file never made it into the commit.",
        16.5,color=MUTED,lh=1.6),
    rect("metafix",96,522,1088,70,SURFACE,radius=12,stroke=BORDER,strokeWidth=1),
    txt("metafixt",96+28,542,1032,32,"THE FIX &mdash; never rename, move, or delete an asset outside Unity's own Project window; let the editor keep the .meta file in sync.",
        14.5,color=MUTED,lh=1.45),
] + footer(24)
slides.append(slide(24, els, "This is the single most common real-world bug report in a student team project, almost always traced to Finder/Explorer renaming a file outside Unity, or a stray '*.meta' line left in someone's .gitignore. Worth a slow, deliberate slide."))

# ============================================================ 25. GIT LFS FOR BINARY ASSETS
els = [
    rect("bg18",0,0,W,H,BG),
    kicker("k18",MX,72,"When your assets outgrow plain git", color=ACCENT2),
    txt("t18",MX,104,1100,64,"Git LFS for Binary Assets",46,weight=800,family=DISPLAY),
    txt("t18b",MX,172,1000,30,"Textures, audio, and models don't diff &mdash; they just get bigger, forever.",17,color=MUTED),
]
els += panel("lfs1",96,220,528,340,"WITHOUT LFS",FAINT,None,
    "Every version of every texture you've ever committed stays in the repo's "
    "history &mdash; forever, even after you delete the file. Edit a 50MB texture 10 "
    "times and that's ~500MB your teammates must download just to clone the project.",
    bodycol=MUTED,bg=SURFACE,border=BORDER,barcol=FAINT,order=0,body_size=16,lh=1.7)
els += panel("lfs2",656,220,528,340,"WITH GIT LFS",ACCENT2,None,
    "Git tracks a small pointer file instead of the binary. The actual asset content "
    "lives in separate LFS storage, fetched only when you check out that version. "
    "The repo itself stays small and fast to clone.",
    bodycol=TEXT,bg=ACCENT2_SOFT,border="rgba(85,214,194,0.35)",barcol=ACCENT2,order=1,body_size=16,lh=1.7)
els += [
    txt("lfscmd",96,584,1088,26,"git lfs track &quot;*.png&quot; &quot;*.wav&quot; &quot;*.fbx&quot;  &mdash;&nbsp; set this up once, before you add your first texture.",
        14.5,color=FAINT,family=MONOF),
] + footer(25)
slides.append(slide(25, els, "Not every student project needs LFS on day one, but every Unity team eventually does — flag it now so nobody discovers it three weeks in with a 2GB repo that takes ten minutes to clone."))

# ============================================================ 26. COMMON PITFALLS & RECOVERY
pitfalls = [
    ("Committed Library/ by accident","Add it to .gitignore, then <code>git rm -r --cached Library</code> to untrack it without deleting your files.",ACCENT),
    ("Wrote a terrible commit message","Fine &mdash; it's permanent, but harmless. Just write a better one next time. Don't rewrite shared history to fix it.",ACCENT2),
    ("Realized the last commit was wrong","<code>git revert</code> adds a new commit that undoes it &mdash; safe, and keeps the history honest.",ACCENT3),
    ("Uncommitted changes you want gone","<code>git checkout -- &lt;file&gt;</code> discards them. There is no undo for this one &mdash; use it deliberately.",ACCENT4),
]
els = [
    rect("bg19",0,0,W,H,BG),
    kicker("k19",MX,72,"You will do at least one of these", color=ACCENT2),
    txt("t19",MX,104,1100,70,"Common Pitfalls &amp; Recovery",44,weight=800,family=DISPLAY),
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
els += footer(26)
slides.append(slide(26, els, "The framing that matters here: almost every git mistake is recoverable, which is the entire point of version control. Say this out loud — students are often more afraid of git than of the bug they're trying to fix."))

# ============================================================ 27. WORKFLOW CHECKLIST
els = [
    rect("bg20",0,0,W,H,BG),
    kicker("k20",MX,72,"Before you write a line of gameplay code", color=ACCENT2),
    txt("t20",MX,104,1100,70,"Your Project's Workflow Checklist",40,weight=800,family=DISPLAY),
    rect("wc1",96,206,1088,410,SURFACE,radius=14,stroke=BORDER,strokeWidth=1,extra={"fx":{"enter":"fade-up","order":0}}),
    txt("wc1b",96+40,240,1008,360,
        "&#9679;&nbsp; Create the repository <b>before</b> you create a single asset<br>"
        "&#9679;&nbsp; Add a Unity .gitignore on day one &mdash; not after the first bloated commit<br>"
        "&#9679;&nbsp; Commit early, commit often, write messages a stranger could understand<br>"
        "&#9679;&nbsp; One feature branch per feature or level &mdash; keep main always working<br>"
        "&#9679;&nbsp; Never commit <code>Library/</code> or <code>Temp/</code><br>"
        "&#9679;&nbsp; Pull before you start work, push before you stop",
        20, color=TEXT, lh=2.15, extra={"fx":{"enter":"fade-up","order":0}}),
] + footer(27)
slides.append(slide(27, els, "This is the slide to screenshot. Every item on it is something a past student learned the hard way — frame it as inherited wisdom, not an arbitrary rulebook. Today's lab walks through the first three items live."))

# ============================================================ 28. VERSION CONTROL RECAP
els = [
    rect("bg21",0,0,W,H,BG),
    kicker("k21",MX,72,"Part 2, in one breath", color=ACCENT2),
    txt("t21",MX,104,1000,70,"Version Control Recap",50,weight=800,family=DISPLAY),
    rect("vcrbox",96,220,1088,360,ACCENT2_SOFT,radius=16,stroke="rgba(85,214,194,0.35)",strokeWidth=1),
    txt("vcrb",96+48,260,992,280,
        "Git keeps <b>snapshots</b>, not copies. You move changes through three trees &mdash; "
        "<b>working directory &rarr; staging &rarr; repository</b> &mdash; with <code>add</code>, "
        "<code>commit</code>, and <code>push/pull</code>. Branches let you experiment without "
        "risking <code>main</code>. Unity's binary files don't merge like code does, so a "
        ".gitignore, tracked .meta files, and LFS for big assets are what make a Unity repo behave.",
        20,color=TEXT,lh=1.85),
] + footer(28)
slides.append(slide(28, els, "Read this slide slowly, it's the entire section in five sentences. If a student remembers nothing else from Part 2, this paragraph is what they should retain."))

# ============================================================ 29. SECTION BREAK — SCENE & GAMEOBJECT HIERARCHY
els = [
    rect("bg22",0,0,W,H,BG),
    rect("sb22line",MX,300,120,4,ACCENT3,shadow=glow(ACCENT3_GLOW,18),
         extra={"fx":{"enter":"fade-up","order":0,"ambient":"kenburns","ken":{"dir":"drift","scale":1.0,"duration":18}}}),
    txt("sb22k",MX,326,700,28,"PART 3 OF TODAY",15,color=ACCENT3,weight=700,family=MONOF,extra={"letterSpacing":3,"fx":{"enter":"fade-up","order":0}}),
    txt("sb22t",MX,346,1120,160,"Scene &amp; GameObject<br>Hierarchy",58,weight=800,family=DISPLAY,extra={"letterSpacing":-1,"fx":{"enter":"fade-up","order":1}}),
    txt("sb22s",MX,556,1000,40,"Everything in Unity is built from two ideas. Today, both of them.",20,color=MUTED,
        extra={"fx":{"enter":"fade-up","order":2}}),
] + footer(29)
slides.append(slide(29, els, "Second half, same energy shift as the git section — but this time it's the part they'll be staring at in the editor every single lab from here on. This is the vocabulary for reading anyone's Hierarchy panel, including their own, six weeks from now.", transition="fade"))

# ============================================================ 30. WHAT IS A SCENE
els = [
    rect("bg23",0,0,W,H,BG),
    kicker("k23",MX,72,"Defining our terms", color=ACCENT3),
    txt("t23",MX,104,1100,64,"What Is a Scene?",50,weight=800,family=DISPLAY),
    rect("qc23",96,196,1088,110,SURFACE2,radius=14,stroke=BORDER2,strokeWidth=1),
    txt("qc23q",96+32,216,1024,50,
        "<i>&ldquo;A Scene contains everything that exists at one moment of your game "
        "&mdash; a level, a menu, a loading screen.&rdquo;</i>",18,color=TEXT,lh=1.4),
    txt("qc23a",96+32,268,1024,22,"&mdash; the mental model this whole section builds on",13.5,color=MUTED,family=MONOF),
]
scene_facts = [
    ("Saved as a file","A Scene is a <code>.unity</code> file &mdash; text-based (YAML), so git can diff it, even if merging it is rare.",ACCENT2),
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
els += footer(30)
slides.append(slide(30, els, "The 'text-based so git CAN diff it' callback ties directly back to Part 2 — Scenes are the one binary-ish Unity asset that at least partially plays nice with version control, unlike prefabs and most imported assets."))

# ============================================================ 31. GAMEOBJECTS & COMPONENTS
comp_chips = [
    ("Transform","always present",ACCENT2),
    ("Sprite Renderer","how it looks",ACCENT3),
    ("Box Collider 2D","how it collides",ACCENT4),
    ("Rigidbody 2D","how it moves",ACCENT),
    ("PlayerController.cs","how it behaves",ACCENT2),
]
els = [
    rect("bg24",0,0,W,H,BG),
    kicker("k24",MX,72,"The single building block", color=ACCENT3),
    txt("t24",MX,104,1100,64,"GameObjects &amp; Components",44,weight=800,family=DISPLAY),
    txt("t24b",MX,168,1000,30,"A GameObject is an empty container. Components are what give it behavior.",17,color=MUTED),
    rect("gobox",470,300,340,140,ACCENT3_SOFT,radius=14,stroke=ACCENT3,strokeWidth=2,shadow=glow(ACCENT3_GLOW,36)),
    txt("gonamekick",470+28,320,284,20,"GAMEOBJECT",12,color=ACCENT3,weight=700,family=MONOF,extra={"letterSpacing":2}),
    txt("goname",470+28,344,284,50,"&ldquo;Player&rdquo;",26,weight=800,family=DISPLAY),
    txt("goempty",470+28,398,284,26,"empty on its own &mdash; just a name and a place",12.5,color=MUTED),
]
chip_pos = [(96,232),(844,232),(96,530),(844,530),(470,502)]
for i,(name,role,col) in enumerate(comp_chips):
    x,y = chip_pos[i]
    fx = {"fx":{"enter":"fade-up","order":i}}
    w = 340
    els += [
        rect(f"cc{i}",x,y,w,64,SURFACE,radius=10,stroke=col,strokeWidth=1.5,extra=fx),
        txt(f"cc{i}n",x+18,y+9,w-36,24,name,15.5,weight=700,family=MONOF if "." in name else DISPLAY,color=col,extra=fx),
        txt(f"cc{i}r",x+18,y+35,w-36,22,role,12.5,color=MUTED,extra=fx),
    ]
els += footer(31)
slides.append(slide(31, els, "This is the composition-over-inheritance idea, stated for the first time — you'll come back to this exact sentence when you teach SOLID and component architecture later in the semester. A GameObject IS its components; remove them all and there's nothing left but a name."))

# ============================================================ 32. THE TRANSFORM COMPONENT
els = [
    rect("bg25",0,0,W,H,BG),
    kicker("k25",MX,72,"The one component every object has", color=ACCENT3),
    txt("t25",MX,104,1100,64,"The Transform Component",44,weight=800,family=DISPLAY),
    txt("t25b",MX,168,1000,30,"Every GameObject has exactly one. It cannot be removed.",17,color=MUTED),
]
tprops = [("Position","Where it is",ACCENT2,"X 2.0   Y 0.5   Z 0.0"),
          ("Rotation","Which way it's facing",ACCENT3,"X 0&deg;   Y 45&deg;   Z 0&deg;"),
          ("Scale","How big it is",ACCENT4,"X 1.0   Y 1.0   Z 1.0")]
for i,(name,desc,col,vals) in enumerate(tprops):
    x = [96,470,844][i]
    fx = {"fx":{"enter":"fade-up","order":i}}
    els += [
        rect(f"tp{i}",x,222,340,230,SURFACE,radius=14,stroke=col,strokeWidth=1.5,extra=fx),
        txt(f"tp{i}t",x+26,248,288,32,name,20,weight=800,family=DISPLAY,color=col,extra=fx),
        txt(f"tp{i}d",x+26,284,288,44,desc,14,color=MUTED,lh=1.4,extra=fx),
        rect(f"tp{i}vbg",x+26,338,288,52,BG,radius=8,stroke=BORDER,strokeWidth=1,extra=fx),
        txt(f"tp{i}v",x+26,338,288,52,vals,13,color=TEXT,family=MONOF,align="center",valign="middle",extra=fx),
    ]
els += [
    rect("tpnote",96,478,1088,80,SURFACE2,radius=12,stroke=BORDER2,strokeWidth=1),
    txt("tpnotet",96+28,498,1032,44,
        "&ldquo;Local&rdquo; values are relative to the parent; the Inspector shows local by default. "
        "&ldquo;World&rdquo; position is where the object actually ends up once every parent's transform stacks on top.",
        15,color=MUTED,lh=1.5),
] + footer(32)
slides.append(slide(32, els, "The local-vs-world distinction is the single most common source of 'why is my object in the wrong place' bugs once hierarchy nesting starts — plant the seed here, it pays off the moment parent-child transforms show up next slide."))

# ============================================================ 33. PARENT-CHILD HIERARCHY
els = [
    rect("bg26",0,0,W,H,BG),
    kicker("k26",MX,72,"Grouping objects on purpose", color=ACCENT3),
    txt("t26",MX,104,1100,64,"Parent-Child Hierarchy",46,weight=800,family=DISPLAY),
]
els += [
    rect("parentbox",96,206,460,420,ACCENT3_SOFT,radius=14,stroke=ACCENT3,strokeWidth=2,shadow=glow(ACCENT3_GLOW,30)),
    txt("parentk",96+28,230,404,20,"PARENT",12,color=ACCENT3,weight=700,family=MONOF,extra={"letterSpacing":2}),
    txt("parentname",96+28,254,404,36,"&ldquo;Enemy Squad&rdquo;",22,weight=800,family=DISPLAY),
    txt("parentdesc",96+28,296,404,60,"An empty GameObject used purely to group and move its children together.",13.5,color=MUTED,lh=1.45),
]
child_names = ["Grunt 01","Grunt 02","Turret"]
for i,name in enumerate(child_names):
    y = 372 + i*82
    fx = {"fx":{"enter":"fade-up","order":i}}
    els += [
        line(f"childlink{i}",96+40,y+20,40,1,BORDER2,strokeWidth=1.5,extra=fx),
        rect(f"childbox{i}",96+80,y,296,66,SURFACE,radius=10,stroke=BORDER,strokeWidth=1,extra=fx),
        txt(f"childname{i}",96+104,y+12,248,26,name,15.5,weight=700,family=DISPLAY,extra=fx),
        txt(f"childpos{i}",96+104,y+38,248,20,"local: relative to parent",11.5,color=FAINT,family=MONOF,extra=fx),
    ]
els += [
    rect("hnote",610,206,478,420,SURFACE,radius=14,stroke=BORDER,strokeWidth=1),
    txt("hnotek",610+28,232,422,22,"WHY GROUP OBJECTS?",13,color=ACCENT3,weight=700,family=MONOF,extra={"letterSpacing":1.5}),
    txt("hnoteb",610+28,266,422,340,
        "&#9679;&nbsp; Move, rotate, or scale the parent and every child follows &mdash; "
        "reposition a whole squad with one drag.<br><br>"
        "&#9679;&nbsp; A child's Transform is stored <i>relative to its parent</i>, "
        "not the world &mdash; move the parent and the children's own numbers never change.<br><br>"
        "&#9679;&nbsp; Deleting the parent deletes every child with it &mdash; a real, "
        "common way to lose more than you meant to.",
        16,color=MUTED,lh=1.65),
] + footer(33)
slides.append(slide(33, els, "Have someone predict out loud what happens to the children's Inspector values if you move the parent — most guess they'll change, and are surprised the local values stay identical. That surprise is the whole point of this slide."))

# ============================================================ 34. ORGANIZING A SCENE LIKE A PRO
hier_tree = [
    (0,"&#128193; Managers",ACCENT2,False),
    (1,"GameManager",MUTED,True),
    (1,"AudioManager",MUTED,True),
    (0,"&#128193; Environment",ACCENT3,False),
    (1,"Ground",MUTED,True),
    (1,"Props",MUTED,True),
    (0,"&#128193; Gameplay",ACCENT4,False),
    (1,"Player",MUTED,True),
    (1,"Enemy Squad",MUTED,True),
    (0,"&#128193; UI",ACCENT,False),
    (1,"HUD Canvas",MUTED,True),
]
els = [
    rect("bg27",0,0,W,H,BG),
    kicker("k27",MX,72,"A convention worth stealing", color=ACCENT3),
    txt("t27",MX,104,1100,64,"Organizing a Scene Like a Pro",44,weight=800,family=DISPLAY),
    rect("hierbox",96,196,560,436,SURFACE2,radius=14,stroke=BORDER2,strokeWidth=1),
    txt("hierk",96+28,216,504,22,"HIERARCHY PANEL",11.5,color=FAINT,weight=700,family=MONOF,extra={"letterSpacing":2}),
]
for i,(depth,label,col,leaf) in enumerate(hier_tree):
    y = 250 + i*33
    x = 96 + 28 + depth*32
    fx = {"fx":{"enter":"fade-up","order":i}}
    if not leaf:
        els.append(txt(f"ht{i}",x,y,480,26,label,15,weight=700,family=DISPLAY,color=col,extra=fx))
    else:
        els.append(txt(f"ht{i}",x,y,480,24,"&#8226;&nbsp; "+label,13.5,color=col,family=BODYF,extra=fx))
els += [
    rect("orgnote",688,196,496,436,SURFACE,radius=14,stroke=BORDER,strokeWidth=1),
    txt("orgnotek",688+28,222,440,22,"WHY EMPTY GAMEOBJECTS AS FOLDERS?",12,color=ACCENT3,weight=700,family=MONOF,extra={"letterSpacing":1.2}),
    txt("orgnoteb",688+28,254,440,340,
        "They cost nothing at runtime and turn a 40-object scene into something you can "
        "actually scan. Four groups here do double duty:<br><br>"
        "&#9679;&nbsp; A visual index for anyone opening the scene cold<br>"
        "&#9679;&nbsp; A shared pivot &mdash; move &ldquo;Environment&rdquo; to reposition a whole level chunk<br>"
        "&#9679;&nbsp; A namespace that avoids duplicate top-level names<br>"
        "&#9679;&nbsp; The exact grouping pattern your lab starter scene already uses",
        15.5,color=MUTED,lh=1.6),
] + footer(34)
slides.append(slide(34, els, "This is the slide that turns 'I have 60 loose objects in my Hierarchy' into a habit fixed before it starts. Point out this is precisely the pattern the lab starter project already ships with — they'll recognize it immediately when they open Unity."))

# ============================================================ 35. SCENES AT SCALE
els = [
    rect("bg28",0,0,W,H,BG),
    kicker("k28",MX,72,"A quick look ahead", color=ACCENT3),
    txt("t28",MX,104,1100,64,"Scenes at Scale",50,weight=800,family=DISPLAY),
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
        "one scene, one moment in the game; many scenes, one project.",
        15.5,color=MUTED,lh=1.6),
] + footer(35)
slides.append(slide(35, els, "Deliberately light-touch — the point is only to stop 'a game is one giant scene' from becoming a misconception, not to teach SceneManager yet. That's Bloom L2 territory: understand it exists, don't implement it yet."))

# ============================================================ 36. BRINGING IT TOGETHER
els = [
    rect("bg29",0,0,W,H,BG),
    kicker("k29",MX,72,"Where today's two halves meet", color=ACCENT2),
    txt("t29",MX,104,1100,64,"Bringing It Together",50,weight=800,family=DISPLAY),
    rect("btbox",96,206,1088,180,SURFACE2,radius=14,stroke=BORDER2,strokeWidth=1),
    txt("btk",96+32,228,1024,22,"WHAT YOU ACTUALLY COMMIT",12.5,color=ACCENT2,weight=700,family=MONOF,extra={"letterSpacing":1.5}),
    txt("btb",96+32,258,1024,110,
        "Add a &ldquo;Player&rdquo; GameObject under Gameplay, give it a Sprite Renderer and a "
        "script, and Unity updates <code>Level01.unity</code> plus a matching "
        "<code>Level01.unity.meta</code>. Both are what git needs to see the change.",
        16.5,color=TEXT,lh=1.55),
    rect("btcmd",96,410,1088,150,BG,radius=12,stroke=ACCENT2,strokeWidth=1.5),
    txt("btcmdk",96+32,432,1024,20,"$ TERMINAL",11,color=FAINT,family=MONOF,extra={"letterSpacing":2}),
    txt("btcmdb",96+32,458,1024,90,
        "git add Assets/Scenes/Level01.unity Assets/Scenes/Level01.unity.meta<br>"
        "git commit -m &quot;Add Player GameObject with movement script&quot;",
        16,color=ACCENT2,family=MONOF,lh=1.9),
] + footer(36)
slides.append(slide(36, els, "This slide is the whole lecture in one worked example — walk it slowly, it's the first time the two halves of today visibly touch. The commit message names WHAT changed in the hierarchy, which is exactly the habit from the workflow checklist."))

# ============================================================ 37. KEY TAKEAWAYS
els = [
    rect("bg30",0,0,W,H,BG),
    kicker("k30",MX,72,"If you remember nothing else", color=ACCENT2),
    txt("t30",MX,104,1100,70,"Key Takeaways",56,weight=800,family=DISPLAY),
]
takeaways = [
    ("Commit like it's free","Small, frequent, honestly-labelled snapshots cost nothing and save everything.",ACCENT2),
    ("A GameObject is its components","Nothing more. Transform is the only one it can never lose.",ACCENT3),
    ("Structure is a habit, not a rule","A clean .gitignore and a tidy Hierarchy both pay off in week 12, not today.",ACCENT4),
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
els += footer(37)
slides.append(slide(37, els, "Read these three out loud slowly, same as Lecture 01's takeaways slide — this is the version students should be able to repeat back next week, even once the command syntax has faded."))

# ============================================================ 38. NEXT UP
els = [
    rect("bg31",0,0,W,H,BG),
    kicker("k31",MX,72,"Looking ahead"),
    txt("t31",MX,104,1100,70,"Next Up",56,weight=800,family=DISPLAY),
    rect("nx1",96,232,528,246,SURFACE,radius=14,stroke=BORDER,strokeWidth=1,extra={"fx":{"enter":"fade-up","order":0}}),
    rect("nx1bar",96,232,528,6,ACCENT2,extra={"fx":{"enter":"fade-up","order":0}}),
    txt("nx1k",96+32,264,460,24,"TODAY'S LAB",13,color=ACCENT2,weight=700,family=MONOF,extra={"letterSpacing":2,"fx":{"enter":"fade-up","order":0}}),
    txt("nx1t",96+32,294,460,44,"Git Setup &amp; Your First Commit",22,weight=700,family=DISPLAY,extra={"fx":{"enter":"fade-up","order":0}}),
    txt("nx1d",96+32,346,460,110,"Install Git, create a GitHub account, initialize a Unity repo with the right .gitignore, and make your first real commit.",16.5,color=MUTED,lh=1.6,extra={"fx":{"enter":"fade-up","order":0}}),
    rect("nx2",656,232,528,246,SURFACE,radius=14,stroke=BORDER,strokeWidth=1,extra={"fx":{"enter":"fade-up","order":1}}),
    rect("nx2bar",656,232,528,6,ACCENT3,extra={"fx":{"enter":"fade-up","order":1}}),
    txt("nx2k",656+32,264,460,24,"LECTURE 03 &middot; TENTATIVE",13,color=ACCENT3,weight=700,family=MONOF,extra={"letterSpacing":2,"fx":{"enter":"fade-up","order":1}}),
    txt("nx2t",656+32,294,460,44,"Components &amp; Your First Script",22,weight=700,family=DISPLAY,extra={"fx":{"enter":"fade-up","order":1}}),
    txt("nx2d",656+32,346,460,110,"Writing a MonoBehaviour, the component lifecycle, and moving a GameObject with real C# &mdash; CLO-3 begins.",16.5,color=MUTED,lh=1.6,extra={"fx":{"enter":"fade-up","order":1}}),
    rect("nxread",96,510,1088,74,ACCENT2_SOFT,radius=12,stroke="rgba(85,214,194,0.3)",strokeWidth=1,extra={"fx":{"enter":"fade-up","order":2}}),
    txt("nxreadt",96+28,533,1032,30,"Before then: install <b>Git</b> and create a free <b>GitHub</b> account &mdash; bring a laptop with both ready for lab.",16.5,color=TEXT,extra={"fx":{"enter":"fade-up","order":2}}),
] + footer(38)
slides.append(slide(38, els, "Lecture 03's exact scope is a placeholder — confirm against the actual week-3 plan before presenting and adjust this card if needed. The lab card is firm: git setup is the natural hands-on partner to today's Part 2."))

# ============================================================ 39. THANK YOU
els = [
    rect("bg32",0,0,W,H,BG),
    rect("tf2", MX, 220, 64, 3, ACCENT2, shadow=glow(ACCENT2_GLOW, 18),
         extra={"fx":{"enter":"fade-up","order":0,"ambient":"kenburns","ken":{"dir":"drift","scale":1.0,"duration":16}}}),
    txt("tyk",MX,256,700,28,"SEE YOU IN LAB",15,color=ACCENT2,weight=700,family=MONOF,extra={"letterSpacing":3,"fx":{"enter":"fade-up","order":0}}),
    txt("tyt",MX,292,1120,120,"Questions?",76,weight=800,family=DISPLAY,extra={"letterSpacing":-1,"fx":{"enter":"fade-up","order":1}}),
    rect("tydiv",MX,428,340,2,BORDER2,extra={"fx":{"enter":"fade-up","order":2}}),
    txt("typrompt",MX,456,760,80,"One thing to bring to lab: create a Git repository for any folder on your computer and make one real commit.",19,color=MUTED,lh=1.55,extra={"fx":{"enter":"fade-up","order":2}}),
    txt("tycontact",MX,560,700,30,"hello@madratzz.net &nbsp;&middot;&nbsp; muhammadraza.vf@itu.edu.pk",15,color=FAINT,family=MONOF,extra={"fx":{"enter":"fade-up","order":3}}),
] + footer(39)
slides.append(slide(39, els, "Close on the discussion prompt — a soft assignment that gets everyone touching git before lab even starts. Stay after for individual questions, especially from anyone whose laptop needs Git installed."))

print(f"Total slides built: {len(slides)}")

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = json.load(open(os.path.join(HERE, "fonts", "fonts.json"), encoding="utf-8"))
PHOTO = json.load(open(os.path.join(HERE, "fonts", "photo-asset.json"), encoding="utf-8"))
LOGO = json.load(open(os.path.join(HERE, "fonts", "unity-logo-asset.json"), encoding="utf-8"))
ASSETS = {**FONTS, **PHOTO, **LOGO}

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
