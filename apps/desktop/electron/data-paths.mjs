// data-paths.mjs — the pure path-resolution core, shared by the desktop app
// (via data-paths.ts, a typed re-export) and the CI smoke driver (which runs
// under Node's type-stripping and therefore cannot import the app's
// extensionless TypeScript directly). No Electron imports here; only node:path.
//
// data-paths.ts re-exports these names and adds the TypeScript-facing
// `HermesHomeOptions` interface. Keep the two in lockstep: every behavior in
// this file is exercised by data-paths.test.ts through the re-export.

import path from 'node:path'

/** A HERMES_HOME rooted inside a `profiles/` directory names the profile's
 * parent (the home), not the profile directory itself. */
function normalizeHermesHomeRoot(hermesHome, pathModule) {
  if (!hermesHome) {
    return hermesHome
  }
  const resolved = pathModule.resolve(String(hermesHome))
  const parent = pathModule.dirname(resolved)
  if (pathModule.basename(parent).toLowerCase() === 'profiles') {
    return pathModule.dirname(parent)
  }
  return resolved
}

export function platformDefaultHermesHome(home, env = process.env, platform = process.platform) {
  const suffix = env.HERMES_DATA_DIR_SUFFIX || ''
  if (platform === 'win32') {
    const base = (env.LOCALAPPDATA || '').trim() || path.win32.join(home, 'AppData', 'Local')
    return path.win32.join(base, 'hermes') + suffix
  }
  return path.posix.join(home, '.hermes') + suffix
}

export function platformDefaultVaelHome(home, env = process.env, platform = process.platform) {
  const suffix = env.HERMES_DATA_DIR_SUFFIX || ''
  if (platform === 'win32') {
    const base = (env.LOCALAPPDATA || '').trim() || path.win32.join(home, 'AppData', 'Local')
    return path.win32.join(base, 'vael') + suffix
  }
  return path.posix.join(home, '.vael') + suffix
}

/**
 * R-7 canonical config-dir resolution (VAEL rebrand, backward compatible).
 * Precedence (never moves or deletes data):
 * 1. VAEL_CONFIG_DIR env (explicit, no warning).
 * 2. ~/.vael (%LOCALAPPDATA%/vael on win32) when it exists.
 * 3. ~/.hermes fallback when it exists (onFallback('hermes-dir') once per call site).
 * 4. Otherwise the VAEL default (created on first write by the caller).
 */
export function resolveConfigDir({ home, env = process.env, platform = process.platform, directoryExists = () => false, onFallback = () => {} } = {}) {
  const paths = platform === 'win32' ? path.win32 : path.posix
  const explicit = (env.VAEL_CONFIG_DIR || '').trim()
  if (explicit) {
    return paths.resolve(explicit)
  }
  const vaelDefault = platformDefaultVaelHome(home, env, platform)
  const hermesDefault = platformDefaultHermesHome(home, env, platform)
  if (directoryExists(vaelDefault)) {
    return vaelDefault
  }
  if (directoryExists(hermesDefault)) {
    onFallback('hermes-dir')
    return hermesDefault
  }
  return vaelDefault
}

/**
 * R-7 env alias mirror (pure): copy VAEL_* onto unset HERMES_* counterparts.
 * Returns a NEW object; the input is never mutated (tests stay isolated).
 * Precedence is always VAEL_* > HERMES_*.
 */
export function mirrorVaelEnv(env = process.env) {
  const out = { ...(env || {}) }
  for (const key of Object.keys(out)) {
    if (!key.startsWith('VAEL_')) continue
    const value = out[key]
    if (typeof value !== 'string' || !value.trim()) continue
    const counterpart = 'HERMES_' + key.slice('VAEL_'.length)
    if (!String(out[counterpart] ?? '').trim()) {
      out[counterpart] = value
    }
  }
  return out
}

export function resolveDesktopUserData(defaultPath, env = process.env) {
  return env.HERMES_DESKTOP_USER_DATA_DIR
    ? path.resolve(env.HERMES_DESKTOP_USER_DATA_DIR)
    : defaultPath + (env.HERMES_DATA_DIR_SUFFIX || '')
}

export function resolveDesktopHermesHome({ home, env = process.env, platform = process.platform, directoryExists = () => false, readWindowsHome = () => null, onFallback = () => {} }) {
  const paths = platform === 'win32' ? path.win32 : path.posix
  // R-7: explicit VAEL_CONFIG_DIR wins (no warning); explicit HERMES_HOME
  // keeps working unchanged (compat).
  if ((env.VAEL_CONFIG_DIR || '').trim()) {
    return normalizeHermesHomeRoot(env.VAEL_CONFIG_DIR.trim(), paths)
  }
  if (env.HERMES_HOME) {
    return normalizeHermesHomeRoot(env.HERMES_HOME, paths)
  }
  // Fresh-install rehearsals must not touch the real Hermes home.
  if (env.HERMES_DESKTOP_USER_DATA_DIR) {
    return paths.join(paths.resolve(env.HERMES_DESKTOP_USER_DATA_DIR), 'hermes-home')
  }
  if (platform === 'win32' && env.HERMES_HOME === undefined && env.VAEL_CONFIG_DIR === undefined) {
    // Explorer can miss setx changes. An explicit empty value opts out of that fallback.
    const registryHome = readWindowsHome()
    if (registryHome) {
      return normalizeHermesHomeRoot(registryHome, paths)
    }
  }
  // R-7: VAEL-aware default (~/.vael → ~/.hermes fallback → ~/.vael).
  const vaelDefault = platformDefaultVaelHome(home, env, platform)
  const hermesDefault = platformDefaultHermesHome(home, env, platform)
  if (directoryExists(vaelDefault)) {
    return vaelDefault
  }
  if (directoryExists(hermesDefault)) {
    onFallback('hermes-dir')
    return hermesDefault
  }
  const defaultHome = vaelDefault
  // Keep the legacy migration for ordinary installs, not isolated suffix runs.
  if (platform === 'win32' && !env.HERMES_DATA_DIR_SUFFIX) {
    const legacy = paths.join(home, '.hermes')
    if (!directoryExists(defaultHome) && directoryExists(legacy)) {
      onFallback('hermes-dir')
      return legacy
    }
  }
  return defaultHome
}
