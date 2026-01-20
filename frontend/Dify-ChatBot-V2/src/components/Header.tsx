
import { Button } from "@/components/ui/button";
import { Menu, UserRound, PanelLeft } from "lucide-react";
import { Link } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { Separator } from "@/components/ui/separator";
import { Link as UILink } from "@/components/ui/link";
import {
  Facebook,
  Instagram,
  Linkedin,
  Globe,
  BookOpen,
  Library,
  LaptopIcon,
  Calendar,
} from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

import { api } from "@/services/api";

interface HeaderProps {
  toggleSidebar: () => void;
  currentChatTitle?: string;
}

export default function Header({ toggleSidebar, currentChatTitle = "無標題對話" }: HeaderProps) {
  const { isAuthenticated } = useAuth();

  const handleLogout = () => {
    api.logout();
  };

  return (
    <header className="border-b py-3 px-4 flex items-center justify-between bg-white">
      <Link to="/" className="flex items-center gap-2">
        <img
          src="/lovable-uploads/44239bf4-86bb-4b1e-ac1c-d73a9d1fb446.png"
          alt="NTPU LawHelper Logo"
          className="h-8 w-auto"
        />
      </Link>
      <div className="text-xs text-muted-foreground">
        {currentChatTitle}
      </div>
      <div className="flex items-center gap-2">
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" onClick={toggleSidebar}>
                <PanelLeft className="h-5 w-5" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              <p>隱藏側邊欄</p>
            </TooltipContent>
          </Tooltip>

          {isAuthenticated ? (
            <Button variant="outline" size="sm" onClick={handleLogout}>
              登出
            </Button>
          ) : (
            <Link to="/login">
              <Button variant="outline" size="sm">登入</Button>
            </Link>
          )}

          <Tooltip>
            <TooltipTrigger asChild>
              <Sheet>
                <SheetTrigger asChild>
                  <Button variant="ghost" size="icon">
                    <Menu className="h-5 w-5" />
                  </Button>
                </SheetTrigger>
                <SheetContent side="right">
                  <SheetHeader>
                    <SheetTitle>常用連結</SheetTitle>
                  </SheetHeader>
                  <div className="py-6 space-y-6">
                    <div>
                      <h3 className="text-sm font-medium mb-3">GDG on Campus NTPU 粉絲專頁</h3>
                      <ul className="space-y-2">
                        <li>
                          <UILink href="https://www.instagram.com/gdg.ntpu/" className="text-sm flex items-center gap-2">
                            <Instagram size={16} /> 主要粉專 | Instagram
                          </UILink>
                        </li>
                        <li>
                          <UILink href="https://www.facebook.com/dscntpu" className="text-sm flex items-center gap-2">
                            <Facebook size={16} /> 主要粉專 | Facebook
                          </UILink>
                        </li>
                        <li>
                          <UILink href="https://www.threads.net/@gdg.ntpu" className="text-sm flex items-center gap-2">
                            <Instagram size={16} /> 社團日常與特殊活動宣傳 | Threads
                          </UILink>
                        </li>
                        <li>
                          <UILink href="https://medium.com/@gdgntpu" className="text-sm flex items-center gap-2">
                            <BookOpen size={16} /> 社課與活動完整回顧 | Medium
                          </UILink>
                        </li>
                        <li>
                          <UILink href="https://www.linkedin.com/company/google-developer-groups-on-campus-ntpu" className="text-sm flex items-center gap-2">
                            <Linkedin size={16} /> 我們的商業名片 | LinkedIn
                          </UILink>
                        </li>
                      </ul>
                    </div>

                    <Separator />

                    <div>
                      <h3 className="text-sm font-medium mb-3">校內常用網站傳送門</h3>
                      <ul className="space-y-2">
                        <li>
                          <UILink href="https://new.ntpu.edu.tw/" className="text-sm flex items-center gap-2">
                            <Globe size={16} /> 國立臺北大學官網
                          </UILink>
                        </li>
                        <li>
                          <UILink href="https://lms3.ntpu.edu.tw/" className="text-sm flex items-center gap-2">
                            <LaptopIcon size={16} /> 數位學苑3.0
                          </UILink>
                        </li>
                        <li>
                          <UILink href="https://cof.ntpu.edu.tw/student_new.htm" className="text-sm flex items-center gap-2">
                            <BookOpen size={16} /> 學生資訊系統（舊版）
                          </UILink>
                        </li>
                        <li>
                          <UILink href="https://my.ntpu.edu.tw/login" className="text-sm flex items-center gap-2">
                            <BookOpen size={16} /> 學生資訊系統（新版單一登入）
                          </UILink>
                        </li>
                        <li>
                          <UILink href="https://cof.ntpu.edu.tw/pls/acad2/leave_sys.home" className="text-sm flex items-center gap-2">
                            <Calendar size={16} /> 學生請假系統
                          </UILink>
                        </li>
                        <li>
                          <UILink href="https://cof.ntpu.edu.tw/pls/eval/REG_2ORDER_M2.event_list?kw=" className="text-sm flex items-center gap-2">
                            <Calendar size={16} /> 活動線上報名系統
                          </UILink>
                        </li>
                        <li>
                          <UILink href="https://ireserve.lib.ntpu.edu.tw/sm/home_web.do" className="text-sm flex items-center gap-2">
                            <Library size={16} /> 圖書館空間座位管理系統
                          </UILink>
                        </li>
                        <li>
                          <UILink href="https://wpac.lib.ntpu.edu.tw/webpac/search.cfm" className="text-sm flex items-center gap-2">
                            <Library size={16} /> 圖書館館藏查詢
                          </UILink>
                        </li>
                      </ul>
                    </div>
                  </div>
                </SheetContent>
              </Sheet>
            </TooltipTrigger>
            <TooltipContent>
              <p>常用連結</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>
    </header>
  );
}
