import baseURL from "../baseUrl";

// --- Services & Triggers/Actions ---

async function getTriggerServices(homeUuid: string) {
  const response = await fetch(
    `${baseURL}sifis/homes/${homeUuid}/trigger-services`,
    {
      method: "GET",
      credentials: "include",
    },
  );
  if (!response.ok) throw await _handleError(response);
  return await response.json();
}

async function getTriggers(homeUuid: string, serviceId: string) {
  const response = await fetch(
    `${baseURL}sifis/homes/${homeUuid}/trigger-services/${serviceId}/triggers`,
    {
      method: "GET",
      credentials: "include",
    },
  );
  if (!response.ok) throw await _handleError(response);
  return await response.json();
}

async function getTriggerDetails(
  homeUuid: string,
  serviceId: string,
  triggerId: string,
) {
  const response = await fetch(
    `${baseURL}sifis/homes/${homeUuid}/trigger-services/${serviceId}/triggers/${triggerId}/details`,
    {
      method: "GET",
      credentials: "include",
    },
  );
  if (!response.ok) throw await _handleError(response);
  return await response.json();
}

async function getActionServices(homeUuid: string) {
  const response = await fetch(
    `${baseURL}sifis/homes/${homeUuid}/action-services`,
    {
      method: "GET",
      credentials: "include",
    },
  );
  if (!response.ok) throw await _handleError(response);
  return await response.json();
}

async function getActions(homeUuid: string, serviceId: string) {
  const response = await fetch(
    `${baseURL}sifis/homes/${homeUuid}/action-services/${serviceId}/actions`,
    {
      method: "GET",
      credentials: "include",
    },
  );
  if (!response.ok) throw await _handleError(response);
  return await response.json();
}

async function getActionDetails(
  homeUuid: string,
  serviceId: string,
  actionId: string,
) {
  const response = await fetch(
    `${baseURL}sifis/homes/${homeUuid}/action-services/${serviceId}/actions/${actionId}/details`,
    {
      method: "GET",
      credentials: "include",
    },
  );
  if (!response.ok) throw await _handleError(response);
  return await response.json();
}

// --- Rules ---

async function getRules(homeUuid: string) {
  const response = await fetch(`${baseURL}sifis/homes/${homeUuid}/rules`, {
    method: "GET",
    credentials: "include",
  });
  if (!response.ok) throw await _handleError(response);
  return await response.json();
}

async function saveRule(homeUuid: string, rule: any) {
  const response = await fetch(`${baseURL}sifis/homes/${homeUuid}/rules`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(rule),
  });
  if (!response.ok) throw await _handleError(response);
  return await response.json();
}

async function deleteRule(homeUuid: string, ruleId: number) {
  const response = await fetch(
    `${baseURL}sifis/homes/${homeUuid}/rules/${ruleId}`,
    {
      method: "DELETE",
      credentials: "include",
    },
  );
  if (!response.ok) throw await _handleError(response);
  return await response.json();
}

async function downloadRule(homeUuid: string, ruleId: number) {
  const response = await fetch(
    `${baseURL}sifis/homes/${homeUuid}/rules/${ruleId}/download`,
    {
      method: "POST",
      credentials: "include",
    },
  );
  if (!response.ok) throw await _handleError(response);

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;

  const contentDisposition = response.headers.get("Content-Disposition");
  let filename = `rule_${ruleId}.xml`;
  if (contentDisposition) {
    const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
    if (filenameMatch && filenameMatch.length === 2)
      filename = filenameMatch[1];
  }

  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);

  return true;
}

async function checkRule(homeUuid: string, ruleId: number) {
  const response = await fetch(
    `${baseURL}sifis/homes/${homeUuid}/rules/${ruleId}/check`,
    {
      method: "GET",
      credentials: "include",
    },
  );
  if (!response.ok) throw await _handleError(response);
  return await response.json();
}

// --- Helper ---

async function _handleError(response: Response) {
  try {
    const errDetail = await response.json();
    if (errDetail?.error) return new Error(errDetail.error);
    if (errDetail?.message) return new Error(errDetail.message);
  } catch {}
  return new Error("Something went wrong");
}

export {
  getTriggerServices,
  getTriggers,
  getTriggerDetails,
  getActionServices,
  getActions,
  getActionDetails,
  getRules,
  saveRule,
  deleteRule,
  downloadRule,
  checkRule,
};
