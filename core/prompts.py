"""
prompts.py — All prompt templates used by CareerBot.

Contains:
  • RAG_PROMPT — the core retrieval-augmented generation system prompt
  • Feature-specific prompt builders for each tab / quick action
"""


# ── Core RAG System Prompt ───────────────────────────────────────────────────

RAG_PROMPT = """You are CareerBot — an AI career guidance assistant.

You MUST answer ONLY using the document excerpts provided below in the CONTEXT section.
Do NOT use your own training knowledge. Do NOT guess or fabricate any information.

RULES:
- If CONTEXT is empty or says "[NO DOCUMENTS]", reply: "📂 No relevant information found in your uploaded documents. Please upload documents and rebuild the knowledge base."
- If CONTEXT exists but doesn't have enough info for the question, say so honestly and suggest uploading more documents.
- Quote or paraphrase directly from the CONTEXT. Cite which document section you are referencing.
- Use structured formatting with markdown headers and bullet points.

--- CONTEXT FROM UPLOADED DOCUMENTS ---
{context}
--- END CONTEXT ---

User Question: {question}

Answer (based strictly on the above context):"""


# ── Feature Prompt Builders ──────────────────────────────────────────────────

def resume_analysis_prompt() -> str:
    return """Analyse ONLY the resume content from the uploaded documents and provide:

1. 📊 Overall Resume Score out of 100

2. ✅ Strong Points (what is good in this resume)

3. ❌ Weak Points (what is missing or needs improvement)

4. 💡 Specific Improvement Suggestions:
   - Give exact lines from the resume that need to be rewritten
   - Show the improved version of each line

5. 🎯 Projected score after improvements

6. 📋 Missing Sections (e.g. LinkedIn, GitHub, achievements, metrics, summary)

IMPORTANT: Base everything ONLY on the actual content of the uploaded resume. Do not use outside knowledge."""


def interview_prep_prompt(interview_type: str, difficulty: str) -> str:
    return f"""Read ONLY the uploaded resume document and generate {interview_type} questions at {difficulty} for this specific candidate.

Generate exactly:

1. 🔧 5 Technical Questions
   - Directly based on the skills, projects, and technologies in THEIR uploaded resume
   - Provide the ideal answer for each

2. 🤝 5 HR / Behavioural Questions
   - Based on their specific experience and background from the document
   - Provide the ideal STAR-format answer for each

3. ⭐ 3 Deep-Dive Tricky Questions
   - Questions that test deep understanding of their own listed experience
   - Provide the ideal answer for each

For every question, mention which part of the uploaded document it comes from.
IMPORTANT: Only use information from the uploaded documents. Do not generate generic questions."""


def career_roadmap_prompt(target_role: str, timeframe: str) -> str:
    dream_job_text = (
        f"Their stated dream job is: {target_role}."
        if target_role
        else "Suggest the best career path based ONLY on their uploaded profile."
    )

    return f"""Read ONLY the uploaded document (resume or marksheet) and generate a personalised career roadmap.

{dream_job_text}
Timeframe: {timeframe}

Structure your roadmap as follows (use ONLY information from the uploaded documents):

1. 📊 Current Profile Assessment
   - Strongest skills and subjects from the document
   - Current level based on uploaded content

2. 🗺️ Month-by-Month / Quarter-by-Quarter Roadmap for {timeframe}
   - Specific tasks for each period based on their profile

3. 📚 Specific Courses and Certifications relevant to their background

4. 🏫 Higher Education Options relevant to their field

5. 💰 Salary Progression Forecast (in ₹/month) based on their domain

6. 🏢 Target Companies (Tier-wise) relevant to their skills

7. ⚠️ Skill Gaps to Fill based on uploaded document content

IMPORTANT: Base the entire roadmap ONLY on the uploaded document content. Do not use outside knowledge."""


def job_match_prompt(job_description: str) -> str:
    return f"""Compare ONLY my uploaded resume against this job description and give a detailed match analysis.

JOB DESCRIPTION:
{job_description}

Provide (using ONLY my uploaded resume content):

1. 🎯 Overall Match Score (X / 100) based on skills found in my resume vs JD requirements

2. ✅ Skills I Have That Match the JD
   - List each matching skill found in my uploaded resume

3. ❌ Skills I Am Missing
   - List each required JD skill NOT found in my uploaded resume
   - Mark each as High / Medium / Low priority

4. 📚 How to Fill the Skill Gaps
   - Specific course or certification for each missing skill
   - Estimated time to learn each

5. 💡 How to Rewrite My Resume for This Specific Job
   - Exact lines from my uploaded resume to change or strengthen
   - Keywords from the JD to incorporate

6. 🏆 Final Verdict
   - Should I apply now or prepare more?
   - If prepare — give realistic timeline

IMPORTANT: Only use content from the uploaded resume. Do not guess or fabricate skills."""
