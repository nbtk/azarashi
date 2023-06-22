class QzssDcrDefinition(dict):
    def __init__(self,
                 default,
                 prefix=None,
                 prefix_extractor=None,
                 undefined=None,
                 *args,
                 **kwargs):
        super().__init__(default, *args, **kwargs)
        self.prefix = prefix
        self.prefix_extractor = prefix_extractor
        self.undefined = undefined

    def __missing__(self, key):
        value = None

        if self.prefix and self.prefix_extractor:
            value = self.prefix.get(self.prefix_extractor(key))
            if value is not None:
                value = value % key

        if value is None and self.undefined:
            value = self.undefined % key

        if value is None:
            raise KeyError(key)

        return value
