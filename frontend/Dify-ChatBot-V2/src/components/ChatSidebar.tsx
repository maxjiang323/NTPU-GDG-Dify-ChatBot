import { useState, useEffect, useCallback } from "react";
import { api } from "@/services/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Menu,
  MessageCircle,
  Search,
  X,
  MoreVertical,
  Edit,
  Trash2
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog";
import { toast } from "sonner";

interface ChatHistory {
  id: string;
  title: string;
  time: string;
  messages: Array<{
    id: number;
    text: string;
    isUser: boolean;
    timestamp: string;
  }>;
}

interface SidebarProps {
  isMobile: boolean;
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
  onSelectChat: (chat: ChatHistory) => void;
  currentChatId?: string;
  currentChat?: ChatHistory;
  onUpdateChat: (chat: ChatHistory) => void;
}

export default function ChatSidebar({
  isMobile,
  isOpen,
  setIsOpen,
  onSelectChat,
  currentChatId,
  currentChat,
  onUpdateChat
}: SidebarProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>([]);
  const [isRenameDialogOpen, setIsRenameDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [selectedChat, setSelectedChat] = useState<ChatHistory | null>(null);
  const [newChatTitle, setNewChatTitle] = useState("");

  // 從 API 載入聊天記錄
  const fetchSessions = useCallback(async () => {
    try {
      const sessions = await api.getSessions();
      // 將後端資料轉換為前端格式
      const formattedSessions = sessions.map((s: any) => ({
        id: s.id,
        title: s.topic || "無標題對話",
        time: new Date(s.updated_at).toLocaleString(),
        difyConversationId: s.dify_conversation_id,
        messages: s.messages.map((m: any) => ({
          id: m.id,
          text: m.content,
          isUser: m.role === "USER",
          timestamp: new Date(m.created_at).toLocaleTimeString()
        }))
      }));
      setChatHistory(formattedSessions);

      // 如果有對話記錄但沒有當前對話，選擇第一個對話
      if (formattedSessions.length > 0 && !currentChat) {
        onSelectChat(formattedSessions[0]);
      }
    } catch (err) {
      console.error("Failed to fetch sessions:", err);
      toast.error("讀取歷史紀錄失敗");
    }
  }, [currentChat, onSelectChat]);

  useEffect(() => {
    fetchSessions();
  }, []);

  // 當 currentChat 更新時，同步更新側邊欄列表（避免頻繁重新 fetch）
  useEffect(() => {
    if (currentChat) {
      // 避免將臨時對話（還沒拿到正式 ID）加入歷史清單，防止重複顯示
      if (currentChat.id.startsWith("temp-")) return;

      setChatHistory(prevHistory => {
        const exists = prevHistory.some(chat => chat.id === currentChat.id);
        if (exists) {
          return prevHistory.map(chat =>
            chat.id === currentChat.id ? currentChat : chat
          );
        } else {
          // 加入新對話，同時確保過濾掉任何可能殘留的臨時對話
          return [currentChat, ...prevHistory.filter(c => !c.id.startsWith("temp-"))];
        }
      });
    }
  }, [currentChat]);


  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  const handleRenameChat = async () => {
    if (selectedChat && newChatTitle.trim()) {
      try {
        await api.updateSession(selectedChat.id, newChatTitle);
        const updatedChat = { ...selectedChat, title: newChatTitle };
        setChatHistory(prevHistory =>
          prevHistory.map(chat =>
            chat.id === selectedChat.id ? updatedChat : chat
          )
        );
        onUpdateChat(updatedChat);
        setIsRenameDialogOpen(false);
        toast.success("已重新命名");
      } catch (err) {
        toast.error("重新命名失敗");
      }
    }
  };

  const handleDeleteChat = async () => {
    if (selectedChat) {
      try {
        await api.deleteSession(selectedChat.id);
        const deletedIndex = chatHistory.findIndex(chat => chat.id === selectedChat.id);
        const newHistory = chatHistory.filter(chat => chat.id !== selectedChat.id);
        setChatHistory(newHistory);
        setIsDeleteDialogOpen(false);
        toast.success("已刪除紀錄");

        // 如果刪除的是當前對話，智慧選擇下一個
        if (selectedChat.id === currentChatId) {
          if (newHistory.length > 0) {
            // 嘗試選擇下一個，如果沒有則選擇上一個（現在的 index 指向的就是原本的下一個）
            const nextChat = newHistory[deletedIndex] || newHistory[newHistory.length - 1];
            onSelectChat(nextChat);
          } else {
            // 沒有對話了，重置為新對話
            onSelectChat(null as any);
          }
        }
      } catch (err) {
        toast.error("刪除失敗");
      }
    }
  };

  const openRenameDialog = (chat: ChatHistory) => {
    setSelectedChat(chat);
    setNewChatTitle(chat.title);
    setIsRenameDialogOpen(true);
  };

  const openDeleteDialog = (chat: ChatHistory) => {
    setSelectedChat(chat);
    setIsDeleteDialogOpen(true);
  };

  const handleNewChat = () => {
    onSelectChat(null as any);
  };

  const filteredHistory = chatHistory.filter(chat =>
    chat.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (isMobile && !isOpen) {
    return null;
  }

  return (
    <div className={`${isMobile ? 'fixed inset-y-0 left-0 z-40' : 'relative'} ${isOpen ? 'block' : 'hidden'} bg-sidebar border-r w-64 h-full flex flex-col`}>
      <div className="p-4 flex items-center justify-between border-b">
        <h2 className="font-semibold text-lg">歷史紀錄</h2>
        {isMobile && (
          <Button variant="ghost" size="icon" onClick={toggleSidebar}>
            <X className="h-5 w-5" />
          </Button>
        )}
      </div>

      <div className="p-3">
        <div className="relative">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="搜尋對話"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9 bg-muted/40"
          />
        </div>
      </div>

      <div className="p-2">
        <Button className="w-full justify-start" onClick={handleNewChat}>
          <MessageCircle className="mr-2 h-4 w-4" />
          新對話
        </Button>
      </div>

      <div className="flex-1 overflow-auto p-2">
        {filteredHistory.map((chat) => (
          <div
            key={chat.id}
            className={`rounded-md p-3 text-sm mb-1 hover:bg-sidebar-accent cursor-pointer flex justify-between items-center group ${chat.id === currentChatId ? 'bg-sidebar-accent' : ''
              }`}
            onClick={() => onSelectChat(chat)}
          >
            <span className="truncate">{chat.title}</span>
            <div className="flex items-center">
              <span className="text-xs text-muted-foreground mr-2">{chat.time}</span>
              {!chat.id.startsWith("temp-") && (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon" className="h-7 w-7 opacity-0 group-hover:opacity-100">
                      <MoreVertical className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => openRenameDialog(chat)}>
                      <Edit className="mr-2 h-4 w-4" />
                      重新命名
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem className="text-destructive" onClick={() => openDeleteDialog(chat)}>
                      <Trash2 className="mr-2 h-4 w-4" />
                      刪除對話
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Rename Dialog */}
      <Dialog
        open={isRenameDialogOpen}
        onOpenChange={(open) => {
          setIsRenameDialogOpen(open);
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>重新命名對話</DialogTitle>
            <DialogDescription>
              請輸入新的對話名稱
            </DialogDescription>
          </DialogHeader>
          <Input
            value={newChatTitle}
            onChange={(e) => setNewChatTitle(e.target.value)}
            placeholder="輸入對話名稱"
            className="mt-2"
          />
          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline">取消</Button>
            </DialogClose>
            <Button onClick={handleRenameChat}>確認</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Dialog */}
      <Dialog
        open={isDeleteDialogOpen}
        onOpenChange={(open) => {
          setIsDeleteDialogOpen(open);
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>刪除對話</DialogTitle>
            <DialogDescription>
              {selectedChat ? `確定要刪除「${selectedChat.title}」嗎？此操作無法還原。` : "確定要刪除這個對話嗎？此操作無法還原。"}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline">取消</Button>
            </DialogClose>
            <Button variant="destructive" onClick={handleDeleteChat}>刪除</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
