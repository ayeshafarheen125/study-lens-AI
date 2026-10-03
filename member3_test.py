"""
Standalone integration test for Member 3.

This test demonstrates the Member 2 → Member 3 workflow.

Member 2 Document Agent
        ↓
Member 3 Tutor Agent
        +
Member 3 Question Agent

Usage:
    python member3_test.py path/to/file.pdf
"""

import json
import sys

from document_agent import DocumentProcessingAgent
from member3_service import Member3Service


def main():
    if len(sys.argv) < 2:
        print("Usage: python member3_test.py <path_to_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]

    print("1. Running Member 2 Document Agent...")
    document_agent = DocumentProcessingAgent()

    document_result = document_agent.process_document(pdf_path)

    if document_result["status"] != "success":
        print("Document processing failed:")
        print(document_result.get("message"))
        sys.exit(1)

    print(f"   Pages: {document_result['total_pages']}")
    print(f"   Characters: {document_result['total_characters']}")
    print(f"   Chunks: {document_result['total_chunks']}")

    print("\n2. Running Member 3 Tutor + Question Agents...")

    service = Member3Service(temperature=0.2)
    member3_result = service.run(document_result["full_text"])

    if member3_result["status"] != "success":
        print("Member 3 failed:")
        print(json.dumps(member3_result, indent=2))
        sys.exit(1)

    print("\n=== TUTOR OUTPUT ===")
    print(member3_result["tutor"]["summary"])

    print("\n=== KEY POINTS ===")
    for point in member3_result["tutor"]["key_points"]:
        print(f"- {point}")

    print("\n=== GENERATED MCQS ===")
    for i, mcq in enumerate(member3_result["questions"]["mcqs"], 1):
        print(f"{i}. {mcq['question']}")
        for option in mcq["options"]:
            print(f"   - {option}")
        print(f"   Answer: {mcq['correct_answer']}")

    with open("member3_output.json", "w", encoding="utf-8") as file:
        json.dump(member3_result, file, indent=2, ensure_ascii=False)

    print("\nFull output saved to member3_output.json")


if __name__ == "__main__":
    main()
