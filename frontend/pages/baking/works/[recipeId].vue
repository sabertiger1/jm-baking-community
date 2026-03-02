<template>
  <v-container :class="isMobile ? 'px-2' : ''">
    <BasePageTitle :title="`${recipeName} - 作品集`" />
    
    <!-- 筛选和排序 -->
    <v-card class="mb-4">
      <v-card-text>
        <v-row>
          <v-col :cols="isMobile ? 4 : 12" md="4">
            <v-select
              v-model="filters.grade"
              :items="gradeList"
              label="按年级筛选"
              clearable
              prepend-icon="$globals.icons.school"
              density="compact"
            />
          </v-col>
          <v-col :cols="isMobile ? 4 : 12" md="4">
            <v-select
              v-model="filters.className"
              :items="classList"
              label="按班级筛选"
              clearable
              prepend-icon="$globals.icons.account"
              density="compact"
            />
          </v-col>
          <v-col :cols="isMobile ? 4 : 12" md="4">
            <v-select
              v-model="sortBy"
              :items="sortOptions"
              label="排序方式"
              prepend-icon="$globals.icons.sort"
              density="compact"
            />
          </v-col>
        </v-row>
        <div class="d-flex justify-end mt-2">
          <v-btn variant="text" @click="resetFilters">清空筛选</v-btn>
        </div>
      </v-card-text>
    </v-card>

    <!-- 作品瀑布流 -->
    <v-row v-if="loading">
      <v-col v-for="i in 6" :key="i" :cols="isMobile ? 4 : 12" sm="6" md="4" lg="3">
        <v-skeleton-loader type="image, article" />
      </v-col>
    </v-row>

    <v-row v-else-if="works.length > 0">
      <v-col
        v-for="work in works"
        :key="work.id"
        :cols="isMobile ? 4 : 12"
        sm="6"
        md="4"
        lg="3"
      >
        <BakingWorkCard
          :work="work"
          :show-excellent-action="!!auth.user.value?.admin"
          :excellent-loading="markExcellentLoadingId === work.id"
          @vote="handleVote"
          @cancel-vote="handleCancelVote"
          @mark-excellent="handleMarkExcellent"
        />
      </v-col>
    </v-row>

    <v-card v-else>
      <v-card-text class="text-center py-8">
        <div class="text-h6 mt-4">暂无作品</div>
        <div class="text-body-2 text-medium-emphasis">还没有学生提交作品</div>
      </v-card-text>
    </v-card>

    <!-- 分页 -->
    <v-pagination
      v-if="pagination.pages > 1"
      v-model="page"
      :length="pagination.pages"
      :total-visible="isMobile ? 5 : 7"
      class="mt-4"
    />
  </v-container>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";
import { useUserApi } from "~/composables/api/api-client";
import { useMealieAuth } from "~/composables/use-mealie-auth";
import type { BakingRecord } from "~/lib/api/user/baking";
import BakingWorkCard from "~/components/Domain/Baking/BakingWorkCard.vue";
import { alert } from "~/composables/use-toast";

definePageMeta({
  layout: "default",
});

const route = useRoute();
const router = useRouter();
const api = useUserApi();
const auth = useMealieAuth();
const display = useDisplay();
const isMobile = computed(() => display.smAndDown.value);
const recipeId = computed(() => route.params.recipeId as string);

const recipeName = ref(
  typeof route.query.recipeName === "string" && route.query.recipeName.trim()
    ? route.query.recipeName.trim()
    : "作品集",
);

async function loadRecipeName() {
  try {
    // 从作品记录中获取食谱名称（如果作品记录包含食谱信息）
    if (works.value.length > 0 && works.value[0].recipeName) {
      recipeName.value = works.value[0].recipeName;
      return;
    }
    // 无作品时，通过配方ID读取配方名称，避免显示“作品集 - 作品集”
    const { data } = await api.recipes.getOne(recipeId.value);
    if (data?.name) {
      recipeName.value = data.name;
    }
  } catch (error) {
    console.error("加载食谱信息失败:", error);
  }
}
const loading = ref(false);
const works = ref<BakingRecord[]>([]);
const page = ref(1);
const perPage = 12;
const pagination = ref({ total: 0, pages: 0 });

const filters = reactive({
  grade: null as string | null,
  className: null as string | null,
});

const sortBy = ref("created_at");
const sortOptions = [
  { title: "最新", value: "created_at" },
  { title: "鲜花最多", value: "flower_count" },
  { title: "鸡蛋最多", value: "egg_count" },
];

const gradeList = ref<string[]>([]);
const classList = ref<string[]>([]);
const resolvedRecipeId = ref<string>("");
const markExcellentLoadingId = ref<string>("");

async function loadWorks() {
  loading.value = true;
  try {
    const targetRecipeId = resolvedRecipeId.value || recipeId.value;
    const result = await api.baking.getBakingRecords({
      recipeId: targetRecipeId,
      grade: filters.grade || undefined,
      className: filters.className || undefined,
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
    gradeList.value = await api.baking.getBakingGradeList();
    classList.value = await api.baking.getBakingClassList(filters.grade || undefined);
  } catch (error) {
    console.error("加载筛选选项失败:", error);
  }
}

async function handleVote(workId: string, voteType: "flower" | "egg") {
  const voteLabel = voteType === "flower" ? "送花 🌸" : "送鸡蛋 🥚";
  const confirmed = window.confirm(`确认${voteLabel}吗？本次投票将扣除 5 积分。`);
  if (!confirmed) {
    return;
  }

  try {
    const result = await api.baking.vote({ workId, voteType });
    alert.success(result.message || "投票成功");
    await loadWorks();
  } catch (error: any) {
    console.error("投票失败:", error);
    alert.warning(error?.response?.data?.detail || "投票失败，请稍后重试");
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

async function handleMarkExcellent(workId: string) {
  if (markExcellentLoadingId.value) {
    return;
  }
  const confirmed = window.confirm("确认将该作品设为精华吗？作者将一次性获得 +30 经验。");
  if (!confirmed) {
    return;
  }
  try {
    markExcellentLoadingId.value = workId;
    await api.baking.markBakingRecordExcellent(workId);
    const target = works.value.find(work => work.id === workId);
    if (target) {
      target.isExcellent = true;
    }
    alert.success("已设为精华，作者已获得 +30 经验");
    await loadWorks();
  } catch (error: any) {
    console.error("设为精华失败:", error);
    alert.warning(error?.response?.data?.detail || "设为精华失败，请稍后重试");
  } finally {
    markExcellentLoadingId.value = "";
  }
}

function triggerListReload() {
  if (page.value !== 1) {
    page.value = 1;
    return;
  }
  loadWorks();
}

function resetFilters() {
  filters.grade = null;
  filters.className = null;
  sortBy.value = "created_at";
  triggerListReload();
}

watch(page, () => {
  loadWorks();
});

watch([sortBy, () => filters.grade, () => filters.className], () => {
  triggerListReload();
});

watch(() => filters.grade, async () => {
  filters.className = null;
  try {
    classList.value = await api.baking.getBakingClassList(filters.grade || undefined);
  } catch (error) {
    console.error("加载班级列表失败:", error);
    classList.value = [];
  }
});

onMounted(() => {
  loadWorks();
  loadFilters();
});

watch(
  () => [works.value.length, recipeId.value],
  () => {
    loadRecipeName();
  },
  { immediate: true },
);
</script>
