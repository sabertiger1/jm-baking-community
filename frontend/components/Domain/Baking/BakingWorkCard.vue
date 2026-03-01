<template>
  <v-card>
    <v-img
      :src="work.imageUrl"
      :aspect-ratio="1"
      cover
      @click="$router.push(`/baking/works/${work.id}`)"
    >
      <template #placeholder>
        <v-skeleton-loader type="image" />
      </template>
    </v-img>

    <v-card-text>
      <!-- 用户信息 -->
      <div class="d-flex align-center mb-2">
        <v-avatar size="32" class="mr-2">
          <img v-if="work.avatarUrl" :src="work.avatarUrl" />
          <v-icon v-else>$globals.icons.account</v-icon>
        </v-avatar>
        <div>
          <div class="text-body-2 font-weight-medium">{{ work.userFullName || work.userName }}</div>
          <div class="text-caption text-medium-emphasis">
            {{ work.grade }} {{ work.className }}
          </div>
        </div>
      </div>

      <!-- 制作心得 -->
      <p v-if="work.notes" class="text-body-2 text-medium-emphasis mb-2">
        {{ work.notes }}
      </p>

      <!-- 统计和操作 -->
      <div class="d-flex justify-space-between align-center">
        <div class="d-flex gap-2">
          <v-chip size="small" color="pink" variant="tonal">
            <v-icon start size="16">$globals.icons.flower</v-icon>
            {{ work.flowerCount }}
          </v-chip>
          <v-chip size="small" color="orange" variant="tonal">
            <v-icon start size="16">$globals.icons.egg</v-icon>
            {{ work.eggCount }}
          </v-chip>
        </div>

        <div class="d-flex gap-1">
          <v-btn
            :disabled="work.hasFlowered"
            :color="work.hasFlowered ? 'pink' : 'default'"
            size="small"
            variant="text"
            icon
            @click="handleVote('flower')"
          >
            <v-icon>$globals.icons.flower</v-icon>
          </v-btn>
          <v-btn
            :disabled="work.hasEgged"
            :color="work.hasEgged ? 'orange' : 'default'"
            size="small"
            variant="text"
            icon
            @click="handleVote('egg')"
          >
            <v-icon>$globals.icons.egg</v-icon>
          </v-btn>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import type { BakingRecord } from "~/lib/api/user/baking";

const props = defineProps<{
  work: BakingRecord;
}>();

const emit = defineEmits<{
  vote: [workId: string, voteType: "flower" | "egg"];
  "cancel-vote": [workId: string, voteType: string];
}>();

function handleVote(type: "flower" | "egg") {
  emit("vote", props.work.id, type);
}
</script>
