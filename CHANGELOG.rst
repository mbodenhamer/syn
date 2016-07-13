Changelog
---------

0.0.5 (2016-07-12)
~~~~~~~~~~~~~~~~~~

- Added conversion classmethods to Base:
    - from_object()
    - from_mapping()
    - from_sequence()
- Added _data member to Base for metaclass-populated values
- Fixed bug in _seq_opts propagation
- Added _seq_opts.metaclass_lookup functionality
- Changed init_hooks and coerce_hooks over to metaclass_lookup (allows subclasses to override hooks)
- Added create_hook functionality
- Added hook decorators:
    - init_hook
    - coerce_hook
    - create_hook
- Removed 3.3 as a supported version

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
