<template>
  <v-container>
    <BasePageTitle :title="$t('baking.my-profile')" />
    
    <!-- 用户信息卡片 -->
    <v-card class="mb-4">
      <v-card-text>
        <v-row align="center">
          <v-col cols="auto">
            <v-avatar size="96">
              <img v-if="userDetails?.avatarUrl" :src="userDetails.avatarUrl" />
              <v-icon v-else size="48">$globals.icons.account</v-icon>
            </v-avatar>
          </v-col>
          <v-col>
            <h2 class="text-h5">{{ userDetails?.realName || user?.fullName }}</h2>
            <p class="text-body-2 text-medium-emphasis">
              {{ userDetails?.grade }} {{ userDetails?.className }}
            </p>
          </v-col>
          <v-col cols="auto">
            <v-chip color="primary" size="large">
              <v-icon start>$globals.icons.star</v-icon>
              {{ points?.totalPoints || 0 }} 积分
            </v-chip>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- 统计信息 -->
    <v-row>
      <v-col cols="12" md="4">
        <v-card>
          <v-card-text>
            <div class="text-h6">{{ myWorksCount }}</div>
            <div class="text-body-2 text-medium-emphasis">我的作品</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card>
          <v-card-text>
            <div class="text-h6">{{ points?.consecutiveDays || 0 }}</div>
            <div class="text-body-2 text-medium-emphasis">连续签到天数</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card>
          <v-card-text>
            <div class="text-h6">{{ receivedFlowers }}</div>
            <div class="text-body-2 text-medium-emphasis">收到鲜花</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card>
          <v-card-text>
            <div class="text-h6">{{ receivedEggs }}</div>
            <div class="text-body-2 text-medium-emphasis">收到鸡蛋</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 我的作品 -->
    <v-card class="mt-4">
      <v-card-title>我的作品</v-card-title>
      <v-card-text>
        <v-row v-if="myWorks.length > 0">
          <v-col
            v-for="work in myWorks"
            :key="work.id"
            cols="12"
            sm="6"
            md="4"
            lg="3"
          >
            <BakingWorkCard :work="work" />
          </v-col>
        </v-row>
        <div v-else class="text-center py-8 text-medium-emphasis">
          暂无作品
        </div>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api/api-client";
import { useMealieAuth } from "~/composables/use-mealie-auth";
import type { BakingRecord } from "~/lib/api/user/baking";
import BakingWorkCard from "~/components/Domain/Baking/BakingWorkCard.vue";

definePageMeta({
  layout: "default",
});

const api = useUserApi();
const auth = useMealieAuth();
const user = computed(() => auth.user.value);

const userDetails = ref<any>(null);
const points = ref<any>(null);
const myWorks = ref<BakingRecord[]>([]);
const myWorksCount = computed(() => myWorks.value.length);
const receivedFlowers = ref(0);
const receivedEggs = ref(0);

async function loadProfile() {
  try {
    // 加载用户详细资料
    const details = await api.users.getUserDetails();
    if (details) {
      userDetails.value = {
        realName: details.real_name,
        grade: details.grade,
        className: details.class_name,
        avatarUrl: details.avatar_url,
      };
    } else {
      // 如果没有详细资料，使用基本信息
      const self = await api.users.getSelf();
      userDetails.value = {
        realName: self.fullName,
        grade: null,
        className: null,
        avatarUrl: null,
      };
    }

    // 加载积分信息
    points.value = await api.baking.getMyPoints();

    // 加载我的作品
    if (user.value?.id) {
      const works = await api.baking.getBakingRecords();
      // 过滤出当前用户的作品
      myWorks.value = works.items.filter(work => work.userId === user.value?.id);

      // 计算收到的鲜花和鸡蛋总数
      receivedFlowers.value = myWorks.value.reduce((sum, work) => sum + work.flowerCount, 0);
      receivedEggs.value = myWorks.value.reduce((sum, work) => sum + work.eggCount, 0);
    }
  } catch (error) {
    console.error("加载个人资料失败:", error);
  }
}

onMounted(() => {
  loadProfile();
});
</script>
