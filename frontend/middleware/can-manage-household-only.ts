const { user } = useMealieAuth();
export default defineNuxtRouteMiddleware(() => {
  // 权限统一策略：仅管理员可访问家庭管理页
  if (user.value?.admin !== true) {
    navigateTo("/");
  }
});
