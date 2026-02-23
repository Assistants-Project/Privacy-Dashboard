import baseURL from "../baseUrl";
import { getApiError } from "../apiError";

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

async function getInstalledApplications(smartHomeUuid: string) {
  let response = await fetch(baseURL + `applications/home/${encodeURIComponent(smartHomeUuid)}`, {
    method: "GET",
    credentials: "include",
  });
  if (response.ok) {
    const applications = await response.json();
    return applications;
  }

  throw await getApiError(response);

}

async function createApplication(name: string,description?: string,availableConsents?: string[]): Promise<unknown> {
  
  const payload: {
    name: string;
    description?: string;
    available_consents?: string[];
  } = { name };

  if (description !== undefined) {
    payload.description = description;
  }
  if (availableConsents && availableConsents.length > 0) {
    payload.available_consents = availableConsents;
  }

  const response = await fetch(baseURL + "applications", {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (response.status === 201) {
    return await response.json();
  }

  throw await getApiError(response);
}

async function assignDpoToManagedApplication(applicationUuid: string, dpoEmail: string): Promise<boolean> {
  const response = await fetch(
    baseURL +
      `applications/managed/${encodeURIComponent(applicationUuid)}/dpo/${encodeURIComponent(dpoEmail)}`,
    {
      method: "PUT",
      credentials: "include",
    },
  );

  if (response.status === 201) return true;
  if (response.status === 204) return false;

  throw await getApiError(response);
}

async function addDataControllerManagerToManagedApplication(applicationUuid: string, userEmail: string): Promise<boolean> {
  const response = await fetch(
    baseURL +
      `applications/managed/${encodeURIComponent(applicationUuid)}/managers/${encodeURIComponent(userEmail)}`,
    {
      method: "PUT",
      credentials: "include",
    },
  );

  if (response.status === 201) return true;
  if (response.status === 204) return false;

  throw await getApiError(response);
}

async function removeDataControllerManagerFromManagedApplication(applicationUuid: string, userEmail: string): Promise<void> {
  const response = await fetch(
    baseURL +
      `applications/managed/${encodeURIComponent(applicationUuid)}/managers/${encodeURIComponent(userEmail)}`,
    {
      method: "DELETE",
      credentials: "include",
    },
  );

  if (response.status === 204) {
    return;
  }

  throw await getApiError(response);
}

async function refreshApplications() {
  let response = await fetch(baseURL + "applications/refresh", { method: "POST", credentials: "include" });
  if (response.ok) {
    return true;
  }

  throw await getApiError(response);
}

async function getPiaTemplate() {
  let response = await fetch(baseURL + "privacy-impact-assessments/template", {
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

async function getPiaByManagedApplicationUuid(applicationUuid: string) {
  let response = await fetch(
    baseURL + "privacy-impact-assessments/managed/" + applicationUuid,
    {
      method: "GET",
      credentials: "include",
    }
  );
  if (response.status === 204 || response.status === 404) {
    return null;
  }
  if (response.ok) {
    const result = await response.json();
    return result;
  } else {
    throw await getApiError(response);
  }
}

async function submitPiaByManagedApplicationUuid(applicationUuid: string, content: any) {
  let response = await fetch(
    baseURL + "privacy-impact-assessments/managed/" + applicationUuid,
    {
      method: "PUT",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ content }),
    }
  );
  if (!response.ok) {
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

async function removePiaByManagedApplicationUuid(applicationUuid: string) {
  let response = await fetch(
    baseURL + "privacy-impact-assessments/managed/" + applicationUuid,
    {
      method: "DELETE",
      credentials: "include",
    }
  );
  if (!response.ok) {
    throw await getApiError(response);
  }
}

export {
  getManagedApplications,
  getPiaTemplate,
  getPiaByManagedApplicationUuid,
  submitPiaByManagedApplicationUuid,
  removePiaByManagedApplicationUuid,
  getInstalledApplications,
  createApplication,
  assignDpoToManagedApplication,
  addDataControllerManagerToManagedApplication,
  removeDataControllerManagerFromManagedApplication,
  refreshApplications,
};
