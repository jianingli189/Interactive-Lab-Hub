// Explicit, non-persistent mode for testing real motion sensors without tool stations.
export const motionOnly = typeof window !== 'undefined' &&
  new URLSearchParams(window.location.search).get('tools') === 'off';
