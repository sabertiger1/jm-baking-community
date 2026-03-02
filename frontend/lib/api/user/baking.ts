import { BaseCRUDAPI } from "../base/base-clients";
import { route } from "../base";
import type { ApiRequestInstance, PaginationData } from "~/lib/api/types/non-generated";

const prefix = "/api";

// Types (需要与后端 Schema 对应)
export interface BakingRecord {
  id: string;
  recipeId: string;
  userId: string;
  imageUrl: string;
  notes?: string;
  flowerCount: number;
  eggCount: number;
  isExcellent?: boolean;
  createdAt: string;
  updateAt: string;
  userName?: string;
  userFullName?: string;
  className?: string;
  groupName?: string;
  hasFlowered: boolean;
  hasEgged: boolean;
  avatarUrl?: string;
  grade?: string;
  recipeName?: string;
  totalExp?: number;
  levelKey?: string;
  levelName?: string;
  levelEmoji?: string;
}

export interface BakingRecordCreate {
  recipeId: string;
  imageUrl: string;
  notes?: string;
}

export interface BakingRecordUpdate {
  imageUrl?: string;
  notes?: string;
}

export interface BakingRecordPagination extends PaginationData {
  items: BakingRecord[];
}

export interface RecipeRating {
  id: string;
  recipeId: string;
  userId: string;
  rating: number;
  comment?: string;
  createdAt: string;
  updateAt: string;
  userName?: string;
  userFullName?: string;
  avatarUrl?: string;
  className?: string;
  grade?: string;
}

export interface RecipeRatingCreate {
  rating: number;
  comment?: string;
}

export interface RecipeRatingUpdate {
  rating?: number;
  comment?: string;
}

export interface RecipeRatingSummary {
  recipeId: string;
  averageRating?: number;
  totalRatings: number;
  ratingDistribution: Record<number, number>;
}

export interface UserPoints {
  id: string;
  userId: string;
  totalPoints: number;
  consecutiveDays: number;
  lastCheckinDate?: string;
  createdAt: string;
  updateAt: string;
}

export interface CheckinRequest {
  // 空对象
}

export interface CheckinResponse {
  success: boolean;
  pointsEarned: number;
  totalPoints: number;
  consecutiveDays: number;
  message?: string;
}

export interface CheckinHistoryResponse {
  checkinDates: string[];
  dailyPoints: number;
}

export interface UserExperience {
  userId: string;
  totalExp: number;
  levelKey: string;
  levelName: string;
  levelEmoji: string;
  currentLevelMinExp?: number;
  nextLevelMinExp?: number | null;
  nextLevelName?: string | null;
}

export interface UserExperienceBatch {
  items: UserExperience[];
}

export interface UserExperienceHistoryItem {
  id: string;
  source: string;
  expDelta: number;
  totalExpAfter: number;
  note?: string;
  createdAt: string;
}

export interface UserExperienceHistory {
  page: number;
  perPage: number;
  total: number;
  pages: number;
  items: UserExperienceHistoryItem[];
}

export interface VoteRequest {
  workId: string;
  voteType: "flower" | "egg";
}

export interface VoteResponse {
  success: boolean;
  workId: string;
  voteType: "flower" | "egg";
  flowerCount: number;
  eggCount: number;
  pointsRemaining: number;
  message?: string;
}

export interface ReceivedVoteRecord {
  voteId: string;
  workId: string;
  recipeId: string;
  recipeName?: string;
  voteType: "flower" | "egg";
  voterUserId: string;
  voterName?: string;
  createdAt: string;
}

export interface ReceivedVoteRecords {
  page: number;
  perPage: number;
  total: number;
  pages: number;
  items: ReceivedVoteRecord[];
}

export interface UserClass {
  id: string;
  userId: string;
  className?: string;
  groupName?: string;
  createdAt: string;
  updateAt: string;
}

export interface UserClassCreate {
  userId: string;
  className?: string;
  groupName?: string;
}

export interface UserClassUpdate {
  className?: string;
  groupName?: string;
}

const routes = {
  bakingRecords: `${prefix}/baking/`,
  bakingRecord: (id: string) => `${prefix}/baking/${id}`,
  bakingRecordExcellent: (id: string) => `${prefix}/baking/${id}/excellent`,
  bakingGrades: `${prefix}/baking/grades`,
  bakingClasses: `${prefix}/baking/classes`,
  recipeRatings: (recipeId: string) => `${prefix}/recipes/${recipeId}/ratings`,
  recipeRating: (recipeId: string, ratingId: string) => `${prefix}/recipes/${recipeId}/ratings/${ratingId}`,
  recipeRatingSummary: (recipeId: string) => `${prefix}/recipes/${recipeId}/ratings/summary`,
  myRating: (recipeId: string) => `${prefix}/recipes/${recipeId}/ratings/my`,
  pointsMe: `${prefix}/points/me`,
  pointsCheckin: `${prefix}/points/checkin`,
  pointsLeaderboard: `${prefix}/points/leaderboard`,
  pointsHistory: `${prefix}/points/history`,
  pointsExperienceMe: `${prefix}/points/experience/me`,
  pointsExperienceUsers: `${prefix}/points/experience/users`,
  pointsExperienceUser: (userId: string) => `${prefix}/points/experience/users/${userId}`,
  pointsExperienceHistory: `${prefix}/points/experience/history`,
  votes: `${prefix}/votes/`,
  votesReceived: `${prefix}/votes/received`,
  voteCancel: (workId: string, voteType: string) => `${prefix}/votes/${workId}/${voteType}`,
  classesMe: `${prefix}/classes/me`,
  classesList: `${prefix}/classes/list`,
  classesGroups: `${prefix}/classes/groups`,
};

export class BakingApi {
  constructor(private request: ApiRequestInstance) {}

  // 作品集相关
  async getBakingRecords(params?: {
    recipeId?: string;
    userId?: string;
    keyword?: string;
    grade?: string;
    className?: string;
    sortBy?: string;
    order?: string;
    page?: number;
    perPage?: number;
  }): Promise<BakingRecordPagination> {
    const query = params
      ? {
          ...(params.recipeId ? { recipe_id: params.recipeId } : {}),
          ...(params.userId ? { user_id: params.userId } : {}),
          ...(params.keyword ? { keyword: params.keyword } : {}),
          ...(params.grade ? { grade: params.grade } : {}),
          ...(params.className ? { class_name: params.className } : {}),
          ...(params.sortBy ? { sort_by: params.sortBy } : {}),
          ...(params.order ? { order: params.order } : {}),
          ...(params.page ? { page: params.page } : {}),
          ...(params.perPage ? { per_page: params.perPage } : {}),
        }
      : {};
    const { data } = await this.request.get<BakingRecordPagination>(route(routes.bakingRecords, query));
    return data;
  }

  async getBakingRecord(id: string): Promise<BakingRecord> {
    const { data } = await this.request.get<BakingRecord>(routes.bakingRecord(id));
    return data;
  }

  async createBakingRecord(record: BakingRecordCreate): Promise<BakingRecord> {
    const { data } = await this.request.post<BakingRecord>(routes.bakingRecords, {
      recipe_id: record.recipeId,
      image_url: record.imageUrl,
      notes: record.notes,
    });
    return data;
  }

  async updateBakingRecord(id: string, record: BakingRecordUpdate): Promise<BakingRecord> {
    const { data } = await this.request.put<BakingRecord>(routes.bakingRecord(id), {
      image_url: record.imageUrl,
      notes: record.notes,
    });
    return data;
  }

  async markBakingRecordExcellent(id: string): Promise<BakingRecord> {
    const { data, error } = await this.request.put<BakingRecord, Record<string, never>>(routes.bakingRecordExcellent(id), {});
    if (!data) {
      throw error || new Error("设为精华失败");
    }
    return data;
  }

  // 评分评论相关
  async getRecipeRatings(recipeId: string): Promise<RecipeRating[]> {
    const { data } = await this.request.get<RecipeRating[]>(routes.recipeRatings(recipeId));
    return data;
  }

  async getMyRating(recipeId: string): Promise<RecipeRating | null> {
    const { data } = await this.request.get<RecipeRating | null>(routes.myRating(recipeId));
    return data;
  }

  async createRating(recipeId: string, rating: RecipeRatingCreate): Promise<RecipeRating> {
    const { data } = await this.request.post<RecipeRating>(routes.recipeRatings(recipeId), {
      recipe_id: recipeId,
      rating: rating.rating,
      comment: rating.comment,
    });
    return data;
  }

  async updateRating(recipeId: string, ratingId: string, rating: RecipeRatingUpdate): Promise<RecipeRating> {
    const { data } = await this.request.put<RecipeRating>(routes.recipeRating(recipeId, ratingId), {
      rating: rating.rating,
      comment: rating.comment,
    });
    return data;
  }

  async getRatingSummary(recipeId: string): Promise<RecipeRatingSummary> {
    const { data } = await this.request.get<RecipeRatingSummary>(routes.recipeRatingSummary(recipeId));
    return data;
  }

  // 积分签到相关
  async getMyPoints(): Promise<UserPoints> {
    const { data } = await this.request.get<UserPoints>(routes.pointsMe);
    return data;
  }

  async checkin(): Promise<CheckinResponse> {
    const { data } = await this.request.post<CheckinResponse>(routes.pointsCheckin, {});
    return data;
  }

  async getLeaderboard(limit: number = 10): Promise<UserPoints[]> {
    const { data } = await this.request.get<UserPoints[]>(route(routes.pointsLeaderboard, { limit }));
    return data;
  }

  async getCheckinHistory(): Promise<CheckinHistoryResponse> {
    const { data } = await this.request.get<CheckinHistoryResponse>(routes.pointsHistory);
    return data;
  }

  async getMyExperience(): Promise<UserExperience> {
    const { data } = await this.request.get<UserExperience>(routes.pointsExperienceMe);
    return data;
  }

  async getUsersExperience(userIds: string[]): Promise<UserExperienceBatch> {
    const query = userIds?.length ? { user_ids: userIds } : {};
    const { data } = await this.request.get<UserExperienceBatch>(route(routes.pointsExperienceUsers, query));
    return data;
  }

  async updateUserExperience(userId: string, totalExp: number): Promise<UserExperience> {
    const { data } = await this.request.put<UserExperience>(routes.pointsExperienceUser(userId), {
      total_exp: totalExp,
    });
    return data;
  }

  async getMyExperienceHistory(page: number = 1, perPage: number = 20): Promise<UserExperienceHistory> {
    const { data } = await this.request.get<UserExperienceHistory>(
      route(routes.pointsExperienceHistory, { page, per_page: perPage }),
    );
    return data;
  }

  // 投票相关
  async vote(vote: VoteRequest): Promise<VoteResponse> {
    const { data, error } = await this.request.post<VoteResponse>(routes.votes, {
      work_id: vote.workId,
      vote_type: vote.voteType,
    });
    if (!data) {
      throw error || new Error("投票失败");
    }
    return data;
  }

  async cancelVote(workId: string, voteType: string): Promise<VoteResponse> {
    const { data, error } = await this.request.delete<VoteResponse>(routes.voteCancel(workId, voteType));
    if (!data) {
      throw error || new Error("取消投票失败");
    }
    return data;
  }

  async getReceivedVotes(params?: { voteType?: "flower" | "egg"; page?: number; perPage?: number }): Promise<ReceivedVoteRecords> {
    const query = {
      vote_type: params?.voteType,
      page: params?.page,
      per_page: params?.perPage,
    };
    const { data } = await this.request.get<ReceivedVoteRecords>(route(routes.votesReceived, query));
    return data;
  }

  // 班级小组相关
  async getMyClass(): Promise<UserClass | null> {
    const { data } = await this.request.get<UserClass | null>(routes.classesMe);
    return data;
  }

  async updateMyClass(update: UserClassUpdate): Promise<UserClass> {
    const { data } = await this.request.put<UserClass>(routes.classesMe, {
      class_name: update.className,
      group_name: update.groupName,
    });
    return data;
  }

  async getClassList(): Promise<string[]> {
    const { data } = await this.request.get<string[]>(routes.classesList);
    return data;
  }

  async getBakingGradeList(): Promise<string[]> {
    const { data } = await this.request.get<string[]>(routes.bakingGrades);
    return data;
  }

  async getBakingClassList(grade?: string): Promise<string[]> {
    const { data } = await this.request.get<string[]>(
      route(routes.bakingClasses, grade ? { grade } : {}),
    );
    return data;
  }

  async getGroupList(className?: string): Promise<string[]> {
    const { data } = await this.request.get<string[]>(
      route(routes.classesGroups, className ? { class_name: className } : {}),
    );
    return data;
  }
}
