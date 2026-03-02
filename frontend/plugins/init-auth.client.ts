import { runAutoCheckin } from "~/composables/baking/use-auto-checkin";

export default defineNuxtPlugin({
  async setup() {
    const auth = useAuthBackend();

    console.debug("Initializing auth plugin");
    await auth.getSession();
    if (auth.status.value === "authenticated" && auth.data.value?.id) {
      await runAutoCheckin(auth.data.value.id, true);
    }
    console.debug("Auth plugin initialized");
  },
});
