# Example Clean Arch Hero Context

Target: existing order management service.

Goal: gradually move order placement and payment confirmation toward Clean
Architecture + DDD while preserving public API behavior.

Constraints:

- no big-bang rewrite;
- keep current database schema;
- keep existing HTTP routes stable;
- add characterization tests before moving business rules;
- split batches by use case.
- treat Clean Architecture as dependency direction and responsibility rules,
  not a directory rename.
- do not create empty folders; create a layer/module only when a concrete
  responsibility exists.

First desired flow:

1. discover current commands and architecture;
2. create baseline report;
3. refactor one use case behind tests;
4. validate dependency direction;
5. produce a before/after map for any structural migration;
6. report next batches.
