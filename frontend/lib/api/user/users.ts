import { BaseCRUDAPI } from "../base/base-clients";
import type {
  ChangePassword,
  DeleteTokenResponse,
  LongLiveTokenIn,
  LongLiveTokenOut,
  ResetPassword,
  UserBase,
  UserIn,
  UserOut,
  UserRatingOut,
  UserRatingSummary,
} from "~/lib/api/types/user";
import type {
  UserDetails,
  UserDetailsPublic,
  UserDetailsCompleteCheck,
  CompleteProfileRequest,
  UserDetailsUpdate,
} from "./user-details";

export interface UserRatingsSummaries {
  ratings: UserRatingSummary[];
}

export interface UserRatingsOut {
  ratings: UserRatingOut[];
}

const prefix = "/api";

const routes = {
  usersSelf: `${prefix}/users/self`,
  ratingsSelf: `${prefix}/users/self/ratings`,
  passwordReset: `${prefix}/users/reset-password`,
  passwordChange: `${prefix}/users/password`,
  users: `${prefix}/users`,

  usersIdImage: (id: string) => `${prefix}/users/${id}/image`,
  usersIdResetPassword: (id: string) => `${prefix}/users/${id}/reset-password`,
  usersId: (id: string) => `${prefix}/users/${id}`,
  usersIdFavorites: (id: string) => `${prefix}/users/${id}/favorites`,
  usersIdFavoritesSlug: (id: string, slug: string) => `${prefix}/users/${id}/favorites/${slug}`,
  usersIdRatings: (id: string) => `${prefix}/users/${id}/ratings`,
  usersIdRatingsSlug: (id: string, slug: string) => `${prefix}/users/${id}/ratings/${slug}`,
  usersRecipeRatings: (slug: string) => `${prefix}/users/recipe/${slug}/ratings`,
  usersSelfFavoritesId: (id: string) => `${prefix}/users/self/favorites/${id}`,
  usersSelfRatingsId: (id: string) => `${prefix}/users/self/ratings/${id}`,

  usersApiTokens: `${prefix}/users/api-tokens`,
  usersApiTokensTokenId: (token_id: string | number) => `${prefix}/users/api-tokens/${token_id}`,
  
  // User Details
  userDetailsMe: `${prefix}/users/me/details`,
  userDetailsMeComplete: `${prefix}/users/me/details/complete`,
  userDetailsMeCheck: `${prefix}/users/me/details/check`,
  userDetailsPublic: (user_id: string) => `${prefix}/users/${user_id}/details/public`,
  userDetailsAdmin: (user_id: string) => `${prefix}/users/${user_id}/details`,
};

export class UserApi extends BaseCRUDAPI<UserIn, UserOut, UserBase> {
  baseRoute: string = routes.users;
  itemRoute = (itemid: string) => routes.usersId(itemid);

  async addFavorite(id: string, slug: string) {
    return await this.requests.post(routes.usersIdFavoritesSlug(id, slug), {});
  }

  async removeFavorite(id: string, slug: string) {
    return await this.requests.delete(routes.usersIdFavoritesSlug(id, slug));
  }

  async getFavorites(id: string) {
    return await this.requests.get<UserRatingsOut>(routes.usersIdFavorites(id));
  }

  async getSelfFavorites() {
    return await this.requests.get<UserRatingsSummaries>(routes.ratingsSelf);
  }

  async getSelf() {
    return await this.requests.get<UserOut>(routes.usersSelf);
  }

  async getRatings(id: string) {
    return await this.requests.get<UserRatingsOut>(routes.usersIdRatings(id));
  }

  async setRating(id: string, slug: string, rating: number | null, isFavorite: boolean | null) {
    return await this.requests.post(routes.usersIdRatingsSlug(id, slug), { rating, isFavorite });
  }

  async getSelfRatings() {
    return await this.requests.get<UserRatingsSummaries>(routes.ratingsSelf);
  }

  async getRecipeRatings(slug: string) {
    return await this.requests.get<UserRatingsOut>(routes.usersRecipeRatings(slug));
  }

  async changePassword(changePassword: ChangePassword) {
    return await this.requests.put(routes.passwordChange, changePassword);
  }

  async createAPIToken(tokenName: LongLiveTokenIn) {
    return await this.requests.post<LongLiveTokenOut>(routes.usersApiTokens, tokenName);
  }

  async deleteAPIToken(tokenId: number) {
    return await this.requests.delete<DeleteTokenResponse>(routes.usersApiTokensTokenId(tokenId));
  }

  userProfileImage(id: string) {
    if (!id || id === undefined) return;
    return `/api/media/users/${id}/profile.webp`;
  }

  async resetPassword(payload: ResetPassword) {
    return await this.requests.post(routes.passwordReset, payload);
  }

  // User Details Methods
  async getUserDetails() {
    return await this.requests.get<UserDetails | null>(routes.userDetailsMe);
  }

  async completeProfile(data: CompleteProfileRequest) {
    return await this.requests.post<UserDetails>(routes.userDetailsMeComplete, {
      real_name: data.realName,
      grade: data.grade,
      class_name: data.className,
      avatar_url: data.avatarUrl,
    });
  }

  async updateUserDetails(data: UserDetailsUpdate) {
    return await this.requests.put<UserDetails>(routes.userDetailsMe, {
      real_name: data.realName,
      grade: data.grade,
      class_name: data.className,
      avatar_url: data.avatarUrl,
    });
  }

  async updateSelfDetails(data: UserDetailsUpdate) {
    return await this.updateUserDetails(data);
  }

  async getUserDetailsCheck() {
    return await this.requests.get<UserDetailsCompleteCheck>(routes.userDetailsMeCheck);
  }

  async getUserDetailsPublic(userId: string) {
    return await this.requests.get<UserDetailsPublic>(routes.userDetailsPublic(userId));
  }

  async getUserDetailsAdmin(userId: string) {
    return await this.requests.get<UserDetails>(routes.userDetailsAdmin(userId));
  }

  async updateUserDetailsAdmin(userId: string, data: UserDetailsUpdate) {
    return await this.requests.put<UserDetails>(routes.userDetailsAdmin(userId), {
      real_name: data.realName,
      grade: data.grade,
      class_name: data.className,
      avatar_url: data.avatarUrl,
    });
  }
}
