import React, { useCallback, useState } from "react";
import {
  Alert,
  Dimensions,
  Modal,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { useFocusEffect } from "@react-navigation/native";
import { LineChart } from "react-native-chart-kit";
import { SafeAreaView } from "react-native-safe-area-context";

import { useApp } from "../context/AppContext";
import { closeTrade, deleteTrade, listTrades } from "../db/database";
import type { Metrics, Trade } from "../engine/types";
import { computeMetrics } from "../services/metrics";
import { colors, common, spacing } from "../theme";
import { openTradingView } from "../utils/format";

function Stat({
  label,
  value,
  suffix,
}: {
  label: string;
  value: string | number | null;
  suffix?: string;
}) {
  return (
    <View style={[common.card, styles.stat]}>
      <Text style={common.cardTitle}>{label}</Text>
      <Text style={[common.big, common.mono]}>
        {value ?? "—"}
        {value !== null && suffix ? suffix : ""}
      </Text>
    </View>
  );
}

function TradeBadge({ label, variant }: { label: string; variant: "long" | "short" | "near" | "watch" }) {
  const bg: Record<string, string> = {
    long: "rgba(46, 204, 143, 0.15)",
    short: "rgba(255, 92, 112, 0.15)",
    near: "rgba(245, 195, 67, 0.15)",
    watch: "rgba(139, 150, 171, 0.15)",
  };
  const fg: Record<string, string> = {
    long: colors.green,
    short: colors.red,
    near: colors.yellow,
    watch: colors.textDim,
  };
  return (
    <View style={[styles.badge, { backgroundColor: bg[variant] }]}>
      <Text style={[styles.badgeText, { color: fg[variant] }]}>{label}</Text>
    </View>
  );
}

export default function JournalScreen() {
  const { refresh: refreshApp } = useApp();
  const [trades, setTrades] = useState<Trade[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [closing, setClosing] = useState<Trade | null>(null);
  const [exitPrice, setExitPrice] = useState("");
  const [mistake, setMistake] = useState(false);
  const [notes, setNotes] = useState("");

  const refresh = useCallback(() => {
    setTrades(listTrades());
    setMetrics(computeMetrics());
    refreshApp();
  }, [refreshApp]);

  useFocusEffect(
    useCallback(() => {
      refresh();
    }, [refresh])
  );

  const submitClose = () => {
    if (!closing) return;
    closeTrade(closing.id, parseFloat(exitPrice), mistake, notes);
    setClosing(null);
    setExitPrice("");
    setMistake(false);
    setNotes("");
    refresh();
  };

  const removeTrade = (id: number) => {
    Alert.alert("Elimina trade", "Eliminare questo trade dal journal?", [
      { text: "Annulla", style: "cancel" },
      {
        text: "Elimina",
        style: "destructive",
        onPress: () => {
          deleteTrade(id);
          refresh();
        },
      },
    ]);
  };

  const chartWidth = Dimensions.get("window").width - spacing.lg * 2 - 36;

  return (
    <SafeAreaView style={common.screen} edges={["bottom"]}>
      <ScrollView contentContainerStyle={common.scrollContent}>
        <View style={styles.statsGrid}>
          <Stat label="Win rate" value={metrics?.win_rate ?? null} suffix="%" />
          <Stat label="Expectancy (R/trade)" value={metrics?.expectancy ?? null} />
          <Stat label="Profit factor" value={metrics?.profit_factor ?? null} />
          <Stat label="Max drawdown (R)" value={metrics?.max_drawdown_r ?? null} />
        </View>

        <View style={[common.card, styles.section]}>
          <Text style={styles.validationTitle}>
            Validazione demo: {metrics?.closed_trades ?? 0} / {metrics?.validation_target ?? 50} trade chiusi
            {metrics?.validation_passed &&
              " — SUPERATA (puoi passare al reale a rischio 0.5%)"}
          </Text>
          <View style={styles.progressTrack}>
            <View
              style={[styles.progressFill, { width: `${metrics?.validation_progress_pct ?? 0}%` }]}
            />
          </View>
          <Text style={[common.muted, { marginTop: 8 }]}>
            Soglie per passare al capitale reale: expectancy &gt; 0.15R · profit factor &gt; 1.4 · 50 trade.
            Errori di esecuzione segnati: {metrics?.mistakes ?? 0}.
          </Text>
          <Text style={[common.muted, { marginTop: 8 }]}>
            I breakdown per timeframe/pattern/scenario si popolano con i nuovi trade registrati
            (n≥10 per riga).
          </Text>
        </View>

        {metrics?.random_benchmark && (
          <View style={[common.card, styles.section]}>
            <Text style={common.cardTitle}>Confronto col caso (R:R 2:1)</Text>
            <Text style={[common.muted, { marginBottom: 8 }]}>
              {metrics.random_benchmark.note}
            </Text>
            <Stat
              label="riferimento caso (≈33% a 2R)"
              value={metrics.random_benchmark.expected_wr_pct}
              suffix="%"
            />
          </View>
        )}

        {metrics && metrics.equity_curve.length > 1 && (
          <View style={[common.card, styles.section]}>
            <Text style={common.cardTitle}>Curva di equity (R cumulato)</Text>
            <LineChart
              data={{
                labels: metrics.equity_curve.map((c) => (c.trade % 5 === 0 ? String(c.trade) : "")),
                datasets: [{ data: metrics.equity_curve.map((c) => c.cum_r) }],
              }}
              width={chartWidth}
              height={220}
              withDots={false}
              withInnerLines
              withOuterLines={false}
              chartConfig={{
                backgroundColor: colors.bgCard,
                backgroundGradientFrom: colors.bgCard,
                backgroundGradientTo: colors.bgCard,
                decimalPlaces: 2,
                color: () => colors.accent,
                labelColor: () => colors.textDim,
                propsForBackgroundLines: { stroke: colors.border, strokeDasharray: "3 3" },
              }}
              bezier
              style={styles.chart}
            />
          </View>
        )}

        <View style={common.card}>
          <Text style={common.cardTitle}>Trade ({trades.length})</Text>
          {trades.length === 0 && (
            <Text style={common.empty}>Nessun trade registrato. Usa il Trade Planner.</Text>
          )}
          {trades.map((t) => (
            <View key={t.id} style={styles.tradeRow}>
              <View style={styles.tradeMain}>
                <Text style={common.muted}>
                  {new Date(t.opened_at).toLocaleDateString("it-IT")}
                </Text>
                <TouchableOpacity onPress={() => openTradingView(t.market, t.symbol)}>
                  <Text style={styles.ticker}>
                    {t.symbol}
                    {t.mistake ? " ⚠️" : ""}
                  </Text>
                </TouchableOpacity>
                <View style={common.row}>
                  <TradeBadge
                    label={t.direction}
                    variant={t.direction === "long" ? "long" : "short"}
                  />
                  <Text style={styles.setupLabel}>Setup {t.setup}</Text>
                </View>
                <Text style={[common.mono, styles.tradeDetail]}>
                  Entrata {t.entry_price} · Stop {t.stop_price} · Size {t.size}
                </Text>
                <View style={common.row}>
                  <TradeBadge
                    label={t.status}
                    variant={t.status === "open" ? "near" : "watch"}
                  />
                  <Text
                    style={[
                      common.mono,
                      t.r_result === null ? styles.neutral : t.r_result > 0 ? common.pos : common.neg,
                    ]}
                  >
                    {t.r_result === null ? "—" : `${t.r_result > 0 ? "+" : ""}${t.r_result}R`}
                  </Text>
                </View>
              </View>
              <View style={styles.tradeActions}>
                {t.status === "open" && (
                  <TouchableOpacity
                    style={[common.btn, common.btnSmall]}
                    onPress={() => {
                      setClosing(t);
                      setExitPrice("");
                    }}
                  >
                    <Text style={[common.btnText, common.btnSmallText]}>Chiudi</Text>
                  </TouchableOpacity>
                )}
                <TouchableOpacity
                  style={[common.btn, common.btnSecondary, common.btnSmall, styles.deleteBtn]}
                  onPress={() => removeTrade(t.id)}
                >
                  <Text style={[common.btnSecondaryText, common.btnSmallText]}>×</Text>
                </TouchableOpacity>
              </View>
            </View>
          ))}
        </View>
      </ScrollView>

      <Modal visible={closing != null} transparent animationType="fade">
        <TouchableOpacity style={styles.modalOverlay} activeOpacity={1} onPress={() => setClosing(null)}>
          <TouchableOpacity activeOpacity={1} style={styles.modal} onPress={() => {}}>
            <Text style={styles.modalTitle}>
              Chiudi {closing?.symbol} ({closing?.direction})
            </Text>
            <View style={common.field}>
              <Text style={common.fieldLabel}>Prezzo di uscita</Text>
              <TextInput
                style={common.input}
                value={exitPrice}
                onChangeText={setExitPrice}
                keyboardType="decimal-pad"
                autoFocus
                placeholderTextColor={colors.textDim}
              />
            </View>
            <View style={common.field}>
              <Text style={common.fieldLabel}>Note (cosa ha funzionato / cosa no)</Text>
              <TextInput
                style={[common.input, styles.textarea]}
                value={notes}
                onChangeText={setNotes}
                multiline
                numberOfLines={3}
                placeholderTextColor={colors.textDim}
              />
            </View>
            <TouchableOpacity
              style={styles.checkRow}
              onPress={() => setMistake((m) => !m)}
            >
              <View style={[styles.checkbox, mistake && styles.checkboxChecked]}>
                {mistake && <Text style={styles.checkMark}>✓</Text>}
              </View>
              <Text style={styles.checkLabel}>Ho violato una regola della strategia in questo trade</Text>
            </TouchableOpacity>
            <View style={[common.row, { marginTop: 12 }]}>
              <TouchableOpacity
                style={[common.btn, !(parseFloat(exitPrice) > 0) && common.btnDisabled]}
                onPress={submitClose}
                disabled={!(parseFloat(exitPrice) > 0)}
              >
                <Text style={common.btnText}>Conferma chiusura</Text>
              </TouchableOpacity>
              <TouchableOpacity style={[common.btn, common.btnSecondary]} onPress={() => setClosing(null)}>
                <Text style={common.btnSecondaryText}>Annulla</Text>
              </TouchableOpacity>
            </View>
          </TouchableOpacity>
        </TouchableOpacity>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  statsGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.md,
    marginBottom: spacing.lg,
  },
  stat: {
    flex: 1,
    minWidth: 140,
  },
  section: {
    marginBottom: spacing.lg,
  },
  validationTitle: {
    color: colors.text,
    fontSize: 14,
    fontWeight: "600",
    marginBottom: spacing.md,
  },
  progressTrack: {
    height: 8,
    backgroundColor: colors.bg,
    borderRadius: 4,
    overflow: "hidden",
  },
  progressFill: {
    height: "100%",
    backgroundColor: colors.accent,
    borderRadius: 4,
  },
  chart: {
    marginLeft: -16,
    borderRadius: 8,
  },
  tradeRow: {
    flexDirection: "row",
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    gap: spacing.md,
  },
  tradeMain: {
    flex: 1,
    gap: 4,
  },
  ticker: {
    color: colors.text,
    fontWeight: "700",
    fontSize: 15,
    textDecorationLine: "underline",
    textDecorationStyle: "dashed",
    textDecorationColor: colors.textDim,
  },
  setupLabel: {
    color: colors.textDim,
    fontSize: 12,
  },
  tradeDetail: {
    color: colors.text,
    fontSize: 12,
  },
  neutral: {
    color: colors.textDim,
  },
  tradeActions: {
    alignItems: "flex-end",
    gap: spacing.sm,
  },
  deleteBtn: {
    minWidth: 36,
    alignItems: "center",
  },
  badge: {
    paddingVertical: 3,
    paddingHorizontal: 9,
    borderRadius: 20,
  },
  badgeText: {
    fontSize: 11,
    fontWeight: "700",
    textTransform: "uppercase",
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.6)",
    justifyContent: "center",
    padding: spacing.lg,
  },
  modal: {
    backgroundColor: colors.bgCard,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
  },
  modalTitle: {
    color: colors.text,
    fontSize: 18,
    fontWeight: "700",
    marginBottom: spacing.lg,
  },
  textarea: {
    minHeight: 80,
    textAlignVertical: "top",
  },
  checkRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: spacing.md,
    marginTop: spacing.sm,
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
});
