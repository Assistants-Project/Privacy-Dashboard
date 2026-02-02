import { Col, Row } from "react-bootstrap";
import { useAuth } from "../../components/Authentication/AuthContext";
import { User } from "../../models/user";

import { useEffect, useRef, useState } from "react";
import { Message } from "../../models/message";
import { getMessagesByUserUuid } from "../../API/Message/messageAPI";

interface MessageResSchema {
  message: Message;
  senderUuid: string;
  receiverUuid: string;
}

export function Chat({ selectedContact }: { selectedContact: User }) {
  const scrollRef = useRef<HTMLDivElement | null>(null);

  const { user, loading } = useAuth();
  const [messageHistory, setMessageHistory] = useState<
    MessageResSchema[] | undefined
  >(undefined);

  useEffect(() => {
    const fetchData = async () => {
      const messagesRes = await fetchMessagesByUserUuid();
      setMessageHistory(messagesRes || undefined);
    };
    fetchData();
  }, [selectedContact]);

  useEffect(() => {
    const container = scrollRef.current;
    if (container) {
      console.log("Scrolling to bottom of messages");
      container.scrollTop = container.scrollHeight;
    }
  }, [messageHistory]);

  const nextBelongsToOtherGroup = (current: number, next: number): boolean => {
    if (!messageHistory) return false;
    return (
      (current < messageHistory.length - 1 &&
        (messageHistory![current].senderUuid !==
          messageHistory![next].senderUuid ||
          !isSameUpToMinute(
            messageHistory![current].message.sentAt,
            messageHistory![next].message.sentAt,
          ))) ||
      current === messageHistory.length - 1
    );
  };

  const fetchMessagesByUserUuid = async (): Promise<
    MessageResSchema[] | undefined
  > => {
    try {
      const messagesRes = await getMessagesByUserUuid(selectedContact.uuid);
      return messagesRes.map(
        (messageRes: any) =>
          ({
            message: {
              uuid: messageRes.message.uuid,
              content: messageRes.message.content,
              attachment: messageRes.message.attachment,
              sentAt: messageRes.message.sent_at,
              isRead: messageRes.message.is_read,
            } as Message,
            senderUuid: messageRes.sender_uuid,
            receiverUuid: messageRes.receiver_uuid,
          }) as MessageResSchema,
      );
    } catch (err) {
      console.error(
        `Error fetching messages for ${selectedContact.uuid}:`,
        err,
      );
    }
  };

  return (
    <>
      {messageHistory ? (
        <Row
          className="flex-grow-1 flex-column flex-nowrap overflow-auto mb-3 pe-0"
          ref={scrollRef}
          style={{ scrollbarWidth: "thin" }}
        >
          {messageHistory.map((messageRes, index) => (
            <Col
              key={messageRes.message.uuid}
              className={`col-8 align-self-${messageRes.senderUuid === user?.uuid ? "end" : "start"} justify-content-${messageRes.senderUuid === user?.uuid ? "end" : "start"} d-flex flex-wrap px-3 pt-1 pb-${
                nextBelongsToOtherGroup(index, index + 1) ? 2 : 0
              }`}
            >
              <div
                className={`bg-${messageRes.senderUuid === user?.uuid ? "primary" : "secondary"} text-white py-2 px-3 message-bubble ${nextBelongsToOtherGroup(index, index + 1) ? "message-bubble-" + (messageRes.senderUuid === user?.uuid ? "sent" : "received") : ""}`}
              >
                {messageRes.message.content}
                <div
                  className="text-end"
                  style={{ fontSize: "0.8rem", opacity: 0.8 }}
                >
                  {formatIsoDateTime(messageRes.message.sentAt)}
                </div>
              </div>
            </Col>
          ))}
        </Row>
      ) : (
        <p>Loading messages...</p>
      )}
    </>
  );
}

function isSameUpToMinute(a: string, b: string): boolean {
  const d1 = new Date(a);
  const d2 = new Date(b);

  return (
    d1.getFullYear() === d2.getFullYear() &&
    d1.getMonth() === d2.getMonth() &&
    d1.getDate() === d2.getDate() &&
    d1.getHours() === d2.getHours() &&
    d1.getMinutes() === d2.getMinutes()
  );
}

function formatIsoDateTime(isoString: string): string {
  const dt = new Date(isoString);

  // Today's midnight
  const now = new Date();
  const todayMidnight = new Date(
    now.getFullYear(),
    now.getMonth(),
    now.getDate(),
  );

  const hours = String(dt.getHours()).padStart(2, "0");
  const minutes = String(dt.getMinutes()).padStart(2, "0");
  if (dt >= todayMidnight) {
    // Same day: return HH:MM
    return `${hours}:${minutes}`;
  } else {
    // Previous day: return HH:MM DD/MM/YYYY
    const day = String(dt.getDate()).padStart(2, "0");
    const month = String(dt.getMonth() + 1).padStart(2, "0");
    const year = dt.getFullYear();
    return `${hours}:${minutes} ${day}/${month}/${year}`;
  }
}
