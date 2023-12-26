begin;

drop table if exists users cascade;
drop table if exists passwords;

create table users (
    id int primary key not null,
    name varchar(25) not null unique,
    surname varchar(25),
    addr varchar(150),
    phone varchar(20),
    spent int not null default 0
);

create table passwords (
    id int primary key not null,
    passw varchar(20) not null
);

drop sequence if exists users_ids;
create sequence users_ids start 0 increment 1 minvalue 0;

insert into users values(nextval('users_ids'),
    'name_0', 'surname_0', 'address_0', 'phone_0');
insert into users values(nextval('users_ids'),
    'name_1', 'surname_1', 'address_1', 'phone_1', 200);
insert into users values(nextval('users_ids'),
    'name_2', NULL, NULL, NULL, 300);
insert into users values(nextval('users_ids'),
    'name_3', NULL, NULL, NULL, 400);
insert into users values(nextval('users_ids'),
    'name_4', NULL, NULL, NULL, 500);
insert into users values(nextval('users_ids'),
    'name_5', NULL, NULL, NULL, 600);
insert into users values(nextval('users_ids'),
    'name_6', NULL, NULL, NULL, 700);
insert into users values(nextval('users_ids'),
    'name_7', NULL, NULL, NULL, 800);
insert into users values(nextval('users_ids'),
    'name_8', NULL, NULL, NULL, 900);
insert into users values(nextval('users_ids'),
    'name_9', NULL, NULL, NULL, 1000);

alter sequence users_ids restart with 0;

insert into passwords values(nextval('users_ids'), 'passw_0');
insert into passwords values(nextval('users_ids'), 'passw_1');
insert into passwords values(nextval('users_ids'), 'passw_2');
insert into passwords values(nextval('users_ids'), 'passw_3');
insert into passwords values(nextval('users_ids'), 'passw_4');
insert into passwords values(nextval('users_ids'), 'passw_5');
insert into passwords values(nextval('users_ids'), 'passw_6');
insert into passwords values(nextval('users_ids'), 'passw_7');
insert into passwords values(nextval('users_ids'), 'passw_8');
insert into passwords values(nextval('users_ids'), 'passw_9');

alter table passwords add foreign key(id) references users(id);

drop table if exists items cascade;

create table items (
    id int primary key not null,
    name varchar(25) not null,
    seller int not null,
    n_total int not null,
    n_sold int not null default 0,
    price numeric not null
);

drop sequence if exists items_ids;
create sequence items_ids start 0 increment 1 minvalue 0;

insert into items values(nextval('items_ids'), 'candle', 9, 3, 0, 1.2);
insert into items values(nextval('items_ids'), 'soap', 7, 2, 0, 6.5);
insert into items values(nextval('items_ids'), 'necklace', 2, 4, 0, 19.2);
insert into items values(nextval('items_ids'), 'knitting work', 3, 1, 0, 60);
insert into items values(nextval('items_ids'), 'carpet', 5, 10, 0, 679.9);
insert into items values(nextval('items_ids'), 'bracelet', 9, 2, 0, 9.9);
insert into items values(nextval('items_ids'), 'portrait', 2, 3, 0, 990.9);
insert into items values(nextval('items_ids'), 'soap', 6, 10, 0, 7.6);
insert into items values(nextval('items_ids'), 'bracelet', 6, 2, 0, 8.1);
insert into items values(nextval('items_ids'), 'necklace', 1, 2, 0, 50);

alter table items add foreign key(seller) references users(id);
alter table items add constraint sold_less_than_tot check(n_total >= n_sold);

drop table if exists buy;

create table buy (
    user_id int not null,
    item_id int not null,
    n int not null
);

alter table buy add foreign key(user_id) references users(id);
alter table buy add foreign key(item_id) references items(id);
alter table buy add constraint positive_n check(n > 0);

create or replace function update_sold() returns trigger as $$
    begin
        update items
        set n_sold = n_sold + new.n
        where items.id = new.item_id;
        return new;
    end;
$$ language 'plpgsql';

create or replace trigger trig_update_sold after insert on buy
    for each row
    execute function update_sold();

insert into buy values(0, 9, 1);
insert into buy values(1, 8, 2);
insert into buy values(2, 7, 2);
insert into buy values(3, 6, 2);
insert into buy values(4, 5, 2);
insert into buy values(5, 4, 1);
insert into buy values(6, 3, 1);
insert into buy values(7, 2, 2);
insert into buy values(8, 1, 2);
insert into buy values(9, 0, 2);

end;
