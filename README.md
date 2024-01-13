# Demo

[video.webm](https://github.com/1lyasm/hobby_store/assets/84722851/3aed8914-add3-4d74-a968-7fd3b92f61e3)

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
