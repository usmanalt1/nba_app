/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_DEFAULT_SEASON: string;
  readonly VITE_DEFAULT_SEASON_TYPE: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
