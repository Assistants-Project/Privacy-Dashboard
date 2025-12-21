from typing import List, TypedDict

from ..models import Question, QuestionType
from ..repositories import QuestionRepository


class QuestionResDict(TypedDict):
    question: Question
    choices: List[str]


class QuestionService:
    @staticmethod
    def get_all_choices(question: Question) -> List[str]:
        """Returns all possible choices for a given question.

        Args:
            question: The `Question` instance to retrieve choices for.
        Returns:
            A list of possible choices for the question.
        """

        green = question.green_choices.split(",") if question.green_choices else []
        orange = question.orange_choices.split(",") if question.orange_choices else []
        red = question.red_choices.split(",") if question.red_choices else []
        return green + orange + red

    @staticmethod
    def get_questionnaire() -> List[QuestionResDict]:
        """Returns a list of questions representing all the questions in the questionnaire each `Application` can be subject to.

        Returns:
            A list of dictionaries each containing the question instance and the list of possible choices, or an empty list if none are found.
        """

        iterator = QuestionRepository.get_questions_by_type(QuestionType.QUESTIONNAIRE)
        return [
            {
                "question": question,
                "choices": QuestionService.get_all_choices(question),
            }
            for question in iterator
        ]
