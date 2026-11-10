import streamlit as st
import plotly.graph_objects as go
from resume_parser import extract_resume_text, ResumeParseError
from ai_engine import analyze_with_groq, AIConfigurationError, AIAnalysisError
from analyzer import validate_analysis, calculate_overall_score
from report_generator import build_pdf_report
from utils import get_api_key, format_score, safe_filename

st.set_page_config(page_title="ResumeIQ | AI Resume Analyzer", page_icon="📄", layout="wide", initial_sidebar_state="expanded")

NAV_ITEMS = ["Dashboard", "Upload Resume", "Resume Analysis", "Skills Gap", "Resume Improvements", "Interview Preparation"]

def inject_css():
    st.markdown("""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
      html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
      .stApp { background: #f6f7fb; color: #172033; }
      [data-testid="stSidebar"] { background: #11152d; }
      [data-testid="stSidebar"] * { color: #eef0ff !important; }
      [data-testid="stSidebar"] [data-testid="stRadio"] label { padding: 8px 10px; border-radius: 9px; }
      .brand { font-family: Manrope,sans-serif; font-size: 27px; font-weight: 800; letter-spacing:-1px; color:#fff; }
      .brand span { color:#a78bfa; }
      .tagline { color:#b8bfd8; font-size:12px; margin-top:-5px; margin-bottom:28px; }
      .hero { background:linear-gradient(120deg,#21184a,#44318c); padding:30px 32px; border-radius:18px; color:white; margin-bottom:22px; }
      .hero h1 { font-family:Manrope,sans-serif; font-size:31px; margin:0 0 8px 0; color:white; }
      .hero p { color:#e4defe; margin:0; }
      .metric { background:white; border:1px solid #e9eaf2; padding:18px 20px; border-radius:15px; box-shadow:0 4px 18px rgba(24,30,60,.035); min-height:112px; }
      .metric-label { color:#737b91; font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:.5px; }
      .metric-value { color:#202744; font-family:Manrope,sans-serif; font-size:30px; font-weight:800; margin-top:7px; }
      .metric-note { color:#8b91a3; font-size:11px; }
      .section-title { font-family:Manrope,sans-serif; font-size:21px; font-weight:800; color:#202744; margin:16px 0 12px; }
      .small-muted { color:#777f94; font-size:13px; }
      div.stButton > button[kind="primary"] { background:#6d4aff; border:0; border-radius:10px; font-weight:700; }
      div.stButton > button { border-radius:10px; }
      .pill { display:inline-block; background:#f0ebff; color:#6341c8; border-radius:30px; padding:5px 10px; font-size:11px; font-weight:700; margin:2px; }
      .stTabs [data-baseweb="tab"] { font-weight:600; }
    </style>
    """, unsafe_allow_html=True)

def metric_card(label, value, note=""):
    st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>', unsafe_allow_html=True)

def score_gauge(label, score, color="#7656e8"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=int(score),
        number={"suffix":"/100","font":{"size":28,"color":"#202744"}},
        title={"text":label,"font":{"size":14,"color":"#69718a"}},
        gauge={"axis":{"range":[0,100],"tickwidth":0,"tickcolor":"#fff"},
               "bar":{"color":color,"thickness":.22},
               "bgcolor":"#f0eff6","borderwidth":0,
               "steps":[{"range":[0,100],"color":"#f0eff6"}]}
    ))
    fig.update_layout(height=210, margin=dict(l=18,r=18,t=45,b=8), paper_bgcolor="rgba(0,0,0,0)", font_family="DM Sans")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

def show_dashboard():
    st.markdown('<div class="hero"><h1>Your Resume. Your Next Opportunity.</h1><p>Turn your resume into a focused job-search strategy with evidence-based AI feedback.</p></div>', unsafe_allow_html=True)
    data = st.session_state.get("analysis")
    if data:
        scores = data["scores"]
        cols = st.columns(4)
        for col, label, value, note in zip(cols, ["Overall score","ATS readability","Job match","Technical skills"], [calculate_overall_score(scores), scores["ats_readability"], scores["job_match"], scores["technical_skills"]], ["Composite assessment","Structure and parseability","Against this job description","Relevant technical skills"]):
            with col: metric_card(label, f"{value}/100", note)
        st.markdown('<div class="section-title">Latest analysis</div>', unsafe_allow_html=True)
        st.write(f"**Target role:** {data.get('target_role') or 'Not identified'}")
        st.write(data.get("executive_summary",""))
        if st.button("Analyse another resume", type="primary"):
            st.session_state.pop("analysis", None); st.session_state.pop("resume_text", None); st.session_state.pop("resume_name", None); st.rerun()
    else:
        c1,c2 = st.columns([1.2,1])
        with c1:
            st.markdown("### A clearer view of your next move")
            st.write("Upload a PDF or DOCX resume, add the job description, and receive a tailored scorecard, skills-gap review, rewrite suggestions and interview practice.")
            st.markdown("- Job-specific resume assessment\n- Honest skills-gap prioritisation\n- Resume improvements grounded in your content\n- Downloadable PDF report")
        with c2:
            st.markdown("#### Start your analysis")
            st.info("Use **Upload Resume** in the sidebar to begin. Your file is processed in memory and is not saved by this app.")

def show_upload():
    st.markdown('<div class="section-title">Upload your resume</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Choose a resume", type=["pdf","docx"], help="PDF or DOCX · Maximum 5 MB")
    jd = st.text_area("Paste the job description", height=220, placeholder="Paste the full job description here…", max_chars=20000)
    if uploaded:
        if uploaded.size > 5 * 1024 * 1024:
            st.error("File exceeds the 5 MB limit. Please upload a smaller file.")
        else:
            st.caption(f"Selected: {uploaded.name} · {uploaded.size/1024:.1f} KB")
    if st.button("Analyse Resume", type="primary", use_container_width=True, disabled=not uploaded or not jd.strip()):
        try:
            with st.spinner("Reading and validating your resume…"):
                resume_text = extract_resume_text(uploaded.getvalue(), uploaded.name)
            if len(resume_text.strip()) < 80:
                st.error("Not enough readable text was found. If this is a scanned PDF, convert it using OCR and upload the searchable PDF.")
                return
            api_key = get_api_key()
            if not api_key:
                st.error("Groq API key not found. Add GROQ_API_KEY to .env locally or Streamlit Cloud Secrets.")
                return
            st.session_state["resume_text"] = resume_text
            st.session_state["resume_name"] = uploaded.name
            with st.spinner("ResumeIQ is comparing your resume with the role. This can take a minute…"):
                result = analyze_with_groq(resume_text, jd.strip(), api_key)
            st.session_state["analysis"] = validate_analysis(result)
            st.session_state["job_description"] = jd.strip()
            st.success("Analysis completed.")
            st.rerun()
        except ResumeParseError as exc:
            st.error(str(exc))
        except (AIConfigurationError, AIAnalysisError) as exc:
            st.error(str(exc))
        except Exception:
            st.error("Something went wrong while processing this file. Check the file and try again.")

def show_analysis():
    data = st.session_state.get("analysis")
    if not data:
        st.info("No analysis yet. Upload a resume and job description first."); return
    s=data["scores"]
    st.markdown('<div class="section-title">Resume scorecard</div>', unsafe_allow_html=True)
    cols=st.columns(3)
    for col,label,key in zip(cols,["Overall resume score","ATS readability","Job description match"],["overall","ats_readability","job_match"]):
        with col: score_gauge(label, calculate_overall_score(s) if key=="overall" else s[key])
    score_keys=[("Technical skills","technical_skills"),("Soft skills","soft_skills"),("Experience relevance","experience_relevance"),("Education relevance","education_relevance"),("Keyword optimisation","keyword_optimization"),("Structure & formatting","structure_formatting")]
    st.markdown("### Dimension breakdown")
    for label,key in score_keys:
        a,b=st.columns([1,5])
        with a: st.write(f"**{label}**")
        with b: st.progress(int(s[key])/100, text=f"{s[key]}/100")
        st.caption(data["score_explanations"].get(key,""))
    st.markdown("### Summary")
    st.write(data["executive_summary"])
    st.caption("These are ResumeIQ's heuristic and AI-assisted assessments, not scores from an actual ATS vendor.")

def show_skills():
    d=st.session_state.get("analysis")
    if not d: st.info("Run an analysis to view your skills gap."); return
    st.markdown('<div class="section-title">Skills gap analysis</div>',unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        st.markdown("**Skills found in your resume**")
        st.write(", ".join(d["skills_present"]) or "No specific skills identified.")
        st.markdown("**Skills to strengthen**")
        st.write(", ".join(d["skills_to_improve"]) or "No improvement areas identified.")
    with c2:
        st.markdown("**Job-specific keywords**")
        st.write(", ".join(d["important_keywords"]) or "None identified.")
        st.markdown("**Missing soft skills**")
        st.write(", ".join(d["missing_soft_skills"]) or "None identified.")
    for priority in ["High","Medium","Low"]:
        items=[x for x in d["missing_technical_skills"] if x.get("priority")==priority]
        if items:
            st.markdown(f"#### {priority} priority")
            for item in items: st.write(f"- **{item.get('skill','Skill')}** — {item.get('reason','')}")

def show_improvements():
    d=st.session_state.get("analysis")
    if not d: st.info("Run an analysis to view improvement suggestions."); return
    st.markdown('<div class="section-title">Resume improvements</div>',unsafe_allow_html=True)
    st.warning("Review every suggested rewrite for accuracy before adding it to your resume. Do not include a claim you cannot substantiate.")
    st.markdown("### Professional summary")
    st.write(d["improved_summary"] or "No summary rewrite suggested.")
    for section,key in [("Experience bullet rewrites","experience_rewrites"),("Project description rewrites","project_rewrites")]:
        st.markdown(f"### {section}")
        for item in d[key]:
            with st.expander(item.get("section","Suggested rewrite")):
                st.write(item.get("original",""))
                st.markdown("**Suggested version**")
                st.write(item.get("improved",""))
                st.caption(item.get("rationale",""))
    st.markdown("### Action verbs")
    st.write(", ".join(d["action_verbs"]) or "No specific verbs suggested.")
    st.markdown("### Keyword suggestions")
    st.write(", ".join(d["keyword_suggestions"]) or "No additional keywords suggested.")

def show_interviews():
    d=st.session_state.get("analysis")
    if not d: st.info("Run an analysis to generate interview preparation."); return
    st.markdown('<div class="section-title">Interview preparation</div>',unsafe_allow_html=True)
    for heading,key in [("HR questions","hr_questions"),("Technical questions","technical_questions"),("Project-based questions","project_questions")]:
        st.markdown(f"### {heading}")
        for i,item in enumerate(d[key],1):
            with st.expander(f"{i}. {item.get('question','Interview question')}"):
                st.markdown("**Suggested answer direction**")
                st.write(item.get("suggested_answer",""))
    st.markdown("### Topics to prepare")
    for topic in d["preparation_topics"]: st.write(f"- {topic}")

def main():
    inject_css()
    with st.sidebar:
        st.markdown('<div class="brand">Resume<span>IQ</span></div><div class="tagline">Your Resume. Your Next Opportunity.</div>',unsafe_allow_html=True)
        page=st.radio("WORKSPACE",NAV_ITEMS,label_visibility="collapsed")
        st.divider()
        st.caption("AI-powered career toolkit")
        if st.button("↻  Reset workspace", use_container_width=True):
            for k in ["analysis","resume_text","resume_name","job_description"]: st.session_state.pop(k,None)
            st.rerun()
        st.caption("Your uploaded resume is not persisted by ResumeIQ.")
    if page=="Dashboard": show_dashboard()
    elif page=="Upload Resume": show_upload()
    elif page=="Resume Analysis": show_analysis()
    elif page=="Skills Gap": show_skills()
    elif page=="Resume Improvements": show_improvements()
    elif page=="Interview Preparation": show_interviews()
    d=st.session_state.get("analysis")
    if d:
        st.divider()
        pdf=build_pdf_report(d, st.session_state.get("resume_name","Resume"), st.session_state.get("job_description",""))
        st.download_button("Download PDF report",data=pdf,file_name=safe_filename(st.session_state.get("resume_name","resume").rsplit(".",1)[0])+"_ResumeIQ_Report.pdf",mime="application/pdf",use_container_width=True)

if __name__=="__main__":
    main()
