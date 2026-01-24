import baseURL from "../baseUrl";

async function getQuestionnaireQuestions() {
  let response = await fetch(baseURL + "questions/questionnaire", {
    method: "GET",
    credentials: "include",
  });
  if (response.ok) {
    const questionnaireQuestions = await response.json();
    return questionnaireQuestions;
  } else {
    const errDetail = await response.json();
    if (errDetail?.message) {
      throw new Error(errDetail.message);
    }

    throw new Error("Something went wrong");
  }
}

async function getQuestionnaireByManagedApplicationUuid(
  applicationUuid: string,
) {
  let response = await fetch(
    baseURL + "questions/view-questionnaire/application/" + applicationUuid,
    {
      method: "GET",
      credentials: "include",
    },
  );
  if (response.ok) {
    const result = await response.json();
    return result;
  } else {
    const errDetail = await response.json();
    // Flask-smorest validation error
    if (errDetail?.errors) {
      const jsonErrors = errDetail.errors.json;
      if (jsonErrors && typeof jsonErrors === "object") {
        const msgs = Object.values(jsonErrors).flat().join("\n");
        throw new Error(msgs || "Validation error");
      }
      if (typeof errDetail.errors === "string") {
        throw new Error(errDetail.errors);
      }
    }
    if (errDetail?.message) {
      throw new Error(errDetail.message);
    }

    throw new Error("Something went wrong");
  }
}

async function submitQuestionnaireByManagedApplicationUuid(
  applicationUuid: string,
  content: any,
) {
  let response = await fetch(
    baseURL + "questions/submit-questionnaire/application/" + applicationUuid,
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
    const errDetail = await response.json();
    // Flask-smorest validation error
    if (errDetail?.errors) {
      const jsonErrors = errDetail.errors.json;
      if (jsonErrors && typeof jsonErrors === "object") {
        const msgs = Object.values(jsonErrors).flat().join("\n");
        throw new Error(msgs || "Validation error");
      }
      if (typeof errDetail.errors === "string") {
        throw new Error(errDetail.errors);
      }
    }
    if (errDetail?.message) {
      throw new Error(errDetail.message);
    }

    throw new Error("Something went wrong");
  }
}

export {
  getQuestionnaireQuestions,
  getQuestionnaireByManagedApplicationUuid,
  submitQuestionnaireByManagedApplicationUuid,
};
