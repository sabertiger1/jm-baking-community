<template>
  <div>
    <div>
      <BaseDialog
        v-model="madeThisDialog"
        :loading="madeThisFormLoading"
        :icon="$globals.icons.chefHat"
        :title="$t('recipe.made-this')"
        :submit-text="$t('recipe.add-to-works')"
        can-submit
        disable-submit-on-enter
        @submit="createTimelineEvent"
      >
        <v-card-text>
          <v-form ref="domMadeThisForm">
            <v-textarea
              v-model="newTimelineEvent.eventMessage"
              autofocus
              :label="$t('recipe.comment')"
              :hint="$t('recipe.how-did-it-turn-out')"
              persistent-hint
              rows="4"
            />
            <div v-if="childRecipes?.length">
              <v-card-text class="pt-6 pb-0">
                {{ $t('recipe.include-linked-recipes') }}
              </v-card-text>
              <v-list>
                <v-list-item
                  v-for="(childRecipe, i) in childRecipes"
                  :key="childRecipe.recipeId + i"
                  density="compact"
                  class="my-0 py-0"
                  @click="childRecipe.checked = !childRecipe.checked"
                >
                  <v-checkbox
                    hide-details
                    density="compact"
                    :input-value="childRecipe.checked"
                    :label="childRecipe.name"
                    class="my-0 py-0"
                    color="secondary"
                  />
                </v-list-item>
              </v-list>
            </div>
            <v-container>
              <v-row>
                <v-col cols="6">
                  <v-menu
                    v-model="datePickerMenu"
                    :disabled="!canSelectMadeDate"
                    :close-on-content-click="false"
                    transition="scale-transition"
                    offset-y
                    max-width="290px"
                  >
                    <template #activator="{ props: activatorProps }">
                      <v-text-field
                        :model-value="$d(newTimelineEventTimestamp)"
                        :prepend-icon="$globals.icons.calendar"
                        v-bind="activatorProps"
                        readonly
                      />
                    </template>
                    <v-date-picker
                      v-model="newTimelineEventTimestamp"
                      :disabled="!canSelectMadeDate"
                      hide-header
                      :first-day-of-week="firstDayOfWeek"
                      :local="$i18n.locale"
                      @update:model-value="datePickerMenu = false"
                    />
                  </v-menu>
                </v-col>
                <v-spacer />
                <v-col cols="auto" align-self="center">
                  <AppButtonUpload
                    v-if="!newTimelineEventImage"
                    class="ml-auto"
                    url="none"
                    file-name="image"
                    accept="image/*"
                    :text="$t('recipe.upload-image')"
                    :text-btn="false"
                    :post="false"
                    @uploaded="uploadImage"
                  />
                  <v-btn v-if="!!newTimelineEventImage" color="error" @click="clearImage">
                    <v-icon start>
                      {{ $globals.icons.close }}
                    </v-icon>
                    {{ $t("recipe.remove-image") }}
                  </v-btn>
                </v-col>
              </v-row>
              <v-row v-if="newTimelineEventImage && newTimelineEventImagePreviewUrl">
                <v-col cols="12" align-self="center">
                  <ImageCropper
                    :img="newTimelineEventImagePreviewUrl"
                    cropper-height="20vh"
                    cropper-width="100%"
                    @save="updateUploadedImage"
                  />
                </v-col>
              </v-row>
            </v-container>
          </v-form>
        </v-card-text>
      </BaseDialog>
    </div>
    <div>
      <div v-if="lastMadeReady && !hasSubmittedWork" class="d-flex justify-center flex-wrap">
        <v-row no-gutters class="d-flex flex-wrap align-center" style="font-size: larger">
          <v-tooltip location="bottom">
            <template #activator="{ props: tooltipProps }">
              <v-btn
                rounded
                variant="outlined"
                size="x-large"
                v-bind="tooltipProps"
                style="border-color: rgb(var(--v-theme-primary));"
                @click="madeThisDialog = true"
              >
                <v-icon start size="large" color="primary">
                  {{ $globals.icons.calendar }}
                </v-icon>
                <span class="text-body-1 opacity-80">
                  <b>{{ $t("general.last-made") }}</b>
                  <br>
                  {{ lastMade ? $d(new Date(lastMade)) : $t("general.never") }}
                </span>
                <v-icon end size="large" color="primary">
                  {{ $globals.icons.createAlt }}
                </v-icon>
              </v-btn>
            </template>
            <span>{{ $t("recipe.made-this") }}</span>
          </v-tooltip>
        </v-row>
      </div>
      <div v-else-if="lastMadeReady && hasSubmittedWork" class="d-flex justify-center flex-wrap">
        <v-chip color="success" variant="tonal" size="large">
          <v-icon start>
            {{ $globals.icons.check }}
          </v-icon>
          已提交作品
        </v-chip>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { whenever } from "@vueuse/core";
import { formatISO } from "date-fns";
import { useUserApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";
import { useHouseholdSelf } from "~/composables/use-households";
import type { Recipe, RecipeTimelineEventIn, RecipeTimelineEventOut } from "~/lib/api/types/recipe";
import type { BakingRecord } from "~/lib/api/user/baking";
import type { VForm } from "~/types/auto-forms";

const props = defineProps<{ recipe: Recipe }>();
const emit = defineEmits<{
  eventCreated: [event: RecipeTimelineEventOut];
}>();

const madeThisDialog = ref(false);
const userApi = useUserApi();
const { household } = useHouseholdSelf();
const i18n = useI18n();
const auth = useMealieAuth();
const domMadeThisForm = ref<VForm>();
const newTimelineEvent = ref<RecipeTimelineEventIn>({
  subject: "",
  eventType: "comment",
  eventMessage: "",
  timestamp: undefined,
  recipeId: props.recipe?.id || "",
});
const newTimelineEventImage = ref<Blob | File>();
const newTimelineEventImageName = ref<string>("");
const newTimelineEventImagePreviewUrl = ref<string>();
const newTimelineEventTimestamp = ref<Date>(new Date());
const newTimelineEventTimestampString = computed(() => {
  return formatISO(newTimelineEventTimestamp.value, { representation: "date" });
});
const canSelectMadeDate = computed(() => !!auth.user.value?.admin);

const lastMade = ref(props.recipe.lastMade);
const lastMadeReady = ref(false);
const hasSubmittedWork = ref(false);

async function loadSubmissionStatus() {
  if (!props.recipe?.id || !auth.user.value?.id) {
    hasSubmittedWork.value = false;
    return;
  }
  try {
    const result = await userApi.baking.getBakingRecords({
      recipeId: props.recipe.id,
      userId: auth.user.value.id,
      perPage: 1,
    });
    hasSubmittedWork.value = (result.items?.length || 0) > 0;
  } catch (error) {
    console.error("Failed to load baking submission status:", error);
    hasSubmittedWork.value = false;
  }
}

function handleWorkSubmitted(event: Event) {
  const customEvent = event as CustomEvent<{ recipeId?: string }>;
  if (customEvent.detail?.recipeId !== props.recipe.id) {
    return;
  }
  hasSubmittedWork.value = true;
}

onMounted(async () => {
  if (!auth.user?.value?.householdSlug) {
    lastMade.value = props.recipe.lastMade;
  }
  else {
    const { data } = await userApi.households.getCurrentUserHouseholdRecipe(props.recipe.slug || "");
    lastMade.value = data?.lastMade;
  }

  await loadSubmissionStatus();
  lastMadeReady.value = true;

  if (process.client) {
    window.addEventListener("baking-work-submitted", handleWorkSubmitted as EventListener);
  }
});

onBeforeUnmount(() => {
  if (process.client) {
    window.removeEventListener("baking-work-submitted", handleWorkSubmitted as EventListener);
  }
});

const childRecipes = computed(() => {
  return props.recipe.recipeIngredient?.map((ingredient) => {
    if (ingredient.referencedRecipe) {
      return {
        checked: false, // Default value for checked
        recipeId: ingredient.referencedRecipe.id || "", // Non-nullable recipeId
        ...ingredient.referencedRecipe, // Spread the rest of the referencedRecipe properties
      };
    }
    else {
      return undefined;
    }
  }).filter(recipe => recipe !== undefined); // Filter out undefined values
});

whenever(
  () => madeThisDialog.value,
  () => {
    // Set timestamp to now
    newTimelineEventTimestamp.value = new Date();
  },
);

const firstDayOfWeek = computed(() => {
  return household.value?.preferences?.firstDayOfWeek || 0;
});

function clearImage() {
  newTimelineEventImage.value = undefined;
  newTimelineEventImageName.value = "";
  newTimelineEventImagePreviewUrl.value = undefined;
}

function uploadImage(fileObject: File) {
  newTimelineEventImage.value = fileObject;
  newTimelineEventImageName.value = fileObject.name;
  newTimelineEventImagePreviewUrl.value = URL.createObjectURL(fileObject);
}

function updateUploadedImage(fileObject: Blob) {
  newTimelineEventImage.value = fileObject;
  newTimelineEventImagePreviewUrl.value = URL.createObjectURL(fileObject);
}

function blobToDataUrl(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve((reader.result as string) || "");
    reader.onerror = () => reject(reader.error || new Error("读取图片失败"));
    reader.readAsDataURL(blob);
  });
}

async function syncToBakingWorks() {
  if (!newTimelineEventImage.value || !props.recipe?.id) {
    return;
  }

  const imageUrl = await blobToDataUrl(newTimelineEventImage.value);
  if (!imageUrl) {
    return;
  }

  const notes = newTimelineEvent.value.eventMessage?.trim() || undefined;

  try {
    await userApi.baking.createBakingRecord({
      recipeId: props.recipe.id,
      imageUrl,
      notes,
    });
    return;
  }
  catch (error: any) {
    const detail = error?.response?.data?.detail;
    const duplicateError = typeof detail === "string"
      && (detail.includes("已经对该配方提交过作品") || detail.includes("只能提交一次"));
    if (!duplicateError) {
      throw error;
    }
  }

  // 已存在作品时，改为更新当前用户该配方下的作品
  const records = await userApi.baking.getBakingRecords({
    recipeId: props.recipe.id,
    ...(auth.user.value?.id ? { userId: auth.user.value.id } : {}),
    perPage: 1,
  });
  const myRecord = records.items[0];
  if (!myRecord) {
    return;
  }

  await userApi.baking.updateBakingRecord(myRecord.id, {
    imageUrl,
    notes,
  });
}

const datePickerMenu = ref(false);
const madeThisFormLoading = ref(false);

function resetMadeThisForm() {
  madeThisFormLoading.value = false;

  newTimelineEvent.value.eventMessage = "";
  newTimelineEvent.value.timestamp = undefined;
  clearImage();
  madeThisDialog.value = false;
  domMadeThisForm.value?.reset();
}

async function createTimelineEvent() {
  const effectiveDate = canSelectMadeDate.value
    ? newTimelineEventTimestampString.value
    : formatISO(new Date(), { representation: "date" });

  if (!(effectiveDate && props.recipe?.id && props.recipe?.slug)) {
    return;
  }
  try {
    const { data: check } = await userApi.users.getUserDetailsCheck();
    if (check && !check.isComplete) {
      const fieldNames: Record<string, string> = {
        real_name: "真实姓名",
        grade: "年级",
        class_name: "班级",
        avatar_url: "头像",
      };
      const missing = (check.missingFields || [])
        .map(field => fieldNames[field] || field)
        .join("、");
      const msg = check.message || `请先完善个人资料后再提交作品${missing ? `（缺少：${missing}）` : ""}`;
      alert.warning(msg);
      return;
    }
  } catch (error) {
    console.error("Failed to check profile completeness:", error);
  }
  if (!newTimelineEventImage.value) {
    alert.warning("请先上传作品图片，再添加到作品集");
    return;
  }

  madeThisFormLoading.value = true;

  newTimelineEvent.value.recipeId = props.recipe.id;
  // Note: auth.user is now a ref
  newTimelineEvent.value.subject = i18n.t("recipe.user-made-this", { user: auth.user.value?.fullName });

  // the user only selects the date, so we set the time to end of day local time
  // we choose the end of day so it always comes after "new recipe" events
  newTimelineEvent.value.timestamp = new Date(effectiveDate + "T23:59:59").toISOString();

  try {
    await syncToBakingWorks();
    if (process.client) {
      window.dispatchEvent(new CustomEvent("baking-work-submitted", {
        detail: { recipeId: props.recipe.id },
      }));
    }
  }
  catch (error) {
    console.error("Failed to sync to baking works:", error);
    const err = error as any;
    const detail = err?.response?.data?.detail;
    if (err?.response?.status === 403) {
      if (typeof detail === "string") {
        alert.warning(detail);
      } else if (detail && typeof detail === "object" && detail.message) {
        alert.warning(detail.message);
      } else {
        alert.warning("请先完善个人资料（真实姓名、年级、班级、头像）后再提交作品");
      }
    } else {
      alert.error("添加到作品集失败，请稍后重试");
    }
    madeThisFormLoading.value = false;
    return;
  }

  let newEvent: RecipeTimelineEventOut | null = null;
  try {
    const eventResponse = await userApi.recipes.createTimelineEvent(newTimelineEvent.value);
    newEvent = eventResponse.data;
    if (!newEvent) {
      throw new Error("No event created");
    }
  }
  catch (error) {
    console.error("Failed to create timeline event:", error);
    alert.warning("已添加到作品集，但写入时间轴失败");
    resetMadeThisForm();
    return;
  }

  // we also update the recipe's last made value
  if (!lastMade.value || newTimelineEvent.value.timestamp > lastMade.value) {
    try {
      lastMade.value = newTimelineEvent.value.timestamp;
      await userApi.recipes.updateLastMade(props.recipe.slug, newTimelineEvent.value.timestamp);
    }
    catch (error) {
      console.error("Failed to update last made date:", error);
      alert.error(i18n.t("recipe.failed-to-update-recipe"));
    }
  }

  for (const childRecipe of childRecipes.value || []) {
    if (!childRecipe.checked) {
      continue;
    }

    const childTimelineEvent = {
      ...newTimelineEvent.value,
      recipeId: childRecipe.recipeId,
      eventMessage: i18n.t("recipe.made-for-recipe", { recipe: childRecipe.name }),
      image: undefined,
    };
    try {
      await userApi.recipes.createTimelineEvent(childTimelineEvent);
    }
    catch (error) {
      console.error(`Failed to create timeline event for child recipe ${childRecipe.slug}:`, error);
    }

    if (
      newTimelineEvent.value.timestamp
      && (!childRecipe.lastMade || newTimelineEvent.value.timestamp > childRecipe.lastMade)
    ) {
      try {
        await userApi.recipes.updateLastMade(childRecipe.slug || "", newTimelineEvent.value.timestamp);
      }
      catch (error) {
        console.error(`Failed to update last made date for child recipe ${childRecipe.slug}:`, error);
      }
    }
  }

  // update the image, if provided
  let imageError = false;
  if (newTimelineEventImage.value) {
    try {
      const imageResponse = await userApi.recipes.updateTimelineEventImage(
        newEvent.id,
        newTimelineEventImage.value,
        newTimelineEventImageName.value,
      );
      if (imageResponse.data) {
        newEvent.image = imageResponse.data.image;
      }
    }
    catch (error) {
      imageError = true;
      console.error("Failed to upload image for timeline event:", error);
    }
  }
  if (imageError) {
    alert.warning(i18n.t("recipe.added-to-works-but-failed-to-add-image"));
  } else {
    alert.success(i18n.t("recipe.added-to-works"));
  }

  resetMadeThisForm();
  emit("eventCreated", newEvent);
}
</script>
