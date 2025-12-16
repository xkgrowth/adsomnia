"use client";

import { useState, useRef, useEffect } from "react";
import { sendChatMessage, fetchEntities, type Affiliate, type Offer } from "@/lib/api";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
};

type ExampleQueryCategory = {
  category: string;
  queries: string[];
};

// Get real IDs from environment variables if available, otherwise use test data
const getFallbackAffiliates = (): Affiliate[] => {
  // Check for environment variable override
  const envAffiliates = process.env.NEXT_PUBLIC_AFFILIATE_IDS;
  if (envAffiliates) {
    try {
      const ids = JSON.parse(envAffiliates);
      return ids.map((aff: any) => ({
        affiliate_id: typeof aff === 'number' ? aff : aff.id,
        affiliate_name: typeof aff === 'object' ? aff.name : `Partner ${aff}`
      }));
    } catch (e) {
      console.warn("Failed to parse NEXT_PUBLIC_AFFILIATE_IDS, using default");
    }
  }
  // Default test data
  return [
    { affiliate_id: 12345, affiliate_name: "Premium Traffic Partners" },
    { affiliate_id: 23456, affiliate_name: "Global Media Network" },
    { affiliate_id: 34567, affiliate_name: "Digital Marketing Pro" },
  ];
};

const getFallbackOffers = (): Offer[] => {
  // Check for environment variable override
  const envOffers = process.env.NEXT_PUBLIC_OFFER_IDS;
  if (envOffers) {
    try {
      const ids = JSON.parse(envOffers);
      return ids.map((offer: any) => ({
        offer_id: typeof offer === 'number' ? offer : offer.id,
        offer_name: typeof offer === 'object' ? offer.name : `Offer ${offer}`
      }));
    } catch (e) {
      console.warn("Failed to parse NEXT_PUBLIC_OFFER_IDS, using default");
    }
  }
  // Default test data
  return [
    { offer_id: 1001, offer_name: "Summer Promo 2024" },
    { offer_id: 1002, offer_name: "Holiday Special" },
    { offer_id: 1003, offer_name: "Evergreen Offer A" },
  ];
};

const FALLBACK_AFFILIATES = getFallbackAffiliates();
const FALLBACK_OFFERS = getFallbackOffers();

// Generate example queries using real IDs
const generateExampleQueries = (affiliates: Affiliate[], offers: Offer[]): ExampleQueryCategory[] => {
  const aff1 = affiliates[0];
  const aff2 = affiliates[1] || affiliates[0];
  const offer1 = offers[0];
  const offer2 = offers[1] || offers[0];
  const offer3 = offers[2] || offers[0];

  return [
    {
      category: "Landing Pages",
      queries: [
        offer1 ? `Which landing pages work best for ${offer1.offer_name}?` : "Which landing pages work best for Summer Promo 2024?",
        offer1 ? `Show me top 3 landing pages for ${offer1.offer_name} in the US` : "Show me top 3 landing pages for Summer Promo 2024 in the US",
        aff1 ? `What's the best converting LP for ${aff1.affiliate_name}?` : "What's the best converting LP for Premium Traffic Partners?",
        offer2 ? `Top landing pages for ${offer2.offer_name} in Germany` : "Top landing pages for Holiday Special in Germany",
        offer2 ? `Which LPs perform best for ${offer2.offer_name}?` : "Which LPs perform best for Holiday Special?",
      ],
    },
    {
      category: "Export Reports",
      queries: [
        "Export fraud report for last week",
        offer1 ? `Download conversion data for ${offer1.offer_name} from December` : "Download conversion data for Summer Promo 2024 from December",
        "Get me a CSV of conversions with tracking parameters for last month",
        offer1 ? `Export stats for ${offer1.offer_name} from November 1st to 15th` : "Export stats for Summer Promo 2024 from November 1st to 15th",
        aff1 ? `Pull a scrub analysis report for ${aff1.affiliate_name}` : "Pull a scrub analysis report for Premium Traffic Partners",
      ],
    },
  ];
};

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [threadId, setThreadId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [affiliates, setAffiliates] = useState<Affiliate[]>(FALLBACK_AFFILIATES);
  const [offers, setOffers] = useState<Offer[]>(FALLBACK_OFFERS);
  const [entitiesLoading, setEntitiesLoading] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Fetch real entities on mount
  useEffect(() => {
    const loadEntities = async () => {
      try {
        setEntitiesLoading(true);
        const data = await fetchEntities();
        console.log("Fetched entities response:", JSON.stringify(data, null, 2));
        console.log(`Affiliate count: ${data.affiliate_count}, Offer count: ${data.offer_count}`);
        
        if (data.affiliates && data.affiliates.length > 0) {
          console.log(`✅ Loaded ${data.affiliates.length} real affiliates:`, data.affiliates);
          setAffiliates(data.affiliates);
        } else {
          console.warn("⚠️  No affiliates returned from API, using fallback data");
          console.warn("API returned:", data);
        }
        if (data.offers && data.offers.length > 0) {
          console.log(`✅ Loaded ${data.offers.length} real offers:`, data.offers);
          setOffers(data.offers);
        } else {
          console.warn("⚠️  No offers returned from API, using fallback data");
          console.warn("API returned:", data);
        }
      } catch (err) {
        console.error("❌ Failed to fetch real entities, using fallback data:", err);
        // Keep fallback data
      } finally {
        setEntitiesLoading(false);
      }
    };

    loadEntities();
  }, []);

  // Generate example queries with current entities
  const exampleQueries = generateExampleQueries(affiliates, offers);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const submitMessage = async (messageContent: string) => {
    if (!messageContent.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: messageContent.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    setError(null);

    try {
      // Call the API
      const response = await sendChatMessage(userMessage.content, threadId || undefined);
      
      // Update thread ID if provided
      if (response.thread_id) {
        setThreadId(response.thread_id);
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.response,
        timestamp: new Date(),
      };
      
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to get response";
      setError(errorMessage);
      
      const errorResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `**Error**\n\n${errorMessage}\n\nPlease check that the API server is running at http://localhost:8000`,
        timestamp: new Date(),
      };
      
      setMessages((prev) => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await submitMessage(input);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleExampleClick = (query: string) => {
    // Automatically submit the example query
    submitMessage(query);
  };

  const formatContent = (content: string) => {
    // Split by markdown patterns and format
    const parts = content.split(/(\*\*.*?\*\*|`.*?`|\n)/);
    return parts.map((part, i) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return (
          <strong key={i} className="text-accent-yellow font-semibold">
            {part.slice(2, -2)}
          </strong>
        );
      }
      if (part.startsWith("`") && part.endsWith("`")) {
        return (
          <code key={i} className="bg-bg-secondary px-1 py-0.5 rounded text-xs font-mono">
            {part.slice(1, -1)}
          </code>
        );
      }
      if (part === "\n") {
        return <br key={i} />;
      }
      return part;
    });
  };

  return (
    <div className="flex flex-1 flex-col h-full bg-bg-primary">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
        {/* Example Queries - Show when no messages */}
        {messages.length === 0 && (
          <div className="flex justify-start message-enter">
            <div className="max-w-[85%]">
              <div className="border-l-2 border-accent-yellow pl-4">
                <div className="space-y-4">
                  {exampleQueries.map((category, catIdx) => (
                    <div key={catIdx} className="space-y-2">
                      <div className="text-xs font-semibold text-accent-yellow uppercase tracking-wide mb-2">
                        {category.category}
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {category.queries.map((query, qIdx) => (
                          <button
                            key={qIdx}
                            onClick={() => handleExampleClick(query)}
                            className="text-xs px-3 py-1.5 border border-border bg-bg-tertiary hover:bg-bg-secondary hover:border-accent-yellow text-text-primary transition-colors rounded cursor-pointer"
                          >
                            {query}
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`message-enter flex ${
              message.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            {message.role === "assistant" ? (
              // Agent message - left accent border style
              <div className="max-w-[85%]">
                <div className="flex items-center gap-2 mb-2">
                  <span className="label-caps text-accent-yellow">
                    ADSOMNIA AGENT
                  </span>
                  <span className="text-xs text-text-muted font-mono">
                    {message.timestamp.toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                </div>
                <div className="border-l-2 border-accent-yellow pl-4">
                  <div className="text-sm leading-relaxed text-text-primary whitespace-pre-wrap">
                    {formatContent(message.content)}
                  </div>
                </div>
              </div>
            ) : (
              // User message - bordered box style
              <div className="max-w-[85%]">
                <div className="flex items-center justify-end gap-2 mb-2">
                  <span className="text-xs text-text-muted font-mono">
                    {message.timestamp.toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                  <span className="label-caps text-text-secondary">YOU</span>
                </div>
                <div className="border border-border bg-bg-tertiary px-4 py-3">
                  <div className="text-sm leading-relaxed text-text-primary whitespace-pre-wrap">
                    {message.content}
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}

        {/* Typing indicator */}
        {isLoading && (
          <div className="flex justify-start message-enter">
            <div className="max-w-[85%]">
              <div className="flex items-center gap-2 mb-2">
                <span className="label-caps text-accent-yellow">
                  ADSOMNIA AGENT
                </span>
              </div>
              <div className="border-l-2 border-accent-yellow pl-4">
                <div className="flex gap-1.5 py-2">
                  <span className="typing-dot h-2 w-2 bg-accent-yellow" />
                  <span className="typing-dot h-2 w-2 bg-accent-yellow" />
                  <span className="typing-dot h-2 w-2 bg-accent-yellow" />
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-border px-6 py-4">
        <form onSubmit={handleSubmit} className="flex gap-4">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about your Everflow data..."
              className="w-full resize-none border border-border bg-bg-tertiary px-4 py-3 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent-yellow transition-colors font-body"
              rows={1}
              disabled={isLoading}
            />
          </div>
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="btn-primary px-8"
          >
            SEND
          </button>
        </form>
        {error && (
          <p className="text-xs text-accent-orange mt-2 text-center font-mono">
            ⚠️ {error}
          </p>
        )}
        <p className="text-xs text-text-muted mt-3 text-center font-mono tracking-wide">
          ENTER TO SEND • SHIFT+ENTER FOR NEW LINE
        </p>
      </div>
    </div>
  );
}
