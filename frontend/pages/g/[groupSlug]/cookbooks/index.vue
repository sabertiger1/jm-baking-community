<template>
  <div>
    <!-- Create Dialog -->
    <BaseDialog
      v-if="createTarget"
      v-model="dialogStates.create"
      width="100%"
      max-width="1100px"
      :icon="$globals.icons.pages"
      :title="$t('cookbook.create-a-cookbook')"
      :submit-icon="$globals.icons.save"
      :submit-text="$t('general.save')"
      :submit-disabled="!createTarget.queryFilterString"
      can-submit
      @submit="actions.updateOne(createTarget)"
      @cancel="deleteCreateTarget()"
    >
      <v-card-text>
        <CookbookEditor :key="createTargetKey" v-model="createTarget" />
      </v-card-text>
    </BaseDialog>

    <!-- Delete Dialog -->
    <BaseDialog
      v-model="dialogStates.delete"
      :title="$t('general.delete-with-name', { name: $t('cookbook.cookbook') })"
      :icon="$globals.icons.alertCircle"
      color="error"
      can-confirm
      @confirm="deleteCookbook()"
    >
      <v-card-text>
        <p>{{ $t("general.confirm-delete-generic-with-name", { name: $t("cookbook.cookbook") }) }}</p>
        <p v-if="deleteTarget" class="mt-4 ml-4">
          {{ deleteTarget.name }}
        </p>
      </v-card-text>
    </BaseDialog>

    <!-- Cookbook Page -->
    <!-- Page Title -->
    <v-container class="lg-container">
      <BasePageTitle divider>
        <template #header>
          <v-img width="100%" max-height="100" max-width="100" src="/svgs/manage-cookbooks.svg" />
        </template>
        <template #title>
          {{ $t("cookbook.cookbooks") }}
        </template>
        {{ $t("cookbook.description") }}
      </BasePageTitle>

      <template v-if="isReadOnly">
        <v-row class="mt-2" v-if="readonlyCookbooks.length > 0">
          <v-col
            v-for="cookbook in readonlyCookbooks"
            :key="cookbook.id"
            cols="12"
            sm="6"
            md="4"
          >
            <v-card
              class="h-100"
              link
              :to="cookbookLink(cookbook)"
              hover
            >
              <v-card-title class="d-flex align-center">
                <v-icon start>{{ $globals.icons.pages }}</v-icon>
                <span class="text-truncate">{{ cookbook.name }}</span>
              </v-card-title>
              <v-card-subtitle>
                {{ cookbook.household?.name || "未命名家庭" }}
              </v-card-subtitle>
              <v-card-text class="text-body-2 text-medium-emphasis">
                {{ cookbook.description || "点击查看该合集内的配方" }}
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        <v-empty-state
          v-else
          class="mt-4"
          :title="$t('cookbook.cookbooks')"
          text="暂无可浏览的食谱合集"
        />
      </template>

      <template v-else>
        <!-- Create New -->
        <BaseButton create @click="createCookbook" />

        <!-- Cookbook List -->
        <v-expansion-panels class="mt-2">
          <VueDraggable
            v-model="myCookbooks"
            handle=".handle"
            :delay="250"
            :delay-on-touch-only="true"
            style="width: 100%"
            @end="updateAll(myCookbooks)"
          >
            <v-expansion-panel
              v-for="(cookbook, index) in myCookbooks"
              :key="cookbook.id"
              class="my-2 left-border rounded"
            >
              <v-expansion-panel-title disable-icon-rotate class="text-h6 opacity-80">
                <div class="d-flex align-center">
                  <v-icon size="large" start>
                    {{ $globals.icons.pages }}
                  </v-icon>
                  {{ cookbook.name }}
                </div>
                <template #actions>
                  <div class="d-flex align-center">
                    <v-btn icon variant="text" class="ml-2">
                      <v-icon>
                        {{ $globals.icons.edit }}
                      </v-icon>
                    </v-btn>
                    <v-icon class="handle" :size="40">
                      {{ $globals.icons.arrowUpDown }}
                    </v-icon>
                  </div>
                </template>
              </v-expansion-panel-title>
              <v-expansion-panel-text>
                <CookbookEditor
                  v-model="myCookbooks[index]"
                  :collapsable="false"
                />
                <v-card-actions>
                  <v-spacer />
                  <BaseButtonGroup
                    :buttons="[
                      {
                        icon: $globals.icons.delete,
                        text: $t('general.delete'),
                        event: 'delete',
                      },
                      {
                        icon: $globals.icons.save,
                        text: $t('general.save'),
                        event: 'save',
                        disabled: !cookbook.queryFilterString,
                      },
                    ]"
                    @delete="deleteEventHandler(myCookbooks[index])"
                    @save="actions.updateOne(myCookbooks[index])"
                  />
                </v-card-actions>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </VueDraggable>
        </v-expansion-panels>
      </template>
    </v-container>
  </div>
</template>

<script lang="ts">
import { VueDraggable } from "vue-draggable-plus";
import { useCookbookStore } from "~/composables/store/use-cookbook-store";
import { useHouseholdSelf } from "@/composables/use-households";
import CookbookEditor from "~/components/Domain/Cookbook/CookbookEditor.vue";
import type { CreateCookBook, ReadCookBook } from "~/lib/api/types/cookbook";

export default defineNuxtComponent({
  components: { CookbookEditor, VueDraggable },
  middleware: ["group-only"],
  setup() {
    const route = useRoute();
    const auth = useMealieAuth();
    const groupSlug = computed(() => (route.params.groupSlug as string) || auth.user.value?.groupSlug || "");
    const isReadOnly = computed(() => {
      const value = route.query.readonly;
      if (Array.isArray(value)) {
        return value.includes("1") || value.includes("true");
      }
      return value === "1" || value === "true";
    });

    const dialogStates = reactive({
      create: false,
      delete: false,
    });

    const i18n = useI18n();

    // Set page title
    useSeoMeta({
      title: i18n.t("cookbook.cookbooks"),
    });

    const { store: allCookbooks, actions, updateAll } = useCookbookStore();
    const readonlyCookbooks = computed(() => {
      return [...(allCookbooks.value || [])].sort((a, b) => {
        const posA = a.position ?? 0;
        const posB = b.position ?? 0;
        if (posA !== posB) {
          return posA - posB;
        }
        return (a.name || "").localeCompare(b.name || "");
      });
    });

    // Make a local reactive copy of myCookbooks
    const myCookbooks = ref<ReadCookBook[]>([]);
    watch(
      allCookbooks,
      (cookbooks) => {
        myCookbooks.value
          = cookbooks?.filter(
            cookbook => cookbook.householdId === auth.user.value?.householdId,
          ).sort((a, b) => (a.position ?? 0) - (b.position ?? 0)) ?? [];
      },
      { immediate: true },
    );

    function cookbookLink(cookbook: ReadCookBook) {
      const cookbookKey = cookbook.slug || cookbook.id || "";
      return `/g/${groupSlug.value}/cookbooks/${cookbookKey}`;
    }

    const { household } = useHouseholdSelf();

    // create
    const createTargetKey = ref(0);
    const createTarget = ref<ReadCookBook | null>(null);
    async function createCookbook() {
      const name = i18n.t("cookbook.household-cookbook-name", [
        household.value?.name || "",
        String((myCookbooks.value?.length ?? 0) + 1),
      ]) as string;

      const data = { name } as CreateCookBook;
      await actions.createOne(data).then((cookbook) => {
        if (!cookbook) {
          return;
        }

        myCookbooks.value.push(cookbook);
        createTarget.value = cookbook as ReadCookBook;
        createTargetKey.value++;
      });
      dialogStates.create = true;
    }

    // delete
    const deleteTarget = ref<ReadCookBook | null>(null);
    function deleteEventHandler(item: ReadCookBook) {
      deleteTarget.value = item;
      dialogStates.delete = true;
    }
    async function deleteCookbook() {
      if (!deleteTarget.value) {
        return;
      }
      await actions.deleteOne(deleteTarget.value.id);
      myCookbooks.value = myCookbooks.value.filter(c => c.id !== deleteTarget.value?.id);
      dialogStates.delete = false;
      deleteTarget.value = null;
    }

    async function deleteCreateTarget() {
      if (!createTarget.value?.id) {
        return;
      }
      await actions.deleteOne(createTarget.value.id);
      myCookbooks.value = myCookbooks.value.filter(c => c.id !== createTarget.value?.id);
      dialogStates.create = false;
      createTarget.value = null;
    }
    function handleUnmount() {
      if (!createTarget.value?.id || createTarget.value.queryFilterString) {
        return;
      }
      deleteCreateTarget();
    }
    onMounted(() => {
      window.addEventListener("beforeunload", handleUnmount);
    });
    onBeforeUnmount(() => {
      handleUnmount();
      window.removeEventListener("beforeunload", handleUnmount);
    });

    return {
      isReadOnly,
      readonlyCookbooks,
      cookbookLink,
      myCookbooks,
      actions,
      dialogStates,
      // create
      createTargetKey,
      createTarget,
      createCookbook,

      // update
      updateAll,

      // delete
      deleteTarget,
      deleteEventHandler,
      deleteCookbook,
      deleteCreateTarget,
    };
  },
});
</script>
