<template>
  <div>
    <v-text-field
      v-model="recipe.name"
      class="my-3"
      :label="$t('recipe.recipe-name')"
      :rules="[validators.required]"
      density="compact"
      variant="underlined"
    />
    <v-container class="ma-0 pa-0">
      <v-row>
        <v-col cols="3">
          <v-number-input
            :model-value="recipe.recipeServings"
            :min="0"
            :precision="null"
            density="compact"
            :label="$t('recipe.servings')"
            variant="underlined"
            control-variant="hidden"
            @update:model-value="recipe.recipeServings = $event"
          />
        </v-col>
        <v-col cols="3">
          <v-number-input
            :model-value="recipe.recipeYieldQuantity"
            :min="0"
            :precision="null"
            density="compact"
            :label="$t('recipe.yield')"
            variant="underlined"
            control-variant="hidden"
            @update:model-value="recipe.recipeYieldQuantity = $event"
          />
        </v-col>
        <v-col cols="6">
          <v-text-field
            v-model="recipe.recipeYield"
            density="compact"
            :label="$t('recipe.yield-text')"
            variant="underlined"
          />
        </v-col>
      </v-row>
    </v-container>

    <div
      class="d-flex flex-wrap"
      style="gap: 1rem"
    >
      <v-text-field
        v-model="recipe.totalTime"
        :label="$t('recipe.total-time')"
        density="compact"
        variant="underlined"
      />
      <v-text-field
        v-model="recipe.prepTime"
        :label="$t('recipe.prep-time')"
        density="compact"
        variant="underlined"
      />
      <v-text-field
        v-model="recipe.performTime"
        :label="$t('recipe.perform-time')"
        density="compact"
        variant="underlined"
      />
    </div>
    <v-textarea
      v-model="recipe.description"
      auto-grow
      min-height="100"
      :label="$t('recipe.description')"
      density="compact"
      variant="underlined"
    />

    <!-- 视频上传字段 -->
    <v-divider class="my-4" />
    <div class="text-subtitle-2 mb-2">制作视频</div>
    <div class="d-flex flex-wrap align-center" style="gap: 0.75rem;">
      <AppButtonUpload
        :post="false"
        url="none"
        file-name="video"
        accept="video/mp4,video/webm,video/ogg,video/quicktime"
        :text="makingVideoUploading ? '上传中...' : '上传制作过程视频'"
        :text-btn="false"
        :disabled="makingVideoUploading"
        @uploaded="onMakingVideoSelected"
      />
      <v-btn
        v-if="recipe.makingVideoUrl"
        variant="text"
        color="error"
        :disabled="makingVideoUploading"
        @click="recipe.makingVideoUrl = null"
      >
        清除制作过程视频
      </v-btn>
    </div>
    <video
      v-if="recipe.makingVideoUrl"
      :src="recipe.makingVideoUrl"
      controls
      style="width: 100%; max-height: 280px; margin-top: 0.75rem;"
      preload="metadata"
    />
    <div class="text-caption text-medium-emphasis mt-2">
      支持 mp4/webm/ogg/mov，上传后会保存到数据库。
    </div>

    <div class="d-flex flex-wrap align-center mt-4" style="gap: 0.75rem;">
      <AppButtonUpload
        :post="false"
        url="none"
        file-name="video"
        accept="video/mp4,video/webm,video/ogg,video/quicktime"
        :text="keyPointsVideoUploading ? '上传中...' : '上传制作要点视频'"
        :text-btn="false"
        :disabled="keyPointsVideoUploading"
        @uploaded="onKeyPointsVideoSelected"
      />
      <v-btn
        v-if="recipe.keyPointsVideoUrl"
        variant="text"
        color="error"
        :disabled="keyPointsVideoUploading"
        @click="recipe.keyPointsVideoUrl = null"
      >
        清除制作要点视频
      </v-btn>
    </div>
    <video
      v-if="recipe.keyPointsVideoUrl"
      :src="recipe.keyPointsVideoUrl"
      controls
      style="width: 100%; max-height: 280px; margin-top: 0.75rem;"
      preload="metadata"
    />
  </div>
</template>

<script setup lang="ts">
import { validators } from "~/composables/use-validators";
import { useUserApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import type { Recipe } from "~/lib/api/types/recipe";

const recipe = defineModel<NoUndefinedField<Recipe>>({ required: true });
const api = useUserApi();

const makingVideoUploading = ref(false);
const keyPointsVideoUploading = ref(false);

const ALLOWED_VIDEO_TYPES = new Set(["video/mp4", "video/webm", "video/ogg", "video/quicktime"]);
const MAX_VIDEO_SIZE_BYTES = 50 * 1024 * 1024;

function validateVideoFile(file?: File) {
  if (!file) {
    return "未选择视频文件";
  }
  if (!ALLOWED_VIDEO_TYPES.has(file.type)) {
    return "仅支持 mp4/webm/ogg/mov 格式";
  }
  if (file.size > MAX_VIDEO_SIZE_BYTES) {
    return "视频大小不能超过 50MB";
  }
  return null;
}

async function uploadRecipeVideo(file: File, videoType: "making" | "key-points") {
  if (!recipe.value.slug) {
    alert.error("请先保存配方，再上传视频");
    return;
  }

  const validateError = validateVideoFile(file);
  if (validateError) {
    alert.error(validateError);
    return;
  }

  const loadingRef = videoType === "making" ? makingVideoUploading : keyPointsVideoUploading;
  loadingRef.value = true;
  try {
    const { data } = await api.recipes.updateVideo(recipe.value.slug, file, videoType);
    if (videoType === "making") {
      recipe.value.makingVideoUrl = data?.videoUrl || null;
    }
    else {
      recipe.value.keyPointsVideoUrl = data?.videoUrl || null;
    }
    alert.success("视频上传成功");
  }
  catch (error) {
    console.error("视频上传失败:", error);
    alert.error("视频上传失败，请重试");
  }
  finally {
    loadingRef.value = false;
  }
}

function onMakingVideoSelected(file: File | null) {
  if (!file) {
    return;
  }
  uploadRecipeVideo(file, "making");
}

function onKeyPointsVideoSelected(file: File | null) {
  if (!file) {
    return;
  }
  uploadRecipeVideo(file, "key-points");
}
</script>
