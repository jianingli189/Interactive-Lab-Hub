import { motion } from 'framer-motion';
import { actionTools } from '../config/recipeConfig';
import type { CookingSession } from '../state/useCookingSession';
import { useEffect, useState } from 'react';
import type { SensorBridge } from './useSensorBridge';

type Item = { present: boolean | null; valid: boolean; healthKnown: boolean };
type Snapshot = { receivedAt: number; utensils: Record<string, Item> };
const names: Record<string, string> = {
  chopsticks: 'Chopsticks', knife: 'Knife', spatula: 'Spatula',
  salt_shaker: 'Salt grinder', pepper_grinder: 'Pepper grinder',
};
export function UtensilPanel({ sensors, session }: { sensors: SensorBridge; session: CookingSession }) {
  const microId = session.micro?.id;
  const tool = actionTools[microId ?? ''];
  const progress = microId ? session.state.micro[microId] : undefined;
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [connected, setConnected] = useState(false);
  const [lastReceived, setLastReceived] = useState(0);
  const [now, setNow] = useState(Date.now());
  const { enabled, url } = sensors.status;
  useEffect(() => {
    setSnapshot(null); setConnected(false); setLastReceived(0);
    if (!enabled) return;
    const es = new EventSource(`${url.replace(/\/$/, '')}/events`);
    const accept = (data: unknown, fresh: boolean) => {
      const value = data as Snapshot | null;
      if (!value || typeof value !== 'object' || !value.utensils || typeof value.utensils !== 'object') return;
      for (const item of Object.values(value.utensils)) {
        if (!item || typeof item.valid !== 'boolean' || (item.present !== null && typeof item.present !== 'boolean')) return;
      }
      setSnapshot(value);
      if (fresh) setLastReceived(Date.now());
    };
    const parse = (event: Event) => {
      try { return JSON.parse((event as MessageEvent).data); } catch { return null; }
    };
    es.addEventListener('hello', e => {
      const v = parse(e); setConnected(v?.mqttConnected === true);
      // Wait for a fresh periodic state after reconnect; cached state never gets a new timestamp.
      setLastReceived(0); accept(v?.utensils, false);
    });
    es.addEventListener('utensil', e => { accept(parse(e), true); });
    es.addEventListener('utensil_link', e => { setConnected(parse(e)?.connected === true); setLastReceived(0); });
    es.onerror = () => { setConnected(false); setLastReceived(0); };
    const timer = setInterval(() => setNow(Date.now()), 500);
    return () => { clearInterval(timer); es.close(); };
  }, [enabled, url]);
  const fresh = connected && lastReceived > 0 && now - lastReceived < 3500;
  const item = tool ? snapshot?.utensils[tool] : undefined;
  const valid = fresh && item?.valid === true && item.healthKnown === true;
  const { act } = session;
  useEffect(() => {
    if (valid && microId && typeof item?.present === 'boolean') act({ type: 'TOOL_READING', microId, present: item.present });
  }, [valid, item?.present, microId, progress?.toolStage, act]);
  if (session.state.phase !== 'cooking' || !tool) return null;
  const stage = progress?.toolStage ?? 'pickup';
  const title = stage === 'pickup' ? `Pick up the ${names[tool].toLowerCase()}` : stage === 'using' ? `✓ Correct tool picked up · ${names[tool]}` : stage === 'return' ? `Return the ${names[tool].toLowerCase()} to its station` : `✓ ${names[tool]} returned`;
  return <aside className="utensil-panel tool-flow" aria-live="polite">
    <motion.div key={`${tool}:${stage}:${valid}`} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}>
      <div className={`tool-drawing ${stage}`} aria-hidden="true">
        <svg viewBox="0 0 100 70" width="100" height="70" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
          {tool === 'knife' ? <><path d="M20 45L65 15L74 27L38 50Z" fill="#d8e1db"/><path d="M20 45L10 53L16 61L30 50"/></> : tool === 'chopsticks' ? <><path d="M32 12L54 59M45 10L64 57"/></> : tool === 'spatula' ? <><path d="M48 35L30 60M48 35L33 24L50 6L70 23Z" fill="#e8b64b"/><path d="M47 17L56 24M42 23L50 29"/></> : <><path d="M37 18L34 52Q50 61 66 52L63 18Z" fill={tool === 'salt_shaker' ? '#eee8d8' : '#c99873'}/><path d="M37 18Q30 3 50 3Q70 3 63 18ZM40 38H60"/></>}
          <path d="M12 65H88" stroke="#91a875"/>
        </svg>
      </div>
      <strong>{title}</strong>
      <p>{stage === 'pickup' ? 'Pick up the tool, then confirm below.' : stage === 'using' ? 'Begin this action. Nod forward when finished.' : stage === 'return' ? 'Return the tool, then confirm below.' : progress?.status === 'done' ? 'Nod right to enter the next action.' : 'Check the result, then nod forward to complete.'}</p>
      {(stage === 'pickup' || stage === 'return') && <button
        className="confirm is-secondary tool-manual-button"
        disabled={session.state.paused}
        onClick={() => microId && act({ type: 'TOOL_MANUAL', microId, stage: stage === 'pickup' ? 'using' : 'returned', now: Date.now() })}
      >{stage === 'pickup' ? 'I have picked it up' : 'I have put it back'}</button>}
      <small>{progress?.toolManual ? 'Manually confirmed · not sensor-verified' : valid ? 'Tool sensor connected · manual confirmation available' : 'Tool sensor unavailable · please confirm manually'}</small>

    </motion.div>
  </aside>;
}
