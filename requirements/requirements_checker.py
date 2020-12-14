import json
from users.models import UsersGroups


class RequirementsChecker:
    ALL_TYPES = ['BELONGS_TO_ANY_OF', 'DOES_NOT_BELONG_TO_ANY_OF', 'BELONGS_EXACTLY_TO']
    def __init__(self, requirements):
        self.requirements = json.loads(requirements.requirement_json)

    def check(self, user):
        user_groups = list(map(lambda user: user.name, user.groups.all()))
        checks = set([self.check_single_requirement(requirement, user_groups) for requirement in self.requirements])
        return len(self.requirements) == 0 or True in checks and False not in checks

    def check_single_requirement(self, requirement, user_groups):
        if requirement['type'] == 'BELONGS_TO_ANY_OF':
            return len(set(requirement['groups']) - set(user_groups)) < len(requirement['groups'])
        elif requirement['type'] == 'DOES_NOT_BELONG_TO_ANY_OF':
            return len((set(user_groups) - set(requirement['groups']))) == 0
        elif requirement['type'] == 'BELONGS_EXACTLY_TO':
            return len(set(requirement['groups']) - set(user_groups)) == 0
        else:
            raise RuntimeError('Requirement "' + requirement['type'] + '" type not recognized')
