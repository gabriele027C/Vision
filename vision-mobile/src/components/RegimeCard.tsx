import React from "react";
import { StyleSheet, Text, View } from "react-native";

import type { Regime } from "../engine/types";
import { colors, common, spacing } from "../theme";

const MODE_LABEL: Record<string, string> = {
  long: "Long consentiti",
  short: "Short consentiti",
  mixed: "Misto — size dimezzata",
  halt: "STOP — nessuna nuova posizione",
};

const LIGHT_COLORS: Record<string, string> = {
  long: colors.green,
  short: colors.red,
  mixed: colors.yellow,
  halt: "#777",
};

export default function RegimeCard({ title, regime }: { title: string; regime?: Regime }) {
  if (!regime) {
    return (
      <View style={[common.card, styles.card]}>
        <Text style={common.cardTitle}>{title}</Text>
        <Text style={common.muted}>In attesa della prima scansione…</Text>
      </View>
    );
  }

  const detail = Object.entries(regime.detail)
    .map(([k, v]) => `${k}: ${typeof v === "number" ? v.toFixed(1) : v ?? "n/d"}`)
    .join(" · ");
  const lightColor = LIGHT_COLORS[regime.mode] ?? "#777";

  return (
    <View style={[common.card, styles.card]}>
      <Text style={common.cardTitle}>{title}</Text>
      <View style={styles.regime}>
        <View style={[styles.light, { backgroundColor: lightColor, shadowColor: lightColor }]} />
        <View style={styles.regimeText}>
          <Text style={styles.regimeMode}>{MODE_LABEL[regime.mode] ?? regime.mode}</Text>
          <Text style={styles.regimeDetail}>{detail}</Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    flex: 1,
    minWidth: "100%",
  },
  regime: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.md,
  },
  light: {
    width: 18,
    height: 18,
    borderRadius: 9,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.8,
    shadowRadius: 12,
    elevation: 4,
  },
  regimeText: {
    flex: 1,
  },
  regimeMode: {
    fontSize: 16,
    fontWeight: "700",
    color: colors.text,
    textTransform: "uppercase",
  },
  regimeDetail: {
    color: colors.textDim,
    fontSize: 12,
    marginTop: 4,
  },
});
