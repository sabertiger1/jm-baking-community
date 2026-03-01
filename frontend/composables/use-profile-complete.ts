import { useUserApi } from "~/composables/api/api-client";
import { useMealieAuth } from "~/composables/use-mealie-auth";

export const useProfileComplete = () => {
  const api = useUserApi();
  const auth = useMealieAuth();
  
  const isComplete = ref<boolean | null>(null);
  const checkResult = ref<any>(null);
  const showDialog = ref(false);
  const loading = ref(false);
  
  async function checkProfile() {
    if (!auth.user.value) {
      isComplete.value = null;
      return;
    }
    
    loading.value = true;
    try {
      const result = await api.users.getUserDetailsCheck();
      checkResult.value = result;
      isComplete.value = result.is_complete;
      
      // 如果资料不完整，显示弹窗
      if (!result.is_complete) {
        showDialog.value = true;
      }
    } catch (error) {
      console.error("检查资料完整性失败:", error);
      // 如果接口不存在或出错，假设资料不完整
      isComplete.value = false;
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
      checkProfile();
    } else {
      isComplete.value = null;
      showDialog.value = false;
    }
  }, { immediate: true });
  
  return {
    isComplete: readonly(isComplete),
    checkResult: readonly(checkResult),
    showDialog,
    loading: readonly(loading),
    checkProfile,
    refresh,
  };
};
