import { Col, Row } from "react-bootstrap";
import { useAuth } from "./Authentication/AuthContext";
import { User } from "../models/user";

import { useEffect, useRef, useState } from "react";
import {
  fetchMessagesByUserUuid,
  formatIsoDateOrTime,
  isSameUpToMinute,
  MessageResSchema,
} from "../services/MessageService";

export function Chat({ selectedContact }: { selectedContact: User }) {
  const scrollRef = useRef<HTMLDivElement | null>(null);

  const { user } = useAuth();
  const [messageHistory, setMessageHistory] = useState<
    MessageResSchema[] | undefined
  >(undefined);

  useEffect(() => {
    const fetchData = async () => {
      const messagesRes = await fetchMessagesByUserUuid(selectedContact.uuid);
      setMessageHistory(messagesRes || undefined);
    };
    fetchData();
  }, [selectedContact]);

  useEffect(() => {
    const container = scrollRef.current;
    if (container) {
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
                  {formatIsoDateOrTime(messageRes.message.sentAt, true)}
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
