export default defineNuxtPlugin({
  async setup() {
    const auth = useAuthBackend();
    const { $axios } = useNuxtApp();

    function getTodayString() {
      return new Date().toISOString().split("T")[0];
    }

    function getAutoCheckinStorageKey(userId: string) {
      return `baking:auto-checkin:${userId}`;
    }

    async function tryAutoCheckin(userId: string) {
      const today = getTodayString();
      const storageKey = getAutoCheckinStorageKey(userId);
      const checkedToday = localStorage.getItem(storageKey) === today;
      if (checkedToday) {
        return;
      }

      try {
        const { data } = await $axios.get("/api/points/me");
        const lastCheckinDate = data?.lastCheckinDate ?? data?.last_checkin_date ?? null;

        if (lastCheckinDate === today) {
          localStorage.setItem(storageKey, today);
          return;
        }

        await $axios.post("/api/points/checkin", {});
        localStorage.setItem(storageKey, today);
      } catch (error) {
        console.warn("Auto check-in failed:", error);
      }
    }

    console.debug("Initializing auth plugin");
    await auth.getSession();
    if (auth.status.value === "authenticated" && auth.data.value?.id) {
      await tryAutoCheckin(auth.data.value.id);
    }
    console.debug("Auth plugin initialized");
  },
});
