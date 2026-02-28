// iOS Audio Unlock + Asset Preloader for party games.
// iOS Safari blocks audio playback until a user gesture triggers it.
// This component unlocks the AudioContext on the first tap, then preloads
// all game sounds during the lobby phase so gameplay audio is instant.
//
// Usage:
//   Render <AudioProvider> at the app root.
//   Call useAudio().play('buzzer') from any component.

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";
import { Howl, Howler } from "howler";

// ── Types ──────────────────────────────────────────────────────────────────────

interface SoundManifest {
  [key: string]: string; // name -> URL
}

interface AudioContextValue {
  /** Whether the AudioContext is unlocked and ready. */
  unlocked: boolean;
  /** Preload progress 0-1. */
  progress: number;
  /** Play a named sound. No-op if not yet unlocked. */
  play: (name: string) => void;
  /** Stop a named sound. */
  stop: (name: string) => void;
  /** Preload all sounds in the manifest. Call during lobby. */
  preload: (manifest: SoundManifest) => void;
}

const AudioCtx = createContext<AudioContextValue | null>(null);

// ── Provider ───────────────────────────────────────────────────────────────────

export function AudioProvider({ children }: { children: React.ReactNode }) {
  const [unlocked, setUnlocked] = useState(false);
  const [progress, setProgress] = useState(0);
  const sounds = useRef<Map<string, Howl>>(new Map());
  const totalCount = useRef(0);
  const loadedCount = useRef(0);

  // ── iOS unlock ─────────────────────────────────────────────────────────────
  // A silent Howl triggered by user gesture unlocks the global AudioContext.
  // We listen on touchstart AND click to cover all mobile browsers.
  useEffect(() => {
    if (unlocked) return;

    const unlock = () => {
      // Howler exposes the global AudioContext — resume it if suspended.
      const ctx = Howler.ctx;
      if (ctx && ctx.state === "suspended") {
        ctx.resume().then(() => {
          setUnlocked(true);
          cleanup();
        });
      } else {
        setUnlocked(true);
        cleanup();
      }
    };

    const cleanup = () => {
      document.removeEventListener("touchstart", unlock, true);
      document.removeEventListener("click", unlock, true);
    };

    document.addEventListener("touchstart", unlock, { capture: true, once: false });
    document.addEventListener("click", unlock, { capture: true, once: false });

    // Already unlocked (desktop browsers usually are)
    if (Howler.ctx?.state === "running") {
      setUnlocked(true);
      cleanup();
    }

    return cleanup;
  }, [unlocked]);

  // ── Preload ────────────────────────────────────────────────────────────────
  const preload = useCallback((manifest: SoundManifest) => {
    const entries = Object.entries(manifest);
    totalCount.current = entries.length;
    loadedCount.current = 0;
    setProgress(0);

    for (const [name, url] of entries) {
      if (sounds.current.has(name)) {
        loadedCount.current++;
        continue;
      }

      const howl = new Howl({
        src: [url],
        preload: true,
        onload: () => {
          loadedCount.current++;
          setProgress(loadedCount.current / totalCount.current);
        },
        onloaderror: (_id, err) => {
          console.warn(`[audio] Failed to preload "${name}":`, err);
          loadedCount.current++;
          setProgress(loadedCount.current / totalCount.current);
        },
      });

      sounds.current.set(name, howl);
    }
  }, []);

  // ── Play / Stop ────────────────────────────────────────────────────────────
  const play = useCallback(
    (name: string) => {
      if (!unlocked) return;
      const howl = sounds.current.get(name);
      if (!howl) {
        console.warn(`[audio] Sound "${name}" not preloaded`);
        return;
      }
      howl.play();
    },
    [unlocked]
  );

  const stop = useCallback((name: string) => {
    sounds.current.get(name)?.stop();
  }, []);

  return (
    <AudioCtx.Provider value={{ unlocked, progress, play, stop, preload }}>
      {children}
    </AudioCtx.Provider>
  );
}

// ── Hook ─────────────────────────────────────────────────────────────────────

export function useAudio(): AudioContextValue {
  const ctx = useContext(AudioCtx);
  if (!ctx) throw new Error("useAudio must be used within <AudioProvider>");
  return ctx;
}

// ── Example usage in a lobby component ───────────────────────────────────────
//
// function Lobby() {
//   const { preload, progress, unlocked } = useAudio();
//
//   useEffect(() => {
//     preload({
//       'buzzer':  '/sounds/buzzer.mp3',
//       'correct': '/sounds/correct.mp3',
//       'tick':    '/sounds/tick.mp3',
//       'reveal':  '/sounds/reveal.mp3',
//       'winner':  '/sounds/winner.mp3',
//     });
//   }, [preload]);
//
//   return (
//     <div>
//       {!unlocked && <p>Tap anywhere to enable sound</p>}
//       {unlocked && progress < 1 && <p>Loading sounds... {Math.round(progress * 100)}%</p>}
//       {/* lobby UI */}
//     </div>
//   );
// }
