<template>
  <v-container>
    <BasePageTitle :title="$t('baking.leaderboard')" />
    
    <v-card>
      <v-card-title>
        <v-tabs v-model="tab">
          <v-tab value="points">积分排行榜</v-tab>
          <v-tab value="flowers">鲜花榜</v-tab>
          <v-tab value="eggs">鸡蛋榜</v-tab>
        </v-tabs>
      </v-card-title>

      <v-card-text>
        <v-tabs-window v-model="tab">
          <!-- 积分排行榜 -->
          <v-tabs-window-item value="points">
            <v-list>
              <v-list-item
                v-for="(item, index) in pointsLeaderboard"
                :key="item.userId"
                :class="{ 'bg-primary-lighten-5': index < 3 }"
              >
                <template #prepend>
                  <v-avatar :color="getRankColor(index)">
                    <span class="text-h6">{{ index + 1 }}</span>
                  </v-avatar>
                </template>
                <v-list-item-title>{{ item.realName || item.userId }}</v-list-item-title>
                <v-list-item-subtitle>{{ item.className || "" }}</v-list-item-subtitle>
                <template #append>
                  <v-chip color="primary">{{ item.totalPoints }} 积分</v-chip>
                </template>
              </v-list-item>
            </v-list>
          </v-tabs-window-item>

          <!-- 鲜花榜 -->
          <v-tabs-window-item value="flowers">
            <v-list>
              <v-list-item
                v-for="(item, index) in flowersLeaderboard"
                :key="item.id"
                :class="{ 'bg-primary-lighten-5': index < 3 }"
              >
                <template #prepend>
                  <v-avatar :color="getRankColor(index)">
                    <span class="text-h6">{{ index + 1 }}</span>
                  </v-avatar>
                </template>
                <v-list-item-title>{{ item.userFullName }}</v-list-item-title>
                <v-list-item-subtitle>{{ item.className }}</v-list-item-subtitle>
                <template #append>
                  <v-chip color="pink">
                    <v-icon start>$globals.icons.flower</v-icon>
                    {{ item.flowerCount }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
          </v-tabs-window-item>

          <!-- 鸡蛋榜 -->
          <v-tabs-window-item value="eggs">
            <v-list>
              <v-list-item
                v-for="(item, index) in eggsLeaderboard"
                :key="item.id"
                :class="{ 'bg-primary-lighten-5': index < 3 }"
              >
                <template #prepend>
                  <v-avatar :color="getRankColor(index)">
                    <span class="text-h6">{{ index + 1 }}</span>
                  </v-avatar>
                </template>
                <v-list-item-title>{{ item.userFullName }}</v-list-item-title>
                <v-list-item-subtitle>{{ item.className }}</v-list-item-subtitle>
                <template #append>
                  <v-chip color="orange">
                    <v-icon start>$globals.icons.egg</v-icon>
                    {{ item.eggCount }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
          </v-tabs-window-item>
        </v-tabs-window>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api/api-client";
import type { UserPoints, BakingRecord } from "~/lib/api/user/baking";

definePageMeta({
  layout: "default",
});

const api = useUserApi();
const tab = ref("points");
const loading = ref(false);

const pointsLeaderboard = ref<any[]>([]);
const flowersLeaderboard = ref<BakingRecord[]>([]);
const eggsLeaderboard = ref<BakingRecord[]>([]);
const userDetailsCache = ref<Record<string, any>>({});

function getRankColor(index: number): string {
  if (index === 0) return "gold";
  if (index === 1) return "silver";
  if (index === 2) return "bronze";
  return "grey";
}

async function getUserName(userId: string): Promise<string> {
  if (userDetailsCache.value[userId]) {
    return userDetailsCache.value[userId].realName || userId;
  }
  try {
    const details = await api.users.getUserDetailsPublic(userId);
    userDetailsCache.value[userId] = details;
    return details.realName || userId;
  } catch (error) {
    console.error("获取用户详情失败:", error);
    return userId;
  }
}

async function loadPointsLeaderboard() {
  loading.value = true;
  try {
    const leaderboard = await api.baking.getLeaderboard(50);
    // 加载每个用户的详细信息
    const enrichedLeaderboard = await Promise.all(
      leaderboard.map(async (item: any) => {
        try {
          const details = await api.users.getUserDetailsPublic(item.userId);
          return {
            ...item,
            realName: details.realName,
            className: details.className,
          };
        } catch (error) {
          return {
            ...item,
            realName: item.userId,
            className: "",
          };
        }
      })
    );
    pointsLeaderboard.value = enrichedLeaderboard;
  } catch (error) {
    console.error("加载积分排行榜失败:", error);
  } finally {
    loading.value = false;
  }
}

async function loadFlowersLeaderboard() {
  loading.value = true;
  try {
    const result = await api.baking.getBakingRecords({
      sortBy: "flower_count",
      order: "desc",
      perPage: 50,
    });
    flowersLeaderboard.value = result.items;
  } catch (error) {
    console.error("加载鲜花榜失败:", error);
  } finally {
    loading.value = false;
  }
}

async function loadEggsLeaderboard() {
  loading.value = true;
  try {
    const result = await api.baking.getBakingRecords({
      sortBy: "egg_count",
      order: "desc",
      perPage: 50,
    });
    eggsLeaderboard.value = result.items;
  } catch (error) {
    console.error("加载鸡蛋榜失败:", error);
  } finally {
    loading.value = false;
  }
}

watch(tab, (newTab) => {
  if (newTab === "points" && pointsLeaderboard.value.length === 0) {
    loadPointsLeaderboard();
  } else if (newTab === "flowers" && flowersLeaderboard.value.length === 0) {
    loadFlowersLeaderboard();
  } else if (newTab === "eggs" && eggsLeaderboard.value.length === 0) {
    loadEggsLeaderboard();
  }
});

onMounted(() => {
  loadPointsLeaderboard();
});
</script>
