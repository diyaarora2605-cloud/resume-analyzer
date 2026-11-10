from typing import Any

SCORE_KEYS = ["ats_readability","job_match","technical_skills","soft_skills","experience_relevance","education_relevance","keyword_optimization","structure_formatting"]

def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list): return []
    return [str(x).strip()[:500] for x in value if str(x).strip()][:60]

def _rewrite_list(value: Any) -> list[dict]:
    if not isinstance(value,list): return []
    out=[]
    for item in value[:20]:
        if isinstance(item,dict):
            out.append({k:str(item.get(k,""))[:2000] for k in ["section","original","improved","rationale"]})
    return out

def _question_list(value: Any) -> list[dict]:
    if not isinstance(value,list): return []
    out=[]
    for item in value[:15]:
        if isinstance(item,dict):
            out.append({"question":str(item.get("question",""))[:1000],"suggested_answer":str(item.get("suggested_answer",""))[:3000]})
    return out

def validate_analysis(data: dict) -> dict:
    if not isinstance(data,dict): raise ValueError("The AI response was not a JSON object.")
    scores=data.get("scores",{})
    if not isinstance(scores,dict): scores={}
    clean_scores={}
    for key in SCORE_KEYS:
        try: value=float(scores.get(key,0))
        except (TypeError,ValueError): value=0
        clean_scores[key]=max(0,min(100,round(value)))
    explanations=data.get("score_explanations",{})
    if not isinstance(explanations,dict): explanations={}
    missing=data.get("missing_technical_skills",[])
    if not isinstance(missing,list): missing=[]
    clean_missing=[]
    for item in missing[:40]:
        if isinstance(item,dict):
            priority=str(item.get("priority","Medium")).title()
            if priority not in ("High","Medium","Low"): priority="Medium"
            clean_missing.append({"skill":str(item.get("skill",""))[:150],"priority":priority,"reason":str(item.get("reason",""))[:600]})
    result={
      "candidate_name":str(data.get("candidate_name","Not identified"))[:150],
      "target_role":str(data.get("target_role","Not identified"))[:200],
      "executive_summary":str(data.get("executive_summary",""))[:3000],
      "scores":clean_scores,
      "score_explanations":{k:str(explanations.get(k,""))[:1000] for k in SCORE_KEYS},
      "skills_present":_string_list(data.get("skills_present")),
      "missing_technical_skills":clean_missing,
      "missing_soft_skills":_string_list(data.get("missing_soft_skills")),
      "skills_to_improve":_string_list(data.get("skills_to_improve")),
      "important_keywords":_string_list(data.get("important_keywords")),
      "improved_summary":str(data.get("improved_summary",""))[:4000],
      "experience_rewrites":_rewrite_list(data.get("experience_rewrites")),
      "project_rewrites":_rewrite_list(data.get("project_rewrites")),
      "action_verbs":_string_list(data.get("action_verbs")),
      "keyword_suggestions":_string_list(data.get("keyword_suggestions")),
      "hr_questions":_question_list(data.get("hr_questions")),
      "technical_questions":_question_list(data.get("technical_questions")),
      "project_questions":_question_list(data.get("project_questions")),
      "preparation_topics":_string_list(data.get("preparation_topics"))
    }
    if not result["executive_summary"]: raise ValueError("The AI response is missing its executive summary.")
    return result

def calculate_overall_score(scores: dict) -> int:
    keys=["ats_readability","job_match","technical_skills","soft_skills","experience_relevance","education_relevance","keyword_optimization","structure_formatting"]
    weights=[.10,.25,.18,.08,.15,.08,.10,.06]
    return round(sum(float(scores.get(k,0))*w for k,w in zip(keys,weights)))
