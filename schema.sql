begin;

drop table if exists users cascade;
drop table if exists passwords cascade;

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

alter table passwords add foreign key(id) references users(id)
    on delete cascade;

drop table if exists items cascade;

create table items (
    id int primary key not null,
    name varchar(25) not null,
    seller int not null,
    n_total int not null,
    n_sold int not null default 0,
    price numeric not null,
    color varchar(25)
);

drop sequence if exists items_ids;
create sequence items_ids start 0 increment 1 minvalue 0;

insert into items values(nextval('items_ids'), 'candle', 9, 3, 0, 1.2, 'Red');
insert into items values(nextval('items_ids'), 'soap', 7, 2, 0, 6.5);
insert into items values(nextval('items_ids'), 'necklace', 2, 4, 0, 19.2, 'White');
insert into items values(nextval('items_ids'), 'knitting work', 3, 1, 0, 60, 'Blue');
insert into items values(nextval('items_ids'), 'carpet', 5, 10, 0, 679.9);
insert into items values(nextval('items_ids'), 'bracelet', 9, 2, 0, 9.9, 'Red');
insert into items values(nextval('items_ids'), 'portrait', 2, 3, 0, 990.9);
insert into items values(nextval('items_ids'), 'soap', 6, 10, 0, 7.6, 'Green');
insert into items values(nextval('items_ids'), 'bracelet', 6, 2, 0, 8.1, 'White');
insert into items values(nextval('items_ids'), 'necklace', 1, 2, 0, 50);
insert into items values(nextval('items_ids'), 'candle', 7, 4, 0, 100, 'Black');

create or replace function check_duplicates() returns boolean as $$
    declare
        more_than_three cursor for
            select
                name, count(*)
            from
                items
            group by
                name
            having
                count(*) >= 3;
        count int := 0;
        res boolean := true;
    begin
        for i in more_than_three loop
            count = count + 1;
        end loop;
        if count > 0 then
            res = false;
        end if;
        raise notice 'res: %', res;
        return res;
    end;
$$ language 'plpgsql';

alter table items add foreign key(seller) references users(id) on delete cascade;
alter table items add constraint sold_less_than_tot check(n_total >= n_sold);
alter table items add constraint less_than_4_same_name check(check_duplicates());

drop table if exists buy cascade;

create table buy (
    transaction_id int not null,
    user_id int not null,
    item_id int not null,
    n int not null
);

drop sequence if exists buy_sequence;
create sequence buy_sequence start 0 increment 1 minvalue 0;

alter table buy add primary key(transaction_id);
alter table buy add foreign key(user_id) references users(id) on delete cascade;
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

insert into buy values(nextval('buy_sequence'), 0, 9, 1);
insert into buy values(nextval('buy_sequence'), 1, 8, 2);
insert into buy values(nextval('buy_sequence'), 2, 7, 2);
insert into buy values(nextval('buy_sequence'), 3, 6, 2);
insert into buy values(nextval('buy_sequence'), 4, 5, 2);
insert into buy values(nextval('buy_sequence'), 5, 4, 1);
insert into buy values(nextval('buy_sequence'), 6, 3, 1);
insert into buy values(nextval('buy_sequence'), 7, 2, 2);
insert into buy values(nextval('buy_sequence'), 8, 1, 2);
insert into buy values(nextval('buy_sequence'), 9, 0, 2);

create view item_name_sorted as
select items.id as id, items.name as item_name,
        users.name as seller_name, n_total, n_sold, price, color
        from items, users where items.seller = users.id
order by item_name;

create view seller_name_sorted as
select items.id as id, items.name as item_name,
        users.name as seller_name, n_total, n_sold, price, color
        from items, users where items.seller = users.id
order by seller_name;

create view n_total_sorted as
select items.id as id, items.name as item_name,
        users.name as seller_name, n_total, n_sold, price, color
        from items, users where items.seller = users.id
order by n_total;

create view n_sold_sorted as
select items.id as id, items.name as item_name,
        users.name as seller_name, n_total, n_sold, price, color
        from items, users where items.seller = users.id
order by n_sold;

create view price_sorted as
select items.id as id, items.name as item_name,
        users.name as seller_name, n_total, n_sold, price, color
        from items, users where items.seller = users.id
order by price;

drop function search(text);
create or replace function search(query text) returns table (
    id int,
    name varchar(25),
    seller_name varchar(25),
    n_total int,
    n_sold int,
    price numeric,
    color varchar(25)
) as $$
    declare
        rec record;
        matches cursor for
            select
                items.id as id, items.name as name, users.name as seller_name,
                items.n_total as n_total, items.n_sold as n_sold,
                items.price as price, items.color as color
            from items, users
            where items.seller = users.id and
                    items.name like query;
    begin
        for rec in matches loop
            id = rec.id;
            name = rec.name;
            seller_name = rec.seller_name;
            n_total = rec.n_total;
            n_sold = rec.n_sold;
            price = rec.price;
            color = rec.color;
            return next;
        end loop;
    end;
$$ language 'plpgsql';

drop function filter_by_color(text);
create or replace function filter_by_color(filter_color text) returns table (
    id int,
    name varchar(25),
    seller_name varchar(25),
    n_total int,
    n_sold int,
    price numeric,
    color varchar(25)
) as $$
    declare
        rec record;
        matches cursor for
            select
                items.id as id, items.name as name, users.name as seller_name,
                items.n_total as n_total, items.n_sold as n_sold,
                items.price as price, items.color as color
            from items, users
            where items.seller = users.id and
                    items.color = filter_color;
    begin
        for rec in matches loop
            id = rec.id;
            name = rec.name;
            seller_name = rec.seller_name;
            n_total = rec.n_total;
            n_sold = rec.n_sold;
            price = rec.price;
            color = rec.color;
            return next;
        end loop;
    end;
$$ language 'plpgsql';

drop function fetch_items_in_range(int, int);
create or replace function fetch_items_in_range(min_ int, max_ int) returns table (
    id int,
    name varchar(25),
    seller_name varchar(25),
    n_total int,
    n_sold int,
    price numeric,
    color varchar(25)
) as $$
    declare
        rec record;
        matches cursor for
            (select
                items.id as id, items.name as name, users.name as seller_name,
                items.n_total as n_total, items.n_sold as n_sold,
                items.price as price, items.color as color
            from items, users
            where items.price >= min_ and items.seller = users.id)
            intersect
            (select
                items.id as id, items.name as name, users.name as seller_name,
                items.n_total as n_total, items.n_sold as n_sold,
                items.price as price, items.color as color
            from items, users
            where items.price <= max_ and items.seller = users.id);
    begin
        for rec in matches loop
            id = rec.id;
            name = rec.name;
            seller_name = rec.seller_name;
            n_total = rec.n_total;
            n_sold = rec.n_sold;
            price = rec.price;
            color = rec.color;
            return next;
        end loop;
    end;
$$ language 'plpgsql';

end;
