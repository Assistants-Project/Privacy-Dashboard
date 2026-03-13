import { useEffect, useMemo, useState } from "react";
import { Badge, Button, Card, Container, Form, ListGroup, Spinner } from "react-bootstrap";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../../contexts/AuthContext";
import { getNotificationTargetPath, getNotificationTitle, NotificationItem } from "../../models/notification";
import { RIGHT_TYPE_LABELS, RightType } from "../../models/request";
import { formatIsoDateOrTime } from "../../services/MessageService";
import { fetchNotifications, handleMarkAllNotificationsAsRead, handleMarkNotificationAsRead } from "../../services/NotificationService";


const PAGE_LIMIT = 25;
type ReadFilter = "all" | "unread" | "read";


const shortContext = (notification: NotificationItem): string | undefined => {
  if (!notification.processingContextUuid) return undefined;
  return notification.processingContextUuid;
};

const notificationTypeLabel = (type: string, isManagerRole: boolean): string => {
  switch (type) {
    case "CONSENT_GRANTED":
      return "Consent granted";
    case "REQUEST_SUBMITTED":
      return isManagerRole ? "Requests received" : "Request submitted";
    case "REQUEST_ANSWERED":
      return "Request answered";
    case "REQUEST_STATUS_UPDATED":
      return "Request status updated";
    default:
      return type.replaceAll("_", " ").toLowerCase().replace(/^\w/, (char) => char.toUpperCase());
  }
};

const buildNotificationSearchText = (notification: NotificationItem): string =>
  [
    getNotificationTitle(notification),
    notification.applicationName,
    notification.senderEmail,
    notification.requestUuid,
    notification.processingContextUuid,
    notification.payload?.consent_content,
    notification.payload?.consent_uuid,
    notification.payload?.right_type,
    notification.payload?.right_type ? RIGHT_TYPE_LABELS[notification.payload.right_type] : undefined,
  ]
    .filter((value): value is string => typeof value === "string" && value.trim() !== "")
    .join(" ")
    .toLowerCase();

export function Notifications() {
  const navigate = useNavigate();
  const { user, loading, isManagerRole } = useAuth();

  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [query, setQuery] = useState("");
  const [readFilter, setReadFilter] = useState<ReadFilter>("all");
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [rightTypeFilter, setRightTypeFilter] = useState<"all" | RightType>("all");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [sortOrder, setSortOrder] = useState<"newest" | "oldest">("newest");
  const [loadingNotifications, setLoadingNotifications] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [errorNotifications, setErrorNotifications] = useState<string | undefined>(undefined);
  const [hasMore, setHasMore] = useState(false);
  const notificationTypes = useMemo(
    () => [...new Set(notifications.map((notification) => notification.type))].sort(),
    [notifications]
  );
  const requestRightTypes = useMemo(
    () =>
      [...new Set(notifications.map((notification) => notification.payload?.right_type).filter((type): type is RightType => type !== undefined))]
        .sort((left, right) => RIGHT_TYPE_LABELS[left].localeCompare(RIGHT_TYPE_LABELS[right])),
    [notifications]
  );
  const visibleNotifications = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    const fromDate = dateFrom ? new Date(`${dateFrom}T00:00:00`) : undefined;
    const toDate = dateTo ? new Date(`${dateTo}T23:59:59.999`) : undefined;

    const filtered = notifications.filter((notification) => {
      if (readFilter === "unread" && notification.isRead) return false;
      if (readFilter === "read" && !notification.isRead) return false;
      if (typeFilter !== "all" && notification.type !== typeFilter) return false;
      if (rightTypeFilter !== "all" && notification.payload?.right_type !== rightTypeFilter) return false;

      const sentAt = new Date(notification.sentAt);
      if (fromDate && sentAt < fromDate) return false;
      if (toDate && sentAt > toDate) return false;

      if (normalizedQuery && !buildNotificationSearchText(notification).includes(normalizedQuery)) {
        return false;
      }

      return true;
    });

    filtered.sort((left, right) => {
      const leftTime = new Date(left.sentAt).getTime();
      const rightTime = new Date(right.sentAt).getTime();
      return sortOrder === "newest" ? rightTime - leftTime : leftTime - rightTime;
    });

    return filtered;
  }, [notifications, query, readFilter, typeFilter, rightTypeFilter, dateFrom, dateTo, sortOrder]);

  const loadNotifications = async (offset: number, append: boolean) => {
    if (loading || !user) return;

    if (append) {
      setLoadingMore(true);
    } else {
      setLoadingNotifications(true);
    }
    setErrorNotifications(undefined);

    try {
      const res = await fetchNotifications({
        limit: PAGE_LIMIT,
        offset,
      });
      const nextNotifications = res ?? [];
      setNotifications((prev) => (append ? [...prev, ...nextNotifications] : nextNotifications));
      setHasMore(nextNotifications.length === PAGE_LIMIT);
    } catch (err) {
      setErrorNotifications(err instanceof Error ? err.message : "Unexpected Error");
      if (!append) {
        setNotifications([]);
      }
    } finally {
      setLoadingNotifications(false);
      setLoadingMore(false);
    }
  };

  useEffect(() => {
    void loadNotifications(0, false);
  }, [user?.uuid, loading]);

  const unreadCount = useMemo(
    () => notifications.filter((notification) => !notification.isRead).length,
    [notifications]
  );
  const hasActiveFilters =
    query.trim() !== "" ||
    readFilter !== "all" ||
    typeFilter !== "all" ||
    rightTypeFilter !== "all" ||
    dateFrom !== "" ||
    dateTo !== "" ||
    sortOrder !== "newest";

  const handleNotificationClick = (notification: NotificationItem) => {
    if (!notification.isRead) {
      setNotifications((prev) =>
        prev.map((item) => (item.id === notification.id ? { ...item, isRead: true } : item))
      );
      void handleMarkNotificationAsRead(notification.id).catch((err) => {
        console.error(`Failed to mark notification ${notification.id} as read:`, err);
      });
    }
    navigate(getNotificationTargetPath(notification));
  };

  const handleReadAll = async () => {
    await handleMarkAllNotificationsAsRead();
    setNotifications((prev) => prev.map((notification) => ({ ...notification, isRead: true })));
  };

  const handleResetFilters = () => {
    setQuery("");
    setReadFilter("all");
    setTypeFilter("all");
    setRightTypeFilter("all");
    setDateFrom("");
    setDateTo("");
    setSortOrder("newest");
  };

  return (
    <Container fluid className="py-2 d-flex flex-column overflow-hidden h-100" style={{ minHeight: 0 }}>
      <Card className="p-0 d-flex flex-column flex-grow-1 overflow-hidden" style={{ minHeight: 0 }}>
        <Card.Body className="d-flex flex-column gap-3 flex-grow-1 overflow-hidden" style={{ minHeight: 0 }}>
          <div className="d-flex justify-content-between align-items-center gap-3 flex-wrap">
            <div>
              <h2 className="h4 mb-1">Notification History</h2>
            </div>
            <div className="d-flex align-items-center gap-2 flex-wrap">
              <div className="text-muted small">
                Showing <strong>{visibleNotifications.length}</strong> of <strong>{notifications.length}</strong>
              </div>
              <Button variant="outline-secondary" disabled={unreadCount === 0} onClick={() => void handleReadAll()}>
                Mark all as read
              </Button>
            </div>
          </div>

          <Card className="p-0 border-0 bg-body-tertiary">
            <Card.Body className="d-flex flex-column gap-3">
              <div className="d-flex justify-content-between align-items-center gap-3 flex-wrap">
                <strong>Filters</strong>
                <Button variant="outline-secondary" size="sm" onClick={handleResetFilters} disabled={!hasActiveFilters}>
                  Reset filters
                </Button>
              </div>

              <div className="row g-3">
                <div className="col-12 col-xl-4">
                  <Form.Group controlId="notifications-query">
                    <Form.Label className="mb-1">Search</Form.Label>
                    <Form.Control
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      placeholder="App, sender, consent, context…"
                    />
                  </Form.Group>
                </div>

                <div className="col-12 col-sm-6 col-xl-2">
                  <Form.Group controlId="notifications-read-filter">
                    <Form.Label className="mb-1">Read status</Form.Label>
                    <Form.Select value={readFilter} onChange={(e) => setReadFilter(e.target.value as ReadFilter)}>
                      <option value="all">All</option>
                      <option value="unread">Unread</option>
                      <option value="read">Read</option>
                    </Form.Select>
                  </Form.Group>
                </div>

                <div className="col-12 col-sm-6 col-xl-3">
                  <Form.Group controlId="notifications-type-filter">
                    <Form.Label className="mb-1">Type</Form.Label>
                    <Form.Select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
                      <option value="all">All types</option>
                      {notificationTypes.map((type) => (
                        <option key={type} value={type}>
                          {notificationTypeLabel(type, isManagerRole)}
                        </option>
                      ))}
                    </Form.Select>
                  </Form.Group>
                </div>

                <div className="col-12 col-sm-6 col-xl-3">
                  <Form.Group controlId="notifications-right-type-filter">
                    <Form.Label className="mb-1">Right request type</Form.Label>
                    <Form.Select
                      value={rightTypeFilter}
                      onChange={(e) => setRightTypeFilter(e.target.value as "all" | RightType)}
                      disabled={requestRightTypes.length === 0}
                    >
                      <option value="all">All right types</option>
                      {requestRightTypes.map((type) => (
                        <option key={type} value={type}>
                          {RIGHT_TYPE_LABELS[type]}
                        </option>
                      ))}
                    </Form.Select>
                  </Form.Group>
                </div>

                <div className="col-12 col-sm-6 col-xl-3">
                  <Form.Group controlId="notifications-sort-order">
                    <Form.Label className="mb-1">Order</Form.Label>
                    <Form.Select value={sortOrder} onChange={(e) => setSortOrder(e.target.value as "newest" | "oldest")}>
                      <option value="newest">Newest first</option>
                      <option value="oldest">Oldest first</option>
                    </Form.Select>
                  </Form.Group>
                </div>

                <div className="col-12 col-sm-6 col-xl-3">
                  <Form.Group controlId="notifications-date-from">
                    <Form.Label className="mb-1">From</Form.Label>
                    <Form.Control type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} />
                  </Form.Group>
                </div>

                <div className="col-12 col-sm-6 col-xl-3">
                  <Form.Group controlId="notifications-date-to">
                    <Form.Label className="mb-1">To</Form.Label>
                    <Form.Control type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)} />
                  </Form.Group>
                </div>
              </div>
            </Card.Body>
          </Card>

          <div className="d-flex flex-column flex-grow-1 overflow-hidden" style={{ minHeight: 0 }}>
            {loadingNotifications ? (
              <div className="d-flex align-items-center gap-2 text-muted">
                <Spinner animation="border" size="sm" />
                Loading…
              </div>
            ) : undefined}

            {errorNotifications ? (
              <Card bg="danger" text="white" className="p-0">
                <Card.Body>{errorNotifications}</Card.Body>
              </Card>
            ) : undefined}

            {!loadingNotifications && !errorNotifications ? (
              visibleNotifications.length === 0 ? (
                <Card className="p-0">
                  <Card.Body className="text-muted">
                    {hasActiveFilters ? "No notifications match the current filters." : "No notifications."}
                  </Card.Body>
                </Card>
              ) : (
                <div className="rounded-4 border bg-body-tertiary ps-2 pe-3 py-3 flex-grow-1 overflow-auto" style={{ minHeight: 0 }}>
                  <ListGroup className="gap-3 bg-transparent">
                    {visibleNotifications.map((notification) => {
                      const contextLabel = shortContext(notification);
                      const rightTypeLabel = notification.payload?.right_type
                        ? RIGHT_TYPE_LABELS[notification.payload.right_type]
                        : undefined;
                      const typeLabel = notificationTypeLabel(notification.type, isManagerRole);

                      return (
                        <ListGroup.Item
                          key={notification.id}
                          as="div"
                          role="button"
                          tabIndex={0}
                          className={[
                            "list-group-item-action",
                            "text-start",
                            "rounded-4",
                            "border",
                            "shadow-sm",
                            "px-3",
                            "py-3",
                            notification.isRead ? "bg-white border-light-subtle" : "bg-primary-subtle border-primary-subtle",
                          ].join(" ")}
                          onClick={() => void handleNotificationClick(notification)}
                          onKeyDown={(e) => {
                            if (e.key === "Enter" || e.key === " ") {
                              e.preventDefault();
                              void handleNotificationClick(notification);
                            }
                          }}
                        >
                          <div className="d-flex flex-column gap-2">
                            <div className="d-flex justify-content-between align-items-start gap-3 flex-wrap flex-md-nowrap">
                              <div className="fw-semibold text-break flex-grow-1">
                                {getNotificationTitle(notification)}
                              </div>
                              <div className="d-flex align-items-center gap-2 flex-wrap justify-content-end">
                                <button
                                  type="button"
                                  className="badge bg-light text-dark border fw-normal"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setTypeFilter(notification.type);
                                  }}
                                >
                                  {typeLabel}
                                </button>
                                {!notification.isRead ? <Badge bg="primary">Unread</Badge> : undefined}
                              </div>
                            </div>

                            <div className="d-flex align-items-center gap-2 gap-md-3 flex-wrap text-muted small">
                              {notification.applicationName ? (
                                <span className="fw-medium text-body">{notification.applicationName}</span>
                              ) : undefined}
                              {rightTypeLabel ? <span>{rightTypeLabel}</span> : undefined}
                              {contextLabel ? (
                                <span title={notification.processingContextUuid}>
                                  Context ID: <span className="font-monospace">{contextLabel}</span>
                                </span>
                              ) : undefined}
                              <span className="ms-md-auto">{formatIsoDateOrTime(notification.sentAt, true)}</span>
                            </div>
                          </div>
                        </ListGroup.Item>
                      );
                    })}
                  </ListGroup>
                </div>
              )
            ) : undefined}
          </div>

          {!loadingNotifications && !errorNotifications && hasMore ? (
            <div className="d-flex justify-content-center">
              <Button
                variant="outline-secondary"
                disabled={loadingMore}
                onClick={() => void loadNotifications(notifications.length, true)}
              >
                {loadingMore ? "Loading..." : "Load more"}
              </Button>
            </div>
          ) : undefined}
        </Card.Body>
      </Card>
    </Container>
  );
}
