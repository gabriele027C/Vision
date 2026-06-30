import { StyleSheet } from "react-native";

export const colors = {
  bg: "#0b0f17",
  bgCard: "#121826",
  bgCardHover: "#1a2234",
  border: "#232d42",
  text: "#e6ebf4",
  textDim: "#8b96ab",
  accent: "#4f8cff",
  green: "#2ecc8f",
  red: "#ff5c70",
  yellow: "#f5c343",
};

export const radius = 12;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
};

export const common = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: colors.bg,
  },
  scrollContent: {
    padding: spacing.lg,
    paddingBottom: spacing.xl * 2,
  },
  card: {
    backgroundColor: colors.bgCard,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius,
    padding: 18,
  },
  cardTitle: {
    fontSize: 13,
    textTransform: "uppercase",
    letterSpacing: 1,
    color: colors.textDim,
    marginBottom: spacing.md,
    fontWeight: "600",
  },
  muted: {
    color: colors.textDim,
    fontSize: 12,
  },
  mono: {
    fontVariant: ["tabular-nums"],
  },
  row: {
    flexDirection: "row",
    alignItems: "center",
    flexWrap: "wrap",
    gap: spacing.md,
  },
  empty: {
    color: colors.textDim,
    padding: spacing.xl,
    textAlign: "center",
    fontSize: 14,
  },
  btn: {
    backgroundColor: colors.accent,
    paddingVertical: 9,
    paddingHorizontal: 18,
    borderRadius: 8,
  },
  btnText: {
    color: "#fff",
    fontWeight: "600",
    fontSize: 14,
  },
  btnSecondary: {
    backgroundColor: colors.bgCardHover,
    borderWidth: 1,
    borderColor: colors.border,
  },
  btnSecondaryText: {
    color: colors.text,
    fontWeight: "600",
    fontSize: 14,
  },
  btnSmall: {
    paddingVertical: 5,
    paddingHorizontal: 12,
  },
  btnSmallText: {
    fontSize: 12,
  },
  btnDisabled: {
    opacity: 0.5,
  },
  pos: {
    color: colors.green,
  },
  neg: {
    color: colors.red,
  },
  tabs: {
    flexDirection: "row",
    gap: spacing.sm,
  },
  tab: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.bgCard,
  },
  tabActive: {
    backgroundColor: colors.accent,
    borderColor: colors.accent,
  },
  tabText: {
    color: colors.textDim,
    fontWeight: "600",
    fontSize: 13,
  },
  tabTextActive: {
    color: "#fff",
  },
  field: {
    marginBottom: spacing.md,
  },
  fieldLabel: {
    color: colors.textDim,
    fontSize: 12,
    marginBottom: 6,
  },
  input: {
    backgroundColor: colors.bg,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    color: colors.text,
    fontSize: 14,
  },
  big: {
    fontSize: 28,
    fontWeight: "700",
    color: colors.text,
  },
});
