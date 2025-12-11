export default function Loading() {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-3xl animate-blob" />
        <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-pink-500/20 rounded-full blur-3xl animate-blob" style={{ animationDelay: "2s" }} />
        <div className="absolute bottom-1/4 left-1/3 w-96 h-96 bg-cyan-500/20 rounded-full blur-3xl animate-blob" style={{ animationDelay: "4s" }} />
      </div>

      <div className="relative flex flex-col items-center gap-8">
        {/* Logo Animation */}
        <div className="relative">
          <div className="w-20 h-20 rounded-2xl gradient-bg flex items-center justify-center animate-bounce-subtle">
            <span className="text-white font-bold text-4xl">S</span>
          </div>
          {/* Pulse Ring */}
          <div className="absolute inset-0 rounded-2xl gradient-bg animate-ping opacity-20" />
        </div>

        {/* Loading Text */}
        <div className="flex flex-col items-center gap-2">
          <p className="text-xl font-semibold gradient-text">Loading</p>
          <div className="flex gap-1">
            <span className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "0ms" }} />
            <span className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "150ms" }} />
            <span className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "300ms" }} />
          </div>
        </div>
      </div>
    </div>
  );
}
