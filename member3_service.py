from typing import Any, Dict

from llm_client import GroqLLM
from tutor_agent import TutorAgent
from question_agent import QuestionAgent


class Member3Service:
    """
    Simple Member 3 service layer.

    The Orchestrator can call this class without knowing
    the internal implementation of the two agents.
    """

    def __init__(
        self,
        api_key=None,
        model=None,
        temperature=0.2,
    ):
        llm = GroqLLM(
            api_key=api_key,
            model=model,
            temperature=temperature,
        )

        self.tutor_agent = TutorAgent(llm)
        self.question_agent = QuestionAgent(llm)

    def run(self, processed_content: str) -> Dict[str, Any]:
        tutor_result = self.tutor_agent.process(processed_content)

        if tutor_result.get("status") != "success":
            return {
                "status": "error",
                "stage": "tutor_agent",
                "tutor": tutor_result,
                "questions": None,
            }

        question_result = self.question_agent.generate(processed_content)

        if question_result.get("status") != "success":
            return {
                "status": "error",
                "stage": "question_agent",
                "tutor": tutor_result,
                "questions": question_result,
            }

        return {
            "status": "success",
            "tutor": tutor_result,
            "questions": question_result,
        }
