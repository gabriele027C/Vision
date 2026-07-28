import React, { useCallback, useEffect, useMemo, useState } from "react";
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
import type { AssetDiagnostics, FilterResult } from "../engine/types";
import { scanner } from "../services/scanner";
import { colors, common, spacing } from "../theme";
import { openTradingView, fmt } from "../utils/format";

function statusIcon(status: FilterResult["status"]): string {
  if (status === "pass") return "✓";
  if (status === "fail") return "✗";
  if (status === "warn") return "⚠";
  return "—";
}

function FilterList({ filters }: { filters: FilterResult[] }) {
  return (
    <View style={styles.filterList}>
      {filters.map((f) => (
        <View key={f.id} style={[styles.filterItem, styles[`filter_${f.status}` as keyof typeof styles]]}>
          <Text style={styles.filterIcon}>{statusIcon(f.status)}</Text>
          <View style={styles.filterBody}>
            <Text style={styles.filterLabel}>{f.label}</Text>
            {f.message ? <Text style={[common.muted, styles.filterMsg]}>{f.message}</Text> : null}
          </View>
        </View>
      ))}
    </View>
  );
}

function RsBar({ rs }: { rs: number | null }) {
  if (rs === null) return <Text style={common.muted}>n/d</Text>;
  const pct = rs * 100;
  return (
    <View style={styles.rsWrap}>
      <View style={styles.rsBar}>
        <View style={[styles.rsZone, styles.rsZoneShort]} />
        <View style={[styles.rsZone, styles.rsZoneMid]} />
        <View style={[styles.rsZone, styles.rsZoneLong]} />
        <View style={[styles.rsMarker, { left: `${Math.min(100, Math.max(0, pct))}%` }]} />
      </View>
      <Text style={[common.mono, styles.rsPct]}>{pct.toFixed(0)}%</Text>
    </View>
  );
}

function SetupBadge({ ok }: { ok: boolean }) {
  return <Text style={ok ? common.pos : common.neg}>{ok ? "✓" : "✗"}</Text>;
}

function AssetCard({ asset }: { asset: AssetDiagnostics }) {
  const [open, setOpen] = useState({
    regime: true,
    screener: true,
    scenarios: true,
    a: false,
    b: false,
  });

  return (
    <View style={[common.card, styles.diagCard]}>
      <View style={common.row}>
        <TouchableOpacity onPress={() => openTradingView(asset.market, asset.symbol)}>
          <Text style={styles.ticker}>{asset.symbol}</Text>
        </TouchableOpacity>
        {asset.on_watchlist && (
          <View style={[styles.wlBadge]}>
            <Text style={styles.wlBadgeText}>In watchlist</Text>
          </View>
        )}
        <View style={{ flex: 1 }} />
        <View style={[styles.dirBadge, asset.direction === "long" ? styles.dirLong : styles.dirShort]}>
          <Text style={styles.dirBadgeText}>{asset.direction}</Text>
        </View>
        {asset.best_setup && (
          <View style={styles.setupBadge}>
            <Text style={styles.setupBadgeText}>Setup {asset.best_setup}</Text>
          </View>
        )}
      </View>

      <Text style={[common.muted, common.mono, { marginBottom: 8, fontSize: 12 }]}>
        {asset.price_live
          ? `Prezzo live ${fmt(asset.last_price)}${
              asset.price_asof ? ` @ ${new Date(asset.price_asof).toLocaleString()}` : ""
            }`
          : `Prezzo close D ${fmt(asset.last_price)}${
              asset.price_asof || asset.close_d_asof
                ? ` @ ${new Date(asset.price_asof ?? asset.close_d_asof!).toLocaleString()}`
                : ""
            }`}
        {asset.close_d_price != null && asset.price_live
          ? ` · filtri close D ${fmt(asset.close_d_price)}`
          : ""}
      </Text>

      {asset.blockers.length > 0 && (
        <View style={styles.blockers}>
          <Text style={styles.blockersTitle}>Blocker principali</Text>
          {asset.blockers.map((b, i) => (
            <Text key={i} style={styles.blockerItem}>• {b}</Text>
          ))}
        </View>
      )}

      <View style={styles.diagSection}>
        <TouchableOpacity onPress={() => setOpen((o) => ({ ...o, regime: !o.regime }))}>
          <Text style={styles.diagToggle}>1. Regime mercato {open.regime ? "▾" : "▸"}</Text>
        </TouchableOpacity>
        {open.regime && <FilterList filters={asset.regime_filters} />}
      </View>

      <View style={styles.diagSection}>
        <TouchableOpacity onPress={() => setOpen((o) => ({ ...o, screener: !o.screener }))}>
          <Text style={styles.diagToggle}>2. Screener (§3) {open.screener ? "▾" : "▸"}</Text>
        </TouchableOpacity>
        {open.screener && (
          <>
            <Text style={[common.muted, styles.rsLabel]}>Forza relativa (percentile)</Text>
            <RsBar rs={asset.rs_score} />
            <FilterList filters={asset.screener_filters} />
          </>
        )}
      </View>

      {(asset.scenarios?.length ?? 0) > 0 && (
        <View style={styles.diagSection}>
          <TouchableOpacity onPress={() => setOpen((o) => ({ ...o, scenarios: !o.scenarios }))}>
            <Text style={styles.diagToggle}>
              Scenari attivi ({asset.scenarios!.length}) {open.scenarios ? "▾" : "▸"}
            </Text>
          </TouchableOpacity>
          {open.scenarios &&
            asset.scenarios!.map((sc) => (
              <View key={sc.id} style={[common.card, { marginTop: 8 }]}>
                <Text style={styles.strong}>
                  {sc.titolo}
                  {!sc.lato_operativo ? " · protezione" : ""}
                </Text>
                <Text style={[common.muted, { fontSize: 11 }]}>{sc.id}</Text>
                <Text style={{ marginTop: 6 }}>{sc.lettura}</Text>
                <Text style={[common.muted, { marginTop: 6 }]}>Monitorare:</Text>
                {sc.monitorare.map((m, i) => (
                  <Text key={i} style={common.muted}>
                    • {m}
                  </Text>
                ))}
                <Text style={[common.muted, { marginTop: 6 }]}>
                  Invalidazione: {sc.invalidazione}
                </Text>
                <Text style={[common.muted, { fontSize: 11, marginTop: 4 }]}>{sc.footer}</Text>
              </View>
            ))}
        </View>
      )}

      <View style={styles.diagSection}>
        <TouchableOpacity onPress={() => setOpen((o) => ({ ...o, a: !o.a }))}>
          <Text style={styles.diagToggle}>
            3. Setup A {asset.setup_a.eligible ? "✓" : "✗"} {open.a ? "▾" : "▸"}
          </Text>
        </TouchableOpacity>
        {open.a && <FilterList filters={asset.setup_a.filters} />}
      </View>

      <View style={styles.diagSection}>
        <TouchableOpacity onPress={() => setOpen((o) => ({ ...o, b: !o.b }))}>
          <Text style={styles.diagToggle}>
            4. Setup B {asset.setup_b.eligible ? "✓" : "✗"} {open.b ? "▾" : "▸"}
          </Text>
        </TouchableOpacity>
        {open.b && <FilterList filters={asset.setup_b.filters} />}
      </View>

      <Text style={[common.muted, styles.footerMeta]}>
        Direzione analizzata: <Text style={styles.strong}>{asset.direction}</Text>
        {asset.suggested_direction && asset.suggested_direction !== asset.direction && (
          <> · naturale RS: {asset.suggested_direction}</>
        )}
        {" · "}
        Candidato screener: {asset.watchlist_eligible ? "sì" : "no"}
      </Text>
    </View>
  );
}

export default function DiagnosticsScreen() {
  const { state } = useApp();
  const [market, setMarket] = useState<"crypto" | "stocks">("crypto");
  const [items, setItems] = useState<AssetDiagnostics[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sortRs, setSortRs] = useState<"asc" | "desc">("asc");

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    try {
      const res = scanner.getDiagnostics(market);
      setItems(res.items);
      setSelected((prev) => prev ?? (res.items.length > 0 ? res.items[0].symbol : null));
    } catch (e) {
      setError((e as Error).message);
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, [market]);

  useEffect(() => {
    setSelected(null);
    load();
  }, [market, state?.last_scan, load]);

  const sorted = useMemo(() => {
    const copy = [...items];
    copy.sort((a, b) => {
      const ra = a.rs_score ?? 0.5;
      const rb = b.rs_score ?? 0.5;
      return sortRs === "asc" ? ra - rb : rb - ra;
    });
    return copy;
  }, [items, sortRs]);

  const selectedAsset = items.find((i) => i.symbol === selected) ?? null;

  const searchSymbol = async () => {
    const raw = query.trim().toUpperCase();
    if (!raw) return;
    const sym = market === "crypto" && !raw.endsWith("USDT") ? `${raw}USDT` : raw;
    setLoading(true);
    setError(null);
    try {
      const one = await scanner.getSymbolDiagnostic(market, sym);
      if (!one) throw new Error(`Simbolo ${sym} non trovato o dati insufficienti`);
      setItems((prev) => {
        const rest = prev.filter((p) => p.symbol !== one.symbol);
        return [...rest, one];
      });
      setSelected(one.symbol);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const filtered = sorted.filter(
    (r) => !query.trim() || r.symbol.includes(query.trim().toUpperCase())
  );

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
          <TextInput
            style={[common.input, styles.search]}
            placeholder="Cerca simbolo (es. ETHUSDT, NVDA)"
            placeholderTextColor={colors.textDim}
            value={query}
            onChangeText={setQuery}
            onSubmitEditing={searchSymbol}
            autoCapitalize="characters"
          />
          <TouchableOpacity
            style={[common.btn, common.btnSecondary, common.btnSmall, loading && common.btnDisabled]}
            onPress={searchSymbol}
            disabled={loading}
          >
            <Text style={common.btnSecondaryText}>Cerca</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[common.btn, common.btnSecondary, common.btnSmall, loading && common.btnDisabled]}
            onPress={load}
            disabled={loading}
          >
            <Text style={common.btnSecondaryText}>Aggiorna</Text>
          </TouchableOpacity>
        </View>

        {!state?.last_scan && (
          <View style={[common.card, styles.section]}>
            <Text style={common.muted}>
              Nessuna scansione ancora — avvia il backend o premi "Scansiona ora" dalla Dashboard.
            </Text>
          </View>
        )}

        {error && (
          <View style={[common.card, styles.section]}>
            <Text style={common.neg}>{error}</Text>
          </View>
        )}
        {loading && <Text style={[common.muted, styles.section]}>Caricamento diagnostica…</Text>}

        {selectedAsset ? (
          <View style={styles.section}>
            <AssetCard asset={selectedAsset} />
          </View>
        ) : (
          <View style={[common.card, styles.section]}>
            <Text style={common.empty}>Seleziona un asset dalla tabella o cerca un simbolo.</Text>
          </View>
        )}

        <View style={[common.card, styles.section]}>
          <View style={common.row}>
            <Text style={styles.universeTitle}>Riepilogo universo</Text>
            <View style={{ flex: 1 }} />
            <TouchableOpacity
              style={[common.btn, common.btnSecondary, common.btnSmall]}
              onPress={() => setSortRs((s) => (s === "asc" ? "desc" : "asc"))}
            >
              <Text style={common.btnSecondaryText}>RS {sortRs === "asc" ? "↑" : "↓"}</Text>
            </TouchableOpacity>
          </View>

          {filtered.length === 0 ? (
            <Text style={common.empty}>Nessun dato diagnostico.</Text>
          ) : (
            filtered.map((r) => (
              <TouchableOpacity
                key={r.symbol}
                style={[styles.universeRow, r.symbol === selected && styles.universeRowSelected]}
                onPress={() => setSelected(r.symbol)}
              >
                <Text style={[common.mono, styles.universeSym]}>{r.symbol}</Text>
                <Text style={[common.mono, styles.universeCol]}>
                  {r.rs_score !== null ? (r.rs_score * 100).toFixed(0) : "—"}
                </Text>
                <Text style={styles.universeCol}>{r.on_watchlist ? "✓" : "—"}</Text>
                <SetupBadge ok={r.setup_a.eligible} />
                <SetupBadge ok={r.setup_b.eligible} />
                <Text style={[common.muted, styles.universeBlocker]} numberOfLines={2}>
                  {r.blockers[0] ?? (r.on_watchlist ? "In watchlist" : "—")}
                </Text>
              </TouchableOpacity>
            ))
          )}

          <Text style={[common.muted, styles.universeFooter]}>
            {items.length} asset in cache
            {market === "stocks" ? " (top 30 RS + watchlist)" : " (universo crypto)"}.
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
  search: {
    flex: 1,
    minWidth: 160,
  },
  diagCard: {
    gap: spacing.sm,
  },
  ticker: {
    color: colors.text,
    fontWeight: "700",
    fontSize: 18,
    textDecorationLine: "underline",
    textDecorationStyle: "dashed",
    textDecorationColor: colors.textDim,
  },
  wlBadge: {
    marginLeft: 8,
    backgroundColor: "rgba(79, 140, 255, 0.2)",
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 12,
  },
  wlBadgeText: {
    color: colors.accent,
    fontSize: 11,
    fontWeight: "700",
  },
  dirBadge: {
    paddingHorizontal: 9,
    paddingVertical: 3,
    borderRadius: 20,
    marginLeft: 6,
  },
  dirLong: { backgroundColor: "rgba(46, 204, 143, 0.15)" },
  dirShort: { backgroundColor: "rgba(255, 92, 112, 0.15)" },
  dirBadgeText: {
    fontSize: 11,
    fontWeight: "700",
    textTransform: "uppercase",
    color: colors.text,
  },
  setupBadge: {
    marginLeft: 6,
    backgroundColor: "rgba(79, 140, 255, 0.12)",
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 12,
  },
  setupBadgeText: {
    color: colors.accent,
    fontSize: 11,
    fontWeight: "700",
  },
  blockers: {
    backgroundColor: "rgba(255, 92, 112, 0.08)",
    borderRadius: 8,
    padding: spacing.md,
    marginVertical: spacing.sm,
  },
  blockersTitle: {
    color: colors.red,
    fontWeight: "700",
    marginBottom: 4,
  },
  blockerItem: {
    color: colors.text,
    fontSize: 13,
    marginBottom: 2,
  },
  diagSection: {
    marginTop: spacing.sm,
  },
  diagToggle: {
    color: colors.text,
    fontWeight: "600",
    fontSize: 14,
    paddingVertical: 6,
  },
  rsLabel: {
    marginBottom: 6,
    fontSize: 12,
  },
  rsWrap: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.md,
    marginBottom: spacing.sm,
  },
  rsBar: {
    flex: 1,
    height: 10,
    flexDirection: "row",
    borderRadius: 5,
    overflow: "hidden",
    position: "relative",
  },
  rsZone: { flex: 1 },
  rsZoneShort: { backgroundColor: "rgba(255, 92, 112, 0.25)" },
  rsZoneMid: { backgroundColor: "rgba(139, 150, 171, 0.2)" },
  rsZoneLong: { backgroundColor: "rgba(46, 204, 143, 0.25)" },
  rsMarker: {
    position: "absolute",
    top: -2,
    width: 4,
    height: 14,
    marginLeft: -2,
    backgroundColor: colors.text,
    borderRadius: 2,
  },
  rsPct: {
    color: colors.text,
    fontSize: 13,
    minWidth: 36,
  },
  filterList: {
    gap: spacing.sm,
    marginTop: spacing.sm,
  },
  filterItem: {
    flexDirection: "row",
    gap: spacing.sm,
    padding: spacing.sm,
    borderRadius: 8,
    backgroundColor: colors.bg,
  },
  filter_pass: {},
  filter_fail: {},
  filter_warn: {},
  filter_skip: {},
  filterIcon: {
    fontSize: 16,
    width: 20,
    color: colors.text,
  },
  filterBody: {
    flex: 1,
  },
  filterLabel: {
    color: colors.text,
    fontWeight: "600",
    fontSize: 13,
  },
  filterMsg: {
    fontSize: 12,
    marginTop: 2,
  },
  footerMeta: {
    marginTop: 12,
    fontSize: 12,
    lineHeight: 18,
  },
  strong: {
    fontWeight: "700",
    color: colors.text,
  },
  universeTitle: {
    color: colors.textDim,
    fontSize: 13,
    textTransform: "uppercase",
    letterSpacing: 1,
    fontWeight: "600",
  },
  universeRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  universeRowSelected: {
    backgroundColor: "rgba(79, 140, 255, 0.08)",
  },
  universeSym: {
    color: colors.text,
    fontWeight: "600",
    width: 72,
    fontSize: 12,
  },
  universeCol: {
    color: colors.text,
    width: 36,
    fontSize: 12,
    textAlign: "center",
  },
  universeBlocker: {
    flex: 1,
    fontSize: 11,
  },
  universeFooter: {
    marginTop: spacing.md,
    fontSize: 12,
  },
});
