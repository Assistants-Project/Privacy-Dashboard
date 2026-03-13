import { getMessagesByUserUuid, sendMessage } from "../API/Message/messageAPI";
import { getContacts, getMessagedContacts } from "../API/User/userAPI";
import { Message } from "../models/message";
import { RelatedApplicationModel, Role, UserModel } from "../models/user";

export interface MessagedContact {
  user: UserModel;
  last_message: Message;
}

export interface MessageResSchema {
  message: Message;
  senderUuid: string;
  receiverUuid: string;
}

type ContactDto = {
  user: {
    uuid: string;
    firstname: string;
    lastname: string;
    email: string;
    role: Role;
  };
  related_applications?: Array<{
    uuid: string;
    name: string;
    title: string;
  }>;
};

export const fetchMessagedContacts = async (): Promise<
  MessagedContact[] | undefined
> => {
  try {
    const contacts = await getMessagedContacts();
    return contacts.map(
      (contact: any) =>
        ({
          user: {
            uuid: contact.user.uuid,
            firstname: contact.user.firstname,
            lastname: contact.user.lastname,
            email: contact.user.email,
            role: contact.user.role,
          } as UserModel,
          last_message: {
            uuid: contact.last_message.message.uuid,
            content: contact.last_message.message.content,
            attachment: contact.last_message.message.attachment,
            sentAt: contact.last_message.message.sent_at,
            isRead: contact.last_message.message.is_read,
          } as Message,
        }) as MessagedContact,
    );
  } catch (err) {
    console.error("Error fetching messaged contacts:", err);
  }
};

export const fetchMessagesByUserUuid = async (
  contactUuid: string,
): Promise<MessageResSchema[] | undefined> => {
  try {
    const messagesRes = await getMessagesByUserUuid(contactUuid);
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
    console.error(`Error fetching messages for ${contactUuid}:`, err);
  }
};

export const fetchContacts = async (): Promise<UserModel[] | undefined> => {
  try {
    const contacts = await getContacts();
    return contacts.map(
      (contact: ContactDto) =>
        ({
          uuid: contact.user.uuid,
          email: contact.user.email,
          firstname: contact.user.firstname,
          lastname: contact.user.lastname,
          role: contact.user.role as Role,
          relatedApplications: Array.isArray(contact.related_applications)
            ? contact.related_applications.map(
                (application): RelatedApplicationModel => ({
                  uuid: application.uuid,
                  name: application.name,
                  title: application.title,
                }),
              )
            : [],
        }) as UserModel,
    );
  } catch (err) {
    console.error("Error fetching contacts:", err);
  }
};

export const handleSendMessage = async (
  receiverUuid: string,
  content: string,
  attachment?: string,
) => {
  if (!receiverUuid) {
    alert("Please select a contact.");
    return;
  }
  try {
    const result = await sendMessage(receiverUuid, content.trim(), attachment);
    return result;
  } catch (err) {
    console.error(`Error sending message to ${receiverUuid}:`, err);
  }
};

export function formatIsoDateOrTime(
  isoString: string,
  dateAndTime: boolean = false,
): string {
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
    // Previous day: return DD/MM/YYYY or HH:MM DD/MM/YYYY
    const day = String(dt.getDate()).padStart(2, "0");
    const month = String(dt.getMonth() + 1).padStart(2, "0");
    const year = dt.getFullYear();
    if (dateAndTime) {
      return `${hours}:${minutes} ${day}/${month}/${year}`;
    }
    return `${day}/${month}/${year}`;
  }
}

export function isSameUpToMinute(a: string, b: string): boolean {
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
