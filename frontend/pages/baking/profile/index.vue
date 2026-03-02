<template>
  <v-container :class="isMobile ? 'px-2' : ''">
    <BasePageTitle :title="$t('baking.my-profile')" />
    
    <v-card class="mb-4 profile-hero-card" rounded="lg">
      <v-card-text>
        <v-row align="center" :class="isMobile ? 'text-center' : ''">
          <v-col :cols="isMobile ? 12 : 'auto'">
            <div class="clickable-profile d-inline-flex" @click="openProfileSettings">
              <UserAvatar
                v-if="user?.id"
                :user-id="user.id"
                :size="isMobile ? '84' : '96'"
                :tooltip="false"
              />
              <v-avatar v-else :size="isMobile ? 84 : 96">
                <v-icon>{{ $globals.icons.account }}</v-icon>
              </v-avatar>
            </div>
          </v-col>
          <v-col :cols="isMobile ? 12 : undefined">
            <h2 :class="isMobile ? 'text-h6 mb-1 clickable-profile' : 'text-h5 mb-1 clickable-profile'" @click="openProfileSettings">
              {{ userDetails?.realName || user?.fullName }}
            </h2>
            <p class="text-body-2 text-medium-emphasis mb-0 clickable-profile" @click="openProfileSettings">
              {{ profileClassText }}
            </p>
          </v-col>
          <v-col :cols="isMobile ? 12 : 'auto'">
            <div class="d-flex flex-wrap justify-center" style="gap: 8px;">
              <v-chip color="primary" :size="isMobile ? 'default' : 'large'" variant="elevated">
                <v-icon start>{{ $globals.icons.star }}</v-icon>
                {{ points.totalPoints }} 积分
              </v-chip>
              <v-chip :size="isMobile ? 'default' : 'large'" variant="tonal" :class="experience.levelKey || 'level-1'">
                {{ experience.levelEmoji || "🧈" }} {{ experience.levelName || "烘焙小白" }}
              </v-chip>
            </div>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- 统计信息 -->
    <v-row>
      <v-col cols="6" md="4">
        <v-card class="clickable-card" @click="openMyWorksSpace">
          <v-card-text>
            <div class="text-h6">{{ myWorksCount }}</div>
            <div class="text-body-2 text-medium-emphasis">我的作品</div>
            <div class="text-caption text-medium-emphasis mt-1">点击进入作品空间</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="6" md="4">
        <v-card class="clickable-card" @click="openCheckinCalendar">
          <v-card-text>
            <div class="text-h6">{{ points.consecutiveDays }}</div>
            <div class="text-body-2 text-medium-emphasis">连续签到天数</div>
            <div class="text-caption text-medium-emphasis mt-1">点击查看签到日历</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="6" md="4">
        <v-card class="clickable-card" @click="goVoteHistory('flower')">
          <v-card-text>
            <div class="d-flex align-center" style="gap: 8px;">
              <div class="text-h6">{{ receivedFlowers }}</div>
              <v-chip v-if="flowerDelta > 0" size="x-small" color="success" variant="tonal" class="delta-chip-pop">
                +{{ flowerDelta }}
              </v-chip>
            </div>
            <div class="text-body-2 text-medium-emphasis">🌸 收到鲜花</div>
            <v-expand-transition>
              <div v-if="flowerFeedback" class="delta-feedback mt-1">
                {{ flowerFeedback }}
              </div>
            </v-expand-transition>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="6" md="4">
        <v-card class="clickable-card" @click="goVoteHistory('egg')">
          <v-card-text>
            <div class="d-flex align-center" style="gap: 8px;">
              <div class="text-h6">{{ receivedEggs }}</div>
              <v-chip v-if="eggDelta > 0" size="x-small" color="success" variant="tonal" class="delta-chip-pop">
                +{{ eggDelta }}
              </v-chip>
            </div>
            <div class="text-body-2 text-medium-emphasis">🥚 收到鸡蛋</div>
            <v-expand-transition>
              <div v-if="eggFeedback" class="delta-feedback mt-1">
                {{ eggFeedback }}
              </div>
            </v-expand-transition>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-card class="mt-4">
      <v-card-title class="d-flex align-center">
        <span>经验成长</span>
        <v-spacer />
        <v-btn size="small" variant="text" @click="showExpHistoryDialog = true">
          经验变动历史
        </v-btn>
      </v-card-title>
      <v-card-text>
        <div class="d-flex align-center" style="gap: 8px;">
          <span class="text-body-2 text-medium-emphasis">当前等级</span>
          <v-chip size="small" variant="tonal" :class="experience.levelKey || 'level-1'">
            {{ experience.levelEmoji || "🧈" }} {{ experience.levelName || "烘焙小白" }}
          </v-chip>
        </div>
        <v-progress-linear
          class="mt-3"
          color="primary"
          rounded
          height="14"
          :model-value="expProgressPercent"
        />
        <div class="text-caption text-medium-emphasis mt-2">
          <template v-if="experience.nextLevelMinExp">
            {{ experience.totalExp }} / {{ experience.nextLevelMinExp }}（下一等级：{{ experience.nextLevelName }}）
          </template>
          <template v-else>
            {{ experience.totalExp }}（已满级）
          </template>
        </div>
      </v-card-text>
    </v-card>

    <v-dialog v-model="checkinCalendarDialog" max-width="420">
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon class="mr-2">{{ $globals.icons.calendar }}</v-icon>
          签到日历
          <v-spacer />
          <v-btn :icon="$globals.icons.close" variant="text" @click="checkinCalendarDialog = false" />
        </v-card-title>
        <v-card-text>
          <div class="text-body-2 text-medium-emphasis mb-2">
            签到规则：每日签到 +{{ dailyCheckinPoints }} 积分，每天仅可签到 1 次。
          </div>
          <div class="text-body-2 text-medium-emphasis mb-3">
            已记录历史签到 {{ checkinCalendarDates.length }} 天
          </div>
          <v-date-picker
            class="checkin-calendar-readonly"
            :model-value="checkinCalendarDates"
            :multiple="true"
            hide-header
            show-adjacent-months
            color="primary"
            :first-day-of-week="firstDayOfWeek"
            :local="$i18n.locale"
            readonly
          />
        </v-card-text>
      </v-card>
    </v-dialog>

    <v-dialog v-model="showExpHistoryDialog" max-width="560">
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon class="mr-2">{{ $globals.icons.star }}</v-icon>
          经验变动历史
          <v-spacer />
          <v-btn :icon="$globals.icons.close" variant="text" @click="showExpHistoryDialog = false" />
        </v-card-title>
        <v-card-text>
          <div class="text-caption text-medium-emphasis mb-2">
            共 {{ expHistoryPagination.total }} 条
          </div>
          <v-list v-if="expHistory.length > 0" lines="two">
            <v-list-item v-for="item in expHistory" :key="item.id">
              <template #prepend>
                <v-chip size="x-small" :color="item.expDelta >= 0 ? 'success' : 'error'" variant="tonal">
                  {{ item.expDelta >= 0 ? `+${item.expDelta}` : item.expDelta }} EXP
                </v-chip>
              </template>
              <v-list-item-title>{{ expSourceLabel(item.source) }}</v-list-item-title>
              <v-list-item-subtitle>
                {{ formatDateTime(item.createdAt) }} · 总经验 {{ item.totalExpAfter }}
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
          <div v-else class="text-center py-6 text-medium-emphasis">暂无经验变动记录</div>
          <v-pagination
            v-if="expHistoryPagination.pages > 1"
            v-model="expHistoryPage"
            :length="expHistoryPagination.pages"
            :total-visible="isMobile ? 5 : 7"
            class="mt-2"
          />
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- 我的作品 -->
    <v-card class="mt-4">
      <v-card-title>我的作品</v-card-title>
      <v-card-text>
        <v-row v-if="myWorks.length > 0">
          <v-col
            v-for="work in myWorks"
            :key="work.id"
            :cols="isMobile ? mobileWorkCols : 12"
            sm="6"
            md="4"
            lg="3"
          >
            <BakingWorkCard
              :work="work"
              :show-vote-actions="false"
              :show-excellent-action="!!auth.user.value?.admin"
              :excellent-loading="markExcellentLoadingId === work.id"
              @mark-excellent="handleMarkExcellent"
            />
          </v-col>
        </v-row>
        <v-pagination
          v-if="myWorksPagination.pages > 1"
          v-model="myWorksPage"
          :length="myWorksPagination.pages"
          :total-visible="isMobile ? 5 : 7"
          class="mt-4"
        />
        <div v-else class="text-center py-8 text-medium-emphasis">
          暂无作品
        </div>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api/api-client";
import { useMealieAuth } from "~/composables/use-mealie-auth";
import { useHouseholdSelf } from "~/composables/use-households";
import { alert } from "~/composables/use-toast";
import type { BakingRecord, UserExperience, UserExperienceHistoryItem } from "~/lib/api/user/baking";
import BakingWorkCard from "~/components/Domain/Baking/BakingWorkCard.vue";
import UserAvatar from "~/components/Domain/User/UserAvatar.vue";

definePageMeta({
  layout: "default",
});

const api = useUserApi();
const auth = useMealieAuth();
const display = useDisplay();
const router = useRouter();
const { household } = useHouseholdSelf();
const user = computed(() => auth.user.value);
const isMobile = computed(() => display.smAndDown.value);
const mobileWorkCols = computed(() => (display.width.value < 380 ? 6 : 4));
const checkinCalendarDialog = ref(false);
const showExpHistoryDialog = ref(false);
const checkinHistoryDates = ref<string[]>([]);
const dailyCheckinPoints = ref(10);

const userDetails = ref<any>(null);
const points = ref({
  totalPoints: 0,
  consecutiveDays: 0,
  lastCheckinDate: null as string | null,
});
const experience = ref<UserExperience>({
  userId: "",
  totalExp: 0,
  levelKey: "level-1",
  levelName: "烘焙小白",
  levelEmoji: "🧈",
  currentLevelMinExp: 0,
  nextLevelMinExp: 100,
  nextLevelName: "面点学徒",
});
const expHistory = ref<UserExperienceHistoryItem[]>([]);
const expHistoryPage = ref(1);
const expHistoryPerPage = 12;
const expHistoryPagination = ref({ total: 0, pages: 0 });
const myWorks = ref<BakingRecord[]>([]);
const myWorksPage = ref(1);
const myWorksPerPage = 6;
const myWorksPagination = ref({ total: 0, pages: 0 });
const myWorksCount = computed(() => myWorksPagination.value.total);
const receivedFlowers = ref(0);
const receivedEggs = ref(0);
const flowerDelta = ref(0);
const eggDelta = ref(0);
const flowerFeedback = ref("");
const eggFeedback = ref("");
let flowerFeedbackTimer: ReturnType<typeof setTimeout> | null = null;
let eggFeedbackTimer: ReturnType<typeof setTimeout> | null = null;
const markExcellentLoadingId = ref("");

const profileClassText = computed(() => {
  const grade = userDetails.value?.grade;
  const className = userDetails.value?.className;
  const label = [grade, className].filter(Boolean).join(" ");
  return label || "未设置班级信息";
});

const expProgressPercent = computed(() => {
  const total = Number(experience.value.totalExp || 0);
  const minExp = Number(experience.value.currentLevelMinExp || 0);
  const nextExp = experience.value.nextLevelMinExp;
  if (!nextExp || nextExp <= minExp) {
    return 100;
  }
  const ratio = ((total - minExp) / (nextExp - minExp)) * 100;
  return Math.max(0, Math.min(100, ratio));
});

const firstDayOfWeek = computed(() => {
  return household.value?.preferences?.firstDayOfWeek || 0;
});

const checkinCalendarDates = computed<Date[]>(() => {
  return checkinHistoryDates.value
    .map(dateStr => new Date(`${dateStr}T00:00:00`))
    .filter(dateObj => !Number.isNaN(dateObj.getTime()));
});

function normalizePoints(raw: any) {
  return {
    totalPoints: Number(raw?.totalPoints ?? raw?.total_points ?? 0),
    consecutiveDays: Number(raw?.consecutiveDays ?? raw?.consecutive_days ?? 0),
    lastCheckinDate: raw?.lastCheckinDate ?? raw?.last_checkin_date ?? null,
  };
}

function getVoteDeltaStorageKey() {
  return `baking-vote-last-seen:${user.value?.id || "anonymous"}`;
}

function updateVoteDelta() {
  if (typeof localStorage === "undefined") {
    flowerDelta.value = 0;
    eggDelta.value = 0;
    return;
  }
  const key = getVoteDeltaStorageKey();
  const raw = localStorage.getItem(key);
  if (!raw) {
    localStorage.setItem(key, JSON.stringify({ flowers: receivedFlowers.value, eggs: receivedEggs.value }));
    flowerDelta.value = 0;
    eggDelta.value = 0;
    return;
  }

  let previous = { flowers: receivedFlowers.value, eggs: receivedEggs.value };
  if (raw) {
    try {
      previous = JSON.parse(raw);
    } catch {
      previous = { flowers: receivedFlowers.value, eggs: receivedEggs.value };
    }
  }
  const nextFlowerDelta = Math.max(0, receivedFlowers.value - (previous.flowers || 0));
  const nextEggDelta = Math.max(0, receivedEggs.value - (previous.eggs || 0));
  const flowerDeltaChanged = nextFlowerDelta !== flowerDelta.value;
  const eggDeltaChanged = nextEggDelta !== eggDelta.value;

  flowerDelta.value = nextFlowerDelta;
  eggDelta.value = nextEggDelta;

  if (flowerDeltaChanged && flowerDelta.value > 0) {
    flowerFeedback.value = `鲜花 +${flowerDelta.value}`;
    if (flowerFeedbackTimer) {
      clearTimeout(flowerFeedbackTimer);
    }
    flowerFeedbackTimer = setTimeout(() => {
      flowerFeedback.value = "";
    }, 2400);
  }

  if (eggDeltaChanged && eggDelta.value > 0) {
    eggFeedback.value = `鸡蛋 +${eggDelta.value}`;
    if (eggFeedbackTimer) {
      clearTimeout(eggFeedbackTimer);
    }
    eggFeedbackTimer = setTimeout(() => {
      eggFeedback.value = "";
    }, 2400);
  }
}

function goVoteHistory(type: "flower" | "egg") {
  if (typeof localStorage !== "undefined") {
    localStorage.setItem(
      getVoteDeltaStorageKey(),
      JSON.stringify({
        flowers: receivedFlowers.value,
        eggs: receivedEggs.value,
      }),
    );
  }
  flowerDelta.value = 0;
  eggDelta.value = 0;
  flowerFeedback.value = "";
  eggFeedback.value = "";
  router.push({ path: "/baking/votes", query: { type } });
}

function openCheckinCalendar() {
  checkinCalendarDialog.value = true;
}

function formatDateTime(value: string) {
  return new Date(value).toLocaleString("zh-CN");
}

function expSourceLabel(source: string) {
  const map: Record<string, string> = {
    checkin: "每日签到",
    submit_work: "提交烘焙作品",
    recipe_comment: "配方评论",
    work_excellent: "作品被设为优秀",
    receive_flower: "收到鲜花",
  };
  return map[source] || source;
}

function openProfileSettings() {
  router.push("/user/profile/edit");
}

function openMyWorksSpace() {
  router.push("/baking/my-works");
}

async function loadProfile() {
  // 加载用户资料（失败时不影响积分与作品）
  try {
    const { data: details } = await api.users.getUserDetails();
    if (details) {
      userDetails.value = {
        realName: details.realName,
        grade: details.grade,
        className: details.className,
        avatarUrl: details.avatarUrl,
      };
    }
  } catch (error) {
    console.warn("加载用户详情失败，回退到基础资料:", error);
  }

  if (!userDetails.value) {
    try {
      const { data: self } = await api.users.getSelf();
      if (self) {
        userDetails.value = {
          realName: self.fullName,
          grade: null,
          className: null,
          avatarUrl: null,
        };
      }
    } catch (error) {
      console.error("加载基础用户信息失败:", error);
    }
  }

  // 加载积分（独立错误处理，避免被其他请求影响）
  try {
    points.value = normalizePoints(await api.baking.getMyPoints());
  } catch (error) {
    console.error("加载积分失败:", error);
  }

  await loadCheckinHistory();
  await loadExperience();
  await loadExperienceHistory();

  await loadMyWorks();
  await loadMyWorkStats();
}

async function loadExperience() {
  try {
    const result = await api.baking.getMyExperience();
    experience.value = {
      userId: result.userId || (result as any).user_id || "",
      totalExp: Number(result.totalExp ?? (result as any).total_exp ?? 0),
      levelKey: result.levelKey || (result as any).level_key || "level-1",
      levelName: result.levelName || (result as any).level_name || "烘焙小白",
      levelEmoji: result.levelEmoji || (result as any).level_emoji || "🧈",
      currentLevelMinExp: Number(result.currentLevelMinExp ?? (result as any).current_level_min_exp ?? 0),
      nextLevelMinExp: (result.nextLevelMinExp ?? (result as any).next_level_min_exp ?? null) as number | null,
      nextLevelName: (result.nextLevelName ?? (result as any).next_level_name ?? null) as string | null,
    };
  } catch (error) {
    console.error("加载经验信息失败:", error);
  }
}

async function loadExperienceHistory() {
  try {
    const result = await api.baking.getMyExperienceHistory(expHistoryPage.value, expHistoryPerPage);
    expHistory.value = (result.items || []).map((item: any) => ({
      id: item.id,
      source: item.source,
      expDelta: Number(item.expDelta ?? item.exp_delta ?? 0),
      totalExpAfter: Number(item.totalExpAfter ?? item.total_exp_after ?? 0),
      note: item.note,
      createdAt: item.createdAt ?? item.created_at,
    }));
    expHistoryPagination.value = {
      total: Number(result.total ?? 0),
      pages: Number(result.pages ?? 0),
    };
  } catch (error) {
    console.error("加载经验历史失败:", error);
    expHistory.value = [];
    expHistoryPagination.value = { total: 0, pages: 0 };
  }
}

watch(expHistoryPage, () => {
  if (showExpHistoryDialog.value) {
    loadExperienceHistory();
  }
});

watch(showExpHistoryDialog, (opened) => {
  if (opened) {
    expHistoryPage.value = 1;
    loadExperienceHistory();
  }
});

async function loadCheckinHistory() {
  try {
    const history = await api.baking.getCheckinHistory();
    checkinHistoryDates.value = history?.checkinDates
      || (history as any)?.checkin_dates
      || [];
    dailyCheckinPoints.value = Number(
      history?.dailyPoints
      ?? (history as any)?.daily_points
      ?? 10,
    );
  } catch (error) {
    console.error("加载签到历史失败:", error);
    checkinHistoryDates.value = [];
    dailyCheckinPoints.value = 10;
  }
}

async function loadMyWorks() {
  try {
    if (!user.value?.id) {
      myWorks.value = [];
      myWorksPagination.value = { total: 0, pages: 0 };
      return;
    }
    const result = await api.baking.getBakingRecords({
      userId: user.value.id,
      sortBy: "flower_count",
      order: "desc",
      page: myWorksPage.value,
      perPage: myWorksPerPage,
    });
    myWorks.value = result.items;
    myWorksPagination.value = {
      total: result.total,
      pages: result.pages,
    };
  } catch (error) {
    console.error("加载我的作品失败:", error);
  }
}

async function handleMarkExcellent(workId: string) {
  if (markExcellentLoadingId.value) return;
  const confirmed = window.confirm("确认将该作品设为精华吗？作者将一次性获得 +30 经验。");
  if (!confirmed) return;
  try {
    markExcellentLoadingId.value = workId;
    await api.baking.markBakingRecordExcellent(workId);
    const target = myWorks.value.find(work => work.id === workId);
    if (target) {
      target.isExcellent = true;
    }
    alert.success("已设为精华，作者已获得 +30 经验");
    await Promise.all([loadMyWorks(), loadMyWorkStats()]);
  } catch (error: any) {
    console.error("设为精华失败:", error);
    alert.warning(error?.response?.data?.detail || "设为精华失败，请稍后重试");
  } finally {
    markExcellentLoadingId.value = "";
  }
}

async function loadMyWorkStats() {
  try {
    if (!user.value?.id) {
      receivedFlowers.value = 0;
      receivedEggs.value = 0;
      updateVoteDelta();
      return;
    }

    let currentPage = 1;
    let pages = 1;
    let flowers = 0;
    let eggs = 0;

    do {
      const result = await api.baking.getBakingRecords({
        userId: user.value.id,
        page: currentPage,
        perPage: 100,
      });
      result.items.forEach((work) => {
        flowers += work.flowerCount;
        eggs += work.eggCount;
      });
      pages = result.pages || 0;
      currentPage += 1;
    } while (currentPage <= pages);

    receivedFlowers.value = flowers;
    receivedEggs.value = eggs;
    updateVoteDelta();
  } catch (error) {
    console.error("加载作品统计失败:", error);
  }
}

watch(myWorksPage, () => {
  loadMyWorks();
});

onMounted(() => {
  loadProfile();
});

onBeforeUnmount(() => {
  if (flowerFeedbackTimer) {
    clearTimeout(flowerFeedbackTimer);
  }
  if (eggFeedbackTimer) {
    clearTimeout(eggFeedbackTimer);
  }
});
</script>

<style scoped>
.profile-hero-card {
  border: 1px solid rgba(var(--v-theme-primary), 0.14);
  background: linear-gradient(135deg, rgba(var(--v-theme-primary), 0.08), transparent);
}

.clickable-profile {
  cursor: pointer;
}

.clickable-card {
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.clickable-card:hover {
  transform: translateY(-1px);
}

.delta-chip-pop {
  animation: delta-pop 0.35s ease-out;
}

.delta-feedback {
  color: rgb(var(--v-theme-success));
  font-size: 12px;
  font-weight: 600;
  animation: delta-float 0.8s ease-out;
}

@keyframes delta-pop {
  0% { transform: scale(0.7); opacity: 0.4; }
  100% { transform: scale(1); opacity: 1; }
}

@keyframes delta-float {
  0% { transform: translateY(6px); opacity: 0; }
  100% { transform: translateY(0); opacity: 1; }
}

.level-1 { color: #8f8f8f; }
.level-2 { color: #b8860b; }
.level-3 { color: #c06d00; }
.level-4 { color: #d85b9b; }
.level-5 { color: #6e4a2f; }
.level-6 { color: #4a2a1a; }
.level-7 { color: #b13a8f; }
.level-8 { color: #b8860b; }

.checkin-calendar-readonly {
  pointer-events: none;
}
</style>
