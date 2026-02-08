import {
  getQuestionnaireByManagedApplicationUuid,
  getQuestionnaireQuestions,
  submitQuestionnaireByManagedApplicationUuid,
} from "../API/GDPR/questionAPI";
import { Question, Questionnaire } from "../models/question";

const handleGetQuestionnaireByApplication = async (
  applicationUuid: string,
): Promise<Questionnaire | null> => {
  try {
    const result =
      await getQuestionnaireByManagedApplicationUuid(applicationUuid);
    if (!result) return null;
    console.log("Questionnaire retrieved successfully");
    return new Questionnaire(
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

const fetchQuestionnaire = async (): Promise<Question[] | undefined> => {
  try {
    const result = await getQuestionnaireQuestions();
    console.log("Questionnaire template retrieved successfully");
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
    console.error("Error getting questionnaire template:", err);
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
