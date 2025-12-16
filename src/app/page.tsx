import Chat from "@/components/Chat";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col">
      <header className="border-b border-[var(--border)] px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-lg bg-[var(--primary)] flex items-center justify-center">
            <span className="text-white font-bold text-sm">A</span>
          </div>
          <div>
            <h1 className="font-semibold">Adsomnia</h1>
            <p className="text-xs text-[var(--muted)]">Talk-to-Data Agent</p>
          </div>
        </div>
      </header>
      
      <Chat />
    </main>
  );
}

