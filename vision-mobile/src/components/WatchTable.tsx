import React, { useEffect, useRef } from "react";
import {
  Alert,
  Animated,
  FlatList,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";

import type { WatchRow } from "../engine/types";
import { colors, common, spacing } from "../theme";
import { fmt, openTradingView } from "../utils/format";

const COLUMNS = [
  { key: "symbol", label: "Asset", width: 100 },
  { key: "conf", label: "Conf", width: 45 },
  { key: "direction", label: "Dir", width: 60 },
  { key: "setup", label: "Setup", width: 70 },
  { key: "status", label: "Stato", width: 80 },
  { key: "rs", label: "RS", width: 50 },
  { key: "rvol", label: "RVOL", width: 55 },
  { key: "oi", label: "OI", width: 40 },
  { key: "cvd", label: "CVD", width: 40 },
  { key: "price", label: "Prezzo", width: 75 },
  { key: "trigger", label: "Trigger", width: 75 },
  { key: "stop", label: "Stop", width: 75 },
  { key: "funding", label: "Funding", width: 70 },
  { key: "action", label: "", width: 90 },
] as const;

function Badge({
  label,
  variant,
  pulse,
}: {
  label: string;
  variant: "long" | "short" | "watch" | "near" | "triggered" | "blocked" | "setup";
  pulse?: boolean;
}) {
  const opacity = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    if (!pulse) return;
    const anim = Animated.loop(
      Animated.sequence([
        Animated.timing(opacity, { toValue: 0.55, duration: 800, useNativeDriver: true }),
        Animated.timing(opacity, { toValue: 1, duration: 800, useNativeDriver: true }),
      ])
    );
    anim.start();
    return () => anim.stop();
  }, [pulse, opacity]);

  const bg: Record<string, string> = {
    long: "rgba(46, 204, 143, 0.15)",
    short: "rgba(255, 92, 112, 0.15)",
    watch: "rgba(139, 150, 171, 0.15)",
    near: "rgba(245, 195, 67, 0.15)",
    triggered: "rgba(79, 140, 255, 0.2)",
    blocked: "rgba(255, 92, 112, 0.25)",
    setup: "rgba(79, 140, 255, 0.12)",
  };
  const fg: Record<string, string> = {
    long: colors.green,
    short: colors.red,
    watch: colors.textDim,
    near: colors.yellow,
    triggered: colors.accent,
    blocked: colors.red,
    setup: colors.accent,
  };

  const content = (
    <View style={[styles.badge, { backgroundColor: bg[variant] }]}>
      <Text style={[styles.badgeText, { color: fg[variant] }]}>{label}</Text>
    </View>
  );

  if (pulse) return <Animated.View style={{ opacity }}>{content}</Animated.View>;
  return content;
}

function WatchRowItem({
  row,
  onPlan,
}: {
  row: WatchRow;
  onPlan?: (row: WatchRow) => void;
}) {
  const showWarnings = () => {
    if (row.warnings.length > 0) Alert.alert("Avvisi", row.warnings.join("\n"));
  };

  return (
    <ScrollView horizontal showsHorizontalScrollIndicator={false}>
      <View style={styles.row}>
        <View style={[styles.cell, { width: COLUMNS[0].width }]}>
          <TouchableOpacity onPress={() => openTradingView(row.market, row.symbol)}>
            <Text style={styles.ticker}>{row.symbol}</Text>
          </TouchableOpacity>
          {row.warnings.length > 0 && (
            <TouchableOpacity onPress={showWarnings}>
              <Text> ⚠️</Text>
            </TouchableOpacity>
          )}
        </View>
        <Text style={[styles.cell, styles.mono, { width: COLUMNS[1].width }]}>
          {row.confluence != null ? row.confluence.toFixed(0) : "—"}
        </Text>
        <View style={[styles.cell, { width: COLUMNS[2].width }]}>
          <Badge label={row.direction} variant={row.direction} />
        </View>
        <View style={[styles.cell, { width: COLUMNS[3].width }]}>
          <Badge label={`Setup ${row.setup}`} variant="setup" />
        </View>
        <View style={[styles.cell, { width: COLUMNS[4].width }]}>
          <Badge label={row.status} variant={row.status} pulse={row.status === "triggered"} />
        </View>
        <Text style={[styles.cell, styles.mono, { width: COLUMNS[5].width }]}>
          {(row.rs_score * 100).toFixed(0)}%
        </Text>
        <Text style={[styles.cell, styles.mono, { width: COLUMNS[6].width }]}>
          {row.rvol.toFixed(2)}
        </Text>
        <Text style={[styles.cell, styles.mono, { width: COLUMNS[7].width }]}>
          {row.oi_arrow ?? "—"}
        </Text>
        <Text style={[styles.cell, styles.mono, { width: COLUMNS[8].width }]}>
          {row.cvd_arrow ?? "—"}
        </Text>
        <View style={[styles.cell, { width: COLUMNS[9].width }]}>
          <Text style={[styles.mono, { fontSize: 11 }]}>{fmt(row.last_price)}</Text>
          <Text style={[common.muted, { fontSize: 9 }]}>
            {row.price_live
              ? `live${row.price_asof ? ` ${new Date(row.price_asof).toLocaleTimeString()}` : ""}`
              : "close D"}
          </Text>
        </View>
        <View style={[styles.cell, { width: COLUMNS[10].width }]}>
          <Text style={[styles.mono, { fontSize: 11 }]}>
            {fmt(row.breakout_level ?? row.entry_trigger)}
          </Text>
          <Text style={[common.muted, { fontSize: 9 }]}>livello</Text>
        </View>
        <View style={[styles.cell, { width: COLUMNS[11].width }]}>
          <Text style={[styles.mono, { fontSize: 11 }]}>{fmt(row.stop)}</Text>
          <Text style={[common.muted, { fontSize: 9 }]}>livello</Text>
        </View>
        <Text style={[styles.cell, styles.mono, { width: COLUMNS[12].width }]}>
          {row.funding !== null ? `${(row.funding * 100).toFixed(3)}%` : "—"}
        </Text>
        {onPlan && (
          <View style={[styles.cell, { width: COLUMNS[13].width }]}>
            {row.status === "blocked" ? (
              <TouchableOpacity
                style={[common.btn, common.btnSmall, { opacity: 0.4 }]}
                disabled
              >
                <Text style={[common.btnText, common.btnSmallText]}>Bloccato</Text>
              </TouchableOpacity>
            ) : (
              <TouchableOpacity style={[common.btn, common.btnSmall]} onPress={() => onPlan(row)}>
                <Text style={[common.btnText, common.btnSmallText]}>Pianifica</Text>
              </TouchableOpacity>
            )}
          </View>
        )}
      </View>
    </ScrollView>
  );
}

export default function WatchTable({
  rows,
  market = "crypto",
  onPlan,
}: {
  rows: WatchRow[];
  market?: "crypto" | "stocks";
  onPlan?: (row: WatchRow) => void;
}) {
  if (rows.length === 0) {
    const emptyMsg =
      market === "crypto"
        ? "Nessun setup valido al momento."
        : "Nessun setup valido al momento. Il mercato riapre domani.";
    return <Text style={common.empty}>{emptyMsg}</Text>;
  }

  return (
    <View>
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        <View style={styles.headerRow}>
          {COLUMNS.filter((c) => c.key !== "action" || onPlan).map((c) => (
            <Text key={c.key} style={[styles.headerCell, { width: c.width }]}>
              {c.label}
            </Text>
          ))}
        </View>
      </ScrollView>
      <FlatList
        data={rows}
        keyExtractor={(r) => `${r.market}-${r.symbol}-${r.direction}`}
        renderItem={({ item }) => <WatchRowItem row={item} onPlan={onPlan} />}
        scrollEnabled={false}
        ItemSeparatorComponent={() => <View style={styles.separator} />}
      />
    </View>
  );
}

export { Badge };

const styles = StyleSheet.create({
  headerRow: {
    flexDirection: "row",
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    paddingBottom: spacing.sm,
    marginBottom: spacing.sm,
  },
  headerCell: {
    color: colors.textDim,
    fontSize: 11,
    textTransform: "uppercase",
    letterSpacing: 0.5,
    fontWeight: "600",
    paddingHorizontal: 4,
  },
  row: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 9,
  },
  cell: {
    paddingHorizontal: 4,
    justifyContent: "center",
  },
  mono: {
    color: colors.text,
    fontSize: 13,
    fontVariant: ["tabular-nums"],
  },
  ticker: {
    color: colors.text,
    fontWeight: "700",
    fontSize: 13,
    textDecorationLine: "underline",
    textDecorationStyle: "dashed",
    textDecorationColor: colors.textDim,
  },
  badge: {
    paddingVertical: 3,
    paddingHorizontal: 9,
    borderRadius: 20,
    alignSelf: "flex-start",
  },
  badgeText: {
    fontSize: 11,
    fontWeight: "700",
    textTransform: "uppercase",
  },
  separator: {
    height: 1,
    backgroundColor: colors.border,
  },
});
