import React, { useEffect, useMemo, useState } from "react";
import {
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { useApp } from "../context/AppContext";
import { createTrade, getSettings } from "../db/database";
import { positionSize } from "../engine/sizing";
import type { Sizing } from "../engine/types";
import { isSizingError } from "../engine/types";
import { colors, common, spacing } from "../theme";

const CHECKLIST = [
  "Il regime (semaforo) consente questa direzione?",
  "L'asset è nel top/bottom 20% di forza relativa?",
  'Setup A o B completo su Daily? (non "quasi")',
  "Trigger confermato su 4H con volume?",
  "Stop definito e distanza ≤ 2.5 ATR?",
  "Rischio aperto totale dopo questo trade ≤ 4%?",
  "Niente earnings/eventi macro nelle prossime 48h?",
  "(Crypto) Funding non estremo? Non è weekend?",
  "Ordine stop REALE pronto da inserire insieme all'entrata su TradingView?",
];

export default function PlannerScreen() {
  const { plannedRow, state, refresh } = useApp();
  const [symbol, setSymbol] = useState(plannedRow?.symbol ?? "");
  const [market, setMarket] = useState<"crypto" | "stocks">(plannedRow?.market ?? "crypto");
  const [direction, setDirection] = useState<"long" | "short">(plannedRow?.direction ?? "long");
  const [setup, setSetup] = useState<"A" | "B">(plannedRow?.setup ?? "A");
  const [entry, setEntry] = useState(plannedRow ? String(plannedRow.entry_trigger) : "");
  const [stop, setStop] = useState(plannedRow ? String(plannedRow.stop) : "");
  const [sizing, setSizing] = useState<Sizing | null>(null);
  const [sizingError, setSizingError] = useState<string | null>(null);
  const [checks, setChecks] = useState<boolean[]>(CHECKLIST.map(() => false));
  const [saved, setSaved] = useState<string | null>(null);

  const halfSize = useMemo(() => {
    const regime = state?.regimes?.[market];
    return regime?.half_size ?? false;
  }, [state, market]);

  useEffect(() => {
    if (plannedRow) {
      setSymbol(plannedRow.symbol);
      setMarket(plannedRow.market);
      setDirection(plannedRow.direction);
      setSetup(plannedRow.setup);
      setEntry(String(plannedRow.entry_trigger));
      setStop(String(plannedRow.stop));
      setChecks(CHECKLIST.map(() => false));
      setSaved(null);
    }
  }, [plannedRow]);

  useEffect(() => {
    const e = parseFloat(entry);
    const s = parseFloat(stop);
    if (!(e > 0) || !(s > 0) || e === s) {
      setSizing(null);
      setSizingError(null);
      return;
    }
    const settings = getSettings();
    const result = positionSize(settings.capital, settings.risk_pct, e, s, halfSize);
    if (isSizingError(result)) {
      setSizing(null);
      setSizingError(result.error);
    } else {
      setSizing(result);
      setSizingError(null);
    }
  }, [entry, stop, halfSize]);

  const allChecked = checks.every(Boolean);
  const target2r = sizing
    ? direction === "long"
      ? sizing.target_2r_long
      : sizing.target_2r_short
    : null;

  const registerTrade = () => {
    if (!sizing) return;
    createTrade({
      symbol,
      market,
      direction,
      setup,
      entry_price: parseFloat(entry),
      stop_price: parseFloat(stop),
      size: sizing.size_units,
      risk_amount: sizing.risk_amount,
      notes: `Pianificato dal Planner. Target 2R: ${target2r}`,
    });
    setSaved(`${symbol} registrato nel journal come trade aperto.`);
    refresh();
  };

  return (
    <SafeAreaView style={common.screen} edges={["bottom"]}>
      <ScrollView contentContainerStyle={common.scrollContent}>
        <View style={[common.card, styles.section]}>
          <Text style={common.cardTitle}>Parametri del trade</Text>

          <View style={common.field}>
            <Text style={common.fieldLabel}>Simbolo</Text>
            <TextInput
              style={common.input}
              value={symbol}
              onChangeText={(t) => setSymbol(t.toUpperCase())}
              placeholder="es. BTCUSDT / NVDA"
              placeholderTextColor={colors.textDim}
              autoCapitalize="characters"
            />
          </View>

          <View style={styles.grid3}>
            <View style={[common.field, styles.gridItem]}>
              <Text style={common.fieldLabel}>Mercato</Text>
              <View style={styles.pickerRow}>
                {(["crypto", "stocks"] as const).map((m) => (
                  <TouchableOpacity
                    key={m}
                    style={[styles.pickerBtn, market === m && styles.pickerBtnActive]}
                    onPress={() => setMarket(m)}
                  >
                    <Text style={[styles.pickerBtnText, market === m && styles.pickerBtnTextActive]}>
                      {m === "crypto" ? "Crypto" : "Azioni"}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>
            <View style={[common.field, styles.gridItem]}>
              <Text style={common.fieldLabel}>Direzione</Text>
              <View style={styles.pickerRow}>
                {(["long", "short"] as const).map((d) => (
                  <TouchableOpacity
                    key={d}
                    style={[styles.pickerBtn, direction === d && styles.pickerBtnActive]}
                    onPress={() => setDirection(d)}
                  >
                    <Text style={[styles.pickerBtnText, direction === d && styles.pickerBtnTextActive]}>
                      {d === "long" ? "Long" : "Short"}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>
            <View style={[common.field, styles.gridItem]}>
              <Text style={common.fieldLabel}>Setup</Text>
              <View style={styles.pickerRow}>
                {(["A", "B"] as const).map((s) => (
                  <TouchableOpacity
                    key={s}
                    style={[styles.pickerBtn, setup === s && styles.pickerBtnActive]}
                    onPress={() => setSetup(s)}
                  >
                    <Text style={[styles.pickerBtnText, setup === s && styles.pickerBtnTextActive]}>
                      {s === "A" ? "A — Pullback" : "B — Breakout"}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>
          </View>

          <View style={styles.grid2}>
            <View style={[common.field, styles.gridItem]}>
              <Text style={common.fieldLabel}>Prezzo di entrata (trigger)</Text>
              <TextInput
                style={common.input}
                value={entry}
                onChangeText={setEntry}
                keyboardType="decimal-pad"
                placeholderTextColor={colors.textDim}
              />
            </View>
            <View style={[common.field, styles.gridItem]}>
              <Text style={common.fieldLabel}>Stop loss</Text>
              <TextInput
                style={common.input}
                value={stop}
                onChangeText={setStop}
                keyboardType="decimal-pad"
                placeholderTextColor={colors.textDim}
              />
            </View>
          </View>

          {halfSize && (
            <Text style={[common.muted, styles.halfSizeWarn]}>
              Regime misto: rischio dimezzato automaticamente (§2 della strategia).
            </Text>
          )}
          {sizingError && <Text style={common.neg}>{sizingError}</Text>}

          {sizing && (
            <View style={styles.grid2}>
              <View style={[common.card, styles.innerCard]}>
                <Text style={common.cardTitle}>Size da inserire su TradingView</Text>
                <Text style={[common.big, common.mono]}>{sizing.size_units}</Text>
                <Text style={common.muted}>
                  unità · nozionale ≈ {sizing.notional.toLocaleString("it-IT")} $
                </Text>
              </View>
              <View style={[common.card, styles.innerCard]}>
                <Text style={common.cardTitle}>Rischio / livelli</Text>
                <Text style={[common.mono, styles.line]}>
                  Rischio: {sizing.risk_amount} € ({sizing.half_size ? "0.5%" : "1%"})
                </Text>
                <Text style={[common.mono, styles.line]}>Distanza stop: {sizing.stop_distance_pct}%</Text>
                <Text style={[common.mono, styles.line]}>Target 2R (chiudi 50%): {target2r}</Text>
                <Text style={[common.mono, styles.line]}>A +1R → stop a breakeven</Text>
              </View>
            </View>
          )}
        </View>

        <View style={common.card}>
          <Text style={common.cardTitle}>Checklist pre-trade (§12) — una casella vuota = niente trade</Text>
          {CHECKLIST.map((item, i) => (
            <TouchableOpacity
              key={i}
              style={styles.checkRow}
              onPress={() =>
                setChecks((c) => c.map((v, j) => (j === i ? !v : v)))
              }
            >
              <View style={[styles.checkbox, checks[i] && styles.checkboxChecked]}>
                {checks[i] && <Text style={styles.checkMark}>✓</Text>}
              </View>
              <Text style={styles.checkLabel}>{item}</Text>
            </TouchableOpacity>
          ))}

          <View style={[common.row, styles.actions]}>
            <TouchableOpacity
              style={[
                common.btn,
                (!allChecked || !sizing || !!sizingError || sizing?.liq_safe === false || !symbol) &&
                  common.btnDisabled,
              ]}
              onPress={registerTrade}
              disabled={
                !allChecked || !sizing || !!sizingError || sizing?.liq_safe === false || !symbol
              }
            >
              <Text style={common.btnText}>Registra trade aperto nel journal</Text>
            </TouchableOpacity>
            {!allChecked && <Text style={common.muted}>Completa la checklist per sbloccare.</Text>}
            {(!!sizingError || sizing?.liq_safe === false) && (
              <Text style={common.neg}>
                Registrazione bloccata: sizing non sicuro (liquidazione).
              </Text>
            )}
          </View>
          {saved && <Text style={[common.pos, styles.saved]}>{saved}</Text>}
          <Text style={[common.muted, styles.footer]}>
            Flusso: 1) verifica il grafico su TradingView → 2) inserisci l'ordine paper con questi
            valori → 3) registra qui il trade per il conteggio dei 50 di validazione.
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  section: {
    marginBottom: spacing.lg,
  },
  grid2: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.md,
    marginTop: spacing.sm,
  },
  grid3: {
    gap: spacing.md,
  },
  gridItem: {
    flex: 1,
    minWidth: 140,
  },
  pickerRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
  },
  pickerBtn: {
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.bg,
  },
  pickerBtnActive: {
    borderColor: colors.accent,
    backgroundColor: "rgba(79, 140, 255, 0.15)",
  },
  pickerBtnText: {
    color: colors.textDim,
    fontSize: 12,
    fontWeight: "600",
  },
  pickerBtnTextActive: {
    color: colors.accent,
  },
  halfSizeWarn: {
    color: colors.yellow,
    marginBottom: 10,
  },
  innerCard: {
    flex: 1,
    minWidth: 160,
    backgroundColor: colors.bg,
  },
  line: {
    color: colors.text,
    fontSize: 13,
    marginBottom: 4,
  },
  checkRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: spacing.md,
    marginBottom: spacing.md,
  },
  checkbox: {
    width: 22,
    height: 22,
    borderRadius: 4,
    borderWidth: 1,
    borderColor: colors.border,
    alignItems: "center",
    justifyContent: "center",
    marginTop: 2,
  },
  checkboxChecked: {
    backgroundColor: colors.accent,
    borderColor: colors.accent,
  },
  checkMark: {
    color: "#fff",
    fontSize: 14,
    fontWeight: "700",
  },
  checkLabel: {
    flex: 1,
    color: colors.text,
    fontSize: 14,
    lineHeight: 20,
  },
  actions: {
    marginTop: spacing.lg,
  },
  saved: {
    marginTop: 10,
  },
  footer: {
    marginTop: 14,
  },
});
