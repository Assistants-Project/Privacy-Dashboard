import baseURL from "../baseUrl";

async function getMessagesByUserUuid(userUuid: string) {
  let response = await fetch(baseURL + "messages/history/" + userUuid, {
    method: "GET",
    credentials: "include",
  });
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

async function sendMessage(
  receiverUuid: string,
  content: string,
  attachment?: string,
) {
  let response = await fetch(baseURL + "messages/send", {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      content: content,
      receiver_uuid: receiverUuid,
      attachment: attachment,
    }),
  });
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

export { getMessagesByUserUuid, sendMessage };
