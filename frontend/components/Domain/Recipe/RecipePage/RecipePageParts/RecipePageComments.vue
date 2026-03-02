<template>
  <div>
    <v-card-title class="headline pb-3">
      <v-icon class="mr-2">
        {{ $globals.icons.commentTextMultipleOutline }}
      </v-icon>
      {{ $t("recipe.comments") }}
    </v-card-title>
    <v-divider class="mx-2" />
    <div
      v-if="user.id"
      class="d-flex flex-column"
    >
      <div
        class="d-flex mt-3"
        style="gap: 10px"
      >
        <UserAvatar
          :tooltip="false"
          size="40"
          :user-id="user.id"
        />

        <v-textarea
          v-model="comment"
          hide-details
          density="compact"
          single-line
          variant="outlined"
          auto-grow
          rows="2"
          :placeholder="$t('recipe.join-the-conversation')"
          :disabled="hasCommented || !hasSubmittedWork"
        />
      </div>
      <div class="d-flex flex-wrap mt-2 ml-auto" style="gap: 6px;">
        <v-btn
          v-for="emoji in EMOJI_PRESETS"
          :key="emoji"
          size="x-small"
          variant="text"
          :disabled="hasCommented || !hasSubmittedWork"
          @click="appendEmoji(emoji)"
        >
          {{ emoji }}
        </v-btn>
      </div>
      <div v-if="!hasSubmittedWork" class="text-caption text-warning mt-2 ml-auto">
        请先在“我做了这道菜”中提交该配方作品，才可评分和评论。
      </div>
      <div v-if="hasCommented" class="text-caption text-warning mt-2 ml-auto">
        你已对该配方完成评价，每个用户仅可评论和评分一次。
      </div>
      <div
        v-if="isOwnGroup"
        class="d-flex flex-column align-end mt-2 ml-auto"
        style="gap: 8px"
      >
        <div class="d-flex align-center" style="gap: 8px;">
          <span class="text-caption text-medium-emphasis">我的评分</span>
          <v-rating
            v-model="selectedRating"
            :length="5"
            density="compact"
            size="small"
            hover
            clearable
            color="secondary"
            active-color="secondary"
            :readonly="!hasSubmittedWork || hasCommented"
          />
        </div>
      </div>
      <div class="ml-auto mt-1">
        <BaseButton
          size="small"
          :disabled="!canSubmit"
          @click="submitComment"
        >
          <template #icon>
            {{ $globals.icons.check }}
          </template>
          {{ $t("general.submit") }}
        </BaseButton>
      </div>
    </div>
    <div
      v-for="recipeComment in recipe.comments"
      :key="recipeComment.id"
      class="d-flex my-2"
      style="gap: 10px"
    >
      <UserAvatar
        :tooltip="false"
        size="40"
        :user-id="recipeComment.userId"
      />
      <v-card
        variant="outlined"
        class="flex-grow-1"
      >
        <v-card-text class="pa-3 pb-0">
          <div class="d-flex align-center flex-wrap" style="gap: 8px;">
            <span>{{ recipeComment.user.fullName }} • {{ $d(Date.parse(recipeComment.createdAt), "medium") }}</span>
            <v-rating
              :model-value="commentUserRating(recipeComment.userId)"
              readonly
              half-increments
              density="compact"
              size="x-small"
              color="secondary"
              active-color="secondary"
            />
          </div>
          <SafeMarkdown :source="recipeComment.text" />
        </v-card-text>
        <v-card-actions class="justify-end mt-0 pt-0">
          <v-btn
            v-if="user.admin"
            color="error"
            variant="text"
            size="x-small"
            @click="deleteComment(recipeComment.id)"
          >
            {{ $t("general.delete") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { useUserApi } from "~/composables/api";
import type { Recipe } from "~/lib/api/types/recipe";
import UserAvatar from "~/components/Domain/User/UserAvatar.vue";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import { usePageUser } from "~/composables/recipe-page/shared-state";
import { useUserSelfRatings } from "~/composables/use-users";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { alert } from "~/composables/use-toast";
import SafeMarkdown from "~/components/global/SafeMarkdown.vue";
import type { UserRatingOut } from "~/lib/api/types/user";

const recipe = defineModel<NoUndefinedField<Recipe>>({ required: true });
const api = useUserApi();
const { user } = usePageUser();
const { isOwnGroup } = useLoggedInState();
const { userRatings, setRating } = useUserSelfRatings();
const comment = ref("");
const selectedRating = ref<number | null>(null);
const recipeUserRatings = ref<UserRatingOut[]>([]);

const EMOJI_PRESETS = ["😀", "😋", "😍", "👍", "👏", "🎉", "🌸", "🥚", "🍞", "🍰"] as const;

const currentUserRating = computed<number | null>(() => {
  if (!recipe.value?.id) {
    return null;
  }
  return userRatings.value.find(r => r.recipeId === recipe.value.id)?.rating ?? null;
});

const hasCommented = computed<boolean>(() => {
  const currentUserId = user.value?.id;
  if (!currentUserId) {
    return false;
  }
  return recipe.value.comments.some(c => c.userId === currentUserId);
});

const hasRated = computed<boolean>(() => {
  return typeof currentUserRating.value === "number" && currentUserRating.value > 0;
});

const hasSubmittedWork = ref(false);

const canSubmit = computed<boolean>(() => {
  const score = selectedRating.value;
  return hasSubmittedWork.value
    && !!comment.value.trim()
    && comment.value.trim().length >= 5
    && typeof score === "number"
    && score > 0
    && !hasCommented.value;
});

watch(
  () => currentUserRating.value,
  (val) => {
    selectedRating.value = val;
  },
  { immediate: true },
);

async function loadRecipeRatings() {
  const recipeIdentifier = recipe.value.slug || recipe.value.id;
  if (!recipeIdentifier) {
    recipeUserRatings.value = [];
    return;
  }
  try {
    const { data } = await api.users.getRecipeRatings(recipeIdentifier);
    recipeUserRatings.value = data?.ratings || [];
  } catch (error) {
    console.error("加载评论评分失败:", error);
    recipeUserRatings.value = [];
  }
}

function commentUserRating(userId: string) {
  return recipeUserRatings.value.find(item => item.userId === userId)?.rating ?? 0;
}

function appendEmoji(emoji: string) {
  if (hasCommented.value) {
    return;
  }
  comment.value = `${comment.value}${emoji}`;
}

async function submitComment() {
  if (!hasSubmittedWork.value) {
    alert.warning("请先在“我做了这道菜”中提交该配方作品，再进行评分和评论");
    return;
  }
  if (hasCommented.value) {
    alert.warning("你已对该配方完成评价，每个用户仅可评论和评分一次");
    return;
  }

  const score = selectedRating.value;
  if (!(typeof score === "number" && score > 0)) {
    alert.warning("请先选择星级评分后再提交评论");
    return;
  }
  if (comment.value.trim().length < 5) {
    alert.warning("评论不能少于5字");
    return;
  }

  if (isOwnGroup.value && recipe.value.slug && !hasRated.value) {
    await setRating(recipe.value.slug, score, null);
  }

  const { data } = await api.recipes.comments.createOne({
    recipeId: recipe.value.id,
    text: comment.value.trim(),
  });

  if (data) {
    recipe.value.comments.push(data);
  }

  comment.value = "";
  await loadRecipeRatings();
}

async function loadWorkPermission() {
  if (!recipe.value?.id || !user.value?.id) {
    hasSubmittedWork.value = false;
    return;
  }
  try {
    const result = await api.baking.getBakingRecords({
      recipeId: recipe.value.id,
      userId: user.value.id,
      perPage: 1,
    });
    hasSubmittedWork.value = (result.items?.length || 0) > 0;
  } catch (error) {
    console.error("加载作品提交状态失败:", error);
    hasSubmittedWork.value = false;
  }
}

async function deleteComment(id: string) {
  const { response } = await api.recipes.comments.deleteOne(id);

  if (response?.status === 200) {
    recipe.value.comments = recipe.value.comments.filter(comment => comment.id !== id);
  }
}

watch(
  () => recipe.value.id,
  () => {
    loadRecipeRatings();
    loadWorkPermission();
  },
  { immediate: true },
);

onMounted(() => {
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
  if (customEvent.detail?.recipeId !== recipe.value.id) {
    return;
  }
  loadWorkPermission();
}
</script>
