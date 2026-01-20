
import { useNavigate, useSearchParams } from "react-router-dom";
import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Menu, MessageCircle, Facebook, Instagram, Linkedin, Globe, BookOpen, Library, LaptopIcon, Calendar } from "lucide-react";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { Separator } from "@/components/ui/separator";
import { Link } from "@/components/ui/link";

import { api } from "@/services/api";

export default function Landing() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    // Token is now handled via HttpOnly cookies set by backend redirect
    // Just clear URL params if they exist to be clean, though backend should redirect to /
    if (searchParams.get("token")) {
      navigate("/chat", { replace: true });
    }
  }, [searchParams, navigate]);

  const handleStartChat = async () => {
    try {
      await api.checkAuth();
      navigate('/chat');
    } catch (e) {
      navigate('/login');
    }
  };


  return (
    <div className="min-h-screen flex flex-col">
      <header className="py-3 px-4 flex items-center justify-end">
        <Sheet>
          <SheetTrigger asChild>
            <Button variant="ghost" size="icon" className="relative group">
              <Menu className="h-5 w-5" />
              <span className="sr-only">常用連結</span>
              <span className="absolute -bottom-8 right-0 w-max opacity-0 group-hover:opacity-100 transition-opacity bg-black text-white text-xs rounded px-2 py-1 pointer-events-none">
                常用連結
              </span>
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
                    <Link href="https://www.instagram.com/gdg.ntpu/" className="text-sm flex items-center gap-2">
                      <Instagram size={16} /> 主要粉專 | Instagram
                    </Link>
                  </li>
                  <li>
                    <Link href="https://www.facebook.com/dscntpu" className="text-sm flex items-center gap-2">
                      <Facebook size={16} /> 主要粉專 | Facebook
                    </Link>
                  </li>
                  <li>
                    <Link href="https://www.threads.net/@gdg.ntpu" className="text-sm flex items-center gap-2">
                      <Instagram size={16} /> 社團日常與特殊活動宣傳 | Threads
                    </Link>
                  </li>
                  <li>
                    <Link href="https://medium.com/@gdgntpu" className="text-sm flex items-center gap-2">
                      <BookOpen size={16} /> 社課與活動完整回顧 | Medium
                    </Link>
                  </li>
                  <li>
                    <Link href="https://www.linkedin.com/company/google-developer-groups-on-campus-ntpu" className="text-sm flex items-center gap-2">
                      <Linkedin size={16} /> 我們的商業名片 | LinkedIn
                    </Link>
                  </li>
                </ul>
              </div>

              <Separator />

              <div>
                <h3 className="text-sm font-medium mb-3">校內常用網站傳送門</h3>
                <ul className="space-y-2">
                  <li>
                    <Link href="https://new.ntpu.edu.tw/" className="text-sm flex items-center gap-2">
                      <Globe size={16} /> 國立臺北大學官網
                    </Link>
                  </li>
                  <li>
                    <Link href="https://lms3.ntpu.edu.tw/" className="text-sm flex items-center gap-2">
                      <LaptopIcon size={16} /> 數位學苑3.0
                    </Link>
                  </li>
                  <li>
                    <Link href="https://cof.ntpu.edu.tw/student_new.htm" className="text-sm flex items-center gap-2">
                      <BookOpen size={16} /> 學生資訊系統（舊版）
                    </Link>
                  </li>
                  <li>
                    <Link href="https://my.ntpu.edu.tw/login" className="text-sm flex items-center gap-2">
                      <BookOpen size={16} /> 學生資訊系統（新版單一登入）
                    </Link>
                  </li>
                  <li>
                    <Link href="https://cof.ntpu.edu.tw/pls/acad2/leave_sys.home" className="text-sm flex items-center gap-2">
                      <Calendar size={16} /> 學生請假系統
                    </Link>
                  </li>
                  <li>
                    <Link href="https://cof.ntpu.edu.tw/pls/eval/REG_2ORDER_M2.event_list?kw=" className="text-sm flex items-center gap-2">
                      <Calendar size={16} /> 活動線上報名系統
                    </Link>
                  </li>
                  <li>
                    <Link href="https://ireserve.lib.ntpu.edu.tw/sm/home_web.do" className="text-sm flex items-center gap-2">
                      <Library size={16} /> 圖書館空間座位管理系統
                    </Link>
                  </li>
                  <li>
                    <Link href="https://wpac.lib.ntpu.edu.tw/webpac/search.cfm" className="text-sm flex items-center gap-2">
                      <Library size={16} /> 圖書館館藏查詢
                    </Link>
                  </li>
                </ul>
              </div>
            </div>
          </SheetContent>
        </Sheet>
      </header>

      <main className="flex-1 flex flex-col items-center justify-center p-4">
        <div className="max-w-md w-full text-center space-y-8">
          <img
            src="/lovable-uploads/44239bf4-86bb-4b1e-ac1c-d73a9d1fb446.png"
            alt="NTPU LawHelper Logo"
            className="h-32 w-auto mx-auto"
          />

          <h1 className="text-xl font-medium">
            您好！我是北大法規問答小幫手
            <br />
            今天有什麼可以協助您的嗎？
          </h1>

          <Button
            onClick={handleStartChat}
            className="w-full max-w-xs mx-auto flex items-center gap-2 py-6"
          >
            <MessageCircle className="h-5 w-5" />
            開始對話
          </Button>
        </div>
      </main>
    </div>
  );
}
