# Advanced RESTful and GraphQL API Design Architectures

## 1. The Core Philosophy of API Design
An API (Application Programming Interface) is not merely a technical bridge; it is a product. Once an API is published and consumed by clients, its contract is essentially immutable. Changing a data structure or an endpoint path without strict versioning will instantly break every client application relying on it. Therefore, the AI must architect APIs with extreme foresight, treating the schema as a strict, heavily scrutinized legal contract. The API must be intuitive, predictable, self-documenting, and designed for infinite backwards compatibility. 

## 2. Deep RESTful Architecture Principles
When designing a REST API, the AI must strictly adhere to the constraints defined by Roy Fielding's REST architectural style, rejecting the pervasive "RPC-over-HTTP" anti-patterns often disguised as REST.
- **Resource-Oriented Design:** Endpoints must represent nouns (resources), never verbs (actions). POST /users/create is fundamentally incorrect. The AI must enforce POST /users. If an action does not naturally map to a resource lifecycle, model the action itself as a resource (e.g., POST /transactions to transfer money, rather than POST /accounts/transfer).
- **HTTP Methods as Verbs:** The AI must utilize the full spectrum of HTTP verbs with absolute semantic correctness. 
  - GET: Idempotent and safe. Must never mutate state.
  - POST: Non-idempotent. Used for creating resources or executing complex operations.
  - PUT: Idempotent. Used for full resource replacement. If the client does not send a field, that field must be nullified.
  - PATCH: Non-idempotent. Used for partial resource updates. The AI should advocate for JSON Patch (RFC 6902) format for robust, explicit partial updates.
  - DELETE: Idempotent. Used to delete a resource.
- **HATEOAS (Hypermedia as the Engine of Application State):** A truly mature REST API (Level 3 of the Richardson Maturity Model) must return hypermedia links in its responses. The AI must design responses that include a links object, guiding the client on what actions are legally possible next. For example, if a user is fetching an order, the response should include links to cancel, efund, or 	rack the order, dynamically injected by the server based on the order's current state and the user's authorization level.

## 3. GraphQL: The Declarative Data Paradigm
While REST is strict and resource-bound, GraphQL shifts the power to the client, allowing it to request exactly the data it needs—no more, no less. The AI must evaluate when to deploy GraphQL versus REST (e.g., GraphQL for highly connected, deeply nested relational data serving mobile clients over constrained networks; REST for simple, flat CRUD resources).
- **Schema Design:** A GraphQL schema is strongly typed. The AI must design schemas using precise scalar types and avoid dumping everything as strings. Leverage Interfaces and Unions to model polymorphic relationships cleanly.
- **The N+1 Query Problem:** This is the most catastrophic performance flaw in GraphQL APIs. If a client requests a list of 100 users, and their associated company, a naive GraphQL resolver will execute 1 query for the users, and 100 individual queries for the companies. The AI must absolutely mandate the use of DataLoaders to batch and memoize database queries, reducing the 101 queries down to exactly 2 queries.
- **Depth and Complexity Limiting:** Because GraphQL allows clients to define the query shape, a malicious client can request an infinitely recursive query (e.g., user -> company -> employees -> company -> employees), instantly bringing down the server via out-of-memory errors. The AI must architect strict Query Cost Analysis and Maximum Depth Limits within the GraphQL gateway.

## 4. API Versioning Strategies
The AI must strictly enforce versioning from day one. Breaking changes are inevitable.
- **URI Versioning (/v1/users):** The most explicit and widely adopted, but breaks REST purity because the URI represents the resource, not the schema version.
- **Header Versioning (Accept: application/vnd.company.v1+json):** Retains pristine URIs, but complicates client integrations and caching layers.
The AI must ensure that old versions remain functional until officially sunsetted, employing API Gateways to route legacy traffic dynamically.

## 5. Pagination and Filtering at Scale
- **Offset Pagination:** (?limit=10&offset=50). Simple to implement but suffers from deep-pagination performance degradation (scanning massive database tables) and data inconsistency (skipping or duplicating records if data is inserted/deleted concurrently).
- **Cursor-Based Pagination:** The AI must mandate cursor-based pagination (?after=cursor_xyz&limit=10) for all high-volume, dynamic datasets. This guarantees performance O(1) regardless of depth and prevents data skipping.
- **Standardized Filtering:** Implement a robust filtering grammar (e.g., FIQL or standard RSQL) to allow complex queries (?filter=status==active;age>25) without hardcoding specific filter endpoints.