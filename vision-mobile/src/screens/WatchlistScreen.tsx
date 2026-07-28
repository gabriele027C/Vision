import React, { useState } from "react";
import { ScrollView, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import WatchTable from "../components/WatchTable";
import { useApp } from "../context/AppContext";
import { common, spacing } from "../theme";

export default function WatchlistScreen() {
  const { state, planTrade } = useApp();
  const [market, setMarket] = useState<"crypto" | "stocks">("crypto");
  const [tab, setTab] = useState<"long" | "bearish">("long");
  const rows = state?.watchlist[market] ?? [];
  const bearish = state?.bearish_context?.[market] ?? [];
  const regime = state?.regimes?.[market];

  return (
    <SafeAreaView style={common.screen} edges={["bottom"]}>
      <ScrollView contentContainerStyle={common.scrollContent}>
        <View style={[common.row, styles.section]}>
          <View style={common.tabs}>
            <TouchableOpacity
              style={[common.tab, market === "crypto" && common.tabActive]}
              onPress={() => setMarket("crypto")}
            >
              <Text style={[common.tabText, market === "crypto" && common.tabTextActive]}>Crypto</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[common.tab, market === "stocks" && common.tabActive]}
              onPress={() => setMarket("stocks")}
            >
              <Text style={[common.tabText, market === "stocks" && common.tabTextActive]}>Azioni</Text>
            </TouchableOpacity>
          </View>
        </View>
        <View style={[common.row, styles.section]}>
          <View style={common.tabs}>
            <TouchableOpacity
              style={[common.tab, tab === "long" && common.tabActive]}
              onPress={() => setTab("long")}
            >
              <Text style={[common.tabText, tab === "long" && common.tabTextActive]}>
                Long ({rows.length})
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[common.tab, tab === "bearish" && common.tabActive]}
              onPress={() => setTab("bearish")}
            >
              <Text style={[common.tabText, tab === "bearish" && common.tabTextActive]}>
                Contesto ({bearish.length})
              </Text>
            </TouchableOpacity>
          </View>
        </View>

        {tab === "long" && (
          <View style={common.card}>
            {market === "crypto" && rows.length === 0 && regime?.mode === "short" ? (
              <View>
                <Text style={[common.cardTitle, { marginBottom: 8 }]}>
                  Regime ribassista: lato long senza contesto operativo
                </Text>
                <Text style={[common.muted, { marginBottom: 8 }]}>
                  Il sistema sta funzionando, non è un errore. In regime short non popoliamo la
                  watchlist long.
                </Text>
                <TouchableOpacity style={common.btn} onPress={() => setTab("bearish")}>
                  <Text style={common.btnText}>Apri tab Contesto ribassista</Text>
                </TouchableOpacity>
                <Text style={[common.muted, { marginTop: 8 }]}>
                  Scheda playbook: contesto_ribassista
                </Text>
              </View>
            ) : (
              <WatchTable rows={rows} market={market} onPlan={planTrade} />
            )}
          </View>
        )}

        {tab === "bearish" && (
          <View style={common.card}>
            <Text style={common.cardTitle}>Contesto ribassista (solo informativo)</Text>
            <Text style={[common.muted, { marginBottom: 8 }]}>
              Nessun livello operativo né alert.
            </Text>
            {bearish.length === 0 ? (
              <Text style={common.muted}>Nessun contesto ribassista al momento.</Text>
            ) : (
              bearish.map((r) => (
                <Text key={r.symbol} style={common.mono}>
                  {r.symbol} · RS {(r.rs_score * 100).toFixed(0)}% · {r.last_price}
                </Text>
              ))
            )}
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  section: {
    marginBottom: spacing.lg,
  },
});
