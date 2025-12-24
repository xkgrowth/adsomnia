"use client";

import { useState, useEffect } from "react";

const PASSWORD = "TalkToDataAdsomnia";
const AUTH_KEY = "adsomnia_authenticated";

interface PasswordProtectionProps {
  children: React.ReactNode;
}

export default function PasswordProtection({ children }: PasswordProtectionProps) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is already authenticated in this session
    const authStatus = sessionStorage.getItem(AUTH_KEY);
    if (authStatus === "true") {
      setIsAuthenticated(true);
    }
    setIsLoading(false);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (password === PASSWORD) {
      sessionStorage.setItem(AUTH_KEY, "true");
      setIsAuthenticated(true);
      setPassword("");
    } else {
      setError("Incorrect password. Please try again.");
      setPassword("");
    }
  };

  // Show loading state briefly to prevent flash
  if (isLoading) {
    return (
      <div className="min-h-screen bg-bg-primary flex items-center justify-center">
        <div className="text-text-muted font-mono text-sm">Loading...</div>
      </div>
    );
  }

  // Show password prompt if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-bg-primary flex items-center justify-center">
        <div className="bg-bg-secondary border border-border p-8 max-w-md w-full mx-4">
          <div className="mb-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="h-12 w-12 bg-accent-yellow flex items-center justify-center">
                <span className="font-headline text-2xl text-black tracking-tight">
                  A!
                </span>
              </div>
              <div>
                <h1 className="font-headline text-2xl tracking-wider text-text-primary">
                  ADSOMNIA
                </h1>
                <p className="font-mono text-xs tracking-widest text-text-muted">
                  TALK-TO-DATA
                </p>
              </div>
            </div>
            <p className="text-sm text-text-secondary">
              Please enter the password to access the application.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <input
                type="password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  setError("");
                }}
                placeholder="Enter password"
                className="w-full px-4 py-3 bg-bg-tertiary border border-border text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent-yellow transition-colors font-body"
                autoFocus
              />
              {error && (
                <p className="text-xs text-accent-orange mt-2 font-mono">
                  {error}
                </p>
              )}
            </div>
            <button
              type="submit"
              disabled={!password.trim()}
              className="w-full btn-primary py-3 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              ENTER
            </button>
          </form>
        </div>
      </div>
    );
  }

  // Show the protected content
  return <>{children}</>;
}

