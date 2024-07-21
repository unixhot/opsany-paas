//auto
db = db.getSiblingDB('auto')

db.createUser({
  user: 'auto',
  pwd: 'MONGO_AUTO_PASSWORD',
  roles: [
    {
      role: 'readWrite',
      db: 'auto',
    },
  ],
});

//prom
db = db.getSiblingDB('prom')

db.createUser({
  user: 'prom',
  pwd: 'MONGO_PROM_PASSWORD',
  roles: [
    {
      role: 'readWrite',
      db: 'prom',
    },
  ],
});

//kbase
db = db.getSiblingDB('kbase')

db.createUser({
  user: 'kbase',
  pwd: 'MONGO_KBASE_PASSWORD',
  roles: [
    {
      role: 'readWrite',
      db: 'kbase',
    },
  ],
});
