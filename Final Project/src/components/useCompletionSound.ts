import { useEffect, useRef } from 'react';
// Browsers require one click/key press before audio can play.
export function useCompletionSound(stamp?: number) {
  const audio = useRef<AudioContext | null>(null);
  useEffect(() => {
    const unlock = () => {
      try { audio.current ??= new AudioContext(); void audio.current.resume().catch(() => {}); } catch { /* visual feedback remains available */ }
    };
    window.addEventListener('pointerdown', unlock);
    window.addEventListener('keydown', unlock);
    return () => { window.removeEventListener('pointerdown', unlock); window.removeEventListener('keydown', unlock); void audio.current?.close(); audio.current = null; };
  }, []);
  useEffect(() => {
    const ctx = audio.current;
    if (!stamp || !ctx || ctx.state !== 'running') return;
    [784, 988, 1175].forEach((frequency, i) => {
      const start = ctx.currentTime + i * 0.12;
      const oscillator = ctx.createOscillator(); const gain = ctx.createGain();
      oscillator.frequency.value = frequency;
      gain.gain.setValueAtTime(0, start); gain.gain.linearRampToValueAtTime(0.075, start + 0.015);
      gain.gain.exponentialRampToValueAtTime(0.001, start + 0.3);
      oscillator.connect(gain); gain.connect(ctx.destination);
      oscillator.start(start); oscillator.stop(start + 0.32);
      oscillator.onended = () => { oscillator.disconnect(); gain.disconnect(); };
    });
  }, [stamp]);
}
