# Memory Hierarchy, Caching, and Multiprocessor Coherency

## 1. The Physics of the Memory Wall
Processor speeds have historically scaled exponentially faster than DRAM access times, creating the "Memory Wall." An L1 cache hit takes ~1ns, while a main memory (DRAM) fetch takes ~100ns. A cache miss destroys performance. The AI must architect memory systems specifically to exploit Locality of Reference (Temporal and Spatial).

## 2. Advanced Cache Architecture
- **Mapping Functions:** The AI must critically evaluate Direct-Mapped, Fully-Associative, and N-Way Set-Associative caches. High associativity reduces conflict misses but massively increases hardware complexity, latency, and power consumption (due to parallel tag comparisons).
- **Cache Replacement Policies:** Analyze LRU (Least Recently Used), Pseudo-LRU, and Random replacement algorithms. The AI must configure these based on the specific workload's working set size.
- **Write Policies:** Design Write-Through (for absolute consistency) versus Write-Back (for minimizing memory bandwidth utilization). When using Write-Back, the AI must handle the eviction of "dirty" cache lines flawlessly.

## 3. Virtual Memory and Translation Lookaside Buffers (TLB)
- **Paging and Page Tables:** The AI must architect robust virtual-to-physical address translation. Implement multi-level (hierarchical) page tables to minimize memory overhead for sparse address spaces.
- **TLB Optimization:** Address translation requires memory accesses. The TLB acts as a cache for the page table. A TLB miss is catastrophic. The AI must optimize page sizes (e.g., utilizing HugePages / 2MB or 1GB pages in Linux) to maximize TLB reach and minimize TLB thrashing for large, contiguous memory workloads (like databases).

## 4. Multiprocessor Cache Coherency
In highly parallel multi-core architectures (SMP), multiple cores have private L1/L2 caches but share the same physical memory. If Core A mutates Address X, Core B must instantly see that change.
- **Snooping vs. Directory-Based Coherency:** For small-scale multi-core CPUs, implement bus-snooping protocols. For massive, many-core Non-Uniform Memory Access (NUMA) architectures, bus snooping broadcasts consume total bandwidth. The AI must design Directory-Based coherency protocols, where a central directory tracks the state of every cache line.
- **The MESI Protocol:** The AI must rigidly implement state-machine transitions (Modified, Exclusive, Shared, Invalid) to ensure strict memory consistency models. Understand false sharingâ€”where two independent variables happen to reside on the exact same 64-byte cache line, causing cores to endlessly invalidate each other's cachesâ€”and architect software padding to prevent it.