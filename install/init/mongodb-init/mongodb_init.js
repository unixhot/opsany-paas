//cmdb
db = db.getSiblingDB('cmdb')

db.createUser({
  user: 'cmdb',
  pwd: 'OpsAny@2020',
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
  pwd: 'OpsAny@2020',
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
  pwd: 'OpsAny@2020',
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
  pwd: 'OpsAny@2020',
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
  pwd: 'OpsAny@2020',
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
  pwd: 'OpsAny@2020',
  roles: [
    {
      role: 'readWrite',
      db: 'monitor',
    },
  ],
});