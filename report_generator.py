from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak
from analyzer import calculate_overall_score

NAVY=colors.HexColor("#18213F")
PURPLE=colors.HexColor("#6D4AFF")
PALE=colors.HexColor("#F2EFFF")
GREY=colors.HexColor("#65708A")

def _p(text, style):
    return Paragraph(escape(str(text or "")).replace("\n","<br/>"),style)

def build_pdf_report(data: dict, resume_filename: str, job_description: str=b"") -> bytes:
    buffer=BytesIO()
    doc=SimpleDocTemplate(buffer,pagesize=A4,rightMargin=17*mm,leftMargin=17*mm,topMargin=17*mm,bottomMargin=17*mm,title="ResumeIQ Analysis Report",author="ResumeIQ")
    base=getSampleStyleSheet()
    styles={
      "title":ParagraphStyle("RIQTitle",parent=base["Title"],fontName="Helvetica-Bold",fontSize=23,textColor=NAVY,alignment=TA_LEFT,spaceAfter=4),
      "sub":ParagraphStyle("RIQSub",parent=base["Normal"],fontSize=9,textColor=GREY,spaceAfter=12),
      "h":ParagraphStyle("RIQH",parent=base["Heading2"],fontName="Helvetica-Bold",fontSize=13,textColor=NAVY,spaceBefore=12,spaceAfter=6),
      "body":ParagraphStyle("RIQBody",parent=base["BodyText"],fontSize=8.5,leading=12,textColor=colors.HexColor("#30394F"),spaceAfter=4),
      "small":ParagraphStyle("RIQSmall",parent=base["BodyText"],fontSize=7.5,leading=10,textColor=GREY,spaceAfter=3),
      "q":ParagraphStyle("RIQQ",parent=base["BodyText"],fontName="Helvetica-Bold",fontSize=8.5,leading=11,textColor=NAVY,spaceBefore=5),
    }
    story=[]
    story += [_p("ResumeIQ",styles["title"]),_p("Your Resume. Your Next Opportunity. | AI Resume Analysis Report",styles["sub"])]
    story += [_p(f"Candidate: {data.get('candidate_name','Not identified')}",styles["body"]),_p(f"Target role: {data.get('target_role','Not identified')}",styles["body"]),_p(f"Source file: {resume_filename}",styles["small"])]
    scores=data["scores"]
    rows=[["ASSESSMENT","SCORE"],["Overall resume score",f"{calculate_overall_score(scores)}/100"],["ATS readability",f"{scores['ats_readability']}/100"],["Job description match",f"{scores['job_match']}/100"]]
    t=Table(rows,colWidths=[125*mm,35*mm])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("BACKGROUND",(0,1),(-1,-1),PALE),("TEXTCOLOR",(0,1),(-1,-1),NAVY),("GRID",(0,0),(-1,-1),.3,colors.white),("PADDING",(0,0),(-1,-1),7),("FONTNAME",(0,1),(-1,-1),"Helvetica")]))
    story += [Spacer(1,5*mm),t,_p("Executive summary",styles["h"]),_p(data.get("executive_summary",""),styles["body"])]
    story.append(_p("Score breakdown",styles["h"]))
    for key,val in scores.items():
        story.append(_p(f"{key.replace('_',' ').title()}: {val}/100 — {data['score_explanations'].get(key,'')}",styles["body"]))
    story.append(_p("Skills analysis",styles["h"]))
    for label,key in [("Skills present","skills_present"),("Missing soft skills","missing_soft_skills"),("Skills to improve","skills_to_improve"),("Important keywords","important_keywords")]:
        story.append(_p(f"{label}: {', '.join(data.get(key,[])) or 'Not identified'}",styles["body"]))
    story.append(_p("Missing technical skills",styles["h"]))
    missing=data.get("missing_technical_skills",[])
    if missing:
        for item in missing: story.append(_p(f"{item.get('priority')} priority — {item.get('skill')}: {item.get('reason')}",styles["body"]))
    else: story.append(_p("No missing technical skills identified.",styles["body"]))
    story.append(_p("AI recommendations",styles["h"]))
    story.append(_p(f"Suggested professional summary: {data.get('improved_summary','')}",styles["body"]))
    for heading,key in [("Experience rewrites","experience_rewrites"),("Project rewrites","project_rewrites")]:
        story.append(_p(heading,styles["h"]))
        for item in data.get(key,[]):
            story.append(_p(f"{item.get('section')}: {item.get('improved')} (Rationale: {item.get('rationale')})",styles["body"]))
    story.append(PageBreak())
    story.append(_p("Interview preparation",styles["h"]))
    for heading,key in [("HR questions","hr_questions"),("Technical questions","technical_questions"),("Project questions","project_questions")]:
        story.append(_p(heading,styles["h"]))
        for i,item in enumerate(data.get(key,[]),1):
            story.append(KeepTogether([_p(f"{i}. {item.get('question')}",styles["q"]),_p(f"Suggested answer: {item.get('suggested_answer')}",styles["body"])]))
    story.append(_p("Topics to prepare",styles["h"]))
    for topic in data.get("preparation_topics",[]): story.append(_p(f"• {topic}",styles["body"]))
    story.append(Spacer(1,5*mm))
    story.append(_p("Important: ResumeIQ provides advisory feedback based on the supplied documents. Scores do not represent an actual ATS vendor's scoring algorithm. Review all AI-generated rewrites and include only claims that are accurate and verifiable.",styles["small"]))
    def footer(canvas, doc_obj):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#E6E8F0")); canvas.line(17*mm,13*mm,A4[0]-17*mm,13*mm)
        canvas.setFont("Helvetica",7); canvas.setFillColor(GREY)
        canvas.drawString(17*mm,8*mm,"ResumeIQ · Confidential candidate-provided content")
        canvas.drawRightString(A4[0]-17*mm,8*mm,f"Page {doc_obj.page}")
        canvas.restoreState()
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    return buffer.getvalue()
