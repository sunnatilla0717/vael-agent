import assert from 'node:assert/strict'
import os from 'node:os'
import path from 'node:path'

import { afterEach, test, vi } from 'vitest'

import {
  mirrorVaelEnv,
  platformDefaultHermesHome,
  platformDefaultVaelHome,
  resolveConfigDir,
  resolveDesktopHermesHome,
  resolveDesktopUserData
} from './data-paths'
import { controlSocketPath } from './ssh-connection'

afterEach((): void => {
  vi.unstubAllEnvs()
})

test.skipIf(process.platform === 'win32')('local SSH sockets use the suffixed default root', (): void => {
  vi.stubEnv('HERMES_DATA_DIR_SUFFIX', 'magic-test')
  const socket: string = controlSocketPath('user', 'host', 22)

  assert.equal(path.dirname(socket), path.join(platformDefaultHermesHome(os.homedir()), 'desktop-ssh'))
})

test('default data roots append the suffix literally on each platform', (): void => {
  for (const platform of ['linux', 'darwin', 'win32'] as const) {
    const paths: typeof path = platform === 'win32' ? path.win32 : path.posix
    const home: string = platform === 'win32' ? 'C:\\Users\\test' : '/home/test'
    const local: string = paths.join(home, 'AppData', 'Local')
    const userData: string = paths.join(home, 'app-data', 'Hermes')
    const base: string = platform === 'win32' ? paths.join(local, 'hermes') : paths.join(home, '.hermes')

    for (const suffix of ['', '-asdfasdf', 'magic-test', ' spaced ']) {
      const env: NodeJS.ProcessEnv = { LOCALAPPDATA: local, HERMES_DATA_DIR_SUFFIX: suffix }

      assert.equal(platformDefaultHermesHome(home, env, platform), base + suffix)
      assert.equal(resolveDesktopUserData(userData, env), userData + suffix)
      // R-7: fresh installs default to the VAEL home, not the Hermes one.
      const vaelBase: string = platform === 'win32' ? paths.join(local, 'vael') : paths.join(home, '.vael')
      assert.equal(platformDefaultVaelHome(home, env, platform), vaelBase + suffix)
      assert.equal(
        resolveDesktopHermesHome({ home, env, platform, directoryExists: (): boolean => false }),
        vaelBase + suffix
      )
    }
  }
})

test('explicit homes and userData retain precedence, and suffixed Windows homes never use legacy state', (): void => {
  const home: string = '/home/test'

  const env: NodeJS.ProcessEnv = {
    HERMES_DATA_DIR_SUFFIX: 'magic-test',
    HERMES_HOME: '/explicit/home',
    HERMES_DESKTOP_USER_DATA_DIR: '/explicit/electron'
  }

  assert.equal(resolveDesktopUserData('/default/electron', env), path.resolve(env.HERMES_DESKTOP_USER_DATA_DIR!))
  assert.equal(resolveDesktopHermesHome({ home, env, platform: 'linux' }), env.HERMES_HOME)
  delete env.HERMES_HOME
  assert.equal(resolveDesktopHermesHome({ home, env, platform: 'linux' }), '/explicit/electron/hermes-home')

  const windowsHome: string = 'C:\\Users\\test'
  const windowsEnv: NodeJS.ProcessEnv = { HERMES_DATA_DIR_SUFFIX: 'magic-test' }
  // R-7: everything-exists stub → VAEL default wins (still never legacy state).
  const expected: string = path.win32.join(windowsHome, 'AppData', 'Local', 'vaelmagic-test')

  assert.equal(
    resolveDesktopHermesHome({
      home: windowsHome,
      env: windowsEnv,
      platform: 'win32',
      directoryExists: (): boolean => true
    }),
    expected
  )
  assert.equal(
    resolveDesktopHermesHome({
      home: windowsHome,
      env: windowsEnv,
      platform: 'win32',
      readWindowsHome: (): string => 'C:\\custom'
    }),
    'C:\\custom'
  )
})

test('R-7: VAEL_CONFIG_DIR wins; vael dir wins; hermes fallback warns; default is vael', (): void => {
  const home: string = '/home/test'
  const vaelHome: string = '/home/test/.vael'
  const hermesHome: string = '/home/test/.hermes'
  const exists = (present: string[]): ((dir: string) => boolean) => (dir: string): boolean =>
    present.includes(dir)

  // 1. Explicit VAEL_CONFIG_DIR (no warning expected).
  let warned: string[] = []
  assert.equal(
    resolveDesktopHermesHome({
      home,
      env: { VAEL_CONFIG_DIR: '/explicit/vael' },
      platform: 'linux',
      directoryExists: exists([]),
      onFallback: (reason: string): void => {
        warned.push(reason)
      }
    }),
    '/explicit/vael'
  )
  assert.deepEqual(warned, [])

  // 2. ~/.vael wins over ~/.hermes.
  assert.equal(
    resolveConfigDir({ home, env: {}, platform: 'linux', directoryExists: exists([vaelHome, hermesHome]) }),
    vaelHome
  )

  // 3. ~/.hermes fallback + single warning.
  warned = []
  assert.equal(
    resolveConfigDir({
      home,
      env: {},
      platform: 'linux',
      directoryExists: exists([hermesHome]),
      onFallback: (reason: string): void => {
        warned.push(reason)
      }
    }),
    hermesHome
  )
  assert.deepEqual(warned, ['hermes-dir'])

  // 4. Neither exists → vael default, no warning.
  warned = []
  assert.equal(
    resolveConfigDir({ home, env: {}, platform: 'linux', directoryExists: exists([]) }),
    vaelHome
  )
  assert.deepEqual(warned, [])

  // Explicit HERMES_HOME still respected (compat, no warning from the resolver).
  warned = []
  assert.equal(
    resolveDesktopHermesHome({
      home,
      env: { HERMES_HOME: '/legacy/home' },
      platform: 'linux',
      directoryExists: exists([]),
      onFallback: (reason: string): void => {
        warned.push(reason)
      }
    }),
    '/legacy/home'
  )
  assert.deepEqual(warned, [])
})

test('R-7: mirrorVaelEnv copies VAEL_* onto unset HERMES_* only (pure, no mutation)', (): void => {
  const input = { VAEL_FOO_R7: 'v1', HERMES_BAR_R7: 'keep', VAEL_EMPTY_R7: '   ' }
  const out = mirrorVaelEnv(input as NodeJS.ProcessEnv)
  assert.equal(out.HERMES_FOO_R7, 'v1')
  assert.equal(out.HERMES_BAR_R7, 'keep')
  assert.equal('HERMES_EMPTY_R7' in out, false)
  assert.equal('HERMES_FOO_R7' in input, false)
  // HERMES_* never overwritten.
  const both = mirrorVaelEnv({ VAEL_X_R7: 'new', HERMES_X_R7: 'old' } as NodeJS.ProcessEnv)
  assert.equal(both.HERMES_X_R7, 'old')
})
