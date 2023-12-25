# Schema

1. passw: (id <pk, fk to users> (use sequence), password)
2. item: (id <pk>, name, seller (fk to users), n_total, n_sell <use trigger>, price)
3. buy: (user_id, item_id, n)
4. users: (id <pk>, name, surname, addr, phone, spent <use trigger>)

# Database initialization
Open psql shell and run
```
create database store;

create user ilyas with password ‘password’;

alter database store owner to ilyas;
```
