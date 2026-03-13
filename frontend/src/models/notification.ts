import { RightType } from "./request";

enum NotificationType {
  CONSENT_GRANTED = "CONSENT_GRANTED",
  REQUEST_SUBMITTED = "REQUEST_SUBMITTED",
  REQUEST_ANSWERED = "REQUEST_ANSWERED",
  REQUEST_STATUS_UPDATED = "REQUEST_STATUS_UPDATED",
}


type NotificationPayload = {
  consent_uuid?: string;
  consent_content?: string;
  right_type?: RightType;
};


type NotificationItem = {
  id: number;
  type: string;
  sentAt: string;
  isRead: boolean;
  senderEmail?: string;
  applicationName?: string;
  applicationUuid?: string;
  requestUuid?: string;
  processingContextUuid?: string;
  payload?: NotificationPayload;
};


const getNotificationTitle = (notification: NotificationItem): string => {
  switch (notification.type) {
    case NotificationType.CONSENT_GRANTED:
      return `${notification.senderEmail ?? "A data subject"} granted consent${notification.payload?.consent_content ? ` "${notification.payload.consent_content}"` : ""}.`;
    case NotificationType.REQUEST_SUBMITTED:
      return `${notification.senderEmail ?? "A user"} submitted a rights request.`;
    case NotificationType.REQUEST_ANSWERED:
      return "A rights request has been answered.";
    case NotificationType.REQUEST_STATUS_UPDATED:
      return "A rights request status has been updated.";
    default:
      return "New notification.";
  }
};


const getNotificationTargetPath = (notification: NotificationItem): string => {
  if (notification.requestUuid) {
    return `/rights?request=${encodeURIComponent(notification.requestUuid)}`;
  }
  if (notification.applicationUuid) {
    return "/installed-apps";
  }
  return "/";
};


export { NotificationType, getNotificationTitle, getNotificationTargetPath };
export type { NotificationItem, NotificationPayload };
