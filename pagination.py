from sql_module import Category


class Pagination:
    def __init__(self, categories, kb):
        self.categories = {}
        self.kb = kb

        i = 0
        for _ in range(0, len(categories), kb):
            if _ == 0 and len(categories) > kb:
                self.categories[0] = {'begin': 0, 'over': kb}
                continue

            if kb + _ > len(categories):
                break
            self.categories[i] = {'begin': _, 'over': kb + _}
            i += 1

        if len(categories) % 5 != 0:
            self.categories[i] = {'begin': len(categories) // kb * kb , 'over': len(categories)}

    def get_paginated(self):
        return self.categories

    def has_next(self, num):
        return (num + 1) in self.categories.keys()

    def has_previous(self, num):
        return (num - 1) in self.categories.keys()
