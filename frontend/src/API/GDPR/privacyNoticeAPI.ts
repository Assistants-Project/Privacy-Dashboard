import { getApiError } from "../apiError";
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
    throw await getApiError(response);
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
    throw await getApiError(response);
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
    throw await getApiError(response);
  }
}

async function submitPrivacyNoticeByManagedApplicationUuid(
  applicationUuid: string,
  content: string
) {
  let response = await fetch(
    baseURL + "privacy-notices/managed-application/" + applicationUuid,
    {
      method: "PUT",
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
    throw await getApiError(response);
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
    throw await getApiError(response);
  }
}

export {
  getPrivacyNoticeTemplate,
  getPrivacyNoticeByManagedApplicationUuid,
  removePrivacyNoticeByManagedApplicationUuid,
  getPrivacyNoticeByInstalledApplicationUuid,
  submitPrivacyNoticeByManagedApplicationUuid
};
