import React from "react";
import { StyleSheet, Text, View } from "react-native";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { Ionicons } from "@expo/vector-icons";

import { useApp } from "../context/AppContext";
import DashboardScreen from "../screens/DashboardScreen";
import DiagnosticsScreen from "../screens/DiagnosticsScreen";
import JournalScreen from "../screens/JournalScreen";
import PlannerScreen from "../screens/PlannerScreen";
import SettingsScreen from "../screens/SettingsScreen";
import WatchlistScreen from "../screens/WatchlistScreen";
import type { RootTabParamList } from "../engine/types";
import { colors } from "../theme";

const Tab = createBottomTabNavigator<RootTabParamList>();

function TabIcon({
  name,
  color,
  badge,
}: {
  name: keyof typeof Ionicons.glyphMap;
  color: string;
  badge?: boolean;
}) {
  return (
    <View>
      <Ionicons name={name} size={22} color={color} />
      {badge && <View style={styles.badgeDot} />}
    </View>
  );
}

function HeaderTitle() {
  return (
    <View>
      <Text style={styles.logo}>
        Vision <Text style={styles.logoAccent}>TVS</Text>
      </Text>
      <Text style={styles.subtitle}>Trend · Volume · Struttura — swing D/4H</Text>
    </View>
  );
}

export default function TabNavigator() {
  const { state } = useApp();
  const unread = (state?.unread_alerts ?? 0) > 0;

  return (
    <Tab.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: colors.bg,
          borderBottomWidth: 1,
          borderBottomColor: colors.border,
        },
        headerTitle: () => <HeaderTitle />,
        headerTintColor: colors.text,
        tabBarStyle: {
          backgroundColor: colors.bgCard,
          borderTopColor: colors.border,
          borderTopWidth: 1,
        },
        tabBarActiveTintColor: colors.accent,
        tabBarInactiveTintColor: colors.textDim,
        tabBarLabelStyle: { fontSize: 11, fontWeight: "600" },
      }}
    >
      <Tab.Screen
        name="Dashboard"
        component={DashboardScreen}
        options={{
          tabBarLabel: "Dashboard",
          tabBarIcon: ({ color }) => (
            <TabIcon name="home-outline" color={color} badge={unread} />
          ),
        }}
      />
      <Tab.Screen
        name="Watchlist"
        component={WatchlistScreen}
        options={{
          tabBarLabel: "Watchlist",
          tabBarIcon: ({ color }) => <TabIcon name="list-outline" color={color} />,
        }}
      />
      <Tab.Screen
        name="Diagnostica"
        component={DiagnosticsScreen}
        options={{
          tabBarLabel: "Diagnostica",
          tabBarIcon: ({ color }) => <TabIcon name="search-outline" color={color} />,
        }}
      />
      <Tab.Screen
        name="Planner"
        component={PlannerScreen}
        options={{
          tabBarLabel: "Planner",
          tabBarIcon: ({ color }) => <TabIcon name="calculator-outline" color={color} />,
        }}
      />
      <Tab.Screen
        name="Journal"
        component={JournalScreen}
        options={{
          tabBarLabel: "Journal",
          tabBarIcon: ({ color }) => <TabIcon name="book-outline" color={color} />,
        }}
      />
      <Tab.Screen
        name="Impostazioni"
        component={SettingsScreen}
        options={{
          tabBarLabel: "Impostazioni",
          tabBarIcon: ({ color }) => <TabIcon name="settings-outline" color={color} />,
        }}
      />
    </Tab.Navigator>
  );
}

const styles = StyleSheet.create({
  logo: {
    fontSize: 18,
    fontWeight: "700",
    color: colors.text,
    letterSpacing: 0.5,
  },
  logoAccent: {
    color: colors.accent,
  },
  subtitle: {
    fontSize: 11,
    color: colors.textDim,
    fontWeight: "400",
  },
  badgeDot: {
    position: "absolute",
    top: -2,
    right: -6,
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.red,
  },
});
