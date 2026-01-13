import baseURL from "./baseUrl";

async function getManagedApplications() {
  let response = await fetch(baseURL + "applications/managed", {
    method: "GET",
    credentials: "include",
  });
  if (response.ok) {
    const applications = await response.json();
    return applications;
  } else {
    const errDetail = await response.json();
    if (errDetail?.message) {
      throw new Error(errDetail.message);
    }

    throw new Error("Something went wrong");
  }
}

async function getPiaTemplate() {
  let response = await fetch(baseURL + "applications/pia-template", {
    method: "GET",
    credentials: "include",
  });
  if (response.ok) {
    const piaTemplate = await response.json();
    return piaTemplate;
  } else {
    const errDetail = await response.json();
    if (errDetail?.message) {
      throw new Error(errDetail.message);
    }

    throw new Error("Something went wrong");
  }
}

async function submitPiaByManagedApplicationUuid(
  applicationUuid: string,
  content: any
) {
  let response = await fetch(
    baseURL +
      "applications/managed-application/" +
      applicationUuid +
      "/pia-template",
    {
      method: "PUT",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(content),
    }
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
  getManagedApplications,
  getPiaTemplate,
  submitPiaByManagedApplicationUuid,
};
