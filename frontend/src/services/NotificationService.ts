import { getNotifications, getUnreadNotificationsCount, GetNotificationsOptions, markAllNotificationsAsRead, markNotificationAsRead } from "../API/Notification/notificationAPI";
import { NotificationItem } from "../models/notification";
import { RightType } from "../models/request";


type NotificationItemDto = {
  id: number;
  type: string;
  sent_at: string;
  is_read: boolean;
  sender_email?: string | null;
  application_name?: string | null;
  application_uuid?: string | null;
  request_uuid?: string | null;
  processing_context_uuid?: string | null;
  payload?: Record<string, unknown> | null;
};

const NOTIFICATIONS_CHANGED_EVENT = "notifications:changed";
const NOTIFICATIONS_OPTIMISTIC_UPDATE_EVENT = "notifications:optimistic-update";

type NotificationsOptimisticUpdateDetail = {
  kind: "single-read" | "all-read";
};

const emitNotificationsChanged = () => {
  window.dispatchEvent(new Event(NOTIFICATIONS_CHANGED_EVENT));
};

const emitNotificationsOptimisticUpdate = (detail: NotificationsOptimisticUpdateDetail) => {
  window.dispatchEvent(
    new CustomEvent<NotificationsOptimisticUpdateDetail>(
      NOTIFICATIONS_OPTIMISTIC_UPDATE_EVENT,
      { detail }
    )
  );
};


const normalizeOptionalString = (value: unknown): string | undefined =>
  typeof value === "string" && value.trim() !== "" ? value : undefined;

const normalizeRightType = (value: unknown): RightType | undefined => {
  if (typeof value !== "string") return undefined;
  return Object.values(RightType).includes(value as RightType) ? (value as RightType) : undefined;
};

const normalizeNotificationPayload = (value: unknown) => {
  if (!value || typeof value !== "object") return undefined;
  const payload = value as Record<string, unknown>;
  return {
    consent_uuid: normalizeOptionalString(payload.consent_uuid),
    consent_content: normalizeOptionalString(payload.consent_content),
    right_type: normalizeRightType(payload.right_type),
  };
};


const toNotificationItem = (dto: NotificationItemDto): NotificationItem => {
  return {
    id: dto.id,
    type: dto.type,
    sentAt: dto.sent_at,
    isRead: dto.is_read,
    senderEmail: normalizeOptionalString(dto.sender_email),
    applicationName: normalizeOptionalString(dto.application_name),
    applicationUuid: normalizeOptionalString(dto.application_uuid),
    requestUuid: normalizeOptionalString(dto.request_uuid),
    processingContextUuid: normalizeOptionalString(dto.processing_context_uuid),
    payload: normalizeNotificationPayload(dto.payload),
  };
};


export const fetchNotifications = async (options?: GetNotificationsOptions): Promise<NotificationItem[] | undefined> => {
  const payload = (await getNotifications(options)) as unknown;
  if (!Array.isArray(payload)) {
    console.warn("Unexpected notifications payload:", payload);
    return undefined;
  }
  return (payload as NotificationItemDto[]).map(toNotificationItem);
};

export const fetchUnreadNotificationsCount = async (): Promise<number> => {
  const payload = (await getUnreadNotificationsCount()) as unknown;
  if (typeof payload === "object" && payload !== null && typeof (payload as { unread_count?: unknown }).unread_count === "number") {
    return (payload as { unread_count: number }).unread_count;
  }
  console.warn("Unexpected unread notifications count payload:", payload);
  return 0;
};


export const handleMarkNotificationAsRead = async (notificationId: number): Promise<void> => {
  emitNotificationsOptimisticUpdate({ kind: "single-read" });
  try {
    await markNotificationAsRead(notificationId);
  } finally {
    emitNotificationsChanged();
  }
};


export const handleMarkAllNotificationsAsRead = async (): Promise<void> => {
  emitNotificationsOptimisticUpdate({ kind: "all-read" });
  try {
    await markAllNotificationsAsRead();
  } finally {
    emitNotificationsChanged();
  }
};


export { NOTIFICATIONS_CHANGED_EVENT, NOTIFICATIONS_OPTIMISTIC_UPDATE_EVENT };
