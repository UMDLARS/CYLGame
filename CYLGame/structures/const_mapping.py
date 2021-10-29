class ConstMapping:
    def __init__(self, seq=None, **kwargs):
        """
        dict() -> new empty dictionary
        dict(mapping) -> new dictionary initialized from a mapping object's
            (key, value) pairs
        dict(iterable) -> new dictionary initialized as if via:
            d = {}
            for k, v in iterable:
                d[k] = v
        dict(**kwargs) -> new dictionary initialized with the name=value pairs
            in the keyword argument list.  For example:  dict(one=1, two=2)
        # (copied from class doc)
        """
        self.name_to_val_mapping = {}
        self.val_to_name_mapping = {}
        if isinstance(seq, dict):
            for v, k in seq.items():
                self[v] = k
        elif kwargs:
            for v, k in kwargs:
                self[v] = k
        else:
            for v, k in seq:
                self[v] = k

    def update(self, other):
        for var, val in other.items():
            self[var] = val

    @property
    def names(self):
        return self.name_to_val_mapping.keys()

    @property
    def values(self):
        return self.name_to_val_mapping.values()

    def __iter__(self):
        return iter(self.name_to_val_mapping.items())

    def __contains__(self, item):
        return item in self.name_to_val_mapping or item in self.val_to_name_mapping

    def __getitem__(self, item):
        if isinstance(item, str):
            return self.name_to_val_mapping[item]
        elif isinstance(item, int):
            return self.val_to_name_mapping[item]
        raise TypeError()

    def __setitem__(self, key, value):
        # TODO: assert key is a valid littlepython variable name.
        assert isinstance(key, str), "Key must be a variable name"
        assert isinstance(value, int), "Only valid value is an int currently"

        if key in self.name_to_val_mapping:
            old_value = self.name_to_val_mapping[key]
            del self.name_to_val_mapping[key]
            del self.val_to_name_mapping[old_value]
        assert value not in self.val_to_name_mapping, "This is a one-to-one mapping"

        self.name_to_val_mapping[key] = value
        self.val_to_name_mapping[value] = key

    def __delitem__(self, key):
        value = self.name_to_val_mapping[key]
        del self.name_to_val_mapping[key]
        del self.val_to_name_mapping[value]

    def __len__(self):
        return len(self.name_to_val_mapping)
