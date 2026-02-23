import { getApiError } from "../apiError";
import baseURL from "../baseUrl";

async function getQuestionnaireQuestions() {
  let response = await fetch(baseURL + "questionnaires/template", {
    method: "GET",
    credentials: "include",
  });
  if (response.ok) {
    const questionnaireQuestions = await response.json();
    return questionnaireQuestions;
  } else {
    throw await getApiError(response);
  }
}

async function getQuestionnaireByManagedApplicationUuid(applicationUuid: string) {
  let response = await fetch(
    baseURL + "questionnaires/managed-application/" + applicationUuid,
    {
      method: "GET",
      credentials: "include",
    },
  );
  if (response.ok) {
    const result = await response.json();
    return result;
  } else {
    if (response.status === 404) {
      return null; //questionnaire not found for the given application UUID
    }
    throw await getApiError(response);
  }
}

async function submitQuestionnaireByManagedApplicationUuid(applicationUuid: string, content: any) {
  let response = await fetch(
    baseURL + "questionnaires/managed-application/" + applicationUuid,
    {
      method: "PUT",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(content),
    },
  );
  if (response.ok) {
    const result = await response.json();
    return result;
  } else {
    throw await getApiError(response);
  }
}

export {
  getQuestionnaireQuestions,
  getQuestionnaireByManagedApplicationUuid,
  submitQuestionnaireByManagedApplicationUuid,
};
