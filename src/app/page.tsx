import Chat from "@/components/Chat";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col bg-bg-primary">
      {/* Top brand bar */}
      <header className="border-b border-border px-6 py-3 bg-bg-secondary">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            {/* Logo mark - A! badge style */}
            <div className="relative">
              <div className="h-10 w-10 bg-accent-yellow flex items-center justify-center">
                <span className="font-headline text-xl text-black tracking-tight">
                  A!
                </span>
              </div>
            </div>
            <div>
              <h1 className="font-headline text-xl tracking-wider text-text-primary">
                ADSOMNIA
              </h1>
              <p className="font-mono text-[10px] tracking-widest text-text-muted">
                TALK-TO-DATA
              </p>
            </div>
            {/* Online indicator */}
            <div className="flex items-center gap-2 ml-2">
              <span className="w-2 h-2 bg-success rounded-full animate-pulse" />
              <span className="label-caps text-success">ONLINE</span>
            </div>
          </div>
          
          {/* Main navigation */}
          <nav className="hidden sm:flex items-center gap-6">
            <span className="label-caps !text-text-primary !font-bold cursor-pointer transition-colors">
              CHAT
            </span>
            <span className="label-caps text-text-secondary/50 cursor-not-allowed transition-colors flex items-center gap-2">
              ALERT
              <span className="text-[8px] px-1.5 py-0.5 bg-accent-orange/20 text-accent-orange rounded font-mono">
                SOON
              </span>
            </span>
            <span className="label-caps text-text-secondary/50 cursor-not-allowed transition-colors flex items-center gap-2">
              CREATE
              <span className="text-[8px] px-1.5 py-0.5 bg-accent-orange/20 text-accent-orange rounded font-mono">
                SOON
              </span>
            </span>
          </nav>
        </div>
      </header>

      <Chat />
    </main>
  );
}
