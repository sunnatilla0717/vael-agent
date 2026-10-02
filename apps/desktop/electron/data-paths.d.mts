export function platformDefaultHermesHome(
  home: string,
  env?: NodeJS.ProcessEnv,
  platform?: NodeJS.Platform,
): string

export function platformDefaultVaelHome(
  home: string,
  env?: NodeJS.ProcessEnv,
  platform?: NodeJS.Platform,
): string

export function resolveConfigDir(
  options: HermesHomeOptions & { onFallback?: (reason: string) => void },
): string

export function mirrorVaelEnv(env?: NodeJS.ProcessEnv): NodeJS.ProcessEnv

export function resolveDesktopUserData(defaultPath: string, env?: NodeJS.ProcessEnv): string

export interface HermesHomeOptions {
  home: string
  env?: NodeJS.ProcessEnv
  platform?: NodeJS.Platform
  directoryExists?: (directory: string) => boolean
  readWindowsHome?: () => string | null
  onFallback?: (reason: string) => void
}

export function resolveDesktopHermesHome(options: HermesHomeOptions): string
