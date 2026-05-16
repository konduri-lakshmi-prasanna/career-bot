"""
evaluate.py — RAGAS evaluation pipeline for CareerBot.

Run this from the root careerbot/ folder:
    python evaluate.py

It loads your existing FAISS index, runs 10 test questions through
your RAG pipeline, and evaluates using RAGAS metrics.
Results are printed to the terminal and saved to ragas_results.csv.
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# ── Make sure core/ and services/ are importable ──────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

from services.pipeline import load_existing_knowledge_base
from core.chain import ask
from core.vectorstore import get_embeddings

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from core.chain import get_llm

# ── Load existing RAG pipeline ────────────────────────────────────────────────
print("⏳ Loading knowledge base...")
chain, retriever = load_existing_knowledge_base()

if chain is None or retriever is None:
    print("❌ No knowledge base found!")
    print("👉 Upload documents in the app and click 'Build Knowledge Base' first.")
    sys.exit(1)

print("✅ Knowledge base loaded successfully!")

# ── Test Dataset — 10 Career Guidance Questions ───────────────────────────────
# ground_truth = the correct expected answer
# Customize these questions based on your uploaded documents

test_dataset = [
    {
        "question": "What are the top career options for a student good at mathematics?",
        "ground_truth": "A student good at mathematics can pursue careers like Software Engineering, Data Science, Financial Analyst, Actuary, or Teaching Mathematics."
    },
    {
        "question": "What skills are needed to become a software engineer?",
        "ground_truth": "Skills needed include programming languages like Python and Java, data structures, algorithms, problem solving, and system design."
    },
    {
        "question": "What is the fresher salary for a data scientist in India?",
        "ground_truth": "A fresher data scientist in India earns between 40000 to 80000 rupees per month."
    },
    {
        "question": "Which Indian colleges offer computer science courses?",
        "ground_truth": "Top Indian colleges for computer science include IITs, NITs, BITS Pilani, VIT, SRM, and Manipal."
    },
    {
        "question": "What careers are suitable for a biology student?",
        "ground_truth": "Biology students can pursue careers in Medicine, Pharmacy, Biotechnology, Microbiology, or Nursing."
    },
    {
        "question": "What is the salary of a doctor in India?",
        "ground_truth": "A fresher MBBS doctor earns 40000 to 70000 rupees per month. A specialist earns 100000 to 300000 rupees per month."
    },
    {
        "question": "What skills are needed to become a graphic designer?",
        "ground_truth": "Skills needed include Photoshop, Illustrator, Figma, creativity, typography, and branding."
    },
    {
        "question": "What companies hire software engineers in India?",
        "ground_truth": "Top companies include TCS, Infosys, Wipro, Google, Microsoft, Amazon, and Flipkart."
    },
    {
        "question": "What course should I do to become a chartered accountant?",
        "ground_truth": "To become a CA you need to clear CA Foundation, CA Intermediate, and CA Final exams conducted by ICAI."
    },
    {
        "question": "What careers are good for a student interested in computers and creativity?",
        "ground_truth": "Careers include UI/UX Designer, Web Developer, Game Developer, Graphic Designer, or Digital Marketer."
    },
]

# ── Generate Answers + Contexts using your RAG pipeline ──────────────────────
print(f"\n⏳ Running {len(test_dataset)} questions through your RAG pipeline...")
print("   (This may take 1-2 minutes)\n")

questions     = []
answers       = []
contexts      = []
ground_truths = []

for i, item in enumerate(test_dataset, 1):
    question     = item["question"]
    ground_truth = item["ground_truth"]

    try:
        # Use your existing ask() function — exactly like the app does
        answer = ask(chain, retriever, question, messages=[])

        # Get retrieved context chunks
        if hasattr(retriever, "invoke"):
            retrieved_docs = retriever.invoke(question)
        else:
            retrieved_docs = retriever.get_relevant_documents(question)

        context = [doc.page_content for doc in retrieved_docs]

        questions.append(question)
        answers.append(answer)
        contexts.append(context)
        ground_truths.append(ground_truth)

        print(f"   ✅ Q{i}: {question[:60]}...")

    except Exception as e:
        print(f"   ⚠️  Q{i} failed: {e}")
        # Add empty entries so dataset stays aligned
        questions.append(question)
        answers.append("ERROR")
        contexts.append([""])
        ground_truths.append(ground_truth)

print(f"\n✅ Generated answers for {len(questions)} questions.")

# ── Build RAGAS Dataset ───────────────────────────────────────────────────────
dataset = Dataset.from_dict({
    "question"    : questions,
    "answer"      : answers,
    "contexts"    : contexts,
    "ground_truth": ground_truths,
})

# ── Wrap LLM and Embeddings for RAGAS ────────────────────────────────────────
print("\n⏳ Running RAGAS evaluation (this takes 2-3 minutes)...")

ragas_llm        = LangchainLLMWrapper(get_llm())
ragas_embeddings = LangchainEmbeddingsWrapper(get_embeddings())

# ── Run Evaluation ────────────────────────────────────────────────────────────
results = evaluate(
    dataset    = dataset,
    metrics    = [
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    ],
    llm        = ragas_llm,
    embeddings = ragas_embeddings,
)

# ── Print Results ─────────────────────────────────────────────────────────────
df = results.to_pandas()

print("\n" + "=" * 60)
print("📊 RAGAS EVALUATION RESULTS — CareerBot")
print("=" * 60)

print("\n📋 Per-Question Scores:")
print("-" * 60)
for _, row in df.iterrows():
    print(f"\nQ: {row['question'][:55]}...")
    print(f"   Faithfulness      : {row['faithfulness']:.2f}")
    print(f"   Answer Relevancy  : {row['answer_relevancy']:.2f}")
    print(f"   Context Precision : {row['context_precision']:.2f}")
    print(f"   Context Recall    : {row['context_recall']:.2f}")

print("\n" + "=" * 60)
print("📈 AVERAGE SCORES ACROSS ALL QUESTIONS:")
print("=" * 60)
print(f"   Faithfulness      : {df['faithfulness'].mean():.2f}  {'✅' if df['faithfulness'].mean() >= 0.7 else '⚠️'}")
print(f"   Answer Relevancy  : {df['answer_relevancy'].mean():.2f}  {'✅' if df['answer_relevancy'].mean() >= 0.7 else '⚠️'}")
print(f"   Context Precision : {df['context_precision'].mean():.2f}  {'✅' if df['context_precision'].mean() >= 0.7 else '⚠️'}")
print(f"   Context Recall    : {df['context_recall'].mean():.2f}  {'✅' if df['context_recall'].mean() >= 0.7 else '⚠️'}")
print("=" * 60)

print("\n📌 Score Guide:")
print("   0.8 - 1.0 → Excellent ✅")
print("   0.6 - 0.8 → Good 👍")
print("   0.4 - 0.6 → Average ⚠️")
print("   0.0 - 0.4 → Needs improvement ❌")

# ── Save to CSV ───────────────────────────────────────────────────────────────
output_file = "ragas_results.csv"
df.to_csv(output_file, index=False)
print(f"\n✅ Full results saved to: {output_file}")
print("   Open this file in Excel to view all scores in detail.")