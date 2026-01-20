import { Avatar } from "@/components/ui/avatar";
import { User } from "lucide-react";
import ReactMarkdown from 'react-markdown';
import rehypeSanitize from 'rehype-sanitize';
import { sanitizeHtml } from "@/lib/sanitize";

interface ChatMessageProps {
  message: string;
  isUser: boolean;
  timestamp: string;
}

export default function ChatMessage({ message, isUser, timestamp }: ChatMessageProps) {
  // Sanitize message content as a first line of defense
  const sanitizedMessage = sanitizeHtml(message);

  // 資安驗證：在控制台中印出清理後的原始字串內容
  if (isUser && message.includes('<a')) {
    console.log("原始輸入:", message);
    console.log("清理後字串:", sanitizedMessage);
  }

  return (
    <div className={`flex items-start gap-3 mb-6 message-appear ${isUser ? 'justify-end' : ''}`}>
      {!isUser && (
        <Avatar className="h-8 w-8 bg-white flex items-center justify-center">
          <img src="/lovable-uploads/6835f04d-7fe7-467f-8213-c78b51f2c9bf.png" alt="NTPU Logo" className="h-8 w-8 object-contain" />
        </Avatar>
      )}
      <div className={`flex flex-col flex-1 ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`rounded-2xl px-4 py-3 max-w-[85%] sm:max-w-[70%] ${isUser
            ? 'bg-chat-user text-foreground whitespace-pre-wrap break-words'
            : 'bg-chat-ai text-foreground border'
            }`}
        >
          {isUser ? (
            sanitizedMessage
          ) : (
            <ReactMarkdown
              rehypePlugins={[rehypeSanitize]}
              components={{
                p: ({ children }) => <p className="mb-4 last:mb-0">{children}</p>,
                ul: ({ children }) => <ul className="list-disc pl-6 mb-4 last:mb-0">{children}</ul>,
                ol: ({ children }) => <ol className="list-decimal pl-6 mb-4 last:mb-0">{children}</ol>,
                li: ({ children }) => <li className="mb-1 last:mb-0">{children}</li>,
                strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                em: ({ children }) => <em className="italic">{children}</em>,
                h1: ({ children }) => <h1 className="text-xl font-bold mb-4">{children}</h1>,
                h2: ({ children }) => <h2 className="text-lg font-bold mb-3">{children}</h2>,
                h3: ({ children }) => <h3 className="text-base font-bold mb-2">{children}</h3>,
                code: ({ children }) => <code className="bg-muted px-1 py-0.5 rounded">{children}</code>,
                pre: ({ children }) => <pre className="bg-muted p-2 rounded mb-4 last:mb-0 overflow-x-auto">{children}</pre>,
                // 關鍵修正：確保 Markdown 產生的連結也具備安全屬性
                a: ({ href, children, target }) => (
                  <a
                    href={href}
                    target={target || "_blank"}
                    rel="noopener noreferrer"
                    className="text-primary underline hover:opacity-80 transition-opacity"
                  >
                    {children}
                  </a>
                ),
              }}
            >
              {sanitizedMessage}
            </ReactMarkdown>
          )}
        </div>
        <span className="text-xs text-muted-foreground mt-1 px-2">{timestamp}</span>
      </div>
      {isUser && (
        <Avatar className="h-8 w-8 bg-primary/80 flex items-center justify-center">
          <User className="h-5 w-5 text-white" />
        </Avatar>
      )}
    </div>
  );
}
