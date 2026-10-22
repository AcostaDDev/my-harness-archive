import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { DEFAULT_LANGUAGE, isLanguage, translate } from "./i18n.ts";
import type { Language, MessageKey, Params, Translate } from "./i18n.ts";
import en from "./i18n/en.json";
import es from "./i18n/es.json";
import { managed } from "./managed-api";
import type { S } from "./managed-api";

const CATALOGS = { en, es } satisfies Record<Language, Record<MessageKey, string>>;
// Provisional copy for the next page load only: the service preferences are the authority (D166).
const CACHE = "harness-ui-language";

type I18nValue = {
  language: Language;
  t: Translate;
  /** Last read of the service; undefined until it answers. */
  preferences?: S["PreferencesRead"];
  unavailable: boolean;
  refresh: () => Promise<void>;
  apply: (preferences: S["PreferencesRead"]) => void;
};

const I18nContext = createContext<I18nValue | null>(null);

export function useI18n(): I18nValue {
  const value = useContext(I18nContext);
  if (!value) throw new Error("I18nProvider missing");
  return value;
}

function cached(): Language {
  try { const value = localStorage.getItem(CACHE); return isLanguage(value) ? value : DEFAULT_LANGUAGE; }
  catch { return DEFAULT_LANGUAGE; }
}

/** Visual language of every window of this service; before the first read, the cached value or English. */
export function I18nProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>(cached);
  const [preferences, setPreferences] = useState<S["PreferencesRead"]>();
  const [unavailable, setUnavailable] = useState(false);
  useEffect(() => { document.documentElement.lang = language; }, [language]);
  const apply = useCallback((value: S["PreferencesRead"]) => {
    setPreferences(value);
    setLanguage(value.ui_language);
    setUnavailable(false);
    try { localStorage.setItem(CACHE, value.ui_language); } catch { /* no provisional copy */ }
  }, []);
  // A failed read keeps the current language and says so; it never writes the preferences.
  const refresh = useCallback(async () => {
    try { apply(await managed<S["PreferencesRead"]>("/preferences")); }
    catch { setUnavailable(true); }
  }, [apply]);
  const t = useCallback<Translate>((key: MessageKey, params?: Params) => translate(CATALOGS, language, key, params), [language]);
  const value = useMemo(() => ({ language, t, preferences, unavailable, refresh, apply }), [language, t, preferences, unavailable, refresh, apply]);
  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}
