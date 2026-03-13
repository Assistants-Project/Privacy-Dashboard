import {
  getQuestionnaireByManagedApplicationUuid,
  getQuestionnaireQuestions,
  submitQuestionnaireByManagedApplicationUuid,
} from "../API/GDPR/questionAPI";
import { Question, QuestionnaireModel } from "../models/question";

const handleGetQuestionnaireByApplication = async (
  applicationUuid: string,
): Promise<QuestionnaireModel | null> => {
  try {
    const result =
      await getQuestionnaireByManagedApplicationUuid(applicationUuid);
    if (!result) return null;
    console.log("Questionnaire retrieved successfully");
    return new QuestionnaireModel(
      applicationUuid,
      result.given_answers?.map(
        (q: any) =>
          ({
            uuid: q.question.uuid,
            content: q.question.content,
            additionalInformation: q.question.additional_information,
            answerContent: q.answer.answer_content,
            evaluation: q.answer.evaluation,
          }) as Question,
      ),
      result.application_evaluation,
      result.questionnaire_summary,
    );
  } catch (err) {
    throw err;
  }
};

const fetchQuestionnaire = async (): Promise<Question[] | null> => {
  try {
    const result = await getQuestionnaireQuestions();
    console.log("Questionnaire template retrieved successfully");
    if (!Array.isArray(result) || result.length === 0) {
      return null
    }
    return result.map(
      (q: any) =>
        ({
          uuid: q.question.uuid,
          content: q.question.content,
          additionalInformation: q.question.additional_information,
          choices: q.choices,
        }) as Question,
    );
  } catch (err) {
    throw err;
  }
};

const submitQuestionnaire = async (applicationUuid: string, content: any) => {
  try {
    const result = await submitQuestionnaireByManagedApplicationUuid(
      applicationUuid,
      content,
    );
    console.log("Questionnaire submitted successfully");
    return result;
  } catch (err) {
    console.error("Error submitting questionnaire:", err);
    alert(`Error submitting questionnaire: ${err}`);
  }
};

export {
  handleGetQuestionnaireByApplication,
  fetchQuestionnaire,
  submitQuestionnaire,
};
