import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { AppState as RNAppState, InteractionManager } from "react-native";
import * as SplashScreen from "expo-splash-screen";
import type { NavigationContainerRef } from "@react-navigation/native";

import { countUnreadAlerts, getSettings, initDb, listAlerts, markAlertsRead } from "../db/database";
import type { AppState, RootTabParamList, WatchRow } from "../engine/types";
import { scanner } from "../services/scanner";

interface AppContextValue {
  ready: boolean;
  state: AppState | null;
  error: string | null;
  refresh: () => void;
  triggerScan: () => Promise<void>;
  restartScanLoop: () => void;
  markRead: () => void;
  plannedRow: WatchRow | null;
  planTrade: (row: WatchRow) => void;
  navigationRef: React.RefObject<NavigationContainerRef<RootTabParamList> | null>;
}

const AppContext = createContext<AppContextValue | null>(null);

function buildState(): AppState {
  const snap = scanner.snapshot();
  const alerts = listAlerts(50);
  return {
    ...snap,
    alerts,
    unread_alerts: countUnreadAlerts(),
  };
}

export function AppProvider({ children }: { children: ReactNode }) {
  const [ready, setReady] = useState(false);
  const [state, setState] = useState<AppState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [plannedRow, setPlannedRow] = useState<WatchRow | null>(null);
  const navigationRef = useRef<NavigationContainerRef<RootTabParamList>>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const scanTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const scanLoopActiveRef = useRef(false);

  const refresh = useCallback(() => {
    try {
      setState(buildState());
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    }
  }, []);

  const triggerScan = useCallback(async () => {
    try {
      await scanner.runScan();
      refresh();
    } catch (e) {
      setError((e as Error).message);
      refresh();
    }
  }, [refresh]);

  const markRead = useCallback(() => {
    markAlertsRead();
    refresh();
  }, [refresh]);

  const planTrade = useCallback((row: WatchRow) => {
    setPlannedRow(row);
    navigationRef.current?.navigate("Planner");
  }, []);

  const startPolling = useCallback(() => {
    if (pollRef.current) return;
    pollRef.current = setInterval(refresh, 20_000);
  }, [refresh]);

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  const stopScanLoop = useCallback(() => {
    scanLoopActiveRef.current = false;
    if (scanTimerRef.current) {
      clearTimeout(scanTimerRef.current);
      scanTimerRef.current = null;
    }
  }, []);

  const startScanLoop = useCallback(
    (immediate = false) => {
      stopScanLoop();
      scanLoopActiveRef.current = true;

      const scheduleNext = () => {
        if (!scanLoopActiveRef.current) return;
        const intervalMin = Math.max(getSettings().scan_interval_min, 5);
        scanTimerRef.current = setTimeout(async () => {
          if (!scanLoopActiveRef.current) return;
          await triggerScan();
          scheduleNext();
        }, intervalMin * 60 * 1000);
      };

      if (immediate) {
        void triggerScan().finally(scheduleNext);
      } else {
        scheduleNext();
      }
    },
    [triggerScan, stopScanLoop]
  );

  const restartScanLoop = useCallback(() => {
    startScanLoop(true);
  }, [startScanLoop]);

  useEffect(() => {
    let cancelled = false;

    const boot = InteractionManager.runAfterInteractions(() => {
      try {
        initDb();
        refresh();
        startPolling();
        // Primo scan automatico solo dopo l'intervallo configurato — UI subito visibile
        startScanLoop(false);
      } catch (e) {
        setError((e as Error).message);
      } finally {
        if (!cancelled) setReady(true);
      }
    });

    const sub = RNAppState.addEventListener("change", (next) => {
      if (next === "active") {
        refresh();
        startPolling();
      } else {
        stopPolling();
        stopScanLoop();
      }
    });

    return () => {
      cancelled = true;
      boot.cancel();
      stopPolling();
      stopScanLoop();
      sub.remove();
    };
  }, [refresh, startPolling, stopPolling, startScanLoop, stopScanLoop]);

  useEffect(() => {
    if (ready) {
      SplashScreen.hideAsync().catch(() => {});
    }
  }, [ready]);

  // Aggiorna progresso scansione in tempo quasi reale
  useEffect(() => {
    if (!state?.scanning) return;
    const id = setInterval(refresh, 2000);
    return () => clearInterval(id);
  }, [state?.scanning, refresh]);

  return (
    <AppContext.Provider
      value={{
        ready,
        state,
        error,
        refresh,
        triggerScan,
        restartScanLoop,
        markRead,
        plannedRow,
        planTrade,
        navigationRef,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp(): AppContextValue {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useApp must be used within AppProvider");
  return ctx;
}
