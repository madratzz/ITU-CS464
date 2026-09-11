import json, math, os

# ---------- palette ----------
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

# validated dark-mode categorical set (donut / quadrant identity colors)
QUIZ  = "#C56727"
ASSIGN= "#259583"
LABS  = "#6478E6"
PROJ  = "#AE8525"
MIDT  = "#D14E80"
FINAL = "#5E9C35"

# glow colours (used as shadow colours — a dark deck lives or dies on these)
ACCENT_GLOW  = "rgba(255,138,61,0.55)"
ACCENT2_GLOW = "rgba(85,214,194,0.50)"
ACCENT3_GLOW = "rgba(108,140,255,0.50)"
ACCENT4_GLOW = "rgba(255,79,163,0.50)"
INK_GLOW     = "rgba(0,0,0,0.55)"

# real embedded faces (woff2 data URIs, OFL) — a fontFamily the document does not
# carry falls back silently, so these are shipped inside doc.assets.
DISPLAY = "'Instrument Sans', 'Helvetica Neue', Arial, sans-serif"
BODYF   = "'Instrument Sans', 'Helvetica Neue', Arial, sans-serif"
MONOF   = "'Space Mono', ui-monospace, 'SF Mono', Menlo, Consolas, monospace"

W, H = 1280, 720
MX = 96  # side margin

def glow(color, blur=30, x=None, y=None):
    s = {"blur": blur, "color": color}
    if x is not None: s["x"] = x
    if y is not None: s["y"] = y
    return s

def grad(angle, *stops):
    n = len(stops) - 1
    return {"angle": angle, "stops": [{"at": (i / n if n else 0), "color": c} for i, c in enumerate(stops)]}

def orbit_path(radius, start_deg=-90, steps=48, cw=True, ry=None):
    """A closed circular (or elliptical) motion-path, expressed RELATIVE to the
    element's resting position — the Orbital-template recipe. The element must be
    placed at the orbit's start angle; every point is an offset from there."""
    ry = radius if ry is None else ry
    a0 = math.radians(start_deg)
    x0, y0 = radius * math.cos(a0), ry * math.sin(a0)
    pts = []
    for i in range(steps + 1):
        a = a0 + (1 if cw else -1) * 2 * math.pi * i / steps
        pts.append("%.2f,%.2f" % (radius * math.cos(a) - x0, ry * math.sin(a) - y0))
    return "M0,0 L" + " L".join(pts[1:])

def orbit_pos(cx, cy, radius, deg, size, ry=None):
    """Top-left x,y for a body of `size` sitting on that orbit at `deg`."""
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

def line(id,x,y,w,h,color,strokeWidth=2,dashed=False,opacity=1,lineEnd=None,lineStart=None):
    e = {"id":id,"type":"shape","shape":"line","x":x,"y":y,"w":w,"h":h,"rotation":0,
         "opacity":opacity,"fill":color,"stroke":color,"strokeWidth":strokeWidth,
         "strokeStyle":"dashed" if dashed else "solid"}
    if lineEnd: e["lineEnd"] = lineEnd
    if lineStart: e["lineStart"] = lineStart
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
    """A hollow circle centred on (cx,cy). `march` = (distance, duration) makes its
    dashes crawl round the rim — the Orbital orbit-ring move."""
    e = ellipse(id,cx-d/2.0,cy-d/2.0,d,d,"rgba(0,0,0,0)",stroke=stroke,strokeWidth=strokeWidth,
                opacity=opacity,dashed=dashed,shadow=shadow)
    if march:
        e["fx"] = {"loop":{"type":"dash-march","distance":march[0],"duration":march[1]}}
    if extra: e.update(extra)
    return e

def body(id,cx,cy,radius,deg,size,fill,duration=18,cw=True,gradient=None,shadow=None,ry=None,extra=None):
    """A dot in orbit around (cx,cy): placed on the orbit at `deg`, then looped
    around it with a relative motion-path."""
    x,y = orbit_pos(cx,cy,radius,deg,size,ry=ry)
    e = ellipse(id,x,y,size,size,fill,gradient=gradient,shadow=shadow)
    e["fx"] = {"loop":{"type":"motion-path","duration":duration,
                        "path":orbit_path(radius,start_deg=deg,cw=cw,ry=ry)}}
    if extra: e.update(extra)
    return e

def orbit_motif(p, cx, cy, d_outer, core=86, c1=ACCENT, c2=ACCENT4, g1=ACCENT_GLOW,
                ring_col="rgba(255,138,61,0.30)", label=None):
    """The deck's recurring signature: a marching dashed orbit, a faint inner ring,
    a glowing core, and three bodies going round it at different rates."""
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
    """Slow-drifting motes. spec = [(x, y, size, colour, radius, duration), ...]"""
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
    """A small ring badge with a short glyph (e.g. 'X' or 'in') — a neutral,
    deck-styled stand-in for a platform icon rather than a reproduction of the
    platform's own logo artwork/colours."""
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

# reusable page-number footer + faint grid dot (very small, consistent, non-morph to keep it simple)
def footer(n, total=None, label="CS464 · GAME DEVELOPMENT"):
    # dynamic tokens: the page numbers stay correct no matter how the deck is re-cut
    return [
        txt(f"foot-l-{n}", MX, 664, 500, 28, label, 11, color=FAINT, family=MONOF, extra={"letterSpacing":1.5}),
        txt(f"foot-r-{n}", W-MX-160, 664, 160, 28, "{{page:2}} / {{pages}}", 11, color=FAINT, family=MONOF,
            align="right", extra={"letterSpacing":1.5}),
    ]

TOTAL = 35

# ============================================================ 1. COVER
els = [
    rect("bg1",0,0,W,H,BG),
    # faint corner frame accents
    rect("cf2", MX, 96, 64, 3, ACCENT, shadow=glow(ACCENT_GLOW, 18)),
    txt("k1", MX, 132, 700, 30, "CS464 &middot; GAME DEVELOPMENT &middot; FALL 2025", 15, color=ACCENT,
        weight=700, family=MONOF, extra={"letterSpacing":3}),
    txt("t1", MX, 230, 1100, 220, "Lecture 01", 128, color=TEXT, weight=800, family=DISPLAY,
        extra={"letterSpacing":-2}),
    txt("t1b", MX, 372, 1090, 90, "The Anatomy of Play", 34, color=MUTED, weight=400, family=BODYF),
    rect("cf3", MX, 500, 340, 2, BORDER2),
    {"id":"cvph","type":"image","x":128-32,"y":559-32,"w":64,"h":64,"rotation":0,"opacity":1,
     "src":"asset:photo-instructor","fit":"cover","radius":32},
    ring("cvphborder",128,559,64,"rgba(255,138,61,0.35)",strokeWidth=1.5,dashed=False),
    txt("instr1", 180, 528, 600, 34, "Muhammad Raza Butt &nbsp;&middot;&nbsp; Information Technology University", 17,
        color=MUTED, family=BODYF),
    txt("instr2", 180, 560, 600, 30, "hello@madratzz.net", 15, color=FAINT, family=MONOF),
] + social_badge("cvsocx", 189, 602, 18, "X", ACCENT) + [
    txt("cvsoc1t", 204, 592, 100, 20, "@imadratzz", 12, color=MUTED, family=MONOF),
] + social_badge("cvsocin", 320, 602, 18, "in", ACCENT) + [
    txt("cvsoc2t", 335, 592, 110, 20, "/madratzz", 12, color=MUTED, family=MONOF),
] + orbit_motif("cv", 986, 286, 300, core=92) + stars("cv", [
    (742, 128, 3, "rgba(255,255,255,0.45)", 26, 40),
    (1148, 470, 4, "rgba(255,138,61,0.55)", 34, 52),
    (868, 560, 3, "rgba(85,214,194,0.45)", 30, 46),
    (1176, 128, 3, "rgba(108,140,255,0.50)", 22, 38),
])
slides.append(slide(1, els, "Welcome students as they arrive. Introduce yourself once everyone is roughly settled. Set tone: this is a hands-on, build-things course, not a theory-only course — but today is deliberately theory-first so we share a common vocabulary before opening Unity next week.", transition="none"))

print("built slide 1")

# ============================================================ 2. AGENDA
agenda_part1 = [
    "01&nbsp;&nbsp;Meet your instructor",
    "02&nbsp;&nbsp;Course logistics &amp; format",
    "03&nbsp;&nbsp;What you'll build (final project)",
    "04&nbsp;&nbsp;The 15-week road ahead",
    "05&nbsp;&nbsp;How you're graded",
    "06&nbsp;&nbsp;Learning outcomes",
]
agenda_part2 = [
    "07&nbsp;&nbsp;Games as societal affordance",
    "08&nbsp;&nbsp;The MDA framework",
    "09&nbsp;&nbsp;Mechanics &rarr; Dynamics &rarr; Aesthetics",
    "10&nbsp;&nbsp;Bartle's player types",
    "11&nbsp;&nbsp;Designing for who plays",
    "12&nbsp;&nbsp;Recap &amp; what's next",
]
els = [
    rect("bg2",0,0,W,H,BG),
    kicker("k2",MX,72,"Today's session"),
    txt("t2",MX,104,1000,70,"Agenda",56,weight=800,family=DISPLAY),
    # two columns — card + heading land first, then each line builds in, one at a time, in sync across both columns
    rect("agc1",MX,232,528,392,SURFACE,radius=14,stroke=BORDER,strokeWidth=1,extra={"fx":{"enter":"fade-up","order":0}}),
    rect("agc1bar",MX,232,528,6,ACCENT,radius=0,extra={"fx":{"enter":"fade-up","order":0}}),
    txt("agc1k",MX+32,264,460,26,"PART 1",13,color=ACCENT,weight=700,family=MONOF,extra={"letterSpacing":2,"fx":{"enter":"fade-up","order":0}}),
    txt("agc1t",MX+32,290,460,40,"The Course &amp; You",26,weight=700,family=DISPLAY,extra={"fx":{"enter":"fade-up","order":0}}),
    rect("agc2",656,232,528,392,SURFACE,radius=14,stroke=BORDER,strokeWidth=1,extra={"fx":{"enter":"fade-up","order":0}}),
    rect("agc2bar",656,232,528,6,ACCENT2,radius=0,extra={"fx":{"enter":"fade-up","order":0}}),
    txt("agc2k",656+32,264,460,26,"PART 2",13,color=ACCENT2,weight=700,family=MONOF,extra={"letterSpacing":2,"fx":{"enter":"fade-up","order":0}}),
    txt("agc2t",656+32,290,460,40,"What Is a Game?",26,weight=700,family=DISPLAY,extra={"fx":{"enter":"fade-up","order":0}}),
]
for i, item in enumerate(agenda_part1):
    els.append(txt(f"agc1i{i}",MX+32,344+i*38,464,34,item,19,color=MUTED,extra={"fx":{"enter":"fade-up","order":i+1}}))
for i, item in enumerate(agenda_part2):
    els.append(txt(f"agc2i{i}",656+32,344+i*38,464,34,item,19,color=MUTED,extra={"fx":{"enter":"fade-up","order":i+1}}))
els += footer(2)
slides.append(slide(2, els, "Walk through the two halves of today: administrative/course-setup first, then design theory. Tell them Part 2 is the part they'll actually be tested on conceptually (see midterm spec) and will lean on all semester."))

# ============================================================ 3. INSTRUCTOR
els = [
    rect("bg3",0,0,W,H,BG),
    kicker("k3",MX,72,"Who's teaching this"),
    txt("t3",MX,104,1000,70,"Your Instructor",56,weight=800,family=DISPLAY),
    ring("phring",246,382,300,"rgba(255,138,61,0.40)",strokeWidth=1.5,march=(30,10)),
    {"id":"ph","type":"image","x":246-132,"y":382-132,"w":264,"h":264,"rotation":0,"opacity":1,
     "src":"asset:photo-instructor","fit":"cover","radius":132,
     "shadow":glow(ACCENT_GLOW,42),"fx":{"enter":"fade-up","order":0}},
    ring("phborder",246,382,264,"rgba(255,138,61,0.35)",strokeWidth=1.5,dashed=False,
         extra={"fx":{"enter":"fade-up","order":0}}),
    rect("phsocdiv",114,544,264,1,BORDER,extra={"fx":{"enter":"fade-up","order":0}}),
] + social_badge("phsocx",164,566,26,"X",ACCENT,extra={"fx":{"enter":"fade-up","order":0}}) + [
    txt("phsoc1",187,556,154,20,"@imadratzz",13,color=MUTED,family=MONOF,
        extra={"letterSpacing":0.5,"fx":{"enter":"fade-up","order":0}}),
] + social_badge("phsocin",164,602,26,"in",ACCENT,extra={"fx":{"enter":"fade-up","order":0}}) + [
    txt("phsoc2",187,592,154,20,"/madratzz",13,color=MUTED,family=MONOF,
        extra={"letterSpacing":0.5,"fx":{"enter":"fade-up","order":0}}),
    txt("iname",456,228,700,50,"Muhammad Raza Butt",38,weight=800,family=DISPLAY,extra={"fx":{"enter":"fade-up","order":1}}),
    txt("irole",456,280,700,26,"Technical Head &mdash; Games Dept., 9D Technologies (Lahore)",18,
        color=ACCENT,weight=700,extra={"fx":{"enter":"fade-up","order":1}}),
    txt("iyears",456,308,700,24,"Unity / C# game development &middot; a decade in production",15,
        color=MUTED,extra={"fx":{"enter":"fade-up","order":1}}),
    rect("idiv",456,344,620,1,BORDER,extra={"fx":{"enter":"fade-up","order":2}}),
    txt("iexp1",456,364,620,60,
        "Previously technical lead roles at<br>"
        "<b>ImaginationAI</b> &middot; <b>Mindstorm Studios</b> &middot; <b>Ozi Technology</b>",
        17, color=MUTED, lh=1.7, extra={"fx":{"enter":"fade-up","order":2}}),
    txt("ishipk",456,438,620,18,"SHIPPED",10.5,color=ACCENT2,weight=700,family=MONOF,
        extra={"letterSpacing":2,"fx":{"enter":"fade-up","order":3}}),
] + [e for i,t in enumerate(["Tile Garden","Wordle"])
       for e in chip(f"iship{i}",456+i*164,462,150,34,t,ACCENT2)] + [
    txt("iexp2",456,516,620,60,
        "Hands-on with the full Unity stack &mdash; VContainer DI, ScriptableObject "
        "architecture, Addressables, finite state machines, mobile &amp; GPU-side optimization.",
        15.5, color=MUTED, lh=1.55, extra={"fx":{"enter":"fade-up","order":4}}),
    rect("icontactbar",456,596,620,1,BORDER,extra={"fx":{"enter":"fade-up","order":5}}),
    txt("icontact",456,614,620,30,"hello@madratzz.net &nbsp;&middot;&nbsp; muhammadraza.vf@itu.edu.pk",15,
        color=FAINT, family=MONOF, extra={"fx":{"enter":"fade-up","order":5}}),
] + footer(3)
slides.append(slide(3, els, "Brief personal intro — keep to ~2 minutes. The point isn't the resume, it's credibility: everything taught in this course is stuff used in shipped, real production Unity projects, not just textbook theory."))

# ============================================================ 4. COURSE AT A GLANCE
els = [
    rect("bg4",0,0,W,H,BG),
    kicker("k4",MX,72,"Logistics"),
    txt("t4",MX,104,1000,70,"Course at a Glance",56,weight=800,family=DISPLAY),
    # 4 stat tiles
    rect("g1",96,232,254,190,SURFACE,radius=14,stroke=BORDER,strokeWidth=1,extra={"fx":{"enter":"fade-up","order":0}}),
    txt("g1n",96+24,256,206,70,"15",48,color=ACCENT,weight=800,family=DISPLAY,extra={"fx":{"enter":"fade-up","order":0,"countUp":True}}),
    txt("g1l",96+24,330,206,80,"Lectures<br>1.5 hr each, weekly",16,color=MUTED,lh=1.5,extra={"fx":{"enter":"fade-up","order":0}}),
    rect("g2",374,232,254,190,SURFACE,radius=14,stroke=BORDER,strokeWidth=1,extra={"fx":{"enter":"fade-up","order":1}}),
    txt("g2n",374+24,256,206,70,"1",48,color=ACCENT2,weight=800,family=DISPLAY,extra={"fx":{"enter":"fade-up","order":1,"countUp":True}}),
    txt("g2l",374+24,330,206,80,"Lab / week<br>1.5 hr, hands-on Unity",16,color=MUTED,lh=1.5,extra={"fx":{"enter":"fade-up","order":1}}),
    rect("g3",652,232,254,190,SURFACE,radius=14,stroke=BORDER,strokeWidth=1,extra={"fx":{"enter":"fade-up","order":2}}),
    txt("g3n",652+24,256,206,70,"2+1",48,color=ACCENT3,weight=800,family=DISPLAY,extra={"fx":{"enter":"fade-up","order":2}}),
    txt("g3l",652+24,330,206,80,"Credit hours<br>Core for BSCS &amp; BSAI",16,color=MUTED,lh=1.5,extra={"fx":{"enter":"fade-up","order":2}}),
    rect("g4",930,232,254,190,SURFACE,radius=14,stroke=BORDER,strokeWidth=1,extra={"fx":{"enter":"fade-up","order":3}}),
    txt("g4n",930+24,256,206,70,"1",48,color=TEXT,weight=800,family=DISPLAY,extra={"fx":{"enter":"fade-up","order":3,"countUp":True}}),
    txt("g4l",930+24,330,206,80,"Game shipped<br>by each of you, solo",16,color=MUTED,lh=1.5,extra={"fx":{"enter":"fade-up","order":3}}),
    # resources strip
    rect("res",96,448,1088,176,SURFACE,radius=14,stroke=BORDER,strokeWidth=1),
    txt("resk",96+32,472,400,24,"COURSE RESOURCES",13,color=FAINT,weight=700,family=MONOF,extra={"letterSpacing":2}),
    txt("resb",96+32,500,1024,110,
        "Unity Learn &mdash; <b>Unity Essentials</b> &amp; <b>Create with Code</b> pathways &middot; "
        "Unity Documentation &mdash; Scripting API, UI Toolkit, Input System. Both are free; links go up on the course page today.",
        18, color=MUTED, lh=1.6),
] + footer(4)
slides.append(slide(4, els, "Emphasize the resources are free and official — Unity Learn pathways map closely to what labs will walk through. Mention where the course page / drive folder lives (fill in live)."))

# ============================================================ 5. WHAT YOU'LL BUILD
els = [
    rect("bg5",0,0,W,H,BG),
    kicker("k5",MX,72,"The destination", color=ACCENT2),
    txt("t5",MX,104,1100,70,"What You'll Build",56,weight=800,family=DISPLAY),
    txt("t5b",MX,176,1000,34,"Your final exam is not a paper &mdash; it's a playable game.",19,color=MUTED),
    # left: requirement checklist card
    rect("wb1",96,232,620,392,SURFACE,radius=14,stroke=BORDER,strokeWidth=1,extra={"fx":{"enter":"fade-up","order":0}}),
    txt("wb1k",96+32,264,540,26,"YOUR GAME MUST DEMONSTRATE",13,color=ACCENT2,weight=700,family=MONOF,extra={"letterSpacing":2,"fx":{"enter":"fade-up","order":0}}),
    txt("wb1b",96+32,300,556,300,
        "&#9679;&nbsp; Player movement &amp; controls<br>"
        "&#9679;&nbsp; Physics-based interactions<br>"
        "&#9679;&nbsp; UI &mdash; score, health, menus<br>"
        "&#9679;&nbsp; Collectables or enemies / obstacles<br>"
        "&#9679;&nbsp; Audio &amp; visual feedback<br>"
        "&#9679;&nbsp; 5 levels, or one polished endless loop",
        18.5, color=TEXT, lh=1.95, extra={"fx":{"enter":"fade-up","order":0}}),
    # right: deliverables + framing
    rect("wb2",752,232,432,190,SURFACE2,radius=14,stroke=BORDER2,strokeWidth=1,extra={"fx":{"enter":"fade-up","order":1}}),
    txt("wb2k",752+28,258,376,24,"DELIVERABLES",12,color=ACCENT,weight=700,family=MONOF,extra={"letterSpacing":2,"fx":{"enter":"fade-up","order":1}}),
    txt("wb2b",752+28,286,376,120,"Playable build + full Unity project + a short report / presentation.",17,color=MUTED,lh=1.6,extra={"fx":{"enter":"fade-up","order":1}}),
    rect("wb3",752,438,432,186,ACCENT_SOFT,radius=14,stroke="rgba(255,138,61,0.35)",strokeWidth=1,extra={"fx":{"enter":"fade-up","order":2}}),
    txt("wb3k",752+28,462,376,24,"EVALUATED THROUGH",12,color=ACCENT,weight=700,family=MONOF,extra={"letterSpacing":2,"fx":{"enter":"fade-up","order":2}}),
    txt("wb3b",752+28,490,376,120,"Bartle's Taxonomy &amp; the MDA framework &mdash; the exact theory we cover today.",17,color=TEXT,lh=1.6,extra={"fx":{"enter":"fade-up","order":2}}),
] + footer(5)
slides.append(slide(5, els, "This is the hook slide — make it land. Everything theoretical today (MDA, Bartle) is not academic decoration, it's literally the rubric language for their final grade. That's the throughline for the whole semester."))

# ============================================================ 6-7. THE 15-WEEK ARC
# Rebuilt from scratch: an ascending constellation. Four act-nodes climb a curved
# trajectory (the rise is the point — the workload and the Bloom level both go up).
# Page 1 shows the road ahead as unlit husks; page 2 morphs them into glowing discs.

def catmull_d(pts):
    """SVG cubic path through every point (Catmull-Rom -> Bezier)."""
    n = len(pts)
    d = "M %.1f %.1f" % pts[0]
    for i in range(n - 1):
        p0 = pts[i - 1] if i > 0 else pts[0]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < n else pts[-1]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        d += " C %.1f %.1f %.1f %.1f %.1f %.1f" % (c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])
    return d

def catmull_samples(pts, per_seg=14):
    """Sample the same curve, for a motion-path that rides it."""
    out = []
    n = len(pts)
    for i in range(n - 1):
        p0 = pts[i - 1] if i > 0 else pts[0]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < n else pts[-1]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        for s in range(per_seg + (1 if i == n - 2 else 0)):
            t = s / float(per_seg)
            u = 1 - t
            x = u*u*u*p1[0] + 3*u*u*t*c1[0] + 3*u*t*t*c2[0] + t*t*t*p2[0]
            y = u*u*u*p1[1] + 3*u*u*t*c1[1] + 3*u*t*t*c2[1] + t*t*t*p2[1]
            out.append((x, y))
    return out

# node centres — spacing even, rise accelerating (42 / 70 / 104)
ARC_NODES = [(222, 490), (490, 450), (758, 396), (1026, 330)]
ARC_TRACK = [(118, 498)] + ARC_NODES + [(1150, 308)]
ARC_BOX = (96, 220, 1088, 400)          # x, y, w, h of the path element
ARC_LOCAL = [(x - ARC_BOX[0], y - ARC_BOX[1]) for x, y in ARC_TRACK]

ACTS = [
    ("I",   "WEEKS 1&ndash;3",   "Design<br>Foundations",   "CLO-1 &middot; Understand",
     ACCENT,  grad(35, "#FF8A3D", "#FFC178"), ACCENT_GLOW),
    ("II",  "WEEKS 4&ndash;7",   "Inside Unity",            "CLO-2 &middot; Understand",
     ACCENT2, grad(35, "#55D6C2", "#3FB4E8"), ACCENT2_GLOW),
    ("III", "WEEKS 9&ndash;12",  "Mechanics<br>&amp; Systems", "CLO-3/4 &middot; Apply &amp; Analyze",
     ACCENT3, grad(35, "#6C8CFF", "#A579FF"), ACCENT3_GLOW),
    ("IV",  "WEEKS 13&ndash;15", "Ship It",                 "CLO-5 &middot; Create",
     ACCENT4, grad(35, "#FF4FA3", "#FF8A6B"), ACCENT4_GLOW),
]

ND = 92          # node diameter
COLW = 240       # label column width


def arc_node(i, lit):
    """One act on the trajectory. `lit` toggles between an unlit husk and a
    glowing disc — same ids on both pages, so the morph does the lighting."""
    num, weeks, title, clo, col, gr, gl = ACTS[i]
    cx, cy = ARC_NODES[i]
    lx = cx - COLW / 2
    if lit:
        disc = ellipse(f"nd{i}", cx - ND/2, cy - ND/2, ND, ND, col,
                       gradient=gr, shadow=glow(gl, 70))
        numc, wkc, tc, cloc = BG, col, TEXT, MUTED
    else:
        disc = ellipse(f"nd{i}", cx - ND/2, cy - ND/2, ND, ND, "rgba(255,255,255,0.025)",
                       stroke=BORDER2, strokeWidth=1.5)
        numc, wkc, tc, cloc = FAINT, "rgba(92,100,114,0.85)", "rgba(154,162,177,0.55)", "rgba(92,100,114,0.55)"
    return [
        # an opaque puck so the trajectory never draws across a node
        ellipse(f"ndmask{i}", cx - ND/2 - 6, cy - ND/2 - 6, ND + 12, ND + 12, BG),
        disc,
        txt(f"ndnum{i}", cx - ND/2, cy - 20, ND, 40, num, 27, color=numc, weight=800,
            family=DISPLAY, align="center", valign="middle", lh=1),
        txt(f"ndwk{i}", lx, cy - 88, COLW, 20, weeks, 11, color=wkc, weight=700,
            family=MONOF, align="center", extra={"letterSpacing": 2}),
        txt(f"ndt{i}", lx, cy + 58, COLW, 50, title, 21, color=tc, weight=800,
            family=DISPLAY, align="center", lh=1.15),
        txt(f"ndclo{i}", lx, cy + 58 + (54 if "<br>" in title else 30), COLW, 20, clo, 11,
            color=cloc, family=MONOF, align="center", extra={"letterSpacing": 1}),
    ]


def arc_shared():
    return [
        kicker("k6", MX, 64, "The road ahead"),
        txt("t6", MX, 92, 1000, 62, "The 15-Week Arc", 50, weight=800, family=DISPLAY, role="title"),
        txt("t6b", MX, 158, 900, 26, "Four acts. Each one asks more of you than the last.",
            17, color=MUTED, role="subtitle"),
        # the trajectory itself — dashes crawl uphill the whole time it is on screen
        path_shape("arctrack", ARC_BOX[0], ARC_BOX[1], ARC_BOX[2], ARC_BOX[3],
                   catmull_d(ARC_LOCAL), "rgba(255,255,255,0.20)", strokeWidth=2,
                   strokeStyle="dashed",
                   extra={"fx": {"loop": {"type": "dash-march", "distance": 18, "duration": 2.4}}}),
        # a slow comet tracing the whole semester, out and back so it never snaps
        ellipse("arccomet", ARC_TRACK[0][0] - 5, ARC_TRACK[0][1] - 5, 10, 10, "#FFD9B8",
                shadow=glow("rgba(255,180,120,0.9)", 22),
                extra={"fx": {"loop": {"type": "motion-path", "duration": 22, "ease": "none",
                                       "path": arc_comet_path()}}}),
        # "we are here" halo around Act I
        ring("arcnow", ARC_NODES[0][0], ARC_NODES[0][1], 124, "rgba(255,138,61,0.45)",
             strokeWidth=1.5, march=(26, 6)),
        txt("arcnowlbl", ARC_NODES[0][0] - 90, ARC_NODES[0][1] - 114, 180, 18, "TODAY", 10.5,
            color=ACCENT, weight=700, family=MONOF, align="center", extra={"letterSpacing": 3}),
    ]


def arc_comet_path():
    pts = catmull_samples(ARC_LOCAL, per_seg=12)
    x0, y0 = pts[0]
    fwd = ["%.1f,%.1f" % (x - x0, y - y0) for x, y in pts]
    return "M0,0 L" + " L".join(fwd[1:] + fwd[-2::-1])


# --- Page 1 of 2: only the ground you have covered is lit
els = [rect("bg6", 0, 0, W, H, BG)] + arc_shared()
for i in range(4):
    els += arc_node(i, lit=(i < 2))
els += [
    txt("pgtag6", 1184 - 200, 64, 200, 22, "PART 1 OF 2", 10.5, color=FAINT, weight=700,
        family=MONOF, align="right", extra={"letterSpacing": 3}),
] + footer(6)
slides.append(slide(6, els, "Set expectations for the shape of the semester. Point out that the trajectory RISES — the work gets harder on purpose, and the verbs change from 'understand' to 'create'. Only the first two acts are lit; advance once and the rest of the road comes on.", transition="fade"))

# --- Page 2 of 2: the whole road lights up, and the midterm lands between acts
els = [rect("bg7", 0, 0, W, H, BG)] + arc_shared()
for i in range(4):
    els += arc_node(i, lit=True)
mtx, mty = (ARC_NODES[1][0] + ARC_NODES[2][0]) / 2.0, (ARC_NODES[1][1] + ARC_NODES[2][1]) / 2.0
els += [
    ellipse("mtdot", mtx - 7, mty - 7, 14, 14, "#FFFFFF", stroke=ACCENT, strokeWidth=2.5,
            shadow=glow(ACCENT_GLOW, 20)),
    rect("mttick", mtx - 1, mty - 44, 2, 38, "rgba(255,138,61,0.45)"),
    txt("mtlabel", mtx - 80, mty - 68, 160, 18, "MIDTERM &middot; WK 8", 10.5, color=ACCENT,
        weight=700, family=MONOF, align="center", extra={"letterSpacing": 2}),
    txt("pgtag7", 1184 - 200, 64, 200, 22, "PART 2 OF 2", 10.5, color=FAINT, weight=700,
        family=MONOF, align="right", extra={"letterSpacing": 3}),
] + footer(7)
slides.append(slide(7, els, "Acts III and IV light up: this is where the course stops being about understanding and starts being about building and shipping. Flag the midterm at week 8 — it sits exactly on the seam between 'learning Unity' and 'building systems'.", transition="morph"))

# ============================================================ 8-9. GRADING BREAKDOWN — revealed 3 portions at a time
cats = [
    ("Quizzes","25%","4 quizzes across the term.",QUIZ),
    ("Assignments","15%","6–8 short C#/Unity exercises.",ASSIGN),
    ("Labs","10%","Weekly hands-on practical work.",LABS),
    ("Projects","10%","Project checkpoints along the way.",PROJ),
    ("Midterm Exam","10%","Week 8 &middot; concepts + short code.",MIDT),
    ("Final Exam","30%","Your project, presented &amp; documented.",FINAL),
]

def grade_pie(animate=True):
    e = {"id":"chart7","type":"chart","x":96,"y":224,"w":420,"h":380,"rotation":0,"opacity":1,
     "preset":"pie",
     "option":{
        "color":[QUIZ,ASSIGN,LABS,PROJ,MIDT,FINAL],
        "series":[{"type":"pie","radius":["46%","74%"],
                   "data":[
                       {"name":"Quizzes  25%","value":25},
                       {"name":"Assignments  15%","value":15},
                       {"name":"Labs  10%","value":10},
                       {"name":"Projects  10%","value":10},
                       {"name":"Midterm  10%","value":10},
                       {"name":"Final  30%","value":30},
                   ],
                   "label":False,
                   "itemStyle":{"borderColor":BG,"borderWidth":4}}],
        "legend":False,
        "tooltip":{"show":False},
     }}
    if animate:
        e["fx"] = {"enter":"fade-up"}
    return e

def grade_card(id_prefix,x,y,w,h,name,pct,detail,col,order):
    fx = {"fx":{"enter":"fade-up","order":order}} if order is not None else {}
    return [
        rect(f"{id_prefix}bg",x,y,w,h,SURFACE,radius=12,stroke=BORDER,strokeWidth=1,extra=fx),
        rect(f"{id_prefix}bar",x,y,4,h,col,radius=0,extra=fx),
        txt(f"{id_prefix}name",x+22,y+16,w-100,26,name,16,weight=700,family=DISPLAY,extra=fx),
        txt(f"{id_prefix}pct",x+w-78,y+14,58,28,pct,20,color=col,weight=800,family=DISPLAY,align="right",extra=fx),
        txt(f"{id_prefix}detail",x+22,y+46,w-40,h-56,detail,12.5,color=MUTED,lh=1.35,extra=fx),
    ]

grade_col0_x, grade_col1_x, grade_card_w = 560, 884, 300
grade_rows_y = [224,354,484]

# --- Page 1 of 2: the pie (all six slices) plus the first three portions
els = [
    rect("bg8",0,0,W,H,BG),
    kicker("k8g",MX,72,"Grading"),
    txt("t8g",MX,104,1000,70,"How You're Graded",56,weight=800,family=DISPLAY),
    txt("t8gb",MX,176,1000,30,"Six components &mdash; the final project alone is nearly a third of your grade.",18,color=MUTED),
    grade_pie(),
]
for i,(name,pct,detail,col) in enumerate(cats[:3]):
    els += grade_card(f"gc{i}",grade_col0_x,grade_rows_y[i],grade_card_w,110,name,pct,detail,col,i)
els += [
    rect("gcGhost",grade_col1_x,224,grade_card_w,370,"rgba(255,255,255,0.015)",radius=12,
         stroke="rgba(255,255,255,0.13)",strokeWidth=1,
         extra={"strokeStyle":"dashed","fx":{"enter":"fade-up","order":3}}),
    txt("gcGhostT",grade_col1_x,224,grade_card_w,370,"THREE MORE<br>COMPONENTS<br>&#8595;",11,color=FAINT,
        family=MONOF,align="center",valign="middle",lh=2.0,
        extra={"letterSpacing":2,"fx":{"enter":"fade-up","order":3}}),
    txt("pgtag8",1184-160,72,160,24,"PART 1 OF 2",11.5,color=FAINT,weight=700,family=MONOF,align="right",
        extra={"letterSpacing":1.5}),
] + footer(8)
slides.append(slide(8, els, "Four quizzes, roughly biweekly. Six to eight assignments, mostly short C#/Unity exercises paired to that week's lecture. Reveal one column at a time rather than dumping all six at once.", transition="fade"))

# --- Page 2 of 2 (morph): same pie, same first three cards — the remaining three arrive
els = [
    rect("bg9",0,0,W,H,BG),
    kicker("k8g",MX,72,"Grading"),
    txt("t8g",MX,104,1000,70,"How You're Graded",56,weight=800,family=DISPLAY),
    txt("t8gb",MX,176,1000,30,"Six components &mdash; the final project alone is nearly a third of your grade.",18,color=MUTED),
    grade_pie(animate=False),
]
for i,(name,pct,detail,col) in enumerate(cats[:3]):
    els += grade_card(f"gc{i}",grade_col0_x,grade_rows_y[i],grade_card_w,110,name,pct,detail,col,None)
for i,(name,pct,detail,col) in enumerate(cats[3:]):
    els += grade_card(f"gc{i+3}",grade_col1_x,grade_rows_y[i],grade_card_w,110,name,pct,detail,col,i)
els += [
    txt("pgtag9",1184-160,72,160,24,"PART 2 OF 2",11.5,color=FAINT,weight=700,family=MONOF,align="right",
        extra={"letterSpacing":1.5}),
] + footer(9)
slides.append(slide(9, els, "Projects, the midterm, and the final exam land now. The final exam alone is 30% — it IS the game they build, not a written paper.", transition="morph"))

# ============================================================ 8. LEARNING OUTCOMES
clos = [
    ("CLO-1","Explain game design principles, the MDA framework, and the societal affordances of games.","L2 &middot; Understand"),
    ("CLO-2","Configure the Unity environment, version control, and basic scene hierarchy.","L2 &middot; Understand"),
    ("CLO-3","Implement game mechanics using C# scripting, physics, and mathematical applications.","L3 &middot; Apply"),
    ("CLO-4","Analyze and debug complex game behaviors &mdash; systems, physics, UI, audio, performance.","L4 &middot; Analyze"),
    ("CLO-5","Design, develop, and present a complete, polished game project.","L6 &middot; Evaluate / Create"),
]
rows = [{"cells":[{"html":"CLO#","bold":True},{"html":"Course Learning Outcome","bold":True},{"html":"Bloom Level","bold":True}]}]
for c,o,b in clos:
    rows.append({"cells":[{"html":f"<b>{c}</b>"},{"html":o},{"html":b}]})
els = [
    rect("bg8",0,0,W,H,BG),
    kicker("k8",MX,72,"By the end of the semester"),
    txt("t8",MX,104,1000,70,"Learning Outcomes",56,weight=800,family=DISPLAY),
    txt("t8b",MX,176,1000,30,"CLO-1 &mdash; today's whole lecture &mdash; is where this list begins.",18,color=ACCENT),
    {"id":"clotable","type":"table","x":96,"y":230,"w":1088,"h":410,"rotation":0,"opacity":1,
     "fx":{"enter":"fade-up"},
     "columns":[{"w":0.12},{"w":0.62},{"w":0.26}],
     "header":True,
     "rows":rows,
     "style":{"headerBg":SURFACE2,"headerColor":TEXT,"zebra":True,"borderColor":BORDER,
              "borderWidth":1,"cellPadX":22,"cellPadY":16,"fontSize":16.5,"color":MUTED,"radius":12}},
] + footer(10)
slides.append(slide(10, els, "Five outcomes, roughly one per act of the semester (see the roadmap). Bloom's level climbs as the semester does: Understand -> Apply -> Analyze -> Create. Today lives entirely inside CLO-1."))

# ============================================================ 9. SECTION BREAK — WHAT IS A GAME?
els = [
    rect("bg9",0,0,W,H,BG),
    rect("sb9line",MX,300,120,4,ACCENT2,shadow=glow(ACCENT2_GLOW,18),
         extra={"fx":{"enter":"fade-up","order":0,"ambient":"kenburns","ken":{"dir":"drift","scale":1.0,"duration":18}}}),
    txt("sb9k",MX,326,700,28,"PART 2 OF TODAY",15,color=ACCENT2,weight=700,family=MONOF,extra={"letterSpacing":3,"fx":{"enter":"fade-up","order":0}}),
    txt("sb9t",MX,362,1120,140,"What Is a Game?",84,weight=800,family=DISPLAY,extra={"letterSpacing":-1,"fx":{"enter":"fade-up","order":1}}),
    txt("sb9s",MX,486,1000,40,"From societal affordance, to a framework for talking about design: MDA.",20,color=MUTED,
        extra={"fx":{"enter":"fade-up","order":2}}),
] + orbit_motif("sb9o", 986, 344, 316, core=96, c1=ACCENT2, c2=ACCENT3,
                g1=ACCENT2_GLOW, ring_col="rgba(85,214,194,0.30)") + footer(11)
slides.append(slide(11, els, "Transition moment — close laptops for a minute if you like, this bit is discussion, not note-taking (slides will be posted). Ask the room: 'what's a game you played this week, and why?' Use a couple of answers to seed the affordances discussion on the next slide.", transition="fade"))


# ============================================================ 10. WHAT IS A GAME?
game_parts = [
    ("Players","Someone (or something) choosing to take part."),
    ("Rules","The constraints that make the conflict fair and legible."),
    ("Goals &amp; Conflict","Something to strive for, and something making it hard."),
    ("Boundaries","A space set apart from ordinary life &mdash; next slide's magic circle."),
    ("Outcome","A result you can measure. You can tell who won."),
]
els = [
    rect("bg10",0,0,W,H,BG),
    kicker("k10",MX,72,"Defining our terms", color=ACCENT2),
    txt("t10",MX,104,1100,64,"What Is a Game?",50,weight=800,family=DISPLAY),
    rect("qc10",96,182,1088,94,SURFACE2,radius=14,stroke=BORDER2,strokeWidth=1),
    txt("qc10q",96+32,198,1024,44,
        "<i>&ldquo;A game is a system in which players engage in an artificial conflict, defined by rules, that results in a quantifiable outcome.&rdquo;</i>",
        18,color=TEXT),
    txt("qc10a",96+32,244,1024,22,"&mdash; Katie Salen &amp; Eric Zimmerman, <i>Rules of Play</i> (2004)",13.5,color=MUTED,family=MONOF),
]
xs5 = [96,316,536,756,976]
for i,(name,desc) in enumerate(game_parts):
    x = xs5[i]
    fx = {"fx":{"enter":"fade-up","order":i}}
    els += [
        rect(f"gp{i}",x,292,204,164,SURFACE,radius=12,stroke=BORDER,strokeWidth=1,extra=fx),
        rect(f"gp{i}bar",x,292,204,3,ACCENT2,radius=0,opacity=0.55,extra=fx),
        txt(f"gp{i}n",x+18,310,170,18,f"0{i+1}",11,color=FAINT,weight=700,family=MONOF,
            extra={"letterSpacing":2,**fx}),
        txt(f"gp{i}t",x+18,332,168,46,name,16.5,weight=700,family=DISPLAY,color=ACCENT2,lh=1.15,extra=fx),
        txt(f"gp{i}d",x+18,382,168,66,desc,12,color=MUTED,lh=1.4,extra=fx),
    ]
els += [
    txt("t10note",MX,500,1088,30,
        "Four of these five are negotiable. Change the fifth &mdash; Outcome &mdash; and you're not designing a game anymore.",
        14.5,color=FAINT),
] + footer(12)
slides.append(slide(12, els, "Anchor everything today on this one sentence — Salen & Zimmerman's definition from Rules of Play (2004) is the closest thing game design has to a formal spec. Walk through the five parts quickly; boundaries and rules each get their own slide next."))

# ============================================================ 11. THE MAGIC CIRCLE
# Rebuilt as a live orbit: a marching dashed boundary with players circling the
# game inside it, and ordinary life still turning, untouched, outside.
MC_CX, MC_CY = 296, 378
MC_D = 264                       # the boundary
els = [
    rect("bg11m",0,0,W,H,BG),
    kicker("k11m",MX,64,"Where the game happens", color=ACCENT3),
    txt("t11m",MX,92,1000,60,"The Magic Circle",48,weight=800,family=DISPLAY,role="title"),

    # --- ordinary life, still turning outside the boundary
    txt("olabel",MC_CX-160,196,320,20,"ORDINARY LIFE",10.5,color=FAINT,family=MONOF,
        align="center",weight=700,extra={"letterSpacing":3}),
    body("ol1",MC_CX,MC_CY,168,-60,6,"rgba(154,162,177,0.55)",duration=46),
    body("ol2",MC_CX,MC_CY,176,80,5,"rgba(154,162,177,0.40)",duration=54,cw=False),
    body("ol3",MC_CX,MC_CY,164,205,6,"rgba(154,162,177,0.45)",duration=50),

    # --- the boundary itself: dashes crawl round it the whole time it is on screen
    ring("mcring",MC_CX,MC_CY,MC_D,"rgba(108,140,255,0.55)",strokeWidth=2,march=(30,9),
         shadow=glow("rgba(108,140,255,0.28)",26)),
    ring("mcring2",MC_CX,MC_CY,MC_D+26,"rgba(108,140,255,0.13)",strokeWidth=1,dashed=False),

    # --- the game at the centre, and the players orbiting it
    ellipse("mccore",MC_CX-52,MC_CY-52,104,104,ACCENT3,gradient=grad(35,"#6C8CFF","#9B7BFF"),
            shadow=glow(ACCENT3_GLOW,60)),
    txt("mccoret",MC_CX-52,MC_CY-52,104,104,"THE<br>GAME",14,weight=800,family=DISPLAY,
        color="#0B1024",align="center",valign="middle",lh=1.25,extra={"letterSpacing":1}),
    body("mcp1",MC_CX,MC_CY,80,-90,13,ACCENT2,duration=15,shadow=glow(ACCENT2_GLOW,14)),
    body("mcp2",MC_CX,MC_CY,80,150,11,ACCENT,duration=15,shadow=glow(ACCENT_GLOW,14)),
    body("mcp3",MC_CX,MC_CY,112,20,10,"#FFFFFF",duration=24,cw=False,
         shadow=glow("rgba(255,255,255,0.5)",12)),
    body("mcp4",MC_CX,MC_CY,112,230,9,ACCENT4,duration=24,cw=False,shadow=glow(ACCENT4_GLOW,12)),
    txt("mcinlbl",MC_CX-120,MC_CY+150,240,20,"INSIDE: DIFFERENT RULES",10,color=ACCENT3,
        family=MONOF,align="center",weight=700,extra={"letterSpacing":2}),

    # --- right column
    txt("mc-def",560,206,624,92,
        "A boundary &mdash; in time, space, or attention &mdash; that separates a game's reality from ordinary life. Step inside, and different rules apply than the ones you live by outside.",
        17,color=TEXT,lh=1.5,extra={"fx":{"enter":"fade-up","order":0}}),
    txt("mc-cite",560,312,624,74,
        "Coined by historian Johan Huizinga (1938); brought into game design by Salen &amp; Zimmerman (2004): &ldquo;To play a game means entering into a magic circle.&rdquo;",
        13.5,color=MUTED,lh=1.5,extra={"fx":{"enter":"fade-up","order":1}}),
    rect("mc-sep",560,400,624,1,BORDER,extra={"fx":{"enter":"fade","order":2}}),
    txt("mc-ink",560,418,300,18,"CROSSING IN",10,color=ACCENT2,weight=700,family=MONOF,
        extra={"letterSpacing":2,"fx":{"enter":"fade-up","order":2}}),
    txt("mc-inv",560,440,624,26,"A title screen. A coin toss. Dealing the cards.",15,color=TEXT,
        extra={"fx":{"enter":"fade-up","order":2}}),
    txt("mc-outk",560,478,300,18,"CROSSING OUT",10,color=ACCENT,weight=700,family=MONOF,
        extra={"letterSpacing":2,"fx":{"enter":"fade-up","order":3}}),
    txt("mc-outv",560,500,624,26,"Game over. The final whistle. Closing the box.",15,color=TEXT,
        extra={"fx":{"enter":"fade-up","order":3}}),

    # --- the boundary leaks
    rect("mc-porous",MX,558,1088,86,SURFACE,radius=14,stroke=BORDER,strokeWidth=1,
         extra={"fx":{"enter":"fade-up","order":4}}),
    rect("mc-porousbar",MX,558,4,86,ACCENT4,extra={"fx":{"enter":"fade-up","order":4}}),
    txt("mc-porousk",MX+30,576,1000,18,"THE CIRCLE IS POROUS",10.5,color=ACCENT4,weight=700,
        family=MONOF,extra={"letterSpacing":2,"fx":{"enter":"fade-up","order":4}}),
    txt("mc-porousb",MX+30,598,1026,44,
        "Money, friendships and reputation don't stay inside the circle &mdash; they leak both ways (Castronova). Real-money item trades and esports careers are the circle's edges wearing thin.",
        13.5,color=MUTED,lh=1.4,extra={"fx":{"enter":"fade-up","order":4}}),
] + footer(13)
slides.append(slide(13, els, "Read the Huizinga quote slowly — the magic circle is the reason a tackle that would be assault on the street is just 'good defense' on a football pitch. Point at the diagram: the boundary is DASHED and moving because it is maintained by agreement, not by physics; the grey dots outside keep orbiting whatever happens in the game. The porous-boundary point matters for THEIR games too: any leaderboard, chat, or in-app purchase is a hole they're choosing to put in their own circle."))

# ============================================================ 12. DESIGNING THE MAGIC CIRCLE
mc_considerations = [
    ("Mark the threshold clearly","A title screen, a countdown, a shuffle: players should always know when they've stepped in &mdash; and when they've stepped back out.",ACCENT),
    ("Keep the rules stable once inside","Changing constitutive rules mid-play without warning breaks the trust that makes the circle feel safe to fail in.",ACCENT2),
    ("Decide what leaks through, on purpose","Chat, monetization, leaderboards, real-money trades &mdash; each one you allow makes the circle more porous. Choose deliberately.",ACCENT3),
    ("Make failure safe inside the circle","Consequences that teach, not ones that follow players out the door &mdash; that's the whole point of a safe circle to lose in.",ACCENT),
    ("Design for every circle in the room","A spectator's circle isn't a player's circle. If your game will be watched &mdash; streamed, shoulder-surfed &mdash; design for that audience too.",ACCENT2),
]
els = [
    rect("bg12m",0,0,W,H,BG),
    kicker("k12m",MX,72,"Theory into practice", color=ACCENT),
    txt("t12m",MX,104,1100,70,"Designing the Magic Circle",50,weight=800,family=DISPLAY),
    txt("t12mb",MX,172,1050,30,"Five things worth deciding on purpose, before you build the rest.",18,color=MUTED),
]
xs3b = [96,470,844]
ys2b2 = [280,464]
for i,(name,desc,col) in enumerate(mc_considerations):
    x = xs3b[i%3]; y = ys2b2[i//3]
    fx = {"fx":{"enter":"fade-up","order":i}}
    els += [
        rect(f"mcc{i}",x,y,340,160,SURFACE,radius=12,stroke=BORDER,strokeWidth=1,extra=fx),
        rect(f"mcc{i}bar",x,y,4,160,col,radius=0,extra=fx),
        txt(f"mcc{i}t",x+26,y+22,290,56,name,17,weight=700,family=DISPLAY,lh=1.2,extra=fx),
        txt(f"mcc{i}d",x+26,y+80,290,78,desc,13,color=MUTED,lh=1.45,extra=fx),
    ]
els += footer(14)
slides.append(slide(14, els, "These are practical, arguable design decisions, not laws — ask students to pick one of their own favorite games and identify which of the five it handles well or poorly. The 'safe failure' point directly echoes the Safe Experimentation affordance from earlier; the 'spectator circle' point previews why esports/streaming design is its own discipline."))

# ============================================================ 13. RULES OF PLAY
rop_cols = [
    ("Constitutive","The mathematical skeleton underneath &mdash; how the system actually works.",
     "&ldquo;A bishop moves diagonally, any distance, until blocked.&rdquo;",ACCENT,ACCENT_SOFT),
    ("Operational","The instructions on the box &mdash; what a player actually reads before playing.",
     "&ldquo;White moves first. Touch a piece, you must move it if legal.&rdquo;",ACCENT2,ACCENT2_SOFT),
    ("Implicit","The unwritten social contract around the table &mdash; never on the box, always in force.",
     "&ldquo;Don't distract your opponent mid-think. Shake hands after.&rdquo;",ACCENT3,ACCENT3_SOFT),
]
els = [
    rect("bg13m",0,0,W,H,BG),
    kicker("k13m",MX,72,"‘Rules’ hides three different things", color=ACCENT2),
    txt("t13m",MX,104,1100,64,"Rules of Play",50,weight=800,family=DISPLAY),
    txt("t13mb",MX,172,1050,30,"Same running example throughout &mdash; chess &mdash; so you can see all three side by side.",17,color=MUTED),
]
xs3c = [96,470,844]
for i,(name,desc,example,col,soft) in enumerate(rop_cols):
    x = xs3c[i]
    fx = {"fx":{"enter":"fade-up","order":i}}
    els += [
        rect(f"rop{i}",x,222,340,320,soft,radius=16,stroke=col,strokeWidth=1.5,extra=fx),
        txt(f"rop{i}k",x+28,250,284,26,name.upper(),14,color=col,weight=700,family=MONOF,extra={"letterSpacing":1.5,**fx}),
        txt(f"rop{i}d",x+28,286,284,110,desc,15.5,color=TEXT,lh=1.5,extra=fx),
        rect(f"rop{i}div",x+28,404,284,1,"rgba(255,255,255,0.2)",extra=fx),
        txt(f"rop{i}ek",x+28,420,284,20,"EXAMPLE",11,color=col,weight=700,family=MONOF,extra={"letterSpacing":1.5,**fx}),
        txt(f"rop{i}ex",x+28,444,284,90,example,14,color=MUTED,lh=1.5,extra=fx),
    ]
els += [
    txt("t13mnote",MX,566,1088,40,
        "Most 'rule arguments' in playtesting are actually implicit-rule arguments &mdash; no one wrote them down, so no one agrees they exist.",
        14.5,color=FAINT,lh=1.4),
] + footer(15)
slides.append(slide(15, els, "Constitutive rules are what you'll actually code this semester. Operational rules are your tutorial/UI text. Implicit rules are the ones that blow up playtests — 'I didn't know you weren't supposed to camp the spawn' is an implicit-rule failure, and it's on the designer to either enforce it or accept it."))

# ============================================================ 14. FINITE GAMES, INFINITE GAMES
els = [
    rect("bg14m",0,0,W,H,BG),
    kicker("k14m",MX,72,"A different way to ask ‘when does it end?’", color=ACCENT),
    txt("t14m",MX,104,1100,64,"Finite Games, Infinite Games",44,weight=800,family=DISPLAY),
    txt("t14mb",MX,168,1080,30,"James Carse's 1986 framework &mdash; not game theory's 'finite games,' a philosophical one.",16,color=MUTED),
    rect("fg-card",96,214,528,280,ACCENT_SOFT,radius=16,stroke=ACCENT,strokeWidth=1.5,extra={"fx":{"enter":"fade-up","order":0}}),
    txt("fg-t",96+28,238,472,36,"Finite Games",23,weight=800,family=DISPLAY,color=TEXT,extra={"fx":{"enter":"fade-up","order":0}}),
    txt("fg-d",96+28,278,472,54,"Played to <b>WIN</b>. Fixed players, fixed rules, a real endpoint.",15,color=TEXT,lh=1.4,extra={"fx":{"enter":"fade-up","order":0}}),
]
fg_ex = ["A chess match","A Fortnite round","A story-mode campaign"]
for j,ex in enumerate(fg_ex):
    els += chip(f"fg-c{j}",96+28,346+j*46,472,36,ex,ACCENT)
    els[-1]["fx"]=els[-2]["fx"]={"enter":"fade-up","order":0}
els += [
    rect("ig-card",656,214,528,280,ACCENT3_SOFT,radius=16,stroke=ACCENT3,strokeWidth=1.5,extra={"fx":{"enter":"fade-up","order":1}}),
    txt("ig-t",656+28,238,472,36,"Infinite Games",23,weight=800,family=DISPLAY,color=TEXT,extra={"fx":{"enter":"fade-up","order":1}}),
    txt("ig-d",656+28,278,472,54,"Played to <b>KEEP PLAYING</b>. Rules evolve, boundaries shift, no defined ending.",15,color=TEXT,lh=1.4,extra={"fx":{"enter":"fade-up","order":1}}),
]
ig_ex = ["World of Warcraft (2004&ndash;)","Minecraft","The esports scene itself"]
for j,ex in enumerate(ig_ex):
    els += chip(f"ig-c{j}",656+28,346+j*46,472,36,ex,ACCENT3)
    els[-1]["fx"]=els[-2]["fx"]={"enter":"fade-up","order":1}
els += [
    rect("fi-note",96,512,1088,122,SURFACE2,radius=14,stroke=BORDER2,strokeWidth=1,extra={"fx":{"enter":"fade-up","order":2}}),
    txt("fi-notek",96+32,530,700,22,"FOR YOUR FINAL PROJECT",12.5,color=ACCENT,weight=700,family=MONOF,extra={"letterSpacing":1.5,"fx":{"enter":"fade-up","order":2}}),
    txt("fi-noteb",96+32,554,1024,72,
        "Most successful live games are infinite games built from finite games nested inside them &mdash; every WoW raid ends; the game itself hasn't (yet). You have 15 weeks and a due date: aim for a great <b>finite</b> game, a complete loop with a real ending, not an ambitious infinite one you won't finish.",
        14.5,color=MUTED,lh=1.45,extra={"fx":{"enter":"fade-up","order":2}}),
] + footer(16)
slides.append(slide(16, els, "Carse's book is philosophy, not game design, but the vocabulary maps cleanly onto live-service games. The nested insight is the one worth lingering on: a single raid, match, or quest is finite even inside a game (or a genre-scene) that's designed to never really end. Land hard on the final-project framing — scope discipline is the #1 way past projects have failed."))

# ============================================================ 10. SOCIETAL AFFORDANCES
aff = [
    ("Challenge &amp; Mastery","Clear goals, feedback, and a skill curve worth climbing.",ACCENT),
    ("Social Connection","Co-op, competition, or just something to talk about together.",ACCENT2),
    ("Story &amp; Fantasy","A safe space to be someone, somewhere, else for a while.",ACCENT3),
    ("Safe Experimentation","Consequences that teach without the real-world cost of failing.",ACCENT),
    ("Education &amp; Training","Simulation as rehearsal &mdash; flight decks, surgery, classrooms.",ACCENT2),
    ("Culture &amp; Economy","A multi-billion dollar industry, and a modern art form.",ACCENT3),
]
els = [
    rect("bg10",0,0,W,H,BG),
    kicker("k10",MX,72,"Before we open Unity", color=ACCENT2),
    txt("t10",MX,104,1100,70,"What Games Give Us",56,weight=800,family=DISPLAY),
    txt("t10b",MX,176,1050,32,"Games are systems people choose to spend their time inside. That's not trivial &mdash; it's an affordance.",18,color=MUTED),
]
xs = [96,470,844]
ys = [280,464]
for i,(name,desc,col) in enumerate(aff):
    x = xs[i%3]; y = ys[i//3]
    fx = {"fx":{"enter":"fade-up","order":i}}
    els += [
        rect(f"af{i}",x,y,340,160,SURFACE,radius=12,stroke=BORDER,strokeWidth=1,extra=fx),
        rect(f"af{i}bar",x,y,4,160,col,radius=0,extra=fx),
        txt(f"af{i}t",x+26,y+22,290,52,name,18.5,weight=700,family=DISPLAY,lh=1.2,extra=fx),
        txt(f"af{i}d",x+26,y+78,290,72,desc,14,color=MUTED,lh=1.5,extra=fx),
    ]
els += footer(17)
slides.append(slide(17, els, "Quick round-robin using student examples from the section-break question. The point: games aren't 'just' entertainment — CLO-1 wants you to be able to name WHY a game works on someone, not just THAT it does. This is the 'why' layer; MDA next gives us the 'how'."))

# ============================================================ 11. MDA OVERVIEW
def mda_box(id_prefix, x, y, w, h, title, sub, color, softcolor, big_title_size=24, order=0):
    return [
        rect(f"box-{id_prefix}",x,y,w,h,softcolor,radius=14,stroke=color,strokeWidth=1.5,
             extra={"fx":{"enter":"fade-up","order":order}}),
    ]
els = [
    rect("bg11",0,0,W,H,BG),
    kicker("k11",MX,72,"A shared vocabulary", color=ACCENT2),
    txt("t11",MX,104,1100,70,"The MDA Framework",56,weight=800,family=DISPLAY),
]
els += mda_box("mech",96,280,340,260,"Mechanics","",ACCENT,ACCENT_SOFT,order=0)
els += mda_box("dyn",470,280,340,260,"Dynamics","",ACCENT2,ACCENT2_SOFT,order=1)
els += mda_box("aes",844,280,340,260,"Aesthetics","",ACCENT3,ACCENT3_SOFT,order=2)
els += [
    txt("mech-lbl",96+28,306,284,40,"MECHANICS",15,color=ACCENT,weight=700,family=MONOF,extra={"letterSpacing":2}),
    txt("mech-d",96+28,346,284,170,"The rules, systems, and data.<br>What <b>you</b>, the designer, actually build.",17,color=TEXT,lh=1.55),
    txt("dyn-lbl",470+28,306,284,40,"DYNAMICS",15,color=ACCENT2,weight=700,family=MONOF,extra={"letterSpacing":2}),
    txt("dyn-d",470+28,346,284,170,"The run-time behavior that emerges when rules meet a real player.",17,color=TEXT,lh=1.55),
    txt("aes-lbl",844+28,306,284,40,"AESTHETICS",15,color=ACCENT3,weight=700,family=MONOF,extra={"letterSpacing":2}),
    txt("aes-d",844+28,346,284,170,"The emotional response. What the <b>player</b> actually feels.",17,color=TEXT,lh=1.55),
    line("arr1",436,409,34,1,MUTED,strokeWidth=3,lineEnd="arrow"),
    line("arr2",810,409,34,1,MUTED,strokeWidth=3,lineEnd="arrow"),
    txt("dview",96,232,1088,30,"DESIGNER'S VIEW &nbsp;&rarr;&nbsp; you build left-to-right",13,color=FAINT,family=MONOF,extra={"letterSpacing":1}),
    {**line("pview-arrow",240,567,800,1,ACCENT3,strokeWidth=2,dashed=True,lineStart="arrow"),
     "fx":{"loop":{"type":"dash-march","distance":18,"duration":1.4}}},
    txt("pview",96,592,1088,30,"&larr;&nbsp; PLAYER'S VIEW &mdash; they experience it in reverse: feeling first, rules never seen",13,color=FAINT,family=MONOF,extra={"letterSpacing":1}),
] + footer(18)
slides.append(slide(18, els, "The core insight of MDA (Hunicke, LeBlanc & Zubek, 2004): designers work left-to-right — mechanics first — but players experience it right-to-left, feeling the aesthetics without ever seeing the rules that produced them. Next three slides zoom into each piece."))

# ============================================================ 12-14. MDA DEEP-DIVES
# One box that changes colour, and a chain on the right whose highlight walks down
# it — so the three slides read as one idea in three positions, not three slides.
MDA_STEPS = [
    ("01", "Mechanics",  "what you build",  ACCENT,  ACCENT_SOFT,  ACCENT_GLOW),
    ("02", "Dynamics",   "what emerges",    ACCENT2, ACCENT2_SOFT, ACCENT2_GLOW),
    ("03", "Aesthetics", "what they feel",  ACCENT3, ACCENT3_SOFT, ACCENT3_GLOW),
]
MDA_X, MDA_W, MDA_ROW_H = 808, 376, 108
MDA_ROW_Y = [208, 338, 468]

def mda_chain(active):
    els = []
    for i, (num, name, role, col, soft, gl) in enumerate(MDA_STEPS):
        y = MDA_ROW_Y[i]
        on = (i == active)
        done = (i < active)
        els.append(rect(f"mdastep{i}", MDA_X, y, MDA_W, MDA_ROW_H,
                        soft if on else "rgba(255,255,255,0.02)", radius=14,
                        stroke=col if on else BORDER, strokeWidth=1.5 if on else 1,
                        shadow=glow(gl, 30) if on else None))
        els.append(ellipse(f"mdadot{i}", MDA_X+28, y+30, 10, 10,
                           col if on else ("rgba(154,162,177,0.5)" if done else "rgba(92,100,114,0.5)"),
                           shadow=glow(gl, 14) if on else None))
        els.append(txt(f"mdanum{i}", MDA_X+50, y+26, 60, 18, num, 11,
                       color=col if on else FAINT, weight=700, family=MONOF,
                       extra={"letterSpacing":2}))
        els.append(txt(f"mdaname{i}", MDA_X+28, y+50, MDA_W-56, 30, name, 21,
                       color=TEXT if on else ("rgba(154,162,177,0.65)" if done else "rgba(154,162,177,0.4)"),
                       weight=800, family=DISPLAY))
        els.append(txt(f"mdarole{i}", MDA_X+28, y+80, MDA_W-56, 20, role, 12,
                       color=col if on else FAINT, family=MONOF, extra={"letterSpacing":1}))
        if i < 2:
            els.append(rect(f"mdalink{i}", MDA_X+32, y+MDA_ROW_H, 2, 22, BORDER2))
    els.append(txt("mdachainnote", MDA_X, 598, MDA_W, 40,
                   "You build downwards. Players read it bottom-up &mdash; feeling first.",
                   12.5, color=FAINT, lh=1.5))
    return els

def mda_slide(n, part, title, col, soft, gl, defn, exk, exbody, notes, bgid):
    return [
        rect(bgid,0,0,W,H,BG),
        kicker(f"kmda{n}",MX,72,f"MDA, part {part} of 3", color=col),
        txt(f"tmda{n}",MX,104,660,70,title,56,weight=800,family=DISPLAY,role="title"),
        rect("mdabox",96,208,680,370,soft,radius=16,stroke=col,strokeWidth=1.5,
             shadow=glow(gl,34)),
        txt(f"mdadef{n}",96+40,244,600,100,defn,19,color=TEXT,lh=1.5),
        rect(f"mdadiv{n}",96+40,356,600,1,col,opacity=0.3),
        txt(f"mdaexk{n}",96+40,378,600,22,exk,12,color=col,weight=700,family=MONOF,
            extra={"letterSpacing":2}),
        txt(f"mdaex{n}",96+40,406,600,206,exbody,17.5,color=MUTED,lh=1.75),
    ]

els = mda_slide(19,1,"Mechanics",ACCENT,ACCENT_SOFT,ACCENT_GLOW,
    "The rules, systems, data and algorithms &mdash; the actual code and content you write.",
    "IN UNITY, THIS LOOKS LIKE",
    "&#9679;&nbsp; A jump has a height, a gravity scale, a cooldown<br>"
    "&#9679;&nbsp; Input mappings &mdash; what a button <i>does</i><br>"
    "&#9679;&nbsp; A ScriptableObject holding an enemy's stats<br>"
    "&#9679;&nbsp; Collision layers &amp; physics material values",
    None,"bg12") + mda_chain(0) + footer(19)
slides.append(slide(19, els, "Mechanics are the only layer you directly control as a developer — everything else emerges from these. This is where most of your lab time and C# scripting this semester will live (CLO-3). Point at the chain on the right: we are at the top of it.", transition="morph"))

els = mda_slide(20,2,"Dynamics",ACCENT2,ACCENT2_SOFT,ACCENT2_GLOW,
    "The run-time behaviour that emerges when a player's choices collide with your mechanics. You can't script this directly &mdash; it emerges.",
    "EXAMPLE",
    "Mechanic: <i>jump height + obstacle spawn timer</i><br><br>"
    "Dynamic: a rising rhythm of split-second timing decisions as speed increases &mdash; nobody coded 'tension', it just happens.",
    None,"bg13") + mda_chain(1) + footer(20)
slides.append(slide(20, els, "Dynamics is the layer that separates good designers from good coders — you can't code a dynamic directly, you have to shape mechanics until the emergent behaviour feels right. This is why playtesting exists.", transition="morph"))

els = mda_slide(21,3,"Aesthetics",ACCENT3,ACCENT3_SOFT,ACCENT3_GLOW,
    "The emotional response your dynamics produce. This is the layer players actually talk about &mdash; and the one you design backwards from.",
    "NEXT SLIDE",
    "Hunicke, LeBlanc &amp; Zubek name eight distinct kinds of fun &mdash; &ldquo;fun&rdquo; on its own is too vague to design for.",
    None,"bg14") + mda_chain(2) + footer(21)
slides.append(slide(21, els, "Aesthetics is what the player would actually say if you asked 'why do you like this game?' — never 'because the gravity scale is 9.8', always a feeling. Next slide breaks 'fun' into eight specific, nameable kinds.", transition="morph"))

# ============================================================ 15. THE 8 KINDS OF FUN
kof = [
    ("Sensation","Game as sense-pleasure","Pure sensory payoff &mdash; the crunch of a headshot, the pop of a combo.","1"),
    ("Fantasy","Game as make-believe","Being a wizard, a bounty hunter, a mayor &mdash; someone you are not.","2"),
    ("Narrative","Game as unfolding story","A story that reveals itself through play, not just cutscenes between it.","3"),
    ("Challenge","Game as obstacle course","A fair chance of failure &mdash; the whole reason \"one more try\" exists.","4"),
    ("Fellowship","Game as social framework","Teams, guilds, co-op &mdash; showing up together, not just alongside.","5"),
    ("Discovery","Game as uncharted territory","Secrets and systems &mdash; the small dopamine hit of figuring it out.","6"),
    ("Expression","Game as self-discovery","Building, customizing, leaving a mark in the world that's yours.","7"),
    ("Submission","Game as pastime","Low-stakes and meditative &mdash; something to do because doing is enough.","8"),
]
els = [
    rect("bg15",0,0,W,H,BG),
    kicker("k15",MX,72,"Aesthetics, named", color=ACCENT3),
    txt("t15",MX,104,1100,70,"The 8 Kinds of Fun",56,weight=800,family=DISPLAY),
    txt("t15b",MX,176,1050,30,"Hunicke, LeBlanc &amp; Zubek's answer to \"but what does 'fun' even mean?\"",18,color=MUTED),
]
xs4 = [96,374,652,930]
ys2 = [232,410]
for i,(name,desc,long_desc,num) in enumerate(kof):
    x = xs4[i%4]; y = ys2[i//4]
    fx = {"fx":{"enter":"fade-up","order":i}}
    els += [
        rect(f"kf{i}",x,y,254,164,SURFACE,radius=12,stroke=BORDER,strokeWidth=1,extra=fx),
        txt(f"kf{i}n",x+20,y+16,80,30,num,15,color=FAINT,weight=700,family=MONOF,extra=fx),
        txt(f"kf{i}t",x+20,y+52,214,44,name,19,weight=700,family=DISPLAY,color=ACCENT3,extra=fx),
        txt(f"kf{i}d",x+20,y+96,214,56,long_desc,12.5,color=MUTED,lh=1.35,extra=fx),
    ]
els += footer(22)
slides.append(slide(22, els, "You don't need all eight in one game — most good games lean on two or three. Ask students which 2-3 they think their favorite game leans on; use it to preview that their final project pitch should be able to name its own target aesthetics. Next slide pairs each with a real, recognizable game."))

# ============================================================ 16. FUN, NAMED IN GAMES (morph from 15)
fun_games = [
    ("Beat Saber","Every slash is feedback you feel in your hands."),
    ("Skyrim","Be a dragonborn, a thief, a bard &mdash; your call."),
    ("Life is Strange","Choices ripple forward through the story."),
    ("Celeste","Brutal, fair, and built entirely around retrying."),
    ("Among Us","The game is basically an excuse to talk."),
    ("Outer Wilds","No quest log &mdash; just curiosity and a save file."),
    ("Animal Crossing","A house, an island, entirely arranged by you."),
    ("Stardew Valley","Water the crops. Feed the chickens. Repeat."),
]
els = [
    rect("bg16",0,0,W,H,BG),
    kicker("k16a",MX,72,"Aesthetics, in the wild", color=ACCENT3),
    txt("t16a",MX,104,1100,70,"Fun, Named in Games",56,weight=800,family=DISPLAY),
    txt("t16ab",MX,176,1050,30,"Same eight kinds &mdash; now attached to a game you (probably) know.",18,color=MUTED),
]
ys2b = [212,420]
for i,((name,desc,long_desc,num),(game,why)) in enumerate(zip(kof,fun_games)):
    x = xs4[i%4]; y = ys2b[i//4]
    els += [
        rect(f"kf{i}",x,y,254,190,SURFACE,radius=12,stroke=BORDER,strokeWidth=1),
        txt(f"kf{i}n",x+20,y+14,80,20,num,13,color=FAINT,weight=700,family=MONOF),
        txt(f"kf{i}t",x+20,y+36,214,28,name,18,weight=700,family=DISPLAY,color=ACCENT3),
        rect(f"kf{i}div",x+20,y+70,214,1,BORDER2),
        txt(f"kf{i}g",x+20,y+80,214,22,f"e.g. <b>{game}</b>",13.5,color=ACCENT,weight=600,
            extra={"fx":{"enter":"fade-up","order":i}}),
        txt(f"kf{i}w",x+20,y+106,214,76,why,12,color=MUTED,lh=1.35,
            extra={"fx":{"enter":"fade-up","order":i}}),
    ]
els += footer(23)
slides.append(slide(23, els, "Go around the room fast — for each card, ask if anyone disagrees with the pairing (there's no single right answer; Celeste also has real Sensation, Stardew also has real Fellowship). The point is the vocabulary, not a perfect taxonomy. Next slide shows how two very different games have almost opposite aesthetic profiles.", transition="morph"))

# ============================================================ 17. FUN, COMPARED (bars that grow up into place)
fun_labels = ["Sensation","Fantasy","Narrative","Challenge","Fellowship","Discovery","Expression","Submission"]
stardew_vals = [2,3,3,1,4,4,5,5]
darksouls_vals = [4,4,3,5,2,5,2,1]
fc_bottom, fc_unit = 560, 60  # y of value-0; px per rating point (1-5)
fc_slot_w = 1088 / 8
els = [
    rect("bg17a",0,0,W,H,BG),
    kicker("k17a",MX,72,"Same framework, opposite games", color=ACCENT3),
    txt("t17a",MX,104,1100,64,"Fun, Compared",50,weight=800,family=DISPLAY),
    txt("t17ab",MX,170,1080,30,"Rating two games 1&ndash;5 across all eight aesthetics makes their design intent visible.",17,color=MUTED),
    # legend
    rect("fclswQ",96,222,14,14,QUIZ,radius=3,extra={"fx":{"enter":"fade-up","order":0}}),
    txt("fclslQ",118,220,320,20,"Stardew Valley &middot; cozy sim",13,color=MUTED,extra={"fx":{"enter":"fade-up","order":0}}),
    rect("fclswD",520,222,14,14,LABS,radius=3,extra={"fx":{"enter":"fade-up","order":0}}),
    txt("fclslD",542,220,320,20,"Dark Souls &middot; hardcore action",13,color=MUTED,extra={"fx":{"enter":"fade-up","order":0}}),
    # baseline + gridlines
    rect("fcbase",96,fc_bottom,1088,2,BORDER2),
]
for v in [1,2,3,4,5]:
    gy = fc_bottom - v*fc_unit
    els += [
        rect(f"fcgrid{v}",96,gy,1088,1,BORDER,opacity=0.6),
        txt(f"fcgridl{v}",56,gy-8,30,16,str(v),11,color=MUTED,align="right"),
    ]
els.append(txt("fcgridl0",56,fc_bottom-8,30,16,"0",11,color=MUTED,align="right"))
for i,label in enumerate(fun_labels):
    slot_x = 96 + i*fc_slot_w
    bar_w = 42
    x1 = slot_x + (fc_slot_w - (bar_w*2+10))/2
    x2 = x1 + bar_w + 10
    v1, v2 = stardew_vals[i], darksouls_vals[i]
    h1, h2 = v1*fc_unit, v2*fc_unit
    order = i
    els += [
        rect(f"fcb1_{i}",x1,fc_bottom-h1,bar_w,h1,QUIZ,radius=3,extra={"fx":{"enter":"fade-up","order":order}}),
        txt(f"fcv1_{i}",x1-10,fc_bottom-h1-22,bar_w+20,18,str(v1),12,color=QUIZ,weight=700,family=MONOF,align="center",extra={"fx":{"enter":"fade-up","order":order}}),
        rect(f"fcb2_{i}",x2,fc_bottom-h2,bar_w,h2,LABS,radius=3,extra={"fx":{"enter":"fade-up","order":order}}),
        txt(f"fcv2_{i}",x2-10,fc_bottom-h2-22,bar_w+20,18,str(v2),12,color=LABS,weight=700,family=MONOF,align="center",extra={"fx":{"enter":"fade-up","order":order}}),
        txt(f"fccat{i}",slot_x,fc_bottom+12,fc_slot_w,20,label,12,color=MUTED,align="center",extra={"fx":{"enter":"fade-up","order":order}}),
    ]
els += [
    txt("t17note",96,616,1088,40,
        "Illustrative ratings for class discussion, not a validated instrument &mdash; rate your own final project's profile the same way.",
        13.5, color=FAINT, lh=1.5),
] + footer(24)
slides.append(slide(24, els, "Stardew Valley leans hard into Submission, Expression, and Fellowship — low stakes, make it your own, do it together. Dark Souls leans hard into Challenge and Sensation — punishing, visceral, deliberately unfair-feeling until you master it. Neither is 'more fun' — they're just aiming at different aesthetics on purpose. Watch the bars rise category by category. Ask: which 2-3 bars should YOUR final project be tall on?"))

# ============================================================ 18. MDA IN PRACTICE
els = [
    rect("bg16",0,0,W,H,BG),
    kicker("k16",MX,72,"Putting it together", color=ACCENT),
    txt("t16",MX,104,1100,70,"MDA in Practice",56,weight=800,family=DISPLAY),
    txt("t16b",MX,176,1050,30,"A tiny endless-runner &mdash; not far from your own final project scope.",18,color=MUTED),
    # 3 stacked rows M -> D -> A
    rect("pr1",96,236,1088,104,ACCENT_SOFT,radius=12,stroke=ACCENT,strokeWidth=1,extra={"fx":{"enter":"fade-up","order":0}}),
    txt("pr1k",96+32,256,180,24,"MECHANIC",13,color=ACCENT,weight=700,family=MONOF,extra={"letterSpacing":1.5,"fx":{"enter":"fade-up","order":0}}),
    txt("pr1b",96+32,282,1000,50,"Tap to jump &middot; fixed gravity &middot; obstacle spawn timer that shortens over time",18,color=TEXT,lh=1.4,extra={"fx":{"enter":"fade-up","order":0}}),
    rect("pr2",96,368,1088,104,ACCENT2_SOFT,radius=12,stroke=ACCENT2,strokeWidth=1,extra={"fx":{"enter":"fade-up","order":1}}),
    txt("pr2k",96+32,388,180,24,"DYNAMIC",13,color=ACCENT2,weight=700,family=MONOF,extra={"letterSpacing":1.5,"fx":{"enter":"fade-up","order":1}}),
    txt("pr2b",96+32,414,1000,50,"A rising rhythm of tighter, riskier timing decisions as the spawn rate climbs",18,color=TEXT,lh=1.4,extra={"fx":{"enter":"fade-up","order":1}}),
    rect("pr3",96,500,1088,104,ACCENT3_SOFT,radius=12,stroke=ACCENT3,strokeWidth=1,extra={"fx":{"enter":"fade-up","order":2}}),
    txt("pr3k",96+32,520,180,24,"AESTHETIC",13,color=ACCENT3,weight=700,family=MONOF,extra={"letterSpacing":1.5,"fx":{"enter":"fade-up","order":2}}),
    txt("pr3b",96+32,546,1000,50,"Challenge + Sensation &mdash; the \"one more try\" feeling &mdash; from three numbers you tuned",18,color=TEXT,lh=1.4,extra={"fx":{"enter":"fade-up","order":2}}),
    txt("prar1",128,340,40,28,"&#8595;",16,color="rgba(85,214,194,0.7)",align="center",
        extra={"fx":{"enter":"fade","order":1}}),
    txt("prar2",128,472,40,28,"&#8595;",16,color="rgba(108,140,255,0.7)",align="center",
        extra={"fx":{"enter":"fade","order":2}}),
] + footer(25)
slides.append(slide(25, els, "Walk the arrow top to bottom slowly — this is the whole point of the framework in one example. Three tunable numbers (gravity, jump force, spawn timer) is ALL it takes to produce 'the one more try feeling.' This is exactly the kind of small, complete game the final project asks for."))

# ============================================================ 17. SECTION BREAK — WHO PLAYS?
els = [
    rect("bg17",0,0,W,H,BG),
    rect("sb17line",MX,300,120,4,ACCENT2,shadow=glow(ACCENT2_GLOW,18),
         extra={"fx":{"enter":"fade-up","order":0,"ambient":"kenburns","ken":{"dir":"drift","scale":1.0,"duration":18}}}),
    txt("sb17k",MX,326,700,28,"PART 2, CONTINUED",15,color=ACCENT2,weight=700,family=MONOF,extra={"letterSpacing":3,"fx":{"enter":"fade-up","order":0}}),
    txt("sb17t",MX,362,1120,140,"Who Plays?",84,weight=800,family=DISPLAY,extra={"letterSpacing":-1,"fx":{"enter":"fade-up","order":1}}),
    txt("sb17s",MX,486,1000,40,"MDA tells you how a game works. Now: who is it working on?",20,color=MUTED,
        extra={"fx":{"enter":"fade-up","order":2}}),
] + orbit_motif("sb17o", 986, 344, 316, core=96, c1=ACCENT3, c2=ACCENT4,
                g1=ACCENT3_GLOW, ring_col="rgba(108,140,255,0.30)") + footer(26)
slides.append(slide(26, els, "Second breather slide. Transition line: 'MDA assumed one player having one experience — but not everyone plays for the same reason. That's where Richard Bartle comes in.'", transition="fade"))


# ============================================================ 25. WHO IS RICHARD BARTLE?
els = [
    rect("bg25b",0,0,W,H,BG),
    kicker("k25b",MX,72,"The researcher behind the taxonomy", color=ACCENT2),
    txt("t25b",MX,104,1100,64,"Who Is Richard Bartle?",50,weight=800,family=DISPLAY),
    ring("rbphring",226,344,260,"rgba(85,214,194,0.40)",strokeWidth=1.5,march=(28,10)),
    {"id":"rbph","type":"image","x":226-114,"y":344-114,"w":228,"h":228,"rotation":0,"opacity":1,
     "src":"asset:photo-bartle","fit":"cover","radius":114,
     "shadow":glow(ACCENT2_GLOW,40)},
    ring("rbphborder",226,344,228,"rgba(85,214,194,0.35)",strokeWidth=1.5,dashed=False),
    txt("rbname",396,222,700,44,"Richard A. Bartle",32,weight=800,family=DISPLAY),
    txt("rbrole",396,270,700,28,"Emeritus Professor &middot; University of Essex",17,color=ACCENT2,weight=600),
    rect("rbdiv",396,308,700,1,BORDER),
    txt("rbtl",396,330,720,230,
        "<b>1978</b> &mdash; co-creates MUD1 with Roy Trubshaw at Essex, the first Multi-User Dungeon &mdash; ancestor of every MMORPG.<br>"
        "<b>1988</b> &mdash; PhD in Artificial Intelligence, University of Essex.<br>"
        "<b>1996</b> &mdash; publishes &ldquo;Hearts, Clubs, Diamonds, Spades&rdquo; &mdash; the four-player-type taxonomy we cover next.<br>"
        "<b>2003</b> &mdash; <i>Designing Virtual Worlds</i>, a foundational text on MMORPG design.<br>"
        "<b>2025</b> &mdash; retires as Emeritus Professor; RSA Fellow; IGDA Online Game Legend (2010).",
        15.5,color=MUTED,lh=1.65),
    txt("rbnote",MX,576,1088,30,"<i>The &ldquo;Bartle Test&rdquo; quiz that guesses your player type? Same person, same 1996 paper.</i>",14,color=FAINT),
] + footer(27)
slides.append(slide(27, els, "Two minutes, tops — the point is that the taxonomy about to appear isn't a random internet quiz, it's grounded in one researcher's decades of actual MUD/MMO data going back to 1978, the same year the genre itself was born. MUD1's ancestry line runs directly to every MMORPG mentioned so far in this course."))

# ============================================================ 18b. BARTLE'S TAXONOMY (animated matrix + expanding quadrants)
# The real Bartle diagram: two axes, four quadrants. Each quadrant is clickable and
# morphs open into a full brief; the other three shrink into a locator so you never
# lose your place. Arrow keys skip the expansions, so the linear lecture stays clean.
MAT_X, MAT_Y = 620, 180
CELL_W, CELL_H = 220, 210
MAT_CX, MAT_CY = MAT_X + CELL_W, MAT_Y + CELL_H
LOC_X, LOC_Y, LOC_CW, LOC_CH = 1012, 92, 78, 74

BARTLE = [
    dict(key="soc", col=0, row=0, name="Socializers", axis="INTERACTING &middot; PLAYERS",
         blurb="The game is somewhere to be with other people.", share="~80%",
         col_main=ACCENT2, soft=ACCENT2_SOFT, gl=ACCENT2_GLOW, gr=grad(35,"#55D6C2","#3FB4E8"),
         motive="&ldquo;Who else is here, and what are we doing together?&rdquo;",
         does=["Talk, joke, and hang around in shared spaces",
               "Join guilds, help newcomers, organise events",
               "Trade, gift, and build a reputation",
               "Treat mechanics as an excuse to be social"],
         design="Give them each other: chat and emotes that carry tone, co-op that genuinely needs two, "
                "a persistent place to gather, and something worth giving away.",
         games="Animal Crossing<br>Final Fantasy XIV<br>Among Us &middot; any MMO guild chat"),
    dict(key="exp", col=1, row=0, name="Explorers", axis="INTERACTING &middot; WORLD",
         blurb="The joy is in finding out how the thing works.", share="~10%",
         col_main=ACCENT3, soft=ACCENT3_SOFT, gl=ACCENT3_GLOW, gr=grad(35,"#6C8CFF","#A579FF"),
         motive="&ldquo;What happens if I go over there and try this?&rdquo;",
         does=["Walk the edges of the map looking for seams",
               "Poke at systems to find the rules underneath",
               "Read every note, log and item description",
               "Share discoveries more happily than victories"],
         design="Reward curiosity, not completion: optional rooms with no marker, systems deep enough to "
                "surprise you, and lore that is found rather than handed over.",
         games="Outer Wilds<br>Breath of the Wild<br>Subnautica &middot; Tunic"),
    dict(key="kil", col=0, row=1, name="Killers", axis="ACTING &middot; PLAYERS",
         blurb="The point is to have an effect on other people.", share="~1%",
         col_main=ACCENT4, soft=ACCENT4_SOFT, gl=ACCENT4_GLOW, gr=grad(35,"#FF4FA3","#FF8A6B"),
         motive="&ldquo;I want my play to be something that happened <i>to</i> you.&rdquo;",
         does=["Seek out other players rather than content",
               "Compete for rank, and want the rank seen",
               "Test where the rules can be pushed",
               "Measure a session by who they beat"],
         design="Give them stakes and an audience: real PvP, visible rankings, and &mdash; critically &mdash; "
                "counterplay, so the target has an answer and the loss stays fair.",
         games="Ranked Fortnite<br>Counter-Strike<br>EVE Online &middot; fighting games"),
    dict(key="ach", col=1, row=1, name="Achievers", axis="ACTING &middot; WORLD",
         blurb="The point is to beat the game on its own terms.", share="~10%",
         col_main=ACCENT, soft=ACCENT_SOFT, gl=ACCENT_GLOW, gr=grad(35,"#FF8A3D","#FFC178"),
         motive="&ldquo;What is the target, and how far off it am I?&rdquo;",
         does=["Chase completion, collections and 100%",
               "Optimise routes, builds and numbers",
               "Climb whatever ladder the game provides",
               "Treat the world as a set of problems to solve"],
         design="Make progress legible: goals that state themselves, a bar that visibly moves, and a "
                "difficulty curve that keeps paying out mastery instead of flattening.",
         games="Destiny 2<br>Hades<br>Stardew Valley completion runs"),
]

def cell_xy(col, row, inset=5):
    return MAT_X + col*CELL_W + inset, MAT_Y + row*CELL_H + inset, CELL_W - inset*2, CELL_H - inset*2

def loc_xy(col, row, inset=3):
    return LOC_X + col*LOC_CW + inset, LOC_Y + row*LOC_CH + inset, LOC_CW - inset*2, LOC_CH - inset*2

def bartle_left_column():
    return [
        kicker("k18",MX,64,"A player is not a player", color=ACCENT2),
        txt("t18",MX,92,460,120,"Bartle's<br>Taxonomy",46,weight=800,family=DISPLAY,lh=1.05,role="title"),
        txt("t18b",MX,216,440,72,
            "Four types, from two questions: what do you <b>do</b>, and what do you do it <b>to</b>?",
            16,color=MUTED,lh=1.5,role="subtitle"),
        rect("t18div",MX,308,300,1,BORDER),
        txt("ax1k",MX,326,440,18,"VERTICAL &mdash; WHAT YOU DO",10.5,color=FAINT,weight=700,
            family=MONOF,extra={"letterSpacing":2}),
        txt("ax1b",MX,348,470,44,
            "<b>Acting</b> means you impose on it. <b>Interacting</b> means you engage with it.",
            14,color=MUTED,lh=1.5),
        txt("ax2k",MX,410,440,18,"HORIZONTAL &mdash; WHAT YOU DO IT TO",10.5,color=FAINT,weight=700,
            family=MONOF,extra={"letterSpacing":2}),
        txt("ax2b",MX,432,470,44,
            "<b>Players</b> means other people. <b>World</b> means the game system itself.",
            14,color=MUTED,lh=1.5),
        txt("bhint",MX,520,440,20,"CLICK A QUADRANT TO OPEN IT",10.5,color=ACCENT2,weight=700,
            family=MONOF,extra={"letterSpacing":2,"fx":{"enter":"fade","order":5}}),
    ]

def bartle_axes():
    return [
        rect("axv",MAT_CX-1,MAT_Y-4,2,CELL_H*2+8,BORDER2,extra={"fx":{"enter":"fade","order":0}}),
        rect("axh",MAT_X-4,MAT_CY-1,CELL_W*2+8,2,BORDER2,extra={"fx":{"enter":"fade","order":0}}),
        txt("axlt",MAT_CX-160,MAT_Y-30,320,20,"INTERACTING",11,color=TEXT,weight=700,family=MONOF,
            align="center",extra={"letterSpacing":3,"fx":{"enter":"fade","order":0}}),
        txt("axlb",MAT_CX-160,MAT_Y+CELL_H*2+12,320,20,"ACTING",11,color=TEXT,weight=700,family=MONOF,
            align="center",extra={"letterSpacing":3,"fx":{"enter":"fade","order":0}}),
        txt("axll",MAT_X-150,MAT_CY-9,138,20,"PLAYERS",11,color=TEXT,weight=700,family=MONOF,
            align="right",extra={"letterSpacing":3,"fx":{"enter":"fade","order":0}}),
        txt("axlr",MAT_X+CELL_W*2+12,MAT_CY-9,150,20,"WORLD",11,color=TEXT,weight=700,family=MONOF,
            extra={"letterSpacing":3,"fx":{"enter":"fade","order":0}}),
    ]

els = [rect("bg18",0,0,W,H,BG)] + bartle_left_column() + bartle_axes()
for i, q in enumerate(BARTLE):
    x, y, w, h = cell_xy(q["col"], q["row"])
    sid = "s18x%d" % i
    fx = {"fx": {"enter": "fade-up", "order": i + 1}}
    els += [
        rect(f"q{i}", x, y, w, h, q["soft"], radius=12, stroke=q["col_main"], strokeWidth=1.2,
             extra={"link": sid, **fx}),
        ellipse(f"qd{i}", x + 22, y + 24, 14, 14, q["col_main"], gradient=q["gr"],
                shadow=glow(q["gl"], 22),
                extra={"fx": {"loop": {"type": "motion-path", "duration": 9,
                                       "path": orbit_path(5, start_deg=-90)}}}),
        txt(f"qn{i}", x + 22, y + 48, w - 44, 30, q["name"], 21, color=TEXT, weight=800,
            family=DISPLAY, extra={"link": sid, **fx}),
        txt(f"qx{i}", x + 22, y + 80, w - 44, 18, q["axis"], 9.5, color=q["col_main"], weight=700,
            family=MONOF, extra={"letterSpacing": 1.5, **fx}),
        txt(f"qs{i}", x + 22, y + 104, w - 44, 62, q["blurb"], 12.5, color=MUTED, lh=1.5, extra=fx),
        txt(f"qp{i}", x + 22, y + h - 42, w - 44, 24, q["share"], 16, color=q["col_main"],
            weight=800, family=DISPLAY, extra=fx),
    ]
els += footer(28)
slides.append(slide(28, els, "Draw the two axes first, then let the quadrants land one at a time. The axes are the whole idea: WHAT you do (acting vs interacting) against WHAT you do it to (players vs the world). Click any quadrant to open it — the arrow keys skip those, so you can take them in any order the room asks for, or skip them entirely if you are short on time."))

# ---- the four expansions (hidden states of slide 28)
for i, q in enumerate(BARTLE):
    sid = "s18x%d" % i
    col = q["col_main"]
    e = [rect(f"bgx{i}", 0, 0, W, H, BG)]
    # every other quadrant shrinks into the locator; this one blows up
    for j, o in enumerate(BARTLE):
        if j == i:
            continue
        lx, ly, lw, lh = loc_xy(o["col"], o["row"])
        e += [
            rect(f"q{j}", lx, ly, lw, lh, o["soft"], radius=5, stroke=o["col_main"], strokeWidth=1),
            ellipse(f"qd{j}", lx + lw/2 - 4, ly + lh/2 - 4, 8, 8, o["col_main"]),
        ]
    ax, ay, aw, ah = loc_xy(q["col"], q["row"])
    e += [
        rect(f"locmark{i}", ax, ay, aw, ah, "rgba(0,0,0,0)", radius=5, stroke=col, strokeWidth=1.5,
             extra={"strokeStyle": "dashed"}),
        txt(f"loclbl{i}", LOC_X, LOC_Y + LOC_CH*2 + 10, LOC_CW*2, 18, "YOU ARE HERE", 9,
            color=FAINT, family=MONOF, align="center", extra={"letterSpacing": 2}),
        # the expanded quadrant
        rect(f"q{i}", 96, 232, 640, 392, q["soft"], radius=16, stroke=col, strokeWidth=1.5,
             shadow=glow(q["gl"], 40)),
        ellipse(f"qd{i}", 136, 268, 20, 20, col, gradient=q["gr"], shadow=glow(q["gl"], 26)),
        txt(f"qn{i}", 136, 296, 560, 54, q["name"], 42, color=TEXT, weight=800, family=DISPLAY),
        txt(f"qx{i}", 136, 356, 560, 20, q["axis"], 11, color=col, weight=700, family=MONOF,
            extra={"letterSpacing": 2.5}),
        txt(f"mot{i}", 136, 388, 560, 52, q["motive"], 19, color=TEXT, lh=1.45,
            extra={"fx": {"enter": "fade-up", "order": 0}}),
        rect(f"mdivx{i}", 136, 456, 560, 1, col, opacity=0.3,
             extra={"fx": {"enter": "fade", "order": 1}}),
        txt(f"dok{i}", 136, 474, 560, 18, "WHAT THEY ACTUALLY DO", 10.5, color=col, weight=700,
            family=MONOF, extra={"letterSpacing": 2, "fx": {"enter": "fade-up", "order": 1}}),
        txt(f"dob{i}", 136, 500, 560, 110,
            "<br>".join("&#9679;&nbsp; " + d for d in q["does"]), 14.5, color=MUTED, lh=1.75,
            extra={"fx": {"enter": "fade-up", "order": 2}}),
        # headline share
        txt(f"shr{i}", 772, 88, 240, 72, q["share"], 54, color=col, weight=800, family=DISPLAY,
            extra={"fx": {"enter": "fade-up", "order": 0}}),
        txt(f"shrl{i}", 772, 160, 240, 36, "OF EARLY MUD PLAYERS<br>&mdash; BARTLE'S ROUGH ESTIMATE", 9.5,
            color=FAINT, family=MONOF, lh=1.7, extra={"letterSpacing": 1.5,
                                                      "fx": {"enter": "fade-up", "order": 0}}),
        rect(f"dsg{i}", 772, 250, 412, 190, SURFACE, radius=14, stroke=BORDER, strokeWidth=1,
             extra={"fx": {"enter": "fade-up", "order": 2}}),
        rect(f"dsgb{i}", 772, 250, 4, 190, col,
             extra={"fx": {"enter": "fade-up", "order": 2}}),
        txt(f"dsgk{i}", 800, 272, 356, 18, "DESIGN FOR THEM BY", 10.5, color=col, weight=700,
            family=MONOF, extra={"letterSpacing": 2, "fx": {"enter": "fade-up", "order": 2}}),
        txt(f"dsgb2{i}", 800, 300, 356, 136, q["design"], 14.5, color=TEXT, lh=1.6,
            extra={"fx": {"enter": "fade-up", "order": 2}}),
        rect(f"exg{i}", 772, 460, 412, 164, SURFACE, radius=14, stroke=BORDER, strokeWidth=1,
             extra={"fx": {"enter": "fade-up", "order": 3}}),
        txt(f"exgk{i}", 800, 482, 356, 18, "GAMES BUILT FOR THEM", 10.5, color=FAINT, weight=700,
            family=MONOF, extra={"letterSpacing": 2, "fx": {"enter": "fade-up", "order": 3}}),
        txt(f"exgb{i}", 800, 508, 356, 100, q["games"], 15, color=MUTED, lh=1.9,
            extra={"fx": {"enter": "fade-up", "order": 3}}),
        # a real back control — a full-canvas invisible hit rect picks up the player's
        # link affordance and draws a giant ring across the slide on hover.
        rect(f"backbtn{i}", 96, 636, 276, 32, "rgba(255,255,255,0.04)", radius=16,
             stroke=BORDER2, strokeWidth=1, extra={"link": scene_id(28)}),
        txt(f"backh{i}", 96, 636, 276, 32, "&#8592;&nbsp;&nbsp;BACK TO THE MATRIX", 10,
            color=MUTED, family=MONOF, align="center", valign="middle",
            extra={"letterSpacing": 2, "link": scene_id(28)}),
    ]
    slides.append({"id": sid, "stateOf": scene_id(28), "background": BG, "transition": "morph",
                   "notes": q["name"] + " — expanded. The other three quadrants shrink into the locator "
                            "top-right so the room can still see where this type sits on both axes. Land "
                            "the 'design for them by' box: that is the part they can act on in their own "
                            "project. Click anywhere to return to the matrix.",
                   "elements": e})

# ============================================================ 21. PLAYER TYPES, BY THE NUMBERS (bars grow up into place)
bartle_labels = ["Achievers","Explorers","Socializers","Killers"]
bartle_vals = [10,10,80,1]
pt_bottom, pt_top, pt_max = 560, 260, 90
pt_scale = (pt_bottom - pt_top) / pt_max
pt_slot_w = 1088 / 4
els = [
    rect("bg21a",0,0,W,H,BG),
    kicker("k21a",MX,72,"How common is each type?", color=ACCENT2),
    txt("t21a",MX,104,1100,64,"Player Types, By the Numbers",48,weight=800,family=DISPLAY),
    txt("t21ab",MX,168,1080,30,"Bartle's own rough estimate from early MUD research &mdash; one of the most-cited, least-precise stats in game design.",16.5,color=MUTED,lh=1.4),
    rect("ptbase",96,pt_bottom,1088,2,BORDER2),
]
for v in [30,60,90]:
    gy = pt_bottom - v*pt_scale
    els += [
        rect(f"ptgrid{v}",96,gy,1088,1,BORDER,opacity=0.6),
        txt(f"ptgridl{v}",50,gy-8,38,16,f"{v}%",11,color=MUTED,align="right"),
    ]
els.append(txt("ptgridl0",50,pt_bottom-8,38,16,"0%",11,color=MUTED,align="right"))
for i,label in enumerate(bartle_labels):
    slot_x = 96 + i*pt_slot_w
    bar_w = 130
    bx = slot_x + (pt_slot_w-bar_w)/2
    v = bartle_vals[i]
    h = v*pt_scale
    order = i
    els += [
        rect(f"ptb{i}",bx,pt_bottom-h,bar_w,h,ACCENT2,radius=4,extra={"fx":{"enter":"fade-up","order":order}}),
        txt(f"ptv{i}",bx-10,pt_bottom-h-26,bar_w+20,20,f"~{v}%",14,color=ACCENT2,weight=800,family=MONOF,align="center",extra={"fx":{"enter":"fade-up","order":order}}),
        txt(f"ptcat{i}",slot_x,pt_bottom+14,pt_slot_w,22,label,14,color=TEXT,weight=600,align="center",extra={"fx":{"enter":"fade-up","order":order}}),
    ]
els += [
    rect("bnote",96,610,1088,54,SURFACE,radius=10,stroke=BORDER,strokeWidth=1),
    txt("bnotet",96+24,626,1040,26,
        "&#9679;&nbsp; Widely cited &mdash; but approximate. The real split shifts hugely by genre and community (a competitive shooter skews Killer; a life sim skews Socializer).",
        13.5,color=MUTED,lh=1.4),
] + footer(29)
slides.append(slide(29, els, "Socializers dominate almost every large player base — Bartle's original MUD research and later surveys keep landing here. The tiny Killer share surprises most students because Killers are the loudest, most visible players (leaderboards, trash talk), not the most numerous. Flag clearly: these are Bartle's own rough estimates, commonly repeated, not a precise modern census."))

# ============================================================ 22. PLAYER TYPES IN THE WILD
genre_rows = [
    ("MMORPGs", "Socializers &amp; Achievers", ASSIGN, "World of Warcraft"),
    ("Roguelikes", "Explorers &amp; Achievers", LABS, "Hades, Slay the Spire"),
    ("Battle Royale", "Killers", MIDT, "Fortnite, Apex Legends"),
    ("Walking Simulators", "Explorers", LABS, "Firewatch, Outer Wilds"),
    ("Farming / Life Sims", "Socializers", ASSIGN, "Stardew Valley, Animal Crossing"),
    ("Competitive Shooters", "Killers", MIDT, "Valorant, Counter-Strike"),
]
rows22 = [{"cells":[{"html":"Genre","bold":True},{"html":"Dominant Player Type(s)","bold":True},{"html":"Example Games","bold":True}]}]
for genre,ptype,col,ex in genre_rows:
    rows22.append({"cells":[{"html":f"<b>{genre}</b>"},{"html":f"<b>{ptype}</b>"},{"html":ex}]})
els = [
    rect("bg22a",0,0,W,H,BG),
    kicker("k22a",MX,72,"Illustrative, not exhaustive", color=ACCENT2),
    txt("t22a",MX,104,1100,64,"Player Types in the Wild",50,weight=800,family=DISPLAY),
    txt("t22ab",MX,170,1080,30,"Most real players are a blend &mdash; but genres are still designed toward a dominant type.",17,color=MUTED),
    {"id":"gwtable","type":"table","x":96,"y":222,"w":1088,"h":382,"rotation":0,"opacity":1,
     "columns":[{"w":0.30},{"w":0.32},{"w":0.38}],
     "header":True,
     "rows":rows22,
     "style":{"headerBg":SURFACE2,"headerColor":TEXT,"zebra":True,"borderColor":BORDER,
              "borderWidth":1,"cellPadX":22,"cellPadY":16,"fontSize":16,"color":MUTED,"radius":12}},
    txt("t22note",96,616,1088,32,
        "A single genre can serve more than one type at once &mdash; that overlap is exactly where design choices live.",
        13.5,color=FAINT),
] + footer(30)
slides.append(slide(30, els, "Use this to bridge from theory to their own project pitch: ask each table/group to name the genre their planned final project is closest to, and predict which player type(s) it's implicitly designed for. If it doesn't match what they intended, that's useful information before they build."))

# ============================================================ 23. THE ACTION MATRIX (verbs, complementary to Bartle)
action_quads = [
    ("Explore","Browse &amp; judge what's already there","closest to Bartle's Explorers",
     ["View","Collect","Rate","Vote","Curate","Review"],ACCENT3,ACCENT3_SOFT,(96,222)),
    ("Compete","Act on other players, directly","closest to Bartle's Killers &amp; Achievers",
     ["Win","Challenge","Compare","Showoff","Taunt"],MIDT,"rgba(209,78,128,0.14)",(656,222)),
    ("Create","Make and shape your own content","a builder's flavor of Explorer",
     ["Purchase","Design","Build","Decorate","Customize","Express"],ACCENT,ACCENT_SOFT,(96,427)),
    ("Collaborate","Interact with players, not against them","closest to Bartle's Socializers",
     ["Comment","Like","Greet","Help","Share","Contribute"],ASSIGN,ACCENT2_SOFT,(656,427)),
]
els = [
    rect("bg23m",0,0,W,H,BG),
    kicker("k23m",MX,72,"One more lens on motivation", color=ACCENT2),
    txt("t23m",MX,104,1100,64,"From Motivation to Mechanic",46,weight=800,family=DISPLAY),
    txt("t23mb",MX,168,1080,44,
        "A sibling framework: instead of naming the player, it names the <b>verb</b> your game gives them. "
        "Left&ndash;right is about content vs. about other players; top&ndash;bottom is acting alone vs. interacting with someone.",
        15,color=MUTED,lh=1.45),
]
for qi,(name,desc,tag,verbs,col,soft,(x,y)) in enumerate(action_quads):
    fx = {"fx":{"enter":"fade-up","order":qi}}
    els += [
        rect(f"am-{name}",x,y,528,185,soft,radius=14,stroke=col,strokeWidth=1.5,extra=fx),
        txt(f"am-{name}t",x+28,y+16,472,30,name,21,weight=800,family=DISPLAY,color=TEXT,extra=fx),
        txt(f"am-{name}d",x+28,y+48,472,20,desc,13,color=MUTED,extra=fx),
        txt(f"am-{name}tag",x+28,y+70,472,16,tag.upper(),10.5,color=col,weight=700,family=MONOF,extra={"letterSpacing":1,**fx}),
    ]
    colx = [x+28, x+28+148+14, x+28+2*(148+14)]
    for j,verb in enumerate(verbs):
        cx = colx[j%3]; cy = y+92+ (j//3)*(32+10)
        els += chip(f"am-{name}-c{j}",cx,cy,148,32,verb,col)
        els[-1]["fx"] = fx["fx"]; els[-2]["fx"] = fx["fx"]
els += [
    txt("t23mnote",MX,636,1088,20,
        "For your final project: list the verbs your game actually offers &mdash; a thin verb list is a thin game.",
        13,color=FAINT),
]
els += footer(31)
slides.append(slide(31, els, "This isn't Bartle's own model — it's a complementary one (sometimes called a social/action matrix) that trades player identity for concrete verbs, which is more directly actionable when they're staring at a blank Unity scene. Ask each student to name 3 verbs their planned final project already supports, and 1 it's currently missing."))

# ============================================================ 19. DESIGNING FOR PLAYER TYPES
els = [
    rect("bg19",0,0,W,H,BG),
    kicker("k19",MX,72,"So what?", color=ACCENT2),
    txt("t19",MX,104,1100,70,"Designing for Who Plays",56,weight=800,family=DISPLAY),
    rect("dp1",96,232,528,162,SURFACE,radius=12,stroke=BORDER,strokeWidth=1,extra={"fx":{"enter":"fade-up","order":0}}),
    txt("dp1t",96+28,256,472,28,"Achievers &amp; Explorers",18,weight=700,family=DISPLAY,color=QUIZ,extra={"fx":{"enter":"fade-up","order":0}}),
    txt("dp1d",96+28,290,472,110,"Quests, collectibles, and completion trackers reward Achievers. Hidden rooms and lore reward Explorers.",15.5,color=MUTED,lh=1.55,extra={"fx":{"enter":"fade-up","order":0}}),
    rect("dp2",656,232,528,162,SURFACE,radius=12,stroke=BORDER,strokeWidth=1,extra={"fx":{"enter":"fade-up","order":1}}),
    txt("dp2t",656+28,256,472,28,"Socializers &amp; Killers",18,weight=700,family=DISPLAY,color=MIDT,extra={"fx":{"enter":"fade-up","order":1}}),
    txt("dp2d",656+28,290,472,110,"Co-op and shared spaces reward Socializers. Leaderboards and PvP reward Killers.",15.5,color=MUTED,lh=1.55,extra={"fx":{"enter":"fade-up","order":1}}),
    rect("dp3",96,426,1088,198,ACCENT_SOFT,radius=14,stroke="rgba(255,138,61,0.35)",strokeWidth=1,extra={"fx":{"enter":"fade-up","order":2}}),
    txt("dp3k",96+32,454,600,24,"FOR YOUR FINAL PROJECT",13,color=ACCENT,weight=700,family=MONOF,extra={"letterSpacing":1.5,"fx":{"enter":"fade-up","order":2}}),
    txt("dp3b",96+32,484,1000,120,"You don't need to serve all four. Pick the 1&ndash;2 player types your game is <i>for</i>, and let that choice drive your mechanics &mdash; that's design, not decoration.",18,color=TEXT,lh=1.55,extra={"fx":{"enter":"fade-up","order":2}}),
] + footer(32)
slides.append(slide(32, els, "This is the actionable takeaway of the whole Bartle section: a small student project can't and shouldn't try to serve all four types. Naming your target player type(s) up front is a legitimate design decision they can defend in their final presentation."))

# ============================================================ 20. RECAP
els = [
    rect("bg20",0,0,W,H,BG),
    kicker("k20",MX,72,"Before we go"),
    txt("t20",MX,104,1100,70,"Key Takeaways",56,weight=800,family=DISPLAY),
    rect("rc1",96,232,1088,120,SURFACE,radius=12,stroke=BORDER,strokeWidth=1,extra={"fx":{"enter":"fade-up","order":0}}),
    ellipse("rc1n",112,259,66,66,ACCENT,gradient=grad(35,"#FF8A3D","#FFC178"),shadow=glow(ACCENT_GLOW,34),extra={"fx":{"enter":"fade-up","order":0}}),
    txt("rc1nt",112,259,66,66,"1",30,color=BG,weight=800,family=DISPLAY,align="center",valign="middle",extra={"fx":{"enter":"fade-up","order":0}}),
    txt("rc1t",216,258,900,32,"Games are systems.",21,weight=700,family=DISPLAY,extra={"fx":{"enter":"fade-up","order":0}}),
    txt("rc1d",216,296,900,44,"Mechanics you build become dynamics players feel become aesthetics they remember.",15.5,color=MUTED,lh=1.5,extra={"fx":{"enter":"fade-up","order":0}}),
    rect("rc2",96,368,1088,120,SURFACE,radius=12,stroke=BORDER,strokeWidth=1,extra={"fx":{"enter":"fade-up","order":1}}),
    ellipse("rc2n",112,395,66,66,ACCENT2,gradient=grad(35,"#55D6C2","#3FB4E8"),shadow=glow(ACCENT2_GLOW,34),extra={"fx":{"enter":"fade-up","order":1}}),
    txt("rc2nt",112,395,66,66,"2",30,color=BG,weight=800,family=DISPLAY,align="center",valign="middle",extra={"fx":{"enter":"fade-up","order":1}}),
    txt("rc2t",216,394,900,32,"There is no single \"the player.\"",21,weight=700,family=DISPLAY,extra={"fx":{"enter":"fade-up","order":1}}),
    txt("rc2d",216,432,900,44,"Achievers, Explorers, Socializers, Killers all want something different from your game.",15.5,color=MUTED,lh=1.5,extra={"fx":{"enter":"fade-up","order":1}}),
    rect("rc3",96,504,1088,120,SURFACE,radius=12,stroke=BORDER,strokeWidth=1,extra={"fx":{"enter":"fade-up","order":2}}),
    ellipse("rc3n",112,531,66,66,ACCENT3,gradient=grad(35,"#6C8CFF","#A579FF"),shadow=glow(ACCENT3_GLOW,34),extra={"fx":{"enter":"fade-up","order":2}}),
    txt("rc3nt",112,531,66,66,"3",30,color=BG,weight=800,family=DISPLAY,align="center",valign="middle",extra={"fx":{"enter":"fade-up","order":2}}),
    txt("rc3t",216,530,900,32,"This is the language of the whole semester.",21,weight=700,family=DISPLAY,extra={"fx":{"enter":"fade-up","order":2}}),
    txt("rc3d",216,568,900,44,"MDA and Bartle aren't trivia &mdash; they're literally how your final project gets evaluated.",15.5,color=MUTED,lh=1.5,extra={"fx":{"enter":"fade-up","order":2}}),
] + footer(33)
slides.append(slide(33, els, "Read these three out loud slowly — this is the takeaway students should be able to repeat back a week from now, even if they've forgotten the vocabulary."))

# ============================================================ 21. NEXT UP
els = [
    rect("bg21",0,0,W,H,BG),
    kicker("k21",MX,72,"Looking ahead"),
    txt("t21",MX,104,1100,70,"Next Up",56,weight=800,family=DISPLAY),
    rect("nx1",96,232,528,246,SURFACE,radius=14,stroke=BORDER,strokeWidth=1,extra={"fx":{"enter":"fade-up","order":0}}),
    rect("nx1bar",96,232,528,6,ACCENT,extra={"fx":{"enter":"fade-up","order":0}}),
    txt("nx1k",96+32,264,460,24,"TODAY'S LAB",13,color=ACCENT,weight=700,family=MONOF,extra={"letterSpacing":2,"fx":{"enter":"fade-up","order":0}}),
    txt("nx1t",96+32,294,460,44,"Unity Environment Tour",24,weight=700,family=DISPLAY,extra={"fx":{"enter":"fade-up","order":0}}),
    txt("nx1d",96+32,346,460,110,"Install &amp; account setup, the editor layout, and your first empty scene. Bring a laptop that can run Unity Hub.",16.5,color=MUTED,lh=1.6,extra={"fx":{"enter":"fade-up","order":0}}),
    rect("nx2",656,232,528,246,SURFACE,radius=14,stroke=BORDER,strokeWidth=1,extra={"fx":{"enter":"fade-up","order":1}}),
    rect("nx2bar",656,232,528,6,ACCENT2,extra={"fx":{"enter":"fade-up","order":1}}),
    txt("nx2k",656+32,264,460,24,"LECTURE 02",13,color=ACCENT2,weight=700,family=MONOF,extra={"letterSpacing":2,"fx":{"enter":"fade-up","order":1}}),
    txt("nx2t",656+32,294,460,44,"Inside Unity",24,weight=700,family=DISPLAY,extra={"fx":{"enter":"fade-up","order":1}}),
    txt("nx2d",656+32,346,460,110,"Version control for game projects, and scene / GameObject hierarchy &mdash; CLO-2 begins.",16.5,color=MUTED,lh=1.6,extra={"fx":{"enter":"fade-up","order":1}}),
    rect("nxread",96,510,1088,74,ACCENT_SOFT,radius=12,stroke="rgba(255,138,61,0.3)",strokeWidth=1,extra={"fx":{"enter":"fade-up","order":2}}),
    txt("nxreadt",96+28,533,1032,30,"Before then: skim the <b>Unity Essentials</b> pathway on Unity Learn &mdash; free, ~2 hours.",16.5,color=TEXT,extra={"fx":{"enter":"fade-up","order":2}}),
] + footer(34)
slides.append(slide(34, els, "Confirm the lab room/time if different from lecture. Remind them the reading is skimmable, not a deep study — the point is familiarity with the editor before they touch it hands-on today."))

# ============================================================ 22. THANK YOU
els = [
    rect("bg22",0,0,W,H,BG),
    rect("tf2", MX, 220, 64, 3, ACCENT, shadow=glow(ACCENT_GLOW,18),
         extra={"fx":{"enter":"fade-up","order":0,"ambient":"kenburns","ken":{"dir":"drift","scale":1.0,"duration":16}}}),
    txt("tyk",MX,256,700,28,"SEE YOU IN LAB",15,color=ACCENT,weight=700,family=MONOF,extra={"letterSpacing":3,"fx":{"enter":"fade-up","order":0}}),
    txt("tyt",MX,292,1120,120,"Questions?",76,weight=800,family=DISPLAY,extra={"letterSpacing":-1,"fx":{"enter":"fade-up","order":1}}),
    rect("tydiv",MX,428,340,2,BORDER2,extra={"fx":{"enter":"fade-up","order":2}}),
    txt("typrompt",MX,456,760,80,"One thing to bring to next lecture: name a game that made you feel something you didn't expect &mdash; and guess which of the 8 kinds of fun it leaned on.",19,color=MUTED,lh=1.55,extra={"fx":{"enter":"fade-up","order":2}}),
    txt("tycontact",MX,560,700,30,"hello@madratzz.net &nbsp;&middot;&nbsp; muhammadraza.vf@itu.edu.pk",15,color=FAINT,family=MONOF,extra={"fx":{"enter":"fade-up","order":3}}),
] + orbit_motif("ty", 986, 360, 316, core=100, label="PLAY") + stars("ty", [
    (760, 150, 3, "rgba(255,255,255,0.40)", 24, 44),
    (1160, 560, 4, "rgba(85,214,194,0.45)", 30, 50),
]) + footer(35)
slides.append(slide(35, els, "Close on the discussion prompt — it's a soft assignment for next lecture that gets them practicing the vocabulary before Lecture 2 moves into Unity itself. Stay after for individual questions."))

print(f"Total slides built: {len(slides)}")

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = json.load(open(os.path.join(HERE, "fonts", "fonts.json"), encoding="utf-8"))
PHOTO = json.load(open(os.path.join(HERE, "fonts", "photo-asset.json"), encoding="utf-8"))
PHOTO_BARTLE = json.load(open(os.path.join(HERE, "fonts", "photo-bartle-asset.json"), encoding="utf-8"))
ASSETS = {**FONTS, **PHOTO, **PHOTO_BARTLE}

doc = {
    "format": "bento/slides",
    "version": 1,
    "title": "CS464 — Lecture 01: The Anatomy of Play",
    "size": {"width": W, "height": H},
    "theme": {
        "background": BG,
        "color": TEXT,
        "accent": ACCENT,
        "fontFamily": BODYF
    },
    "meta": {
        "author": "Muhammad Raza Butt",
        "company": "Information Technology University",
        "subject": "CS464 — Game Development",
        "event": "Lecture 01"
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

path = os.path.join(HERE, "..", "CS464-Lecture-01-Anatomy-of-Play.bento.html")
content = open(path, encoding="utf-8").read()

import re
pattern = re.compile(r'(<script type="application/bento\+json" id="bento-doc">)(.*?)(</script>)', re.S)
m = pattern.search(content)
assert m, "bento-doc script block not found"
new_content = content[:m.start(2)] + json_str_escaped + content[m.end(2):]

open(path, "w", encoding="utf-8").write(new_content)
print("Injected doc JSON, length:", len(json_str_escaped))
print("Slide count:", len(slides))
print("Total elements:", sum(len(s["elements"]) for s in slides))
