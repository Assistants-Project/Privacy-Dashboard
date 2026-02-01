export interface Message {
  uuid: string;
  content: string;
  attachment?: string;
  sentAt: string;
  isRead: boolean;
}
