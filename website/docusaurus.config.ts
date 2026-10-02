import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';
import relativeDocLinks from './src/remark/relativeDocLinks';

const config: Config = {
  title: 'VAEL Agent',
  tagline: 'The self-improving AI agent',
  // SVG favicon is the VAEL monogram. The legacy raster favicons
  // (favicon.ico / favicon-*.png / apple-touch-icon.png) are still shipped for
  // older browsers and for iOS home-screen installs; replacing their pixels is
  // tracked as a design task (see docs/open-items.md).
  favicon: 'img/favicon.svg',

  // Deployment identity is intentionally unchanged: this docs site is still
  // published from the upstream GitHub Pages project, so the canonical URL,
  // baseUrl and repo slug must keep matching it. See NOTICE.
  url: 'https://hermes-agent.nousresearch.com',
  baseUrl: '/docs/',

  organizationName: 'NousResearch',
  projectName: 'hermes-agent',

  onBrokenLinks: 'warn',

  markdown: {
    mermaid: true,
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'zh-Hans'],
    localeConfigs: {
      en: {
        label: 'English',
      },
      'zh-Hans': {
        label: '简体中文',
        htmlLang: 'zh-Hans',
      },
    },
  },

  themes: [
    '@docusaurus/theme-mermaid',
  ],

  plugins: [
    // Static /plugins/<name> and /plugins/by/<author> pages generated from the catalog JSON.
    './plugins/plugin-catalog-pages',
    [
      '@docusaurus/plugin-client-redirects',
      {
        // Static-host redirects for renamed doc pages (GitHub Pages can't
        // do server-side redirects). Paths are relative to baseUrl (/docs/).
        redirects: [
          {
            // Renamed in #44470 (Automation Blueprints terminology rebrand)
            from: '/guides/automation-templates',
            to: '/guides/automation-blueprints',
          },
          {
            // Moved when the Plugins subcategory was created under
            // Developer Guide > Extending (docs restructure, July 2026)
            from: '/guides/build-a-hermes-plugin',
            to: '/developer-guide/plugins',
          },
          {
            // Users guess these short paths from abbreviated links and hit
            // raw 404s (consumer-onboarding audit finding #1, Aug 2026).
            from: '/quickstart',
            to: '/getting-started/quickstart',
          },
          {
            from: '/installation',
            to: '/getting-started/installation',
          },
          // W-4: pages whose route contained "hermes" were renamed to "vael".
          // GitHub Pages cannot serve server-side 301s, so
          // @docusaurus/plugin-client-redirects emits a canonical redirect
          // page (meta refresh + rel=canonical to the new route) for each
          // old URL — link equity and bookmarks survive the rename.
          {
            from: '/guides/manage-hermes-cloud-with-mcp',
            to: '/guides/manage-vael-cloud-with-mcp',
          },
          {
            from: '/guides/run-hermes-with-nous-portal',
            to: '/guides/run-vael-with-nous-portal',
          },
          {
            from: '/guides/secure-hermes-on-a-work-machine',
            to: '/guides/secure-vael-on-a-work-machine',
          },
          {
            from: '/guides/use-mcp-with-hermes',
            to: '/guides/use-mcp-with-vael',
          },
          {
            from: '/guides/use-soul-with-hermes',
            to: '/guides/use-soul-with-vael',
          },
          {
            from: '/guides/use-voice-mode-with-hermes',
            to: '/guides/use-voice-mode-with-vael',
          },
        ],
      },
    ],
  ],

  presets: [
    [
      'classic',
      {
        docs: {
          routeBasePath: '/',  // Docs at the root of /docs/
          sidebarPath: './sidebars.ts',
          // Upstream repo on purpose: the docs mirror Hermes Agent's, and the
          // rebrand keeps the upstream merge path intact (see REBRANDING.md).
          editUrl: 'https://github.com/NousResearch/hermes-agent/edit/main/website/',
          // Relative `.md` links (readable on GitHub, #114428) must also resolve
          // across the zh-Hans fallback boundary; see src/remark/relativeDocLinks.js.
          beforeDefaultRemarkPlugins: [[relativeDocLinks, {siteDir: __dirname}]],
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    // Open Graph / Twitter card image for every page without its own.
    // 1200x630, VAEL wordmark — regenerate with
    // `node website/scripts/generate-brand-assets.mjs`.
    image: 'img/vael-agent-banner.png',
    // Algolia DocSearch (replaces @easyops-cn/docusaurus-search-local).
    // The local plugin shipped a ~16 MB client-side lunr index that every
    // visitor downloaded and hydrated before their first result; DocSearch
    // answers from Algolia's servers with no client index at all. These are
    // public search-only credentials — safe to commit (the admin key is not
    // in the repo). Index is populated by the Algolia Crawler configured at
    // crawler.algolia.com; contextualSearch scopes results to the active
    // locale via the docusaurus_tag/lang facets the crawler records carry.
    algolia: {
      appId: '2JLBVEYZN5',
      apiKey: '9629ec26628d1a126535fd5ef408990d',
      // The Algolia index is populated by the upstream crawler, so the index
      // name stays 'hermes docs' until a VAEL-owned DocSearch app exists;
      // renaming it here would silently break search (docs/open-items.md).
      indexName: 'hermes docs',
      contextualSearch: true,
    },
    colorMode: {
      defaultMode: 'dark',
      respectPrefersColorScheme: true,
    },
    docs: {
      sidebar: {
        hideable: true,
        autoCollapseCategories: true,
      },
    },
    navbar: {
      title: 'VAEL Agent',
      logo: {
        alt: 'VAEL Agent',
        src: 'img/vael-wordmark.svg',
        srcDark: 'img/vael-wordmark-dark.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docs',
          position: 'left',
          label: 'Docs',
        },
        {
          to: '/skills',
          label: 'Skills',
          position: 'left',
        },
        {
          to: '/plugins',
          label: 'Plugins',
          position: 'left',
        },
        {
          // Upstream download page: VAEL ships from the same source tree, so
          // this stays until a VAEL-owned distribution URL exists.
          href: 'https://hermes-agent.nousresearch.com/',
          label: 'Download (upstream)',
          position: 'left',
        },
        {
          type: 'localeDropdown',
          position: 'right',
        },
        {
          href: 'https://hermes-agent.nousresearch.com',
          label: 'Home',
          position: 'right',
        },
        {
          href: 'https://github.com/NousResearch/hermes-agent',
          label: 'GitHub',
          position: 'right',
        },
        {
          href: 'https://discord.gg/NousResearch',
          label: 'Discord',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            { label: 'Getting Started', to: '/getting-started/quickstart' },
            { label: 'User Guide', to: '/user-guide/cli' },
            { label: 'Developer Guide', to: '/developer-guide/architecture' },
            { label: 'Reference', to: '/reference/cli-commands' },
          ],
        },
        {
          title: 'Community',
          items: [
            { label: 'Discord', href: 'https://discord.gg/NousResearch' },
            { label: 'GitHub Issues', href: 'https://github.com/NousResearch/hermes-agent/issues' },
            { label: 'Skills Hub', href: 'https://agentskills.io' },
          ],
        },
        {
          title: 'More',
          items: [
            { label: 'Desktop Download', href: 'https://hermes-agent.nousresearch.com/' },
            { label: 'GitHub', href: 'https://github.com/NousResearch/hermes-agent' },
            { label: 'Nous Research', href: 'https://nousresearch.com' },
          ],
        },
      ],
      // Single attribution surface for the upstream project (MIT compliance).
      // Keep it to one place; see NOTICE for the full third-party notice.
      copyright: `VAEL Agent — based on <a href="https://github.com/NousResearch/hermes-agent">Hermes Agent</a> by <a href="https://nousresearch.com">Nous Research</a> · MIT License · ${new Date().getFullYear()}`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['bash', 'yaml', 'json', 'python', 'toml'],
    },
    mermaid: {
      theme: {light: 'neutral', dark: 'dark'},
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
