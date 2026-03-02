<template>
  <v-container :class="isMobile ? 'px-2' : ''">
    <BasePageTitle title="鲜花/鸡蛋记录" />

    <v-card class="mb-4">
      <v-card-text>
        <div class="d-flex align-center flex-wrap" :class="isMobile ? 'vote-toolbar-mobile' : ''" style="gap: 12px;">
          <v-btn-toggle
            v-model="activeType"
            mandatory
            color="primary"
            divided
            class="vote-type-toggle"
            :class="isMobile ? 'w-100' : ''"
          >
            <v-btn value="flower" :class="isMobile ? 'flex-1' : ''">🌸 鲜花</v-btn>
            <v-btn value="egg" :class="isMobile ? 'flex-1' : ''">🥚 鸡蛋</v-btn>
          </v-btn-toggle>
          <span class="text-body-2 text-medium-emphasis">
            共 {{ pagination.total }} 条记录
          </span>
        </div>
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
        <v-list-item
          v-for="item in records"
          :key="item.voteId"
          :to="`/baking/work/${item.workId}`"
          class="vote-record-item"
        >
          <template #prepend>
            <v-avatar color="grey-lighten-4" :size="isMobile ? 32 : 36">
              <span>{{ item.voteType === "flower" ? "🌸" : "🥚" }}</span>
            </v-avatar>
          </template>
          <v-list-item-title class="vote-record-title">
            {{ item.voterName || "未知用户" }} 送出了{{ item.voteType === "flower" ? "鲜花" : "鸡蛋" }}
          </v-list-item-title>
          <v-list-item-subtitle class="vote-record-subtitle">
            {{ item.recipeName || "未知配方" }} · {{ formatDateTime(item.createdAt) }}
          </v-list-item-subtitle>
        </v-list-item>
      </v-list>
      <v-divider />
      <v-card-actions class="justify-center">
        <v-pagination
          v-model="page"
          :length="pagination.pages"
          :total-visible="isMobile ? 5 : 7"
        />
      </v-card-actions>
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
const page = ref(Number(route.query.page || 1));
const perPage = 12;
const pagination = ref({
  total: 0,
  pages: 0,
});

function formatDateTime(value: string) {
  return new Date(value).toLocaleString("zh-CN");
}

async function loadRecords() {
  loading.value = true;
  try {
    const result = await api.baking.getReceivedVotes({
      voteType: activeType.value,
      page: page.value,
      perPage,
    });
    records.value = result.items || [];
    pagination.value.total = result.total || 0;
    pagination.value.pages = result.pages || 0;
  } catch (error) {
    console.error("加载投票记录失败:", error);
    records.value = [];
    pagination.value.total = 0;
    pagination.value.pages = 0;
  } finally {
    loading.value = false;
  }
}

watch(activeType, () => {
  if (page.value !== 1) {
    page.value = 1;
  }
});

watch([activeType, page], async ([type, pageNo]) => {
  await router.replace({ query: { ...route.query, type, page: String(pageNo) } });
  await loadRecords();
}, { immediate: true });
</script>

<style scoped>
.vote-toolbar-mobile {
  flex-direction: column;
  align-items: stretch !important;
}

.vote-type-toggle :deep(.v-btn) {
  min-width: 84px;
}

.flex-1 {
  flex: 1 1 0;
}

.vote-record-item :deep(.v-list-item__content) {
  min-width: 0;
}

.vote-record-title,
.vote-record-subtitle {
  white-space: normal;
  word-break: break-word;
  line-height: 1.35;
}
</style>
