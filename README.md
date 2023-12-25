# Database initialization
Open psql shell and run
```
create database store;

create user ilyas with password ‘password’;

alter database store owner to ilyas;
```

In hobby_store/, run

```
make init
```

Now, database is initialized and site is ready to be used

# Running
```
make debug
```
