import baseURL from "../baseUrl";

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

async function getPrivacyNoticeByInstalledApplicationUuid(
  applicationUuid: string
) {
  let response = await fetch(
    baseURL + "privacy-notices/installed-application/" + applicationUuid,
    {
      method: "GET",
      credentials: "include",
    }
  );
  if (response.ok) {
    if (response.status === 204) {
      return null; //caso privacy notice arrivato ma vuoto (204 -> body vuoto)
    }
    const result = await response.json();
    return result;
  } else {
    //se c'è stato un errore, che è una situazione diversa rispetto a arrivato ma vuoto
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
    if (response.status === 404) {
      return null; //privacy notice non presente
    }
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
  getPrivacyNoticeByInstalledApplicationUuid
};
