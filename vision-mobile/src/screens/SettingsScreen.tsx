import React, { useEffect, useState } from "react";
import { ScrollView, StyleSheet, Text, TextInput, TouchableOpacity, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { useApp } from "../context/AppContext";
import { getSettings, updateSettings } from "../db/database";
import type { Settings } from "../engine/types";
import { sendTelegram } from "../services/alerts";
import { colors, common, spacing } from "../theme";

export default function SettingsScreen() {
  const { restartScanLoop } = useApp();
  const [s, setS] = useState<Settings | null>(null);
  const [msg, setMsg] = useState<string | null>(null);

  useEffect(() => {
    setS(getSettings());
  }, []);

  if (!s) {
    return (
      <SafeAreaView style={common.screen} edges={["bottom"]}>
        <View style={common.scrollContent}>
          <Text style={common.empty}>Caricamento…</Text>
        </View>
      </SafeAreaView>
    );
  }

  const save = () => {
    setMsg(null);
    try {
      const updated = updateSettings(s);
      setS(updated);
      restartScanLoop();
      setMsg("Impostazioni salvate.");
    } catch (e) {
      setMsg((e as Error).message);
    }
  };

  const testTg = async () => {
    setMsg(null);
    try {
      const ok = await sendTelegram(
        s.telegram_token,
        s.telegram_chat_id,
        "<b>Vision TVS</b> — test riuscito. Gli alert arriveranno qui."
      );
      if (!ok) throw new Error("Invio fallito: controlla token e chat_id");
      setMsg("Messaggio di test inviato su Telegram.");
    } catch (e) {
      setMsg((e as Error).message);
    }
  };

  const msgPositive = msg?.includes("salvat") || msg?.includes("inviato");

  return (
    <SafeAreaView style={common.screen} edges={["bottom"]}>
      <ScrollView contentContainerStyle={common.scrollContent}>
        <View style={[common.card, styles.section]}>
          <Text style={common.cardTitle}>Capitale e rischio (§7 della strategia)</Text>
          <View style={common.field}>
            <Text style={common.fieldLabel}>Capitale del conto (€/$)</Text>
            <TextInput
              style={common.input}
              value={String(s.capital)}
              onChangeText={(t) => setS({ ...s, capital: parseFloat(t) || 0 })}
              keyboardType="decimal-pad"
              placeholderTextColor={colors.textDim}
            />
          </View>
          <View style={common.field}>
            <Text style={common.fieldLabel}>
              Rischio per trade (%) — 1% standard, 0.5% nei primi 20 trade reali o in drawdown &gt;10%
            </Text>
            <TextInput
              style={common.input}
              value={String(s.risk_pct)}
              onChangeText={(t) => setS({ ...s, risk_pct: parseFloat(t) || 1 })}
              keyboardType="decimal-pad"
              placeholderTextColor={colors.textDim}
            />
          </View>
          <View style={common.field}>
            <Text style={common.fieldLabel}>Intervallo scansione automatica (minuti)</Text>
            <TextInput
              style={common.input}
              value={String(s.scan_interval_min)}
              onChangeText={(t) => setS({ ...s, scan_interval_min: parseInt(t, 10) || 30 })}
              keyboardType="number-pad"
              placeholderTextColor={colors.textDim}
            />
          </View>
        </View>

        <View style={common.card}>
          <Text style={common.cardTitle}>Notifiche Telegram (gratuito)</Text>
          <Text style={[common.muted, styles.tgHelp]}>
            1) Su Telegram cerca <Text style={styles.strong}>@BotFather</Text> → /newbot → copia il token.{"\n"}
            2) Scrivi un messaggio al tuo bot, poi apri{" "}
            <Text style={styles.code}>api.telegram.org/bot&lt;TOKEN&gt;/getUpdates</Text> e copia il{" "}
            <Text style={styles.code}>chat.id</Text>.
          </Text>
          <View style={common.field}>
            <Text style={common.fieldLabel}>Bot token</Text>
            <TextInput
              style={common.input}
              value={s.telegram_token}
              onChangeText={(t) => setS({ ...s, telegram_token: t.trim() })}
              placeholder="123456:ABC-..."
              placeholderTextColor={colors.textDim}
              autoCapitalize="none"
            />
          </View>
          <View style={common.field}>
            <Text style={common.fieldLabel}>Chat ID</Text>
            <TextInput
              style={common.input}
              value={s.telegram_chat_id}
              onChangeText={(t) => setS({ ...s, telegram_chat_id: t.trim() })}
              placeholder="es. 123456789"
              placeholderTextColor={colors.textDim}
              keyboardType="number-pad"
            />
          </View>
          <View style={common.row}>
            <TouchableOpacity style={common.btn} onPress={save}>
              <Text style={common.btnText}>Salva impostazioni</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[common.btn, common.btnSecondary]} onPress={testTg}>
              <Text style={common.btnSecondaryText}>Test Telegram</Text>
            </TouchableOpacity>
          </View>
          {msg && (
            <Text style={[msgPositive ? common.pos : common.neg, { marginTop: 10 }]}>{msg}</Text>
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  section: {
    marginBottom: spacing.lg,
  },
  tgHelp: {
    marginBottom: 12,
    lineHeight: 18,
  },
  strong: {
    fontWeight: "700",
    color: colors.text,
  },
  code: {
    fontFamily: "monospace",
    color: colors.text,
  },
});
