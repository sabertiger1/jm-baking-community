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
            <v-chip color="primary" :size="isMobile ? 'default' : 'large'" variant="elevated">
              <v-icon start>{{ $globals.icons.star }}</v-icon>
              {{ points.totalPoints }} 积分
            </v-chip>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- 统计信息 -->
    <v-row>
      <v-col cols="6" md="4">
        <v-card>
          <v-card-text>
            <div class="text-h6">{{ myWorksCount }}</div>
            <div class="text-body-2 text-medium-emphasis">我的作品</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="6" md="4">
        <v-card>
          <v-card-text>
            <div class="text-h6">{{ points.consecutiveDays }}</div>
            <div class="text-body-2 text-medium-emphasis">连续签到天数</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="6" md="4">
        <v-card class="clickable-card" @click="goVoteHistory('flower')">
          <v-card-text>
            <div class="d-flex align-center" style="gap: 8px;">
              <div class="text-h6">{{ receivedFlowers }}</div>
              <v-chip v-if="flowerDelta > 0" size="x-small" color="success" variant="tonal">
                +{{ flowerDelta }}
              </v-chip>
            </div>
            <div class="text-body-2 text-medium-emphasis">🌸 收到鲜花</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="6" md="4">
        <v-card class="clickable-card" @click="goVoteHistory('egg')">
          <v-card-text>
            <div class="d-flex align-center" style="gap: 8px;">
              <div class="text-h6">{{ receivedEggs }}</div>
              <v-chip v-if="eggDelta > 0" size="x-small" color="success" variant="tonal">
                +{{ eggDelta }}
              </v-chip>
            </div>
            <div class="text-body-2 text-medium-emphasis">🥚 收到鸡蛋</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 我的作品 -->
    <v-card class="mt-4">
      <v-card-title>我的作品</v-card-title>
      <v-card-text>
        <v-row v-if="myWorks.length > 0">
          <v-col
            v-for="work in myWorks"
            :key="work.id"
            :cols="isMobile ? 4 : 12"
            sm="6"
            md="4"
            lg="3"
          >
            <BakingWorkCard :work="work" />
          </v-col>
        </v-row>
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
import type { BakingRecord } from "~/lib/api/user/baking";
import BakingWorkCard from "~/components/Domain/Baking/BakingWorkCard.vue";
import UserAvatar from "~/components/Domain/User/UserAvatar.vue";

definePageMeta({
  layout: "default",
});

const api = useUserApi();
const auth = useMealieAuth();
const display = useDisplay();
const router = useRouter();
const user = computed(() => auth.user.value);
const isMobile = computed(() => display.smAndDown.value);

const userDetails = ref<any>(null);
const points = ref({
  totalPoints: 0,
  consecutiveDays: 0,
  lastCheckinDate: null as string | null,
});
const myWorks = ref<BakingRecord[]>([]);
const myWorksCount = computed(() => myWorks.value.length);
const receivedFlowers = ref(0);
const receivedEggs = ref(0);
const flowerDelta = ref(0);
const eggDelta = ref(0);

const profileClassText = computed(() => {
  const grade = userDetails.value?.grade;
  const className = userDetails.value?.className;
  const label = [grade, className].filter(Boolean).join(" ");
  return label || "未设置班级信息";
});

function normalizePoints(raw: any) {
  return {
    totalPoints: Number(raw?.totalPoints ?? raw?.total_points ?? 0),
    consecutiveDays: Number(raw?.consecutiveDays ?? raw?.consecutive_days ?? 0),
    lastCheckinDate: raw?.lastCheckinDate ?? raw?.last_checkin_date ?? null,
  };
}

function getVoteDeltaStorageKey() {
  return `baking-vote-delta:${user.value?.id || "anonymous"}`;
}

function updateVoteDelta() {
  if (typeof localStorage === "undefined") {
    flowerDelta.value = 0;
    eggDelta.value = 0;
    return;
  }
  const key = getVoteDeltaStorageKey();
  const raw = localStorage.getItem(key);
  let previous = { flowers: 0, eggs: 0 };
  if (raw) {
    try {
      previous = JSON.parse(raw);
    } catch {
      previous = { flowers: 0, eggs: 0 };
    }
  }
  flowerDelta.value = Math.max(0, receivedFlowers.value - (previous.flowers || 0));
  eggDelta.value = Math.max(0, receivedEggs.value - (previous.eggs || 0));
  localStorage.setItem(
    key,
    JSON.stringify({
      flowers: receivedFlowers.value,
      eggs: receivedEggs.value,
    }),
  );
}

function goVoteHistory(type: "flower" | "egg") {
  router.push({ path: "/baking/votes", query: { type } });
}

function openProfileSettings() {
  router.push("/user/profile/edit");
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

  // 加载我的作品
  try {
    if (user.value?.id) {
      const works = await api.baking.getBakingRecords();
      myWorks.value = works.items.filter(work => work.userId === user.value?.id);
      receivedFlowers.value = myWorks.value.reduce((sum, work) => sum + work.flowerCount, 0);
      receivedEggs.value = myWorks.value.reduce((sum, work) => sum + work.eggCount, 0);
      updateVoteDelta();
    }
  } catch (error) {
    console.error("加载作品失败:", error);
  }
}

onMounted(() => {
  loadProfile();
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
</style>
