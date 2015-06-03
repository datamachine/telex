from abc import ABCMeta, abstractmethod

class IAuthManager(metaclass=ABCMeta):
    @abstractmethod
    def get_groups(self):
        return NotImplemented

    @abstractmethod
    def get_users_from_group(self, group):
        return NotImplemented

    @abstractmethod
    def set_group(self, group, users):
        return NotImplemented

    @abstractmethod
    def remove_group(self, group):
        raise NotImplemented

    def add_user_to_group(self, group, user):
        users = set(self.get_users_from_group(group))
        users.add(user)
        self.set_group(group, users)

    def remove_user_from_group(self, group, user):
        users = set(self.get_users_from_group(group))
        if user in users:
            users.remove(user)
        self.set_group(group, users)

    def group_has_user(self, group, user):
        return user in self.get_users_from_group(group)

    def groups_has_user(self, groups, user):
        for group in groups:
            if self.group_has_user(group, user):
                return True
        return False

