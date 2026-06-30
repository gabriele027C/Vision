import React, { Component, type ReactNode } from "react";
import { ScrollView, Text, View } from "react-native";

import { colors, common, spacing } from "../theme";

interface Props {
  children: ReactNode;
}

interface State {
  error: Error | null;
}

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  render() {
    if (this.state.error) {
      return (
        <View style={[common.screen, { padding: spacing.lg }]}>
          <Text style={{ color: colors.red, fontWeight: "700", fontSize: 16, marginBottom: 8 }}>
            Errore avvio app
          </Text>
          <ScrollView>
            <Text style={{ color: colors.text, fontFamily: "monospace", fontSize: 12 }}>
              {this.state.error.message}
              {"\n\n"}
              {this.state.error.stack}
            </Text>
          </ScrollView>
        </View>
      );
    }
    return this.props.children;
  }
}
