export interface Message {
  id: number;
  text: string;
  isUser: boolean;
  timestamp: string;
}

export interface ChatHistory {
  id: string;
  title: string;
  time: string;
  messages: Message[];
  difyConversationId?: string;
}
