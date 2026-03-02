import { alert } from "~/composables/use-toast";

function getLocalDateString() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function getAutoCheckinStorageKey(userId: string) {
  return `baking:auto-checkin:${userId}`;
}

function isAlreadyCheckedInError(error: any) {
  const status = error?.response?.status;
  const detail = String(error?.response?.data?.detail ?? "");
  return status === 400 && detail.includes("今日已经签到过了");
}

export async function runAutoCheckin(userId: string, showToast = true): Promise<boolean> {
  if (!process.client || !userId) {
    return false;
  }

  const today = getLocalDateString();
  const storageKey = getAutoCheckinStorageKey(userId);
  if (localStorage.getItem(storageKey) === today) {
    return false;
  }

  const { $axios } = useNuxtApp();

  try {
    const { data } = await $axios.post("/api/points/checkin", {});
    localStorage.setItem(storageKey, today);

    if (showToast) {
      const pointsEarned = data?.pointsEarned ?? data?.points_earned ?? 10;
      const message = data?.message || `签到成功，获得 ${pointsEarned} 积分`;
      alert.success(message);
    }
    return true;
  } catch (error) {
    if (isAlreadyCheckedInError(error)) {
      localStorage.setItem(storageKey, today);
      return false;
    }
    console.warn("Auto check-in failed:", error);
    return false;
  }
}
