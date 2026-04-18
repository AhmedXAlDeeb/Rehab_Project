import type { SignalMatrix } from "../types/api";

export const SIGNAL_CHANNELS = 12;
export const SIGNAL_TIMESTEPS = 400;

function pseudoRandom(seed: number): () => number {
  let state = seed >>> 0;
  return () => {
    state = (1664525 * state + 1013904223) >>> 0;
    return state / 0xffffffff;
  };
}

export function createMockSignal(seed = Date.now()): SignalMatrix {
  const rand = pseudoRandom(seed);

  return Array.from({ length: SIGNAL_CHANNELS }, (_, channelIdx) => {
    const freq = 1.0 + channelIdx * 0.27;
    const phase = rand() * Math.PI * 2;
    const amplitude = 0.35 + rand() * 0.55;

    return Array.from({ length: SIGNAL_TIMESTEPS }, (_, t) => {
      const x = t / SIGNAL_TIMESTEPS;
      const wave = Math.sin(2 * Math.PI * freq * x + phase);
      const harmonic = 0.35 * Math.sin(2 * Math.PI * (freq * 2.1) * x + phase / 2);
      const noise = (rand() - 0.5) * 0.08;
      return Number((amplitude * wave + harmonic + noise).toFixed(6));
    });
  });
}

export function hasValidSignalShape(signal: SignalMatrix): boolean {
  if (signal.length !== SIGNAL_CHANNELS) {
    return false;
  }

  return signal.every((channel) => channel.length === SIGNAL_TIMESTEPS);
}
