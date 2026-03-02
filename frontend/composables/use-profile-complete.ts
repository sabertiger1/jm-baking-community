import { useUserApi } from "~/composables/api/api-client";
import { useMealieAuth } from "~/composables/use-mealie-auth";

export const useProfileComplete = () => {
  const api = useUserApi();
  const auth = useMealieAuth();
  const SESSION_SUPPRESS_KEY = "profile-complete:suppress";
  
  const isStudentUser = computed(() => {
    const user = auth.user.value;
    if (!user) return false;
    return user.admin !== true;
  });

  const suppressForSession = computed({
    get: () => {
      if (!process.client) return false;
      return sessionStorage.getItem(SESSION_SUPPRESS_KEY) === "1";
    },
    set: (value: boolean) => {
      if (!process.client) return;
      if (value) {
        sessionStorage.setItem(SESSION_SUPPRESS_KEY, "1");
      } else {
        sessionStorage.removeItem(SESSION_SUPPRESS_KEY);
      }
    },
  });
  
  const isComplete = ref<boolean | null>(null);
  const checkResult = ref<any>(null);
  const showDialog = ref(false);
  const loading = ref(false);
  
  async function checkProfile() {
    if (!auth.user.value) {
      isComplete.value = null;
      return;
    }

    // 仅学生需要完善资料，其他角色直接视为已完善
    if (!isStudentUser.value) {
      isComplete.value = true;
      showDialog.value = false;
      checkResult.value = {
        isComplete: true,
        missingFields: [],
        message: null,
      };
      return;
    }
    
    loading.value = true;
    try {
      const result = await api.users.getUserDetailsCheck();
      checkResult.value = result;
      isComplete.value = result.isComplete;

      // 每次检查后都同步弹窗状态，避免完成后仍残留显示
      showDialog.value = !result.isComplete && !suppressForSession.value;
    } catch (error) {
      console.error("检查资料完整性失败:", error);
      // 接口异常时不强制弹窗，避免误拦截正常用户流程
      isComplete.value = null;
      showDialog.value = false;
    } finally {
      loading.value = false;
    }
  }
  
  async function refresh() {
    await checkProfile();
  }
  
  // 监听用户登录状态
  watch(() => auth.user.value, (newUser) => {
    if (newUser) {
      // 新登录会话时清除“本次不再提示”状态
      suppressForSession.value = false;
      checkProfile();
    } else {
      isComplete.value = null;
      showDialog.value = false;
      suppressForSession.value = false;
    }
  }, { immediate: true });

  watch(showDialog, (visible) => {
    // 用户手动关闭未完成弹窗：本会话不再弹
    if (!visible && isComplete.value === false) {
      suppressForSession.value = true;
    }
    // 重新弹出时取消抑制，确保主动打开后可继续提醒逻辑
    if (visible) {
      suppressForSession.value = false;
    }
  });
  
  return {
    isComplete: readonly(isComplete),
    checkResult: readonly(checkResult),
    showDialog,
    loading: readonly(loading),
    checkProfile,
    refresh,
  };
};
