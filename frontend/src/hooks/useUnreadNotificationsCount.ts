import { useCallback, useEffect, useRef, useState } from "react";

import { useAuth } from "../contexts/AuthContext";
import {
  fetchUnreadNotificationsCount,
  NOTIFICATIONS_CHANGED_EVENT,
  NOTIFICATIONS_OPTIMISTIC_UPDATE_EVENT,
} from "../services/NotificationService";


type UseUnreadNotificationsCountResult = {
  unreadNotificationsCount: number;
  loadUnreadNotificationsCount: (options?: { force?: boolean }) => Promise<void>;
};

const UNREAD_NOTIFICATIONS_COUNT_STALE_MS = 15000;


function useUnreadNotificationsCount(): UseUnreadNotificationsCountResult {
  const { user, loading } = useAuth();

  const [unreadNotificationsCount, setUnreadNotificationsCount] = useState(0);
  const inFlightRef = useRef<Promise<void> | null>(null);
  const lastLoadedAtRef = useRef(0);
  const optimisticCapRef = useRef<number | null>(null);

  const loadUnreadNotificationsCount = useCallback(async (options?: { force?: boolean }) => {
    const force = options?.force ?? false;

    if (loading) return;

    if (!user) {
      setUnreadNotificationsCount(0);
      lastLoadedAtRef.current = 0;
      return;
    }

    const isFresh = lastLoadedAtRef.current > 0 && Date.now() - lastLoadedAtRef.current < UNREAD_NOTIFICATIONS_COUNT_STALE_MS;
    if (!force && isFresh) {
      return;
    }

    if (inFlightRef.current) {
      return await inFlightRef.current;
    }

    const requestPromise = (async () => {
      try {
        const count = await fetchUnreadNotificationsCount();
        let nextCount = count;
        if (optimisticCapRef.current !== null) {
          nextCount = Math.min(count, optimisticCapRef.current);
          if (count <= optimisticCapRef.current) {
            optimisticCapRef.current = null;
          }
        }
        setUnreadNotificationsCount(nextCount);
        lastLoadedAtRef.current = Date.now();
      } catch (err) {
        console.error("Failed to load unread notifications count:", err);
      } finally {
        inFlightRef.current = null;
      }
    })();

    inFlightRef.current = requestPromise;
    return await requestPromise;
  }, [loading, user?.uuid]);

  useEffect(() => {
    void loadUnreadNotificationsCount();
  }, [loadUnreadNotificationsCount]);

  useEffect(() => {
    const handleNotificationsChanged = () => {
      void loadUnreadNotificationsCount({ force: true });
    };

    window.addEventListener(NOTIFICATIONS_CHANGED_EVENT, handleNotificationsChanged);
    return () => {
      window.removeEventListener(NOTIFICATIONS_CHANGED_EVENT, handleNotificationsChanged);
    };
  }, [loadUnreadNotificationsCount]);

  useEffect(() => {
    const handleOptimisticUpdate = (event: Event) => {
      const detail = (event as CustomEvent<{ kind?: string }>).detail;
      if (detail?.kind === "single-read") {
        setUnreadNotificationsCount((prev) => {
          const nextCount = Math.max(0, prev - 1);
          optimisticCapRef.current = nextCount;
          return nextCount;
        });
        return;
      }
      if (detail?.kind === "all-read") {
        optimisticCapRef.current = 0;
        setUnreadNotificationsCount(0);
      }
    };

    window.addEventListener(NOTIFICATIONS_OPTIMISTIC_UPDATE_EVENT, handleOptimisticUpdate);
    return () => {
      window.removeEventListener(NOTIFICATIONS_OPTIMISTIC_UPDATE_EVENT, handleOptimisticUpdate);
    };
  }, []);

  return { unreadNotificationsCount, loadUnreadNotificationsCount };
}


export { useUnreadNotificationsCount };
