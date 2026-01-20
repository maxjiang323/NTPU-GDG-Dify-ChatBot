import { useState, useEffect, useRef } from "react";
import { api } from "@/services/api";
import { useIsMobile } from "@/hooks/use-mobile";
import Header from "@/components/Header";
import ChatSidebar from "@/components/ChatSidebar";
import ChatMessage from "@/components/ChatMessage";
import ChatInput from "@/components/ChatInput";
import { sendMessageToDifyStreaming } from "@/services/difyService";

interface Message {
  id: number;
  text: string;
  isUser: boolean;
  timestamp: string;
}

interface ChatHistory {
  id: string;
  title: string;
  time: string;
  messages: Message[];
  difyConversationId?: string;
}

const WELCOME_MESSAGE: Message = {
  id: 0,
  text: "您好！我是國立臺北大學的AI法律助手。有什麼法律相關問題需要協助嗎？",
  isUser: false,
  timestamp: "剛剛"
};

const Index = () => {
  const isMobile = useIsMobile();
  const [sidebarOpen, setSidebarOpen] = useState(!isMobile);

  const [currentChat, setCurrentChat] = useState<ChatHistory | null>(null);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 初始化：載入聊天記錄
  // ProtectedRoute 已確保此組件只在 authenticated === true 時才會被渲染
  // ProtectedRoute 已確保此組件只在 authenticated === true 時才會被渲染
  // 初期化邏輯改由 ChatSidebar 處理（透過 api.getSessions 抓取並回呼 onSelectChat）
  useEffect(() => {
    // 這裡可以放一些 Index 特有的初始化邏輯，如果有的話
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [currentChat?.messages]);

  const handleSendMessage = async (message: string) => {
    const timestamp = "剛剛";

    // 1. Prepare user message
    const userMsgId = (currentChat?.messages.length || 0) + 1;
    const newMessage: Message = {
      id: userMsgId,
      text: message,
      isUser: true,
      timestamp
    };

    // 2. Prepare AI placeholder
    const aiMsgId = userMsgId + 1;
    const aiPlaceholder: Message = {
      id: aiMsgId,
      text: "",
      isUser: false,
      timestamp
    };

    // Update UI immediately
    const firstMessageTitle = message.slice(0, 30) + (message.length > 30 ? "..." : "");
    if (currentChat) {
      setCurrentChat({
        ...currentChat,
        messages: [...currentChat.messages, newMessage, aiPlaceholder]
      });
    } else {
      // Starting a new chat from ground zero (Gemini style)
      setCurrentChat({
        id: "temp-" + Date.now(), // Temporary ID until backend confirms
        title: firstMessageTitle,
        time: "剛剛",
        messages: [newMessage, aiPlaceholder]
      });
    }

    // Use local variable because state update is async
    const isNewChat = !currentChat || currentChat.id.startsWith("temp-");
    const initialSessionId = isNewChat ? "" : currentChat!.id;
    let activeSessionId = initialSessionId;

    setIsTyping(true);

    // 如果是新對話，先建立正式 Session 以確保後續錯誤能被記錄
    if (isNewChat) {
      try {
        const session = await api.createSession(firstMessageTitle);
        activeSessionId = session.id;
        setCurrentChat(prev => prev ? {
          ...prev,
          id: session.id,
          title: session.topic || firstMessageTitle,
          time: session.updated_at ? new Date(session.updated_at).toLocaleString() : "剛剛"
        } : null);
      } catch (err) {
        console.error("Failed to pre-create session:", err);
        // 如果失敗，activeSessionId 仍為空，後續會由後端在 stream 中嘗試建立
      }
    }

    try {
      await sendMessageToDifyStreaming(
        message,
        "user-123",
        activeSessionId, // 使用已建立或現有的 ID
        (data) => {
          if (data.sessionId) {
            activeSessionId = data.sessionId;
            // Backend created a new session, update our state
            setCurrentChat(prev => {
              if (prev && (prev.id.startsWith("temp-") || prev.title === "新對話" || prev.title === firstMessageTitle)) {
                return {
                  ...prev,
                  id: data.sessionId!,
                  title: firstMessageTitle
                };
              }
              return prev;
            });
          }

          if (data.type === 'chunk' && data.fullAnswer) {
            setIsTyping(false);
            setCurrentChat(prevChat => {
              if (!prevChat) return null;
              const newMessages = [...prevChat.messages];
              const lastMsgIndex = newMessages.length - 1;

              if (lastMsgIndex >= 0) {
                newMessages[lastMsgIndex] = {
                  ...newMessages[lastMsgIndex],
                  text: data.fullAnswer || ""
                };
              }
              return { ...prevChat, messages: newMessages };
            });
          } else if (data.type === 'end') {
            setIsTyping(false);
            if (data.conversationId) {
              setCurrentChat(prev => prev ? { ...prev, difyConversationId: data.conversationId } : null);
            }
          } else if (data.type === 'error') {
            setIsTyping(false);
            console.error("Stream error:", data.message);
          }
        }
      );
    } catch (error) {
      console.error(error);
      setIsTyping(false);

      const errorText = "抱歉，發生錯誤，請稍後再試。";

      // Save error message to database as SYSTEM role
      if (activeSessionId) {
        api.createMessage(activeSessionId, errorText, 'SYSTEM').catch(err => {
          console.error("Failed to save error message to DB:", err);
        });
      }

      // Add error message to UI
      setCurrentChat(prev => {
        if (!prev) return null;
        const msgs = [...prev.messages];
        // If we have the empty placeholder, update it to error.
        const lastIdx = msgs.length - 1;
        if (lastIdx >= 0 && !msgs[lastIdx].isUser) {
          msgs[lastIdx] = { ...msgs[lastIdx], text: errorText };
        }
        return { ...prev, messages: msgs };
      });
    }
  };


  const handleSelectChat = (chat: ChatHistory) => {
    setCurrentChat(chat);
  };

  const handleUpdateChat = (updatedChat: ChatHistory) => {
    setCurrentChat(updatedChat);
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <div className="flex flex-col h-screen bg-background">
      <Header
        toggleSidebar={toggleSidebar}
        currentChatTitle={currentChat?.title || "無標題對話"}
      />

      <div className="flex flex-1 overflow-hidden">
        <ChatSidebar
          isMobile={!!isMobile}
          isOpen={sidebarOpen}
          setIsOpen={setSidebarOpen}
          onSelectChat={handleSelectChat}
          currentChatId={currentChat?.id}
          currentChat={currentChat}
          onUpdateChat={handleUpdateChat}
        />

        <main className="flex-1 flex flex-col overflow-hidden">
          <div className="chat-container overflow-y-auto p-4 space-y-4">
            {(!currentChat || currentChat.messages.length === 0) && (
              <ChatMessage
                message={WELCOME_MESSAGE.text}
                isUser={false}
                timestamp={WELCOME_MESSAGE.timestamp}
              />
            )}
            {currentChat?.messages.map(msg => (
              <ChatMessage
                key={msg.id}
                message={msg.text}
                isUser={msg.isUser}
                timestamp={msg.timestamp}
              />
            ))}

            {isTyping && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground mb-6">
                <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                  <div className="w-4 h-4 relative">
                    <span className="absolute top-0 left-0 w-1.5 h-1.5 bg-white rounded-full animate-pulse-light" style={{ animationDelay: "0ms" }}></span>
                    <span className="absolute top-0 right-0 w-1.5 h-1.5 bg-white rounded-full animate-pulse-light" style={{ animationDelay: "300ms" }}></span>
                    <span className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-1.5 h-1.5 bg-white rounded-full animate-pulse-light" style={{ animationDelay: "600ms" }}></span>
                  </div>
                </div>
                <span>AI正在回覆...</span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <ChatInput onSendMessage={handleSendMessage} sessionId={currentChat?.id} />
        </main>
      </div>
    </div>
  );
};

export default Index;