<template>
  <v-card class="work-card-clickable" @click="openWorkDetail">
    <v-img
      :src="work.imageUrl"
      :aspect-ratio="1"
      cover
    >
      <template #placeholder>
        <v-skeleton-loader type="image" />
      </template>
    </v-img>

    <v-card-text>
      <!-- 用户信息 -->
      <div class="d-flex align-center mb-2">
        <v-avatar size="32" class="mr-2">
          <v-img :src="workAvatarSrc" cover />
        </v-avatar>
        <div class="flex-grow-1" style="min-width: 0;">
          <div class="text-body-2 font-weight-medium">
            {{ work.userFullName || work.userName }}
            <span v-if="work.recipeName" class="text-medium-emphasis"> · {{ work.recipeName }}</span>
          </div>
          <div class="text-caption text-medium-emphasis">
            制作时间：{{ createdAtText }}<span v-if="classText"> · {{ classText }}</span>
          </div>
        </div>
      </div>

      <!-- 制作心得 -->
      <p v-if="work.notes" class="text-body-2 text-medium-emphasis mb-2">
        {{ work.notes }}
      </p>

      <!-- 统计和操作 -->
      <div class="d-flex" :class="isMobile ? 'flex-column' : 'justify-space-between align-center'" style="gap: 8px;">
        <div class="d-flex flex-column text-caption text-medium-emphasis" style="gap: 4px;">
          <div>🌸 鲜花数：{{ work.flowerCount }}</div>
          <div>🥚 鸡蛋数：{{ work.eggCount }}</div>
        </div>

        <div class="d-flex gap-1" :class="isMobile ? 'justify-end' : ''">
          <v-btn
            :disabled="work.hasFlowered"
            :color="work.hasFlowered ? 'pink' : 'default'"
            size="small"
            variant="text"
            @click.stop="handleVote('flower')"
          >
            送花 🌸
          </v-btn>
          <v-btn
            :disabled="work.hasEgged"
            :color="work.hasEgged ? 'orange' : 'default'"
            size="small"
            variant="text"
            @click.stop="handleVote('egg')"
          >
            送鸡蛋 🥚
          </v-btn>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api/api-client";
import type { BakingRecord } from "~/lib/api/user/baking";

const props = defineProps<{
  work: BakingRecord;
}>();

const emit = defineEmits<{
  vote: [workId: string, voteType: "flower" | "egg"];
  "cancel-vote": [workId: string, voteType: string];
}>();
const router = useRouter();
const display = useDisplay();
const isMobile = computed(() => display.smAndDown.value);
const api = useUserApi();
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

const classText = computed(() => {
  const workRaw = props.work as unknown as Record<string, unknown>;
  const grade = (typeof props.work.grade === "string" ? props.work.grade : workRaw.grade) as string | undefined;
  const className = (
    typeof props.work.className === "string"
      ? props.work.className
      : workRaw.class_name
  ) as string | undefined;
  return [grade, className].filter(value => typeof value === "string" && value.trim().length > 0).join(" ");
});

const workAvatarSrc = computed(() => {
  const detailAvatar = normalizeAvatarUrl(props.work.avatarUrl);
  if (detailAvatar) {
    return detailAvatar;
  }
  if (props.work.userId) {
    return api.users.userProfileImage(props.work.userId) || fallbackAvatar;
  }
  return fallbackAvatar;
});

const createdAtText = computed(() => {
  if (!props.work.createdAt) {
    return "-";
  }
  return new Date(props.work.createdAt).toLocaleString("zh-CN");
});

function openWorkDetail() {
  router.push({
    path: `/baking/work/${props.work.id}`,
  });
}

function handleVote(type: "flower" | "egg") {
  emit("vote", props.work.id, type);
}
</script>

<style scoped>
.work-card-clickable {
  cursor: pointer;
}
</style>
