<template>
  <v-container :class="isMobile ? 'px-2' : ''">
    <BasePageTitle title="作品详情" />
    <div class="d-flex flex-wrap mb-3" style="gap: 8px;">
      <v-btn variant="text" prepend-icon="$globals.icons.back" @click="goBack">
        返回
      </v-btn>
      <v-btn
        v-if="work"
        variant="text"
        :to="`/baking/works/${work.recipeId}`"
      >
        返回作品集
      </v-btn>
      <v-btn
        v-if="recipeRoute"
        color="primary"
        variant="tonal"
        :to="recipeRoute"
      >
        查看配方页
      </v-btn>
    </div>

    <v-card v-if="loading">
      <v-card-text>
        <v-skeleton-loader type="image, article, actions" />
      </v-card-text>
    </v-card>

    <v-card v-else-if="work">
      <v-img :src="work.imageUrl" :aspect-ratio="isMobile ? 1 : 16 / 9" cover />
      <v-card-text>
        <div class="d-flex align-center mb-3" style="gap: 10px;">
          <v-avatar size="36">
            <v-img :src="workAvatarSrc" cover />
          </v-avatar>
          <div>
            <div class="text-subtitle-1 font-weight-medium">{{ work.userFullName || work.userName }}</div>
          </div>
        </div>

        <div class="text-body-2 text-medium-emphasis mb-2">
          配方：
          <NuxtLink
            v-if="recipeRoute"
            :to="recipeRoute"
            class="recipe-link"
          >
            {{ work.recipeName || "-" }}
          </NuxtLink>
          <span v-else>{{ work.recipeName || "-" }}</span>
        </div>
        <div class="text-body-2 text-medium-emphasis mb-4">
          制作时间：{{ createdAtText }}<span v-if="classText"> · {{ classText }}</span>
        </div>

        <div v-if="work.notes" class="text-body-1 mb-4">
          {{ work.notes }}
        </div>

        <div class="d-flex align-center flex-wrap mb-4" style="gap: 8px;">
          <v-chip color="pink" variant="tonal">🌸 {{ work.flowerCount }}</v-chip>
          <v-chip color="orange" variant="tonal">🥚 {{ work.eggCount }}</v-chip>
        </div>

        <div class="d-flex flex-wrap" style="gap: 8px;">
          <v-btn
            :disabled="work.hasFlowered"
            :color="work.hasFlowered ? 'pink' : 'default'"
            variant="outlined"
            @click="handleVote('flower')"
          >
            送花 🌸
          </v-btn>
          <v-btn
            :disabled="work.hasEgged"
            :color="work.hasEgged ? 'orange' : 'default'"
            variant="outlined"
            @click="handleVote('egg')"
          >
            送鸡蛋 🥚
          </v-btn>
          <v-btn variant="text" :to="`/baking/works/${work.recipeId}`">查看该配方作品集</v-btn>
        </div>
      </v-card-text>
    </v-card>

    <v-card v-else>
      <v-card-text class="text-center py-8 text-medium-emphasis">
        作品不存在或已被删除
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api/api-client";
import type { BakingRecord } from "~/lib/api/user/baking";
import { alert } from "~/composables/use-toast";
import { useMealieAuth } from "~/composables/use-mealie-auth";

definePageMeta({
  layout: "default",
});

const route = useRoute();
const router = useRouter();
const api = useUserApi();
const auth = useMealieAuth();
const display = useDisplay();
const isMobile = computed(() => display.smAndDown.value);
const workId = computed(() => route.params.workId as string);
const recipeSlug = ref<string | null>(null);
const groupSlug = computed(() => (route.params.groupSlug as string) || auth.user.value?.groupSlug || "");
const recipeRoute = computed(() => {
  if (!recipeSlug.value || !groupSlug.value) {
    return "";
  }
  return `/g/${groupSlug.value}/r/${recipeSlug.value}`;
});

const loading = ref(false);
const work = ref<BakingRecord | null>(null);
const fallbackAvatar = "/img/default-avatar.svg";

function normalizeAvatarUrl(value?: string | null) {
  if (!value) {
    return null;
  }
  const trimmed = value.trim();
  if (!trimmed || trimmed === "null" || trimmed === "undefined") {
    return null;
  }
  if (
    trimmed.startsWith("data:image/")
    || trimmed.startsWith("http://")
    || trimmed.startsWith("https://")
    || trimmed.startsWith("/")
  ) {
    return trimmed;
  }
  return null;
}

const workAvatarSrc = computed(() => {
  const detailAvatar = normalizeAvatarUrl(work.value?.avatarUrl);
  if (detailAvatar) {
    return detailAvatar;
  }
  if (work.value?.userId) {
    return api.users.userProfileImage(work.value.userId) || fallbackAvatar;
  }
  return fallbackAvatar;
});

const createdAtText = computed(() => {
  if (!work.value?.createdAt) {
    return "-";
  }
  return new Date(work.value.createdAt).toLocaleString("zh-CN");
});

const classText = computed(() => {
  if (!work.value) {
    return "";
  }
  const workRaw = work.value as unknown as Record<string, unknown>;
  const grade = (typeof work.value.grade === "string" ? work.value.grade : workRaw.grade) as string | undefined;
  const className = (
    typeof work.value.className === "string"
      ? work.value.className
      : workRaw.class_name
  ) as string | undefined;
  return [grade, className].filter(value => typeof value === "string" && value.trim().length > 0).join(" ");
});

async function loadWork() {
  loading.value = true;
  try {
    work.value = await api.baking.getBakingRecord(workId.value);
    recipeSlug.value = null;
    if (work.value?.recipeId) {
      const { data } = await api.recipes.getOne(work.value.recipeId);
      if (data?.slug) {
        recipeSlug.value = data.slug;
      }
    }
  } catch (error) {
    console.error("加载作品详情失败:", error);
    work.value = null;
  } finally {
    loading.value = false;
  }
}

function goBack() {
  if (window.history.length > 1) {
    router.back();
    return;
  }
  if (work.value?.recipeId) {
    router.push(`/baking/works/${work.value.recipeId}`);
    return;
  }
  router.push("/baking/profile");
}

async function handleVote(type: "flower" | "egg") {
  if (!work.value) {
    return;
  }
  try {
    await api.baking.vote({ workId: work.value.id, voteType: type });
    await loadWork();
  } catch (error: any) {
    console.error("投票失败:", error);
    alert.error(error?.response?.data?.detail || "投票失败，请稍后重试");
  }
}

onMounted(() => {
  loadWork();
});
</script>

<style scoped>
.recipe-link {
  text-decoration: none;
  color: rgb(var(--v-theme-primary));
}
</style>
