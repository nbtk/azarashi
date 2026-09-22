"""The code tables the fields of a CAMF message index, whoever assigns the values.

CAMF defines most of them. Some it leaves to others: each country names its own providers for
A3, and a country's guidance library gives the sentences A11 indexes. They belong here all the
same, because any service carrying a CAMF message reads the same table, and a new service adds
entries rather than a table of its own.

What a service adds to CAMF, its own fields and their tables, belongs under that service.
"""
