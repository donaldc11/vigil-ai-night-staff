from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
import vigil, adapters
P=Presentation(); P.slide_width=Inches(13.333); P.slide_height=Inches(7.5)
BG=RGBColor(0x12,0x15,0x1a); FG=RGBColor(0xe8,0xe8,0xe8); AC=RGBColor(0x55,0xd6,0x8a)
def slide(title, lines, notes="", size=22):
    s=P.slides.add_slide(P.slide_layouts[6]); s.background.fill.solid(); s.background.fill.fore_color.rgb=BG
    tb=s.shapes.add_textbox(Inches(.7),Inches(.5),Inches(12),Inches(1.1)).text_frame; tb.word_wrap=True
    r=tb.paragraphs[0].add_run(); r.text=title; r.font.size=Pt(38); r.font.bold=True; r.font.color.rgb=AC
    bx=s.shapes.add_textbox(Inches(.7),Inches(1.8),Inches(12),Inches(5)).text_frame; bx.word_wrap=True
    for i,l in enumerate(lines):
        p=bx.paragraphs[0] if i==0 else bx.add_paragraph(); p.space_after=Pt(10)
        r=p.add_run(); r.text=l; r.font.size=Pt(size); r.font.color.rgb=FG
    ft=s.shapes.add_textbox(Inches(.7),Inches(6.9),Inches(12),Inches(.4)).text_frame
    r=ft.paragraphs[0].add_run(); r.text="Fictional data. Each sponsor integration shows its true mode; no real call is placed."; r.font.size=Pt(12); r.font.color.rgb=RGBColor(0xaa,0xaa,0xaa)
    s.notes_slide.notes_text_frame.text=notes
slide("Vigil",["The AI night shift for family-owned funeral homes.","So no first call goes unanswered and no director loses sleep.","Track: Business / Growth / Productivity"],"Say the one-liner, then go straight to the problem.",30)
slide("The problem",["Roughly 15,400 US funeral homes, most family-owned on older software (our research estimate, not independently verified).","A first call is worth roughly $6-8K. Nights and weekends are where homes lose it.","Directors do not want another system of record. They want revenue protection and sleep."],"Label the numbers as estimates from our own research.")
_AVS=["mara","quinn","sol","paige","faye","vera"]
def _avs():
    s=P.slides[-1]
    for i,n in enumerate(_AVS):
        s.shapes.add_picture(f"avatars/{n}_deck.jpg",Inches(.7+i*2.05),Inches(4.8),Inches(1.8),Inches(1.8))
        tf=s.shapes.add_textbox(Inches(.7+i*2.05),Inches(6.6),Inches(1.9),Inches(.35)).text_frame; r=tf.paragraphs[0].add_run(); r.text=(vigil.STAFF[i][0]); r.font.size=Pt(14); r.font.color.rgb=FG
    tf=s.shapes.add_textbox(Inches(.7),Inches(4.3),Inches(6),Inches(.35)).text_frame; r=tf.paragraphs[0].add_run(); r.text="avatars: Masky (AI, fictional)"; r.font.size=Pt(12); r.font.color.rgb=RGBColor(0xaa,0xaa,0xaa)
slide("Six workers, one human Director",["Mara intake, Quinn quoter, Sol scheduler, Paige paperwork, Faye family liaison, Lex compliance logger. All report to the human Director.","The Director approves every family message and every removal dispatch.","Honest note: Mara and Faye are OpenAI-assisted ($3 cap, lint + approval + fallback). Quinn, Sol, Paige, Lex are deterministic code."],"Point at each role. Stress: humans stay the face, AI works behind the scenes. Agents never make arrangements, that is for licensed staff.",15)
_avs()
slide("The loop",["Request: a family calls at 2 AM.","Delegate: Mara classifies it as a first call, routes to Quinn, Sol, Paige.","Act: GPL-based price range, on-call director, pre-filled paperwork.","Check: Lex lints for recording disclosure and no arrangement-making.","Approve: the Director signs off on the message and dispatch.","Report and improve: case logged, intake checklist updated."],"Play demo.html here. About 60 seconds.",22)
slide("Sponsor tools, each with a job",[f"{a.name}: {a.job}" for a in adapters.registry().values()]+["Status shown per run in the demo: REAL / SIMULATED / FALLBACK / EXTERNAL. Today: n8n, Snyk, BAND real; Prelint external; 7 simulated."],"Be honest and update the status line to the live count before presenting.",16)
slide("Honesty and safety",["Fictional data only. No real calls, no real families. Phone numbers redacted to last 4.","Every run reports which steps were real, simulated, fallback or external (55 automated tests).","Compliance by design: inbound only, recording disclosure, GPL quotes, no arrangements.","Human approval gates cannot be skipped; a declined approval stops the case."],"This is the trust slide for judges.")
slide("What's next",["Swap mock adapters for live integrations, one at a time.","Write into the funeral home's existing case software, not replace it.","Pilot with one family-owned home.","Ask: intros to state funeral director associations."],"Close on the pilot ask.")
P.save("Vigil_deck.pptx")
