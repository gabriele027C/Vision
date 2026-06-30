import React from "react";
import { ScrollView, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import RegimeCard from "../components/RegimeCard";
import WatchTable from "../components/WatchTable";
import { useApp } from "../context/AppContext";
import { colors, common, spacing } from "../theme";

export default function DashboardScreen() {
  const { state, triggerScan, markRead, planTrade } = useApp();

  const hot = state
    ? [...state.watchlist.crypto, ...state.watchlist.stocks].filter((r) => r.status !== "watch")
    : [];
  const alerts = state?.alerts.slice(0, 8) ?? [];

  return (
    <SafeAreaView style={common.screen} edges={["bottom"]}>
      <ScrollView contentContainerStyle={common.scrollContent}>
        <View style={[common.row, styles.section]}>
          <TouchableOpacity
            style={[common.btn, state?.scanning && common.btnDisabled]}
            onPress={triggerScan}
            disabled={state?.scanning}
          >
            <Text style={common.btnText}>
              {state?.scanning ? "Scansione in corso…" : "Scansiona ora"}
            </Text>
          </TouchableOpacity>
          {state?.scanning && <Text style={styles.scanline}>{state.progress}</Text>}
          {!state?.scanning && state?.last_scan && (
            <Text style={common.muted}>
              Ultima scansione: {new Date(state.last_scan).toLocaleString("it-IT")}
            </Text>
          )}
          {state?.last_error && <Text style={common.neg}>Errore: {state.last_error}</Text>}
        </View>

        <View style={styles.section}>
          <RegimeCard title="Regime Azioni (SPY · QQQ · VIX)" regime={state?.regimes?.stocks} />
          <View style={{ height: spacing.lg }} />
          <RegimeCard title="Regime Crypto (BTC)" regime={state?.regimes?.crypto} />
        </View>

        <View style={[common.card, styles.section]}>
          <Text style={common.cardTitle}>Setup caldi (near / triggered)</Text>
          {hot.length > 0 ? (
            <WatchTable rows={hot} onPlan={planTrade} />
          ) : (
            <Text style={common.empty}>Nessun trigger attivo. Pazienza è una posizione.</Text>
          )}
        </View>

        <View style={[common.card, styles.section]}>
          <View style={common.row}>
            <Text style={common.cardTitle}>Alert recenti</Text>
            <View style={{ flex: 1 }} />
            {(state?.unread_alerts ?? 0) > 0 && (
              <TouchableOpacity
                style={[common.btn, common.btnSecondary, common.btnSmall]}
                onPress={markRead}
              >
                <Text style={common.btnSecondaryText}>Segna come letti</Text>
              </TouchableOpacity>
            )}
          </View>
          {alerts.length === 0 && <Text style={common.empty}>Nessun alert.</Text>}
          {alerts.map((a) => (
            <View key={a.id} style={[styles.alertItem, !a.read && styles.alertUnread]}>
              <Text style={styles.alertText}>
                <Text style={{ fontWeight: "700" }}>{a.symbol}</Text>
                <Text style={common.muted}> ({a.market})</Text> — {a.message}
              </Text>
              <Text style={styles.alertWhen}>
                {new Date(a.created_at).toLocaleString("it-IT")}
              </Text>
            </View>
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  section: {
    marginBottom: spacing.lg,
  },
  scanline: {
    color: colors.accent,
    fontSize: 13,
  },
  alertItem: {
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  alertUnread: {
    borderLeftWidth: 3,
    borderLeftColor: colors.accent,
    paddingLeft: 10,
  },
  alertText: {
    color: colors.text,
    fontSize: 13,
  },
  alertWhen: {
    color: colors.textDim,
    fontSize: 11,
    marginTop: 4,
  },
});
