from typing import List, TypedDict
from uuid import UUID

from ..exceptions import (
    ApplicationNotFoundException,
    InvalidAnswerContentException,
    MissingRequiredAnswerException,
    QuestionnaireNotFoundException,
    QuestionnaireSubmissionException,
    QuestionNotFoundException,
)
from ..models import Evaluation, Question, QuestionApplication, QuestionType
from ..repositories import ApplicationRepository, QuestionRepository


class QuestionResDict(TypedDict):
    question: Question
    choices: List[str]


class AnswerReqDict(TypedDict):
    question_uuid: UUID
    answer_content: str


class QuestionAnsweredDict(TypedDict):
    question_id: int
    answer_content: str
    evaluation: Evaluation | None


class GivenAnswerDict(TypedDict):
    question: Question
    answer: QuestionApplication


class QuestionnaireResDict(TypedDict):
    application_evaluation: Evaluation | None
    given_answers: List[GivenAnswerDict]


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
    def get_questionnaire_questions() -> List[QuestionResDict]:
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

    @staticmethod
    def submit_questionnaire_by_managed_application_uuid(
        current_user_id: int,
        application_uuid: UUID,
        answers: List[AnswerReqDict],
        check_required: bool,
    ) -> QuestionnaireResDict:
        """Submits a questionnaire for an `Application` if the `Application` with the given `UUID`
        exists and is managed by the given `DATA_CONTROLLER` or `DPO` user.

        Args:
            current_user_id: The ID of the user with role `DATA_CONTROLLER` or `DPO` who manages the application.
            application_uuid: The UUID of the managed application.
            answers: A list of dictionaries each containing an answer provided for the questionnaire, each with keys `question_uuid` and `answer_content`.
            check_required: A boolean indicating whether to check for required questions, should be set to True if all required questions must be answered.

        Returns:
            A dictionary containing the result of the submission, with keys `application_evaluation` and `given_answers`, where `application_evaluation` is the
            overall evaluation of the application based on the questionnaire answers, and `given_answers` is a list of dictionaries each containing a `question` and the corresponding `answer`.
        """

        application = (
            ApplicationRepository.get_application_by_user_id_and_application_uuid(
                current_user_id, application_uuid
            )
        )
        if not application:
            raise ApplicationNotFoundException(
                f"Application with uuid {application_uuid} not found among the managed applications!"
            )
        questions_answered: List[QuestionAnsweredDict] = []
        for answer in answers:
            question = QuestionRepository.get_question_by_uuid(answer["question_uuid"])
            if not question:
                raise QuestionNotFoundException(
                    f"Question with uuid {answer['question_uuid']} not found!"
                )
            green = question.green_choices.split(",") if question.green_choices else []
            orange = (
                question.orange_choices.split(",") if question.orange_choices else []
            )
            red = question.red_choices.split(",") if question.red_choices else []
            all_choices = green + orange + red
            evaluation = None
            if all_choices:
                if answer["answer_content"] not in all_choices:
                    raise InvalidAnswerContentException(
                        f"Invalid answer content '{answer['answer_content']}' for question with uuid {answer['question_uuid']}!"
                    )
                if answer["answer_content"] in green:
                    evaluation = Evaluation.GREEN
                elif answer["answer_content"] in orange:
                    evaluation = Evaluation.ORANGE
                elif answer["answer_content"] in red:
                    evaluation = Evaluation.RED
            questions_answered.append(
                QuestionAnsweredDict(
                    question_id=question.id,
                    answer_content=answer["answer_content"],
                    evaluation=evaluation,
                )
            )
        if check_required and len(questions_answered) < 25:
            # 25 is the amount of questions in initial_data.py not marked as optional
            raise MissingRequiredAnswerException(
                "Not all required questions have been answered!"
            )
        try:
            QuestionRepository.submit_questionnaire_by_application_uuid(
                application.id, questions_answered
            )
            questionnaire_summary_iterator = (
                QuestionRepository.get_questionnaire_summary_by_application_id(
                    application.id
                )
            )
            given_answers: List[GivenAnswerDict] = [
                GivenAnswerDict(question=question, answer=question_application)
                for question_application, question in questionnaire_summary_iterator
            ]
            answers_evaluation = [
                item["answer"].evaluation
                for item in given_answers
                if item["answer"].evaluation is not None
            ]
            if answers_evaluation:
                if Evaluation.RED in answers_evaluation:
                    application_evaluation = Evaluation.RED
                elif Evaluation.ORANGE in answers_evaluation:
                    application_evaluation = Evaluation.ORANGE
                else:
                    application_evaluation = Evaluation.GREEN
                ApplicationRepository.update_application_evaluation(
                    application.id, application_evaluation
                )
            else:
                application_evaluation = None
            return QuestionnaireResDict(
                application_evaluation=ApplicationRepository.get_application_by_user_id_and_application_uuid(
                    current_user_id, application_uuid
                ).evaluation,
                given_answers=given_answers,
            )
        except Exception:
            raise QuestionnaireSubmissionException(
                "An error occurred while submitting the questionnaire!"
            )

    @staticmethod
    def view_questionnaire_by_managed_application_uuid(
        current_user_id: int,
        application_uuid: UUID,
    ) -> QuestionnaireResDict:
        """Retrieves a summary of the submitted questionnaire for an `Application` if the `Application` with the given `UUID`
        exists and is managed by the given `DATA_CONTROLLER` or `DPO` user.

        Args:
            current_user_id: The ID of the user with role `DATA_CONTROLLER` or `DPO` who manages the application.
            application_uuid: The UUID of the managed application.

        Returns:
            A dictionary containing the result of the view request, with keys `application_evaluation` and `given_answers`, where `application_evaluation` is the
            overall evaluation of the application based on the questionnaire answers, and `given_answers` is a list of dictionaries each containing a `question` and the corresponding `answer`.
        """

        application = (
            ApplicationRepository.get_application_by_user_id_and_application_uuid(
                current_user_id, application_uuid
            )
        )
        if not application:
            raise ApplicationNotFoundException(
                f"Application with uuid {application_uuid} not found among the managed applications!"
            )
        questionnaire_summary_iterator = (
            QuestionRepository.get_questionnaire_summary_by_application_id(
                application.id
            )
        )
        given_answers: List[GivenAnswerDict] = [
            GivenAnswerDict(question=question, answer=question_application)
            for question_application, question in questionnaire_summary_iterator
        ]
        if not given_answers:
            raise QuestionnaireNotFoundException(
                f"No questionnaire was submitted for application with uuid {application_uuid}!"
            )
        return QuestionnaireResDict(
            application_evaluation=application.evaluation, given_answers=given_answers
        )
