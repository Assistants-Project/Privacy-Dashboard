import baseURL from "./baseUrl";

async function getPrivacyNoticeTemplate() {
  let response = await fetch(baseURL + "privacy-notices/template", {
    method: "GET",
    credentials: "include",
  });
  if (response.ok) {
    const result = await response.json();
    return result;
  } else {
    const errDetail = await response.json();
    if (errDetail?.message) {
      throw new Error(errDetail.message);
    }

    throw new Error("Something went wrong");
  }
}

async function getPrivacyNoticeByManagedApplicationUuid(
  applicationUuid: string
) {
  let response = await fetch(
    baseURL + "privacy-notices/managed-application/" + applicationUuid,
    {
      method: "GET",
      credentials: "include",
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

async function writePrivacyNoticeByManagedApplicationUuid(
  applicationUuid: string,
  content: string
) {
  let response = await fetch(
    baseURL + "privacy-notices/managed-application/" + applicationUuid,
    {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ content: content }),
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

async function removePrivacyNoticeByManagedApplicationUuid(
  applicationUuid: string
) {
  let response = await fetch(
    baseURL + "privacy-notices/managed-application/" + applicationUuid,
    {
      method: "DELETE",
      credentials: "include",
    }
  );
  if (response.ok) {
    return;
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
  getPrivacyNoticeTemplate,
  getPrivacyNoticeByManagedApplicationUuid,
  writePrivacyNoticeByManagedApplicationUuid,
  removePrivacyNoticeByManagedApplicationUuid,
};
