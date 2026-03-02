<template>
  <div>
    <!-- 视频播放区域 -->
    <v-card v-if="recipe.makingVideoUrl || recipe.keyPointsVideoUrl" class="mb-4">
      <v-card-title>{{ $t("baking.making-video") }}</v-card-title>
      <v-card-text>
        <v-row v-if="recipe.makingVideoUrl">
          <v-col cols="12">
            <div class="text-subtitle-2 mb-2">{{ $t("baking.making-process") }}</div>
            <video
              :src="recipe.makingVideoUrl"
              controls
              style="width: 100%; max-height: 500px;"
              preload="metadata"
            />
          </v-col>
        </v-row>
        <v-row v-if="recipe.keyPointsVideoUrl" class="mt-4">
          <v-col cols="12">
            <div class="text-subtitle-2 mb-2">{{ $t("baking.key-points") }}</div>
            <video
              :src="recipe.keyPointsVideoUrl"
              controls
              style="width: 100%; max-height: 500px;"
              preload="metadata"
            />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- 作品集入口 -->
    <v-card>
      <v-card-title>
        <span>{{ $t("baking.works-collection") }}</span>
        <v-spacer />
        <v-btn
          v-if="profileComplete && !myWork"
          color="primary"
          prepend-icon="$globals.icons.plus"
          class="mr-2"
          @click="showSubmitDialog = true"
        >
          {{ $t("baking.submit-work") }}
        </v-btn>
        <v-chip
          v-else-if="myWork"
          color="success"
          class="mr-2"
        >
          <v-icon start :icon="$globals.icons.check" />
          {{ $t("baking.work-submitted") }}
        </v-chip>
        <v-btn
          color="primary"
          prepend-icon="$globals.icons.image"
          :to="`/baking/works/${recipe.id}`"
        >
          {{ $t("baking.view-all-works") }}
        </v-btn>
      </v-card-title>
      <v-card-text>
        <v-row v-if="recentWorks.length > 0">
          <v-col
            v-for="work in recentWorks"
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
              @mark-excellent="handleMarkExcellent"
            />
          </v-col>
        </v-row>
        <v-empty-state v-else :title="$t('baking.no-works')">
          <template #text>
            <div>{{ $t("baking.no-works-description") }}</div>
            <div v-if="profileComplete && !myWork" class="mt-2">
              <v-btn color="primary" @click="showSubmitDialog = true">
                {{ $t("baking.be-first") }}
              </v-btn>
            </div>
          </template>
        </v-empty-state>
      </v-card-text>
    </v-card>

    <!-- 作品提交对话框 -->
    <BakingWorkSubmitDialog
      v-model="showSubmitDialog"
      :recipe-id="recipe.id"
      @submitted="loadRecentWorks"
    />
  </div>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api/api-client";
import { useMealieAuth } from "~/composables/use-mealie-auth";
import { alert } from "~/composables/use-toast";
import type { Recipe } from "~/lib/api/types/recipe";
import BakingWorkCard from "./BakingWorkCard.vue";
import BakingWorkSubmitDialog from "./BakingWorkSubmitDialog.vue";

const props = defineProps<{
  recipe: Recipe;
}>();

const api = useUserApi();
const auth = useMealieAuth();
const { t: $t } = useI18n();
const display = useDisplay();
const isMobile = computed(() => display.smAndDown.value);

const recentWorks = ref<any[]>([]);
const myWork = ref<any>(null); // 我的作品
const profileComplete = ref(true);

// 检查资料完整性
async function checkProfileComplete() {
  try {
    const { data: check } = await api.users.getUserDetailsCheck();
    profileComplete.value = !!check?.isComplete;
  } catch (error) {
    console.error($t("baking.profile-incomplete-message"), error);
    profileComplete.value = false;
  }
}

const showRatingDialog = ref(false);
const showSubmitDialog = ref(false);
const markExcellentLoadingId = ref<string>("");

async function loadRecentWorks() {
  try {
    const result = await api.baking.getBakingRecords({
      recipeId: props.recipe.id,
      sortBy: "flower_count",
      order: "desc",
      perPage: 6,
    });
    recentWorks.value = result.items;
    
    // 检查当前用户是否已提交作品
    if (auth.user.value) {
      const myWorkResult = await api.baking.getBakingRecords({
        recipeId: props.recipe.id,
        userId: auth.user.value.id,
        perPage: 1,
      });
      myWork.value = myWorkResult.items[0] || null;
    }
  } catch (error) {
    console.error("加载作品失败:", error);
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
    await loadRecentWorks();
  } catch (error: any) {
    console.error("投票失败:", error);
    alert.warning(error?.response?.data?.detail || "投票失败，请稍后重试");
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
    const target = recentWorks.value.find((w: any) => w.id === workId);
    if (target) {
      target.isExcellent = true;
    }
    alert.success("已设为精华，作者已获得 +30 经验");
    await loadRecentWorks();
  } catch (error: any) {
    console.error("设为精华失败:", error);
    alert.warning(error?.response?.data?.detail || "设为精华失败，请稍后重试");
  } finally {
    markExcellentLoadingId.value = "";
  }
}

onMounted(() => {
  checkProfileComplete();
  loadRecentWorks();

  if (process.client) {
    window.addEventListener("baking-work-submitted", handleWorkSubmitted as EventListener);
  }
});

onBeforeUnmount(() => {
  if (process.client) {
    window.removeEventListener("baking-work-submitted", handleWorkSubmitted as EventListener);
  }
});

function handleWorkSubmitted(event: Event) {
  const customEvent = event as CustomEvent<{ recipeId?: string }>;
  if (customEvent.detail?.recipeId !== props.recipe.id) {
    return;
  }
  loadRecentWorks();
}
</script>
