import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Send } from "lucide-react";

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  sessionId?: string;
}

export default function ChatInput({ onSendMessage, sessionId }: ChatInputProps) {
  const [message, setMessage] = useState("");
  const [isComposing, setIsComposing] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // 當進入頁面、切換 session (sessionId 改變)、或按下新對話時自動聚焦
  useEffect(() => {
    // 延遲一點點確保 DOM 已完全就緒，特別是在行動裝置或複雜渲染時
    const timer = setTimeout(() => {
      textareaRef.current?.focus();
    }, 100);
    return () => clearTimeout(timer);
  }, [sessionId]);

  const sendMessage = () => {
    const trimmedMessage = message.trim();
    if (trimmedMessage) {
      onSendMessage(trimmedMessage);
      setMessage("");
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isComposing) {
      sendMessage();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && !isComposing) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t p-4 bg-background">
      <div className="relative">
        <Textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          onCompositionStart={() => setIsComposing(true)}
          onCompositionEnd={() => setIsComposing(false)}
          placeholder="請輸入訊息..."
          className="pr-12 resize-none min-h-[60px] max-h-[200px] border-muted bg-chat-input focus-visible:ring-0 focus-visible:ring-offset-0 focus:border-muted outline-none transition-none shadow-none"
          rows={2}
        />
        <Button
          type="submit"
          size="icon"
          className="absolute right-2 bottom-2 rounded-full"
          disabled={!message.trim() || isComposing}
        >
          <Send className="h-4 w-4" />
        </Button>
      </div>
      <div className="text-xs text-center mt-2 text-muted-foreground">
        按 Enter 發送、Shift+Enter 換行
      </div>
    </form>
  );
}
