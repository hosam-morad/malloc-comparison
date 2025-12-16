# mallocs/

Builds (or imports) the allocator shared libraries used by the framework.

## What `make mallocs` does

* Initializes git submodules (allocator sources)
* Runs CMake in `mallocs/build/` to discover/build allocators
* Copies a prebuilt standalone allocator into the build output
* Generates a sorted allocator list

## Allocators

* Built via CMake: `dlmalloc`, `mimalloc` (and anything else CMake adds via `versions.mk`)
* Imported (copy only): `malloc-standalone` from:
  `../malloc-standalone/build/libmalloc_try.so`

## Outputs

* Shared libs:

  * `mallocs/build/lib/lib<allocator>.so`
  * includes `libmalloc-standalone.so`
* Allocator names list:

  * `mallocs/malloc_list.txt`

## Useful targets

```bash
make mallocs-submodules   # init/update submodules
make mallocs              # build/copy libs + write malloc_list.txt
```
