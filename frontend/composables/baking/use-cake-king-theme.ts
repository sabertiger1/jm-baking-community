import { useUserApi } from "~/composables/api/api-client";

const THEME_CLASS = "cake-king-theme";

export function useCakeKingTheme() {
  const auth = useMealieAuth();
  const route = useRoute();
  const api = useUserApi();
  const isCakeKingTheme = useState<boolean>("cake-king-theme-active", () => false);
  const lastFetchedAt = useState<number>("cake-king-theme-last-fetched-at", () => 0);
  const lastFetchedUserId = useState<string>("cake-king-theme-last-user-id", () => "");

  function applyThemeClass(enabled: boolean) {
    if (!process.client) return;
    document.documentElement.classList.toggle(THEME_CLASS, enabled);
    document.body.classList.toggle(THEME_CLASS, enabled);
  }

  async function refreshCakeKingTheme(force = false) {
    const userId = auth.user.value?.id || "";
    if (!userId) {
      isCakeKingTheme.value = false;
      applyThemeClass(false);
      return;
    }

    const now = Date.now();
    const shouldSkip =
      !force
      && lastFetchedUserId.value === userId
      && now - lastFetchedAt.value < 60_000;
    if (shouldSkip) return;

    try {
      const exp = await api.baking.getMyExperience();
      isCakeKingTheme.value = (exp.levelKey || "").trim() === "level-8";
    } catch {
      isCakeKingTheme.value = false;
    } finally {
      lastFetchedAt.value = now;
      lastFetchedUserId.value = userId;
      applyThemeClass(isCakeKingTheme.value);
    }
  }

  watch(
    () => auth.user.value?.id,
    () => {
      refreshCakeKingTheme(true);
    },
    { immediate: true },
  );

  watch(
    () => route.fullPath,
    () => {
      refreshCakeKingTheme(false);
    },
  );

  onMounted(() => {
    applyThemeClass(isCakeKingTheme.value);
    refreshCakeKingTheme(true);
  });

  onBeforeUnmount(() => {
    applyThemeClass(isCakeKingTheme.value);
  });

  return {
    isCakeKingTheme,
    refreshCakeKingTheme,
  };
}
