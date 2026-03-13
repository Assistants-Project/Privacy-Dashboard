import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { useAuth } from "../contexts/AuthContext";
import { NotificationItem } from "../models/notification";
import { fetchNotifications, handleMarkAllNotificationsAsRead, handleMarkNotificationAsRead } from "../services/NotificationService";


type UseNotificationsResult = {
  notifications: NotificationItem[] | undefined;
  unreadCount: number;
  loadingNotifications: boolean;
  errorNotifications: string | undefined;
  loadNotifications: (options?: { force?: boolean; silent?: boolean }) => Promise<void>;
  markNotificationAsRead: (notificationId: number) => Promise<void>;
  markAllNotificationsAsRead: () => Promise<void>;
};

const NOTIFICATIONS_STALE_MS = 15000;
const DEFAULT_LIMIT = 8;


function useNotifications(limit = DEFAULT_LIMIT): UseNotificationsResult {
  const { user, loading } = useAuth();

  const [notifications, setNotifications] = useState<NotificationItem[] | undefined>(undefined);
  const [loadingNotifications, setLoadingNotifications] = useState<boolean>(true);
  const [errorNotifications, setErrorNotifications] = useState<string | undefined>(undefined);
  const inFlightRef = useRef<Promise<void> | null>(null);
  const lastLoadedAtRef = useRef<number>(0);

  const loadNotifications = useCallback(async (options?: { force?: boolean; silent?: boolean }) => {
    const force = options?.force ?? false;
    const silent = options?.silent ?? false;

    if (loading) return;

    if (!user) {
      setNotifications(undefined);
      setLoadingNotifications(false);
      setErrorNotifications(undefined);
      return;
    }

    const isFresh = lastLoadedAtRef.current > 0 && Date.now() - lastLoadedAtRef.current < NOTIFICATIONS_STALE_MS;
    if (!force && isFresh) {
      return;
    }

    if (inFlightRef.current) {
      return await inFlightRef.current;
    }

    const requestPromise = (async () => {
      if (!silent) {
        setLoadingNotifications(true);
      }
      setErrorNotifications(undefined);

      try {
        const res = await fetchNotifications({ limit, offset: 0 });
        setNotifications(res ?? []);
        lastLoadedAtRef.current = Date.now();
      } catch (err) {
        setErrorNotifications(err instanceof Error ? err.message : "Unexpected Error");
        setNotifications(undefined);
      } finally {
        setLoadingNotifications(false);
        inFlightRef.current = null;
      }
    })();

    inFlightRef.current = requestPromise;
    return await requestPromise;
  }, [loading, user?.uuid, limit]);

  const markNotificationAsRead = useCallback(async (notificationId: number) => {
    await handleMarkNotificationAsRead(notificationId);
    setNotifications((prev) =>
      prev?.map((notification) =>
        notification.id === notificationId ? { ...notification, isRead: true } : notification
      )
    );
  }, []);

  const markAllNotificationsAsRead = useCallback(async () => {
    await handleMarkAllNotificationsAsRead();
    setNotifications((prev) => prev?.map((notification) => ({ ...notification, isRead: true })));
  }, []);

  useEffect(() => {
    void loadNotifications({ silent: true });
  }, [loadNotifications]);

  const unreadCount = useMemo(
    () => notifications?.filter((notification) => !notification.isRead).length ?? 0,
    [notifications]
  );

  return {
    notifications,
    unreadCount,
    loadingNotifications,
    errorNotifications,
    loadNotifications,
    markNotificationAsRead,
    markAllNotificationsAsRead,
  };
}


export { useNotifications };
