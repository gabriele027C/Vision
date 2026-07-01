import * as Updates from "expo-updates";

/**
 * Controlla aggiornamenti OTA (EAS Update) all'avvio.
 * In __DEV__ non fa nulla: Expo Go / Metro gestiscono il bundle localmente.
 */
export async function checkForAppUpdates(): Promise<void> {
  if (__DEV__) return;
  if (!Updates.isEnabled) return;

  try {
    const result = await Updates.checkForUpdateAsync();
    if (!result.isAvailable) return;

    await Updates.fetchUpdateAsync();
    await Updates.reloadAsync();
  } catch (err) {
    console.warn("[updates] OTA check failed:", err);
  }
}
