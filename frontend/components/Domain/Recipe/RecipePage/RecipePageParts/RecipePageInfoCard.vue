<template>
  <div>
    <div class="d-flex justify-end flex-wrap align-stretch">
      <RecipePageInfoCardImage
        v-if="landscape"
        :recipe="recipe"
      />
      <v-card
        :width="landscape ? '100%' : '50%'"
        flat
        class="d-flex flex-column justify-center align-center"
      >
        <v-card-text class="w-100">
          <div class="d-flex flex-column align-center">
            <v-card-title class="text-h5 font-weight-regular pa-0 text-wrap text-center opacity-80">
              {{ recipe.name }}
            </v-card-title>
            <div class="d-flex align-center mt-2" style="gap: 8px;">
              <span class="text-caption text-medium-emphasis">平均评分</span>
              <v-rating
                :model-value="recipe.rating || 0"
                readonly
                half-increments
                size="small"
                color="primary"
              />
              <span class="text-caption text-medium-emphasis">
                {{ typeof recipe.rating === "number" && recipe.rating > 0 ? recipe.rating.toFixed(1) : "暂无评分" }}
              </span>
            </div>
          </div>
          <v-divider class="my-2" />
          <SafeMarkdown :source="recipe.description" class="my-3" />
          <v-divider v-if="recipe.description" />
          <v-container class="d-flex flex-row flex-wrap justify-center">
            <div class="mx-6">
              <v-row no-gutters>
                <v-col
                  v-if="recipe.recipeYieldQuantity || recipe.recipeYield"
                  cols="12"
                  class="d-flex flex-wrap justify-center"
                >
                  <RecipeYield
                    :yield-quantity="recipe.recipeYieldQuantity"
                    :yield-text="recipe.recipeYield"
                    :scale="recipeScale"
                    class="mb-4"
                  />
                </v-col>
              </v-row>
              <v-row no-gutters>
                <v-col
                  cols="12"
                  class="d-flex flex-wrap justify-center"
                >
                  <RecipeLastMade
                    v-if="isOwnGroup"
                    :recipe="recipe"
                    class="mb-4"
                  />
                </v-col>
              </v-row>
            </div>
            <div v-if="recipe.prepTime || recipe.totalTime || recipe.performTime" class="mx-6">
              <RecipeTimeCard
                container-class="d-flex flex-wrap justify-center"
                :prep-time="recipe.prepTime"
                :total-time="recipe.totalTime"
                :perform-time="recipe.performTime"
                class="mb-4"
              />
            </div>
          </v-container>
        </v-card-text>
      </v-card>
      <RecipePageInfoCardImage
        v-if="!landscape"
        :recipe="recipe"
        max-width="50%"
        class="my-auto"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useLoggedInState } from "~/composables/use-logged-in-state";
import RecipeLastMade from "~/components/Domain/Recipe/RecipeLastMade.vue";
import RecipeTimeCard from "~/components/Domain/Recipe/RecipeTimeCard.vue";
import RecipeYield from "~/components/Domain/Recipe/RecipeYield.vue";
import RecipePageInfoCardImage from "~/components/Domain/Recipe/RecipePage/RecipePageParts/RecipePageInfoCardImage.vue";
import type { Recipe } from "~/lib/api/types/recipe";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";

interface Props {
  recipe: NoUndefinedField<Recipe>;
  recipeScale?: number;
  landscape: boolean;
}

withDefaults(defineProps<Props>(), {
  recipeScale: 1,
});

const { isOwnGroup } = useLoggedInState();
</script>
