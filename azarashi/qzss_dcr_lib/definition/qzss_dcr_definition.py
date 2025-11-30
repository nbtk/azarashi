import warnings


class QzssDcrDefinition(dict):
    def __init__(self,
                 default,
                 prefix=None,
                 prefix_extractor=None,
                 undefined=None,
                 *args,
                 **kwargs):
        super().__init__(default, *args, **kwargs)
        
        if (prefix is None) != (prefix_extractor is None):
            warnings.warn(
                "prefix and prefix_extractor should be both set or both None",
                RuntimeWarning,
                stacklevel=2
            )
        
        if undefined is not None and not isinstance(undefined, str) and prefix is not None:
            warnings.warn(
                "prefix is ignored when undefined is not a string",
                RuntimeWarning,
                stacklevel=2
            )
        
        self.prefix = prefix
        self.prefix_extractor = prefix_extractor
        self.undefined = undefined

    def __missing__(self, key):
        # for non-string undefined values, return as-is
        if self.undefined is not None and not isinstance(self.undefined, str):
            return self.undefined
        
        # for string values, apply formatting
        value = None
        
        if self.prefix and self.prefix_extractor:
            value = self.prefix.get(self.prefix_extractor(key))
            if value is not None:
                value = value % key
        
        if value is None and self.undefined is not None:
            value = self.undefined % key
        
        if value is None:
            raise KeyError(key)
        
        return value
