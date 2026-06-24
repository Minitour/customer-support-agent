import { useState, useRef, useEffect, useCallback } from "react";
import {
  Send,
  Bot,
  User,
  Wrench,
  ChevronDown,
  Loader2,
  MessageSquare,
  X,
  Maximize2,
  Minimize2,
  SquarePen,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { streamChat, chatApi } from "@/lib/api";
import { cn } from "@/lib/utils";
import { Markdown } from "@/components/chat/Markdown";
import { useScreenStore } from "@/store/screen";
import { useCartStore } from "@/store/cart";
import { useAuthStore } from "@/store/auth";

const CONVERSATION_ID_KEY = "chat_conversation_id";

interface ToolCall {
  name: string;
  input: string;
  output?: string;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  toolCalls?: ToolCall[];
  streaming?: boolean;
}

const INITIAL_MESSAGE: Message = {
  role: "assistant",
  content:
    "Hi! I'm ShopEase support. I can help you with order status, return policies, shipping info, and more. How can I help you today?",
};

function getStoredConversationId(): string | null {
  return localStorage.getItem(CONVERSATION_ID_KEY);
}

function setStoredConversationId(id: string): void {
  localStorage.setItem(CONVERSATION_ID_KEY, id);
}

function clearStoredConversationId(): void {
  localStorage.removeItem(CONVERSATION_ID_KEY);
}

export function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [maximized, setMaximized] = useState(false);
  const [messages, setMessages] = useState<Message[]>([INITIAL_MESSAGE]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const conversationIdRef = useRef<string | null>(getStoredConversationId());
  const abortRef = useRef<AbortController | null>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [expandedTools, setExpandedTools] = useState<Set<string>>(new Set());
  const productsOnScreen = useScreenStore((s) => s.productsOnScreen);
  const cartItems = useCartStore((s) => s.items);
  const user = useAuthStore((s) => s.user);
  const authLoading = useAuthStore((s) => s.loading);
  // Tracks the last *settled* user id so we can distinguish a real login/logout
  // from the initial null -> user hydration that happens on every page load.
  const prevUserIdRef = useRef<number | null | undefined>(undefined);

  // Scroll to bottom whenever messages change or chat opens
  useEffect(() => {
    if (open) bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, open]);

  // Keep the composer focused while the chat is open and not loading history.
  useEffect(() => {
    if (open && !loadingHistory) inputRef.current?.focus();
  }, [open, loadingHistory, streaming]);

  const startNewConversation = useCallback(() => {
    clearStoredConversationId();
    conversationIdRef.current = null;
    setMessages([INITIAL_MESSAGE]);
  }, []);

  // When auth state genuinely changes (login / logout), the stored conversation
  // id may no longer be valid for the new user context — reset to be safe.
  // We wait for auth to finish loading and skip the initial hydration so a
  // page refresh doesn't wipe an existing conversation.
  useEffect(() => {
    if (authLoading) return;
    const currentId = user?.id ?? null;
    if (prevUserIdRef.current === undefined) {
      // First settle after load — just record it, don't reset.
      prevUserIdRef.current = currentId;
      return;
    }
    if (prevUserIdRef.current !== currentId) {
      prevUserIdRef.current = currentId;
      startNewConversation();
    }
  }, [user, authLoading, startNewConversation]);

  // On open, if we have a stored conversation id, fetch its history
  useEffect(() => {
    if (!open) return;
    const storedId = conversationIdRef.current;
    if (!storedId) return;

    setLoadingHistory(true);
    chatApi
      .getConversation(storedId)
      .then((data) => {
        const loaded: Message[] = data.messages
          .filter((m) => m.role === "user" || m.role === "assistant")
          .map((m) => ({ role: m.role as "user" | "assistant", content: m.content }));
        setMessages(loaded.length > 0 ? loaded : [INITIAL_MESSAGE]);
      })
      .catch(() => {
        // 403/404 — conversation no longer accessible; start fresh
        clearStoredConversationId();
        conversationIdRef.current = null;
        setMessages([INITIAL_MESSAGE]);
      })
      .finally(() => setLoadingHistory(false));
    // Only run once per open when there's a stored id
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  const sendMessage = () => {
    const text = input.trim();
    if (!text || streaming) return;
    setInput("");

    const userMsg: Message = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg, { role: "assistant", content: "", streaming: true }]);
    setStreaming(true);
    // Keep focus on the composer so the user can immediately type the next message.
    inputRef.current?.focus();

    const context = {
      products_on_screen: productsOnScreen,
      products_in_cart: cartItems.map((i) => i.product.id),
    };

    let assistantContent = "";
    const toolCalls: ToolCall[] = [];
    let pendingTool: Partial<ToolCall> | null = null;

    abortRef.current = streamChat(
      {
        conversationId: conversationIdRef.current ?? undefined,
        message: text,
        context,
      },
      (id) => {
        conversationIdRef.current = id;
        setStoredConversationId(id);
      },
      (event) => {
        if (event.type === "token" && event.content) {
          assistantContent += event.content;
          setMessages((prev) => {
            const updated = [...prev];
            updated[updated.length - 1] = {
              role: "assistant",
              content: assistantContent,
              streaming: true,
              toolCalls: [...toolCalls],
            };
            return updated;
          });
        } else if (event.type === "tool_start" && event.name) {
          pendingTool = { name: event.name, input: event.input ?? "" };
        } else if (event.type === "tool_end" && pendingTool) {
          toolCalls.push({ ...pendingTool, output: event.output ?? "" } as ToolCall);
          pendingTool = null;
          setMessages((prev) => {
            const updated = [...prev];
            updated[updated.length - 1] = {
              role: "assistant",
              content: assistantContent,
              streaming: true,
              toolCalls: [...toolCalls],
            };
            return updated;
          });
        }
      },
      () => {
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            role: "assistant",
            content: assistantContent || "I couldn't generate a response. Please try again.",
            streaming: false,
            toolCalls: [...toolCalls],
          };
          return updated;
        });
        setStreaming(false);
      },
      (err) => {
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            role: "assistant",
            content: `Error: ${err}`,
            streaming: false,
          };
          return updated;
        });
        setStreaming(false);
      }
    );
  };

  const toggleTool = (key: string) => {
    setExpandedTools((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        aria-label="Open support chat"
        className="fixed bottom-6 right-6 z-50 h-14 w-14 rounded-full bg-gray-900 text-white shadow-lg flex items-center justify-center cursor-pointer hover:bg-gray-800 hover:scale-105 transition-[transform,background-color] duration-150 anim-fab"
      >
        <MessageSquare className="h-6 w-6" />
      </button>
    );
  }

  return (
    <div
      className={cn(
        "fixed z-50 flex flex-col bg-white shadow-2xl border border-gray-200 overflow-hidden anim-chat-panel",
        maximized
          ? "inset-2 sm:inset-6 rounded-2xl"
          : "bottom-6 right-6 w-[calc(100vw-3rem)] sm:w-[400px] h-[600px] max-h-[calc(100vh-3rem)] rounded-2xl"
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b bg-gray-900 text-white flex-shrink-0">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-full bg-white/10 flex items-center justify-center">
            <Bot className="h-4 w-4" />
          </div>
          <div>
            <p className="text-sm font-semibold leading-tight">ShopEase Support</p>
            <p className="text-xs text-white/60 leading-tight">Always here to help</p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={startNewConversation}
            aria-label="New conversation"
            title="New conversation"
            disabled={streaming}
            className="h-8 w-8 rounded-md flex items-center justify-center cursor-pointer hover:bg-white/10 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <SquarePen className="h-4 w-4" />
          </button>
          <button
            onClick={() => setMaximized((m) => !m)}
            aria-label={maximized ? "Restore chat" : "Maximize chat"}
            className="h-8 w-8 rounded-md flex items-center justify-center cursor-pointer hover:bg-white/10 transition-colors"
          >
            {maximized ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
          </button>
          <button
            onClick={() => setOpen(false)}
            aria-label="Close chat"
            className="h-8 w-8 rounded-md flex items-center justify-center cursor-pointer hover:bg-white/10 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {loadingHistory ? (
          <div className="flex items-center justify-center h-full">
            <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} className="message-bubble">
              <div className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                {msg.role === "assistant" && (
                  <div className="h-8 w-8 rounded-full bg-gray-900 flex items-center justify-center flex-shrink-0">
                    <Bot className="h-4 w-4 text-white" />
                  </div>
                )}
                <div
                  className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm ${
                    msg.role === "user"
                      ? "bg-gray-900 text-white rounded-br-sm"
                      : "bg-gray-100 text-gray-900 rounded-bl-sm"
                  }`}
                >
                  {msg.content ? (
                    msg.role === "assistant" ? (
                      <Markdown content={msg.content} />
                    ) : (
                      msg.content
                    )
                  ) : (
                    msg.streaming && <Loader2 className="h-4 w-4 animate-spin" />
                  )}
                </div>
                {msg.role === "user" && (
                  <div className="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                    <User className="h-4 w-4 text-gray-600" />
                  </div>
                )}
              </div>

              {/* Tool calls panel */}
              {msg.role === "assistant" && msg.toolCalls && msg.toolCalls.length > 0 && (
                <div className="ml-11 mt-2 space-y-1">
                  {msg.toolCalls.map((tc, ti) => {
                    const key = `${idx}-${ti}`;
                    const expanded = expandedTools.has(key);
                    return (
                      <div key={ti} className="rounded-lg border border-blue-100 bg-blue-50 text-xs overflow-hidden">
                        <button
                          className="flex items-center gap-2 w-full px-3 py-2 text-left cursor-pointer hover:bg-blue-100 transition-colors"
                          onClick={() => toggleTool(key)}
                        >
                          <Wrench className="h-3 w-3 text-blue-500 flex-shrink-0" />
                          <span className="font-medium text-blue-700">{tc.name}</span>
                          <ChevronDown
                            className="h-3 w-3 text-blue-400 ml-auto transition-transform duration-200"
                            style={{ transform: expanded ? "rotate(0deg)" : "rotate(-90deg)" }}
                          />
                        </button>
                        {/* CSS grid-row accordion — no hard cuts */}
                        <div className={`tool-expand ${expanded ? "tool-expand--open" : ""}`}>
                          <div>
                            <div className="px-3 pb-3 space-y-2">
                              <div>
                                <p className="text-blue-500 font-semibold mb-1">Input</p>
                                <pre className="text-gray-700 whitespace-pre-wrap break-all font-mono text-xs bg-white/60 rounded p-2">
                                  {tc.input}
                                </pre>
                              </div>
                              {tc.output && (
                                <div>
                                  <p className="text-blue-500 font-semibold mb-1">Output</p>
                                  <pre className="text-gray-700 whitespace-pre-wrap break-all font-mono text-xs bg-white/60 rounded p-2">
                                    {tc.output}
                                  </pre>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          ))
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="border-t bg-white p-3 flex-shrink-0">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            sendMessage();
          }}
          className="flex gap-2"
        >
          <Input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your order, policies, returns..."
            className="flex-1"
          />
          <Button type="submit" disabled={streaming || loadingHistory || !input.trim()} size="icon">
            {streaming ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          </Button>
        </form>
      </div>
    </div>
  );
}
