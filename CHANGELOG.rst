Changelog
---------

0.0.4 (2016-07-11)
~~~~~~~~~~~~~~~~~~

- Added init_hooks to base.Base
- Refactored sequence-based options to be defined in Base._seq_opts
- Added Type extensions:
    - Hashable
    - Tuple
- Added conf.vars
- Added coerce_hooks to base.Base

0.0.3 (2016-04-21)
~~~~~~~~~~~~~~~~~~

- Added syn.conf module
- Added syn.five module
- Added coerce() classmethod to base.Base
- Added Mapping Type extension

0.0.2 (2016-04-21)
~~~~~~~~~~~~~~~~~~

- Fixed type.MultiType typemap references for subclasses
- Added Type extensions:
    - Callable
    - Sequence
- Added attribute groups to base.Base
- Added base.Base class options:
    - id_equality
    - init_order
- Added base.Attr attributes:
    - group
    - groups
    - call
    - init
    - internal
- Added group-based excludes and includes to base.Base.to_dict()

0.0.1 (2016-04-17)
~~~~~~~~~~~~~~~~~~

Initial release.
