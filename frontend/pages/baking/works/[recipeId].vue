<template>
  <v-container>
    <BasePageTitle :title="`${recipeName} - 作品集`" />
    
    <!-- 筛选和排序 -->
    <v-card class="mb-4">
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-select
              v-model="filters.className"
              :items="classList"
              label="按班级筛选"
              clearable
              prepend-icon="$globals.icons.school"
            />
          </v-col>
          <v-col cols="12" md="4">
            <v-select
              v-model="filters.groupName"
              :items="groupList"
              label="按小组筛选"
              clearable
              prepend-icon="$globals.icons.accountGroup"
            />
          </v-col>
          <v-col cols="12" md="4">
            <v-select
              v-model="sortBy"
              :items="sortOptions"
              label="排序方式"
              prepend-icon="$globals.icons.sort"
            />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- 作品瀑布流 -->
    <v-row v-if="loading">
      <v-col v-for="i in 6" :key="i" cols="12" sm="6" md="4" lg="3">
        <v-skeleton-loader type="image, article" />
      </v-col>
    </v-row>

    <v-row v-else-if="works.length > 0">
      <v-col
        v-for="work in works"
        :key="work.id"
        cols="12"
        sm="6"
        md="4"
        lg="3"
      >
        <BakingWorkCard
          :work="work"
          @vote="handleVote"
          @cancel-vote="handleCancelVote"
        />
      </v-col>
    </v-row>

    <v-card v-else>
      <v-card-text class="text-center py-8">
        <v-icon size="64" color="grey">$globals.icons.image</v-icon>
        <div class="text-h6 mt-4">暂无作品</div>
        <div class="text-body-2 text-medium-emphasis">还没有学生提交作品</div>
      </v-card-text>
    </v-card>

    <!-- 分页 -->
    <v-pagination
      v-if="pagination.pages > 1"
      v-model="page"
      :length="pagination.pages"
      :total-visible="7"
      class="mt-4"
    />
  </v-container>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";
import { useUserApi } from "~/composables/api/api-client";
import type { BakingRecord } from "~/lib/api/user/baking";
import BakingWorkCard from "~/components/Domain/Baking/BakingWorkCard.vue";
import { useRecipeApi } from "~/composables/api/api-client";

definePageMeta({
  layout: "default",
});

const route = useRoute();
const api = useUserApi();
const recipeId = computed(() => route.params.recipeId as string);

const recipeName = ref("作品集");

async function loadRecipeName() {
  try {
    // 从作品记录中获取食谱名称（如果作品记录包含食谱信息）
    if (works.value.length > 0 && works.value[0].recipeName) {
      recipeName.value = works.value[0].recipeName;
      return;
    }
    // 否则尝试从API获取
    // 注意：这里需要根据实际的API结构调整
    // 如果baking records包含recipe信息，可以直接使用
  } catch (error) {
    console.error("加载食谱信息失败:", error);
  }
}
const loading = ref(false);
const works = ref<BakingRecord[]>([]);
const page = ref(1);
const perPage = 20;
const pagination = ref({ total: 0, pages: 0 });

const filters = reactive({
  className: null as string | null,
  groupName: null as string | null,
});

const sortBy = ref("created_at");
const sortOptions = [
  { title: "最新", value: "created_at" },
  { title: "鲜花最多", value: "flower_count" },
  { title: "鸡蛋最多", value: "egg_count" },
];

const classList = ref<string[]>([]);
const groupList = ref<string[]>([]);

async function loadWorks() {
  loading.value = true;
  try {
    const result = await api.baking.getBakingRecords({
      recipeId: recipeId.value,
      className: filters.className || undefined,
      groupName: filters.groupName || undefined,
      sortBy: sortBy.value,
      order: "desc",
      page: page.value,
      perPage,
    });
    works.value = result.items;
    pagination.value = {
      total: result.total,
      pages: result.pages,
    };
    
    // 如果还没有加载食谱名称，从第一个作品获取
    if (works.value.length > 0 && works.value[0].recipeName && recipeName.value === "作品集") {
      recipeName.value = works.value[0].recipeName;
    }
  } catch (error) {
    console.error("加载作品失败:", error);
  } finally {
    loading.value = false;
  }
}

async function loadFilters() {
  try {
    classList.value = await api.baking.getClassList();
    groupList.value = await api.baking.getGroupList();
  } catch (error) {
    console.error("加载筛选选项失败:", error);
  }
}

async function handleVote(workId: string, voteType: "flower" | "egg") {
  try {
    await api.baking.vote({ workId, voteType });
    await loadWorks();
  } catch (error: any) {
    console.error("投票失败:", error);
    // 显示错误提示
  }
}

async function handleCancelVote(workId: string, voteType: string) {
  try {
    await api.baking.cancelVote(workId, voteType);
    await loadWorks();
  } catch (error) {
    console.error("取消投票失败:", error);
  }
}

watch([page, sortBy, () => filters.className, () => filters.groupName], () => {
  loadWorks();
});

onMounted(() => {
  loadRecipeName();
  loadWorks();
  loadFilters();
});
</script>
