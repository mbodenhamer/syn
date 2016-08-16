Changelog
---------

0.0.11 (2016-08-16)
~~~~~~~~~~~~~~~~~~~
- Added syn.schema.sequence.Type for explicit type specifications
- Added repr template functionality to syn.base.b.Base
- Added Type random generation
- Added automatic metadata harvesting for sub-packages

0.0.10 (2016-08-12)
~~~~~~~~~~~~~~~~~~
- Added lazy sampling and enumeration to syn.sets
- Removed syn.sets.Complement
- Added syn.sets.Product
- Added syn.schema.sequence (syn.schema.b.sequence)

0.0.9 (2016-08-09)
~~~~~~~~~~~~~~~~~~
- Fixed setup.py for wheel

0.0.8 (2016-08-09)
~~~~~~~~~~~~~~~~~~
- Added display() and rst() methods to Type classes (syn.type.a)
- Added class member/invocation auto-documentation
- Added make_hashable functionality to Base
- Added syn.sets (syn.sets.b)

0.0.7 (2016-07-20)
~~~~~~~~~~~~~~~~~~
- Moved check_idempotence to syn.base.b.examine

0.0.6 (2016-07-20)
~~~~~~~~~~~~~~~~~~

- Added context management utilities to base_utils
- Moved metaclass data population code to base.b.meta
- Added rudimentary init functionality to base.a.Attr and base.a.Base
- Added register_subclass functionality
- Refactored (improved) internal hook processing
- Added setstate_hook functionality
- Added _aliases functionality
- Added base.b.Base.istr()
- Added syn.tree functionality (syn.tree.b)
- Added syn.type.This type for recursive type definitions

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
