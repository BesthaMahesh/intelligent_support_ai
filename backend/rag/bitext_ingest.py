import os
from pathlib import Path
import pandas as pd
from typing import Dict, List, Any

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def generate_bitext_knowledge_documents():
    """
    Process the Hugging Face Bitext customer support dataset (27k rows)
    and generate structured enterprise policy playbooks and FAQ documents.
    """
    csv_path = BASE_DIR / "data" / "bitext_customer_support.csv"
    if not os.path.exists(csv_path):
        print(f"Dataset {csv_path} not found.")
        return 0

    df = pd.read_csv(csv_path)
    output_dir = BASE_DIR / "data" / "knowledge" / "bitext_enterprise"
    os.makedirs(output_dir, exist_ok=True)

    grouped = df.groupby(["category", "intent"])
    generated_count = 0

    for (cat, intent), group in grouped:
        cat_str = str(cat).strip().lower()
        intent_str = str(intent).strip().lower()
        intent_title = intent_str.replace("_", " ").title()
        doc_id = f"KB-BTX-{cat_str[:3].upper()}-{intent_str[:6].upper()}"

        # Sample representative instructions and high-quality responses
        sample_queries = group["instruction"].dropna().head(6).tolist()
        sample_responses = group["response"].dropna().head(3).tolist()

        # Build clean markdown enterprise playbook
        md_content = f"""# Enterprise Support Playbook: {intent_title}

**Document ID**: {doc_id}  
**Category**: {cat_str}  
**Intent**: {intent_str}  
**Version**: 1.0  
**Source**: Bitext Enterprise Customer Support Benchmark  

## Standard Operating Procedure & Policy
Our enterprise customer support platform resolves `{intent_title}` inquiries with standard operating resolution protocols.

### Resolution Directive:
{sample_responses[0] if sample_responses else 'Address customer inquiry directly according to standard enterprise guidelines.'}

## Frequently Asked Customer Variations
Customers commonly express this request in the following formats:
"""
        for q in sample_queries:
            md_content += f"- \"{q.strip()}\"\n"

        if len(sample_responses) > 1:
            md_content += "\n## Alternative Resolution Guidance:\n"
            for r in sample_responses[1:]:
                md_content += f"> {r.strip()}\n\n"

        file_name = f"{cat_str}_{intent_str}.md"
        file_path = output_dir / file_name
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        generated_count += 1

    print(f"Generated {generated_count} enterprise knowledge playbooks in {output_dir}")
    return generated_count

if __name__ == "__main__":
    generate_bitext_knowledge_documents()
