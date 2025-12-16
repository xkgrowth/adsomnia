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
          </div>
          
          {/* Optional: Quick status or nav */}
          <nav className="hidden sm:flex items-center gap-6">
            <span className="label-caps text-text-secondary hover:text-text-primary cursor-pointer transition-colors">
              DASHBOARD
            </span>
            <span className="label-caps text-text-secondary hover:text-text-primary cursor-pointer transition-colors">
              REPORTS
            </span>
          </nav>
        </div>
      </header>

      <Chat />
    </main>
  );
}
