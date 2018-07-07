# -*- coding: utf-8 -*-


class Codes(object):
    def __init__(self, **kws):
        self._reverse_dict = {}
        for k, v in kws.items():
            self.__setattr__(k, v)

    def str_value(self, value):
        return self._reverse_dict[value]

    def __setattr__(self, name, value):
        super(Codes, self).__setattr__(name, value)
        if not name.startswith("_"):
            self._reverse_dict[value] = name

    def __repr__(self):
        constants_str = ", ".join(
            f"{v}={k!r}" for k, v in sorted(self._reverse_dict.items())
        )
        return f"Codes({constants_str})"

    def __getitem__(self, key):
        return self.__dict__[key.replace("-", "_").upper()]
