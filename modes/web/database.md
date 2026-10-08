# Database Architecture
- Relational (PostgreSQL, MySQL, SQLite) for ACID transactions, structured relational entities.
- Document/NoSQL (MongoDB, Redis) for caches, sessions, unstructured documents.
- Always use migrations (Prisma, Alembic, Drizzle, TypeORM, Knex). Never alter production schemas manually.
- Index foreign keys and frequently queried filters.
