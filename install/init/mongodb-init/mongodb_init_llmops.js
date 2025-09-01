//auto
db = db.getSiblingDB('llmops')

db.createUser({
  user: 'llmops',
  pwd: 'MONGO_LLMOPS_PASSWORD',
  roles: [
    {
      role: 'readWrite',
      db: 'llmops',
    },
  ],
});
