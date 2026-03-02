<template>
  <v-container :class="isMobile ? 'px-2' : ''">
    <BasePageTitle title="鲜花/鸡蛋记录" />

    <v-card class="mb-4">
      <v-card-text>
        <v-btn-toggle v-model="activeType" mandatory color="primary" divided>
          <v-btn value="flower">🌸 鲜花</v-btn>
          <v-btn value="egg">🥚 鸡蛋</v-btn>
        </v-btn-toggle>
      </v-card-text>
    </v-card>

    <v-row v-if="loading">
      <v-col cols="12" v-for="idx in 4" :key="idx">
        <v-skeleton-loader type="list-item-two-line" />
      </v-col>
    </v-row>

    <v-card v-else-if="records.length === 0">
      <v-card-text class="text-medium-emphasis text-center py-8">
        暂无记录
      </v-card-text>
    </v-card>

    <v-card v-else>
      <v-list lines="two">
        <v-list-item v-for="item in records" :key="item.voteId">
          <template #prepend>
            <v-avatar color="grey-lighten-4" size="36">
              <span>{{ item.voteType === "flower" ? "🌸" : "🥚" }}</span>
            </v-avatar>
          </template>
          <v-list-item-title>
            {{ item.voterName || "未知用户" }} 送出了{{ item.voteType === "flower" ? "鲜花" : "鸡蛋" }}
          </v-list-item-title>
          <v-list-item-subtitle>
            {{ item.recipeName || "未知配方" }} · {{ formatDateTime(item.createdAt) }}
          </v-list-item-subtitle>
        </v-list-item>
      </v-list>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api/api-client";
import type { ReceivedVoteRecord } from "~/lib/api/user/baking";

definePageMeta({
  layout: "default",
});

const api = useUserApi();
const display = useDisplay();
const route = useRoute();
const router = useRouter();
const isMobile = computed(() => display.smAndDown.value);

const activeType = ref<"flower" | "egg">((route.query.type as "flower" | "egg") || "flower");
const loading = ref(false);
const records = ref<ReceivedVoteRecord[]>([]);

function formatDateTime(value: string) {
  return new Date(value).toLocaleString("zh-CN");
}

async function loadRecords() {
  loading.value = true;
  try {
    const result = await api.baking.getReceivedVotes({
      voteType: activeType.value,
      limit: 200,
    });
    records.value = result.items || [];
  } catch (error) {
    console.error("加载投票记录失败:", error);
    records.value = [];
  } finally {
    loading.value = false;
  }
}

watch(activeType, async (val) => {
  await router.replace({ query: { ...route.query, type: val } });
  await loadRecords();
}, { immediate: true });
</script>
