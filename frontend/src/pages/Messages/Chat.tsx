import { Col, Row } from "react-bootstrap";
import { useAuth } from "../../components/Authentication/AuthContext";
import { User } from "../../models/user";

import { useEffect, useState } from "react";
import { Message } from "../../models/message";
import { getMessagesByUserUuid } from "../../API/Message/messageAPI";
import { formatIsoDateOrTime } from "./Messages";

interface MessageResSchema {
  message: Message;
  senderUuid: string;
  receiverUuid: string;
}

export function Chat({ selectedContact }: { selectedContact: User }) {
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
          className="flex-column"
          style={{ overflowY: "auto", maxHeight: "100%" }}
        >
          {messageHistory.map((messageRes) => (
            <Col
              key={messageRes.message.uuid}
              className={`col-8 align-self-${messageRes.senderUuid === user?.uuid ? "end" : "start"} justify-content-${messageRes.senderUuid === user?.uuid ? "end" : "start"} d-flex flex-wrap p-2`}
            >
              <div
                className={`bg-${messageRes.senderUuid === user?.uuid ? "primary" : "secondary"} text-white rounded p-2 message-bubble`}
              >
                {messageRes.message.content}
              </div>{" "}
              <div
                className={`w-100 text-${messageRes.senderUuid === user?.uuid ? "end" : "start"} text-muted`}
              >
                {formatIsoDateOrTime(messageRes.message.sentAt)}{" "}
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
