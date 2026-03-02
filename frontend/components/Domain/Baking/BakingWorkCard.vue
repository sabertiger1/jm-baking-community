<template>
  <v-card class="work-card-clickable" :class="levelCardClass" @click="openWorkDetail">
    <div v-if="workIsExcellent" class="excellent-corner-badge">
      ⭐ 精华作品
    </div>
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
          <div class="text-caption level-badge" :class="levelCardClass">
            {{ work.levelEmoji || "🧈" }} {{ work.levelName || "烘焙小白" }}
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

        <div v-if="props.showVoteActions" :class="isMobile ? 'vote-actions-mobile' : 'd-flex gap-1'">
          <v-btn
            class="vote-btn"
            :disabled="work.hasFlowered"
            :color="work.hasFlowered ? 'pink' : 'default'"
            size="small"
            variant="text"
            @click.stop="handleVote('flower')"
          >
            送花 🌸
          </v-btn>
          <v-btn
            class="vote-btn"
            :disabled="work.hasEgged"
            :color="work.hasEgged ? 'orange' : 'default'"
            size="small"
            variant="text"
            @click.stop="handleVote('egg')"
          >
            送鸡蛋 🥚
          </v-btn>
        </div>
        <div v-if="props.showExcellentAction && !workIsExcellent" class="ml-auto">
          <v-btn
            size="x-small"
            color="warning"
            variant="tonal"
            :loading="props.excellentLoading"
            :disabled="props.excellentLoading"
            @click.stop="handleMarkExcellent"
          >
            设为精华
          </v-btn>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api/api-client";
import type { BakingRecord } from "~/lib/api/user/baking";

const props = withDefaults(defineProps<{
  work: BakingRecord;
  showVoteActions?: boolean;
  showExcellentAction?: boolean;
  excellentLoading?: boolean;
}>(), {
  showVoteActions: true,
  showExcellentAction: false,
  excellentLoading: false,
});

const emit = defineEmits<{
  vote: [workId: string, voteType: "flower" | "egg"];
  "cancel-vote": [workId: string, voteType: string];
  "mark-excellent": [workId: string];
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
  const legacyRelativeMatch = trimmed.match(/^\/api\/users\/([^/]+)\/image(?:\?.*)?$/);
  if (legacyRelativeMatch?.[1]) {
    return api.users.userProfileImage(legacyRelativeMatch[1]) || null;
  }
  const legacyAbsoluteMatch = trimmed.match(/^https?:\/\/[^/]+\/api\/users\/([^/]+)\/image(?:\?.*)?$/);
  if (legacyAbsoluteMatch?.[1]) {
    return api.users.userProfileImage(legacyAbsoluteMatch[1]) || null;
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
  return new Date(props.work.createdAt).toLocaleDateString("zh-CN");
});

const levelCardClass = computed(() => props.work.levelKey || "level-1");
const workIsExcellent = computed(() => {
  const raw = props.work as unknown as Record<string, unknown>;
  return Boolean(
    props.work.isExcellent
    ?? raw.is_excellent
    ?? raw.isExcellent,
  );
});

function openWorkDetail() {
  router.push({
    path: `/baking/work/${props.work.id}`,
  });
}

function handleVote(type: "flower" | "egg") {
  emit("vote", props.work.id, type);
}

function handleMarkExcellent() {
  emit("mark-excellent", props.work.id);
}
</script>

<style scoped>
.work-card-clickable {
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.level-badge {
  width: fit-content;
  margin-top: 2px;
  padding: 1px 8px;
  border-radius: 12px;
  border: 1px solid currentColor;
}

.work-card-clickable.level-1 {
  border: 1px solid #e8e8e8;
  background: #ffffff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.work-card-clickable.level-2 {
  border: 1px solid #e9d9a1;
  background: linear-gradient(180deg, #fffef6, #fffdf2);
  box-shadow: 0 2px 8px rgba(201, 156, 53, 0.10);
}

.work-card-clickable.level-3 {
  border: 2px solid #efc16a;
  background: linear-gradient(180deg, #fffaf0, #fff6e8);
  box-shadow: 0 4px 12px rgba(192, 109, 0, 0.16);
}

.work-card-clickable.level-4 {
  border: 2px solid #efb0cf;
  background: linear-gradient(180deg, #fff7fc, #fff1f8);
  box-shadow: 0 5px 14px rgba(216, 91, 155, 0.18);
}

.work-card-clickable.level-5 {
  border: 2px solid #7d5837;
  background: linear-gradient(180deg, #fff8f2, #f7ede4);
  box-shadow: 0 6px 16px rgba(110, 74, 47, 0.24);
}

.work-card-clickable.level-6 {
  border: 2px solid #6b3f27;
  background: linear-gradient(135deg, #fff5eb, #f2e0d2);
  box-shadow: 0 8px 18px rgba(74, 42, 26, 0.30);
}

.work-card-clickable.level-7 {
  border: 2px solid #b13a8f;
  background: linear-gradient(135deg, #fff4fc, #f9e8f8 45%, #f4e6ff);
  box-shadow: 0 0 0 1px rgba(177, 58, 143, 0.2), 0 10px 22px rgba(177, 58, 143, 0.30);
}

.work-card-clickable.level-8 {
  border: 2px solid #f2c94c;
  background: linear-gradient(100deg, #fff8df, #ffffff 45%, #fff4cc);
  background-size: 220% 100%;
  box-shadow: 0 0 0 1px rgba(242, 201, 76, 0.35), 0 12px 24px rgba(242, 201, 76, 0.36);
  animation: king-shine 1.9s linear infinite, king-float 2.8s ease-in-out infinite;
}

.level-badge.level-1 { color: #8f8f8f; }
.level-badge.level-2 { color: #b8860b; background: #fff8dd; }
.level-badge.level-3 { color: #c06d00; background: #ffeecf; }
.level-badge.level-4 { color: #d85b9b; background: #ffe6f3; }
.level-badge.level-5 { color: #6e4a2f; background: #f5e6da; }
.level-badge.level-6 { color: #4a2a1a; background: #efd7c5; }
.level-badge.level-7 { color: #b13a8f; background: #fbe6fb; }
.level-badge.level-8 { color: #9a6a00; background: #fff1ba; }

@keyframes king-shine {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

@keyframes king-float {
  0% {
    transform: translateY(0);
    box-shadow: 0 0 0 1px rgba(242, 201, 76, 0.35), 0 12px 24px rgba(242, 201, 76, 0.36);
  }
  50% {
    transform: translateY(-3px);
    box-shadow: 0 0 0 1px rgba(242, 201, 76, 0.45), 0 16px 28px rgba(242, 201, 76, 0.46);
  }
  100% {
    transform: translateY(0);
    box-shadow: 0 0 0 1px rgba(242, 201, 76, 0.35), 0 12px 24px rgba(242, 201, 76, 0.36);
  }
}

.vote-actions-mobile {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 6px;
  width: 100%;
}

.vote-btn {
  min-width: 0;
}

.excellent-corner-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 2px 8px;
  border-radius: 999px;
  background: linear-gradient(135deg, #ffcf5c, #f5a623);
  color: #4c3000;
  text-align: center;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.4px;
  z-index: 2;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.22);
  border: 1px solid rgba(255, 255, 255, 0.6);
}
</style>
