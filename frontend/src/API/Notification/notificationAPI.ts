import { getApiError } from "../apiError";
import baseURL from "../baseUrl";


type GetNotificationsOptions = {
  onlyUnread?: boolean;
  limit?: number;
  offset?: number;
};


async function getNotifications(options?: GetNotificationsOptions) {
  const params = new URLSearchParams();
  if (options?.onlyUnread) {
    params.set("only_unread", "true");
  }
  if (typeof options?.limit === "number") {
    params.set("limit", String(options.limit));
  }
  if (typeof options?.offset === "number") {
    params.set("offset", String(options.offset));
  }
  const query = params.toString() ? `?${params.toString()}` : "";
  const response = await fetch(baseURL + `notifications/${query}`, {
    method: "GET",
    credentials: "include",
  });
  if (response.ok) {
    return await response.json();
  }

  throw await getApiError(response);
}

async function getUnreadNotificationsCount() {
  const response = await fetch(baseURL + "notifications/unread-count", {
    method: "GET",
    credentials: "include",
  });
  if (response.ok) {
    return await response.json();
  }

  throw await getApiError(response);
}


async function markNotificationAsRead(notificationId: number) {
  const response = await fetch(baseURL + `notifications/${encodeURIComponent(String(notificationId))}/read`, {
    method: "PUT",
    credentials: "include",
  });
  if (response.ok) {
    return;
  }

  throw await getApiError(response);
}


async function markAllNotificationsAsRead() {
  const response = await fetch(baseURL + "notifications/read-all", {
    method: "PUT",
    credentials: "include",
  });
  if (response.ok) {
    return;
  }

  throw await getApiError(response);
}


export { getNotifications, getUnreadNotificationsCount, markNotificationAsRead, markAllNotificationsAsRead };
export type { GetNotificationsOptions };
