//event
db = db.getSiblingDB('event')

db.createUser({
  user: 'event',
  pwd: 'MONGO_EVENT_PASSWORD',
  roles: [
    {
      role: 'readWrite',
      db: 'event',
    },
  ],
});
