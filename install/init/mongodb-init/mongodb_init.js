//cmdb
db = db.getSiblingDB('cmdb')

db.createUser({
  user: 'cmdb',
  pwd: 'MONGO_CMDB_PASSWORD',
  roles: [
    {
      role: 'readWrite',
      db: 'cmdb',
    },
  ],
});

//job
db = db.getSiblingDB('job')

db.createUser({
  user: 'job',
  pwd: 'MONGO_JOB_PASSWORD',
  roles: [
    {
      role: 'readWrite',
      db: 'job',
    },
  ],
});

//workbench
db = db.getSiblingDB('workbench')

db.createUser({
  user: 'workbench',
  pwd: 'MONGO_WORKBENCH_PASSWORD',
  roles: [
    {
      role: 'readWrite',
      db: 'workbench',
    },
  ],
});

//devops
db = db.getSiblingDB('devops')

db.createUser({
  user: 'devops',
  pwd: 'MONGO_DEVOPS_PASSWORD',
  roles: [
    {
      role: 'readWrite',
      db: 'devops',
    },
  ],
});

//cmp
db = db.getSiblingDB('cmp')

db.createUser({
  user: 'cmp',
  pwd: 'MONGO_CMP_PASSWORD',
  roles: [
    {
      role: 'readWrite',
      db: 'cmp',
    },
  ],
});

//monitor
db = db.getSiblingDB('monitor')

db.createUser({
  user: 'monitor',
  pwd: 'MONGO_MONITOR_PASSWORD',
  roles: [
    {
      role: 'readWrite',
      db: 'monitor',
    },
  ],
});

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