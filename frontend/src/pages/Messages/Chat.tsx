import { Col, Row } from "react-bootstrap";
import { useAuth } from "../../components/Authentication/AuthContext";
import { User } from "../../models/user";

import { useEffect, useRef, useState } from "react";
import { Message } from "../../models/message";
import { getMessagesByUserUuid } from "../../API/Message/messageAPI";
import { formatIsoDateOrTime } from "./Messages";

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

  const nextBelongsToSameGroup = (current: number, next: number): boolean => {
    return (
      messageHistory![current].senderUuid ===
        messageHistory![next].senderUuid &&
      isSameUpToMinute(
        messageHistory![current].message.sentAt,
        messageHistory![next].message.sentAt,
      )
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
              className={`col-8 align-self-${messageRes.senderUuid === user?.uuid ? "end" : "start"} justify-content-${messageRes.senderUuid === user?.uuid ? "end" : "start"} d-flex flex-wrap px-2 pt-1 pb-${
                (index < messageHistory.length - 1 &&
                  !nextBelongsToSameGroup(index, index + 1)) ||
                index === messageHistory.length - 1
                  ? 2
                  : 0
              }`}
            >
              <div
                className={`bg-${messageRes.senderUuid === user?.uuid ? "primary" : "secondary"} text-white rounded p-2 message-bubble`}
              >
                {messageRes.message.content}
              </div>{" "}
              <div
                className={`w-100 text-${messageRes.senderUuid === user?.uuid ? "end" : "start"} text-muted`}
              >
                {((index < messageHistory.length - 1 &&
                  !nextBelongsToSameGroup(index, index + 1)) ||
                  index === messageHistory.length - 1) &&
                  formatIsoDateOrTime(messageRes.message.sentAt)}{" "}
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
