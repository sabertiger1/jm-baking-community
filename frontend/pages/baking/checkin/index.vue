<template>
  <v-container>
    <BasePageTitle :title="$t('baking.daily-checkin')" />
    
    <v-row justify="center">
      <v-col cols="12" md="8" lg="6">
        <v-card>
          <v-card-title class="text-h5 text-center">
            <v-icon size="48" color="primary" class="mr-2">$globals.icons.calendar</v-icon>
            每日签到
          </v-card-title>
          
          <v-card-text>
            <!-- 积分信息 -->
            <v-row class="mb-4">
              <v-col cols="6">
                <v-card variant="outlined" color="primary">
                  <v-card-text class="text-center">
                    <div class="text-h4">{{ points?.totalPoints || 0 }}</div>
                    <div class="text-body-2">总积分</div>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="6">
                <v-card variant="outlined" color="success">
                  <v-card-text class="text-center">
                    <div class="text-h4">{{ points?.consecutiveDays || 0 }}</div>
                    <div class="text-body-2">连续签到</div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>

            <!-- 签到按钮 -->
            <v-btn
              :disabled="isCheckedIn || loading"
              :loading="loading"
              color="primary"
              size="large"
              block
              @click="handleCheckin"
            >
              <v-icon start>$globals.icons.check</v-icon>
              {{ isCheckedIn ? "今日已签到" : "立即签到" }}
            </v-btn>

            <!-- 签到提示 -->
            <v-alert
              v-if="isCheckedIn"
              type="success"
              class="mt-4"
              variant="tonal"
            >
              今日已签到，获得 10 积分！已连续签到 {{ points?.consecutiveDays }} 天
            </v-alert>

            <v-alert
              v-else
              type="info"
              class="mt-4"
              variant="tonal"
            >
              每日签到可获得 10 积分，连续签到有额外奖励！
            </v-alert>
          </v-card-text>
        </v-card>

        <!-- 签到历史 -->
        <v-card class="mt-4">
          <v-card-title>签到记录</v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item>
                <v-list-item-title>最后签到日期</v-list-item-title>
                <v-list-item-subtitle>
                  {{ points?.lastCheckinDate || "从未签到" }}
                </v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <v-list-item-title>连续签到天数</v-list-item-title>
                <v-list-item-subtitle>{{ points?.consecutiveDays || 0 }} 天</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api/api-client";
import type { UserPoints } from "~/lib/api/user/baking";
import { alert } from "~/composables/use-toast";

definePageMeta({
  layout: "default",
});

const api = useUserApi();
const loading = ref(false);
const points = ref<UserPoints | null>(null);

function getLocalDateString() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

const isCheckedIn = computed(() => {
  if (!points.value?.lastCheckinDate) return false;
  const today = getLocalDateString();
  return points.value.lastCheckinDate === today;
});

async function loadPoints() {
  try {
    points.value = await api.baking.getMyPoints();
  } catch (error) {
    console.error("加载积分信息失败:", error);
  }
}

async function handleCheckin() {
  if (isCheckedIn.value) return;
  
  loading.value = true;
  try {
    const result = await api.baking.checkin();
    points.value = {
      ...points.value!,
      totalPoints: result.totalPoints,
      consecutiveDays: result.consecutiveDays,
      lastCheckinDate: getLocalDateString(),
    };
    alert.success(result.message || `签到成功，获得 ${result.pointsEarned || 10} 积分`);
  } catch (error: any) {
    console.error("签到失败:", error);
    const detail = error?.response?.data?.detail || error?.message || "签到失败，请稍后重试";
    alert.warning(String(detail));
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadPoints();
});
</script>
