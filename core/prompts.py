"""
prompts.py — All prompt templates used by CareerBot.

Changes vs original:
  • RAG_PROMPT now has a {history} slot injected before the user question.
    When history is empty the section header is still rendered but blank —
    the LLM ignores it gracefully.
"""


# ── Core RAG System Prompt ────────────────────────────────────────────────────

RAG_PROMPT = """You are CareerBot — an AI career guidance assistant.

You have access to two sources of information inside the CONTEXT section below:
1. UPLOADED DOCUMENTS (marked with source: <filename>): Personal context containing the user's resume, marksheet, or certificates.
2. WEB SEARCH RESULTS (marked with source: web_search): General/external context from the web (e.g. current job listings, skill definitions, salaries, company info).

RULES:
- You MUST answer the user's question ONLY using the provided CONTEXT. Do NOT guess or use outside training knowledge not present in the CONTEXT.
- If CONTEXT is empty or does not contain relevant information, reply: "📂 No relevant information found in your uploaded documents or web search."
- Prioritize UPLOADED DOCUMENTS for personal queries (e.g. "what is my GPA?", "summarize my projects").
- Use WEB SEARCH RESULTS to provide accurate, up-to-date answers for general or external queries (e.g. "what is the salary of a React developer?", "how to learn Docker?").
- Cite your sources clearly:
  - If from an uploaded document: cite the document name (e.g. "According to your [resume.pdf]...").
  - If from a web search: cite the website title and provide the URL if available in the context metadata (e.g. "According to [website name](url)...").
- Use structured formatting with markdown headers and bullet points.
- If the user refers to something mentioned earlier, use the CONVERSATION HISTORY below to resolve the reference.

--- CONVERSATION HISTORY (last few turns) ---
{history}
--- END HISTORY ---

--- CONTEXT (Documents and Web Search) ---
{context}
--- END CONTEXT ---

User Question: {question}

Answer (based strictly on the above context):"""


# ── Feature Prompt Builders ───────────────────────────────────────────────────

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