import React from "react";
import { StatusBar } from "expo-status-bar";
import { Text, View } from "react-native";
import { NavigationContainer } from "@react-navigation/native";
import { SafeAreaProvider } from "react-native-safe-area-context";

import { AppProvider, useApp } from "./src/context/AppContext";
import ErrorBoundary from "./src/components/ErrorBoundary";
import TabNavigator from "./src/navigation/TabNavigator";
import { colors, common } from "./src/theme";

function AppContent() {
  const { error, navigationRef } = useApp();

  return (
    <>
      <StatusBar style="light" />
      {error && (
        <View style={[common.card, { margin: 16, borderColor: colors.red }]}>
          <Text style={common.neg}>Errore: {error}</Text>
        </View>
      )}
      <NavigationContainer ref={navigationRef}>
        <TabNavigator />
      </NavigationContainer>
    </>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <SafeAreaProvider>
        <AppProvider>
          <View style={{ flex: 1, backgroundColor: colors.bg }}>
            <AppContent />
          </View>
        </AppProvider>
      </SafeAreaProvider>
    </ErrorBoundary>
  );
}
