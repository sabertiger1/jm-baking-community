"""用户班级和小组路由"""
from sqlalchemy import distinct, select

from mealie.routes._base import BaseUserController, controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.baking.classes import UserClassCreate, UserClassOut, UserClassUpdate

router = UserAPIRouter()


@controller(router)
class ClassesController(BaseUserController):
    @router.get("/me", response_model=UserClassOut | None)
    async def get_my_class(self):
        """获取当前用户的班级和小组信息"""
        user_class = self.repos.user_classes.get_one(self.user.id, "user_id")
        if not user_class:
            return None
        return UserClassOut.model_validate(user_class)

    @router.post("/me", response_model=UserClassOut, status_code=201)
    async def create_my_class(self, data: UserClassCreate):
        """创建或更新当前用户的班级和小组信息"""
        # 检查是否已存在
        existing = self.repos.user_classes.get_one(self.user.id, "user_id")
        
        if existing:
            # 更新现有记录
            update_data = data.model_dump(exclude_unset=True, exclude={"user_id"})
            for key, value in update_data.items():
                setattr(existing, key, value)
            self.repos.user_classes.update(existing.id, existing)
            return UserClassOut.model_validate(existing)
        else:
            # 创建新记录
            create_data = data.model_dump()
            create_data["user_id"] = self.user.id
            new_class = self.repos.user_classes.create(create_data)
            return UserClassOut.model_validate(new_class)

    @router.put("/me", response_model=UserClassOut)
    async def update_my_class(self, data: UserClassUpdate):
        """更新当前用户的班级和小组信息"""
        user_class = self.repos.user_classes.get_one(self.user.id, "user_id")
        if not user_class:
            # 如果不存在，创建新记录
            create_data = data.model_dump(exclude_unset=True)
            create_data["user_id"] = self.user.id
            user_class = self.repos.user_classes.create(create_data)
        else:
            # 更新现有记录
            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(user_class, key, value)
            self.repos.user_classes.update(user_class.id, user_class)
        
        return UserClassOut.model_validate(user_class)

    @router.get("/list", response_model=list[str])
    async def get_class_list(self):
        """获取所有班级列表（用于筛选）"""
        from mealie.db.models.baking.classes import UserClass
        
        # 查询所有不重复的班级名称
        stmt = select(distinct(UserClass.class_name)).where(
            UserClass.class_name.isnot(None),
            UserClass.class_name != ""
        )
        result = self.session.execute(stmt).scalars().all()
        
        # 转换为列表并排序
        class_list = sorted([name for name in result if name])
        return class_list

    @router.get("/groups", response_model=list[str])
    async def get_group_list(self, class_name: str | None = None):
        """获取小组列表（可按班级筛选）"""
        from mealie.db.models.baking.classes import UserClass
        
        # 构建查询
        stmt = select(distinct(UserClass.group_name)).where(
            UserClass.group_name.isnot(None),
            UserClass.group_name != ""
        )
        
        # 如果指定了班级，添加筛选条件
        if class_name:
            stmt = stmt.where(UserClass.class_name == class_name)
        
        result = self.session.execute(stmt).scalars().all()
        
        # 转换为列表并排序
        group_list = sorted([name for name in result if name])
        return group_list
