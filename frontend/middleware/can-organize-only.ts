export default defineNuxtRouteMiddleware(() => {
  const { user } = useMealieAuth();
  // 权限统一策略：仅管理员可访问数据管理页
  if (user.value?.admin !== true) {
    console.warn("User is not allowed to organize data");
    navigateTo("/");
  }
});
