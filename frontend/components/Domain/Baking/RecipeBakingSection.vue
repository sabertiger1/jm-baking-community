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

    <!-- 评分和评论 -->
    <v-card class="mb-4">
      <v-card-title>{{ $t("baking.ratings-and-comments") }}</v-card-title>
      <v-card-text>
        <!-- 评分统计 -->
        <div v-if="ratingSummary" class="mb-4">
          <div class="d-flex align-center mb-2">
            <v-rating
              :model-value="ratingSummary.averageRating || 0"
              readonly
              half-increments
              color="primary"
              size="large"
            />
            <span class="ml-2 text-h6">
              {{ ratingSummary.averageRating?.toFixed(1) || $t("baking.no-rating") }}
            </span>
            <span class="ml-2 text-body-2 text-medium-emphasis">
              ({{ $t("baking.ratings-count", { count: ratingSummary.totalRatings }) }})
            </span>
          </div>
        </div>

        <!-- 我的评分 -->
        <div v-if="profileComplete" class="mb-4">
          <v-btn
            v-if="!myRating"
            color="primary"
            prepend-icon="$globals.icons.star"
            @click="showRatingDialog = true"
          >
            {{ $t("baking.rate-now") }}
          </v-btn>
          <div v-else>
            <v-card variant="outlined" color="primary">
              <v-card-text>
                <div class="d-flex align-center justify-space-between">
                  <div>
                    <div class="text-subtitle-2 mb-1">{{ $t("baking.my-rating") }}</div>
                    <v-rating
                      :model-value="myRating.rating"
                      readonly
                      size="small"
                      color="primary"
                    />
                    <div v-if="myRating.comment" class="text-body-2 mt-2">
                      {{ myRating.comment }}
                    </div>
                  </div>
                  <v-btn
                    color="primary"
                    variant="text"
                    prepend-icon="$globals.icons.edit"
                    @click="editMyRating"
                  >
                    {{ $t("baking.edit") }}
                  </v-btn>
                </div>
              </v-card-text>
            </v-card>
          </div>
        </div>

        <!-- 评论列表 -->
        <div v-if="ratings.length > 0">
          <v-list>
            <v-list-item
              v-for="rating in ratings"
              :key="rating.id"
              class="mb-2"
            >
              <template #prepend>
                <v-avatar size="40">
                  <img v-if="rating.avatarUrl" :src="rating.avatarUrl" />
                  <v-icon v-else>$globals.icons.account</v-icon>
                </v-avatar>
              </template>
              <v-list-item-title>
                {{ rating.userFullName || rating.userName }}
              </v-list-item-title>
              <v-list-item-subtitle>
                <div class="d-flex align-center">
                  <v-rating
                    :model-value="rating.rating"
                    readonly
                    size="small"
                    color="primary"
                  />
                  <span class="ml-2">{{ formatDate(rating.createdAt) }}</span>
                  <span v-if="rating.className" class="ml-2 text-caption">
                    {{ rating.grade }} {{ rating.className }}
                  </span>
                </div>
              </v-list-item-subtitle>
              <v-list-item-text v-if="rating.comment">
                {{ rating.comment }}
              </v-list-item-text>
            </v-list-item>
          </v-list>
        </div>
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
          <v-icon start>$globals.icons.check</v-icon>
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
            cols="12"
            sm="6"
            md="4"
            lg="3"
          >
            <BakingWorkCard :work="work" />
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

    <!-- 评分对话框 -->
    <v-dialog v-model="showRatingDialog" max-width="600">
      <v-card>
        <v-card-title>{{ $t("baking.ratings-and-comments") }}</v-card-title>
        <v-card-text>
          <v-form @submit.prevent="submitRating">
            <v-rating
              v-model="ratingForm.rating"
              color="primary"
              size="large"
              class="mb-4"
            />
            <v-textarea
              v-model="ratingForm.comment"
              :label="$t('baking.comment-optional')"
              rows="4"
            />
            <v-card-actions>
              <v-spacer />
              <v-btn @click="showRatingDialog = false">{{ $t("baking.cancel") }}</v-btn>
              <v-btn type="submit" color="primary" :loading="submitting">
                {{ $t("baking.submit") }}
              </v-btn>
            </v-card-actions>
          </v-form>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api/api-client";
import { useMealieAuth } from "~/composables/use-mealie-auth";
import type { Recipe } from "~/lib/api/types/recipe";
import type { RecipeRating, RecipeRatingSummary } from "~/lib/api/user/baking";
import BakingWorkCard from "./BakingWorkCard.vue";
import BakingWorkSubmitDialog from "./BakingWorkSubmitDialog.vue";

const props = defineProps<{
  recipe: Recipe;
}>();

const api = useUserApi();
const auth = useMealieAuth();
const { t: $t } = useI18n();

const ratings = ref<RecipeRating[]>([]);
const myRating = ref<RecipeRating | null>(null);
const ratingSummary = ref<RecipeRatingSummary | null>(null);
const recentWorks = ref<any[]>([]);
const myWork = ref<any>(null); // 我的作品
const profileComplete = ref(true);

// 检查资料完整性
async function checkProfileComplete() {
  try {
    const check = await api.users.getUserDetailsCheck();
    profileComplete.value = check.is_complete;
  } catch (error) {
    console.error($t("baking.profile-incomplete-message"), error);
    profileComplete.value = false;
  }
}

const showRatingDialog = ref(false);
const showSubmitDialog = ref(false);
const submitting = ref(false);
const ratingForm = reactive({
  rating: 5,
  comment: "",
});

async function loadRatings() {
  try {
    ratings.value = await api.baking.getRecipeRatings(props.recipe.id);
    myRating.value = await api.baking.getMyRating(props.recipe.id);
    ratingSummary.value = await api.baking.getRatingSummary(props.recipe.id);
  } catch (error) {
    console.error($t("baking.loading-ratings-failed"), error);
  }
}

async function loadRecentWorks() {
  try {
    const result = await api.baking.getBakingRecords({
      recipeId: props.recipe.id,
      perPage: 4,
    });
    recentWorks.value = result.items;
    
    // 检查当前用户是否已提交作品
    if (auth.user.value) {
      const myWorkRecord = result.items.find(
        (work: any) => work.userId === auth.user.value?.id
      );
      myWork.value = myWorkRecord || null;
    }
  } catch (error) {
    console.error("加载作品失败:", error);
  }
}

async function submitRating() {
  submitting.value = true;
  try {
    if (myRating.value) {
      // 更新现有评分
      await api.baking.updateRating(props.recipe.id, myRating.value.id, {
        rating: ratingForm.rating,
        comment: ratingForm.comment || undefined,
      });
    } else {
      // 创建新评分
      await api.baking.createRating(props.recipe.id, {
        recipeId: props.recipe.id,
        rating: ratingForm.rating,
        comment: ratingForm.comment || undefined,
      });
    }
    showRatingDialog.value = false;
    ratingForm.rating = 5;
    ratingForm.comment = "";
    await loadRatings();
  } catch (error) {
    console.error($t("baking.rating-submit-failed"), error);
  } finally {
    submitting.value = false;
  }
}

function editMyRating() {
  if (myRating.value) {
    ratingForm.rating = myRating.value.rating;
    ratingForm.comment = myRating.value.comment || "";
    showRatingDialog.value = true;
  }
}

function formatDate(date: string): string {
  return new Date(date).toLocaleDateString("zh-CN");
}

onMounted(() => {
  checkProfileComplete();
  loadRatings();
  loadRecentWorks();
});
</script>
