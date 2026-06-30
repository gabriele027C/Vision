import React, { useState } from "react";
import { ScrollView, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import WatchTable from "../components/WatchTable";
import { useApp } from "../context/AppContext";
import { common, spacing } from "../theme";

export default function WatchlistScreen() {
  const { state, planTrade } = useApp();
  const [market, setMarket] = useState<"crypto" | "stocks">("crypto");
  const rows = state?.watchlist[market] ?? [];

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
          <Text style={common.muted}>
            Top {rows.length} per forza relativa con Setup A/B valido — verifica sempre il grafico su
            TradingView prima di ordinare.
          </Text>
        </View>
        <View style={common.card}>
          <WatchTable rows={rows} market={market} onPlan={planTrade} />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  section: {
    marginBottom: spacing.lg,
  },
});
